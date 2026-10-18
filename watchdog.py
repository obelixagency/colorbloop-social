"""Colorbloop posting watchdog (same pattern as the Unshaken engine).
Runs every 30 min from .github/workflows/watchdog.yml. For every calendar.json entry whose time
(US Eastern, DST-safe via zoneinfo) has passed:
  - posts it to every platform for its kind that hasn't succeeded yet (retry with cooldown);
  - entries with "requires_link" (e.g. "amazon:abc") wait until links.json has that link, so a book is
    never promoted before it is live; they then go out on the next run;
  - NOTHING posts before launch: the first run that finds any Amazon link in links.json records that ET date
    as "_launch" in publish_log.json, and every calendar date is shifted so PLAN_START lands on launch day;
  - a non-gated entry still unposted STALE_HOURS after its time -> exit 1 (GitHub emails the repo owner).
"""
import datetime as dt, json, os, sys
from zoneinfo import ZoneInfo
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import publish as PUB

ET = ZoneInfo("America/New_York")
LOG = os.path.join(HERE, "publish_log.json")
STALE_HOURS = 2.5
RETRY_COOLDOWN_MIN = 25
PLAN_START = dt.date(2026, 10, 19)   # the date calendar.json was written against
PLATFORMS = {
    "post": ["instagram_post", "facebook_post"],
    "carousel": ["instagram_carousel", "facebook_carousel"],
    "reel": ["instagram_reel", "facebook_reel", "youtube_short", "instagram_story", "facebook_story"],
    "story": ["instagram_story", "facebook_story"],
}
ENABLED = set(os.environ.get("PLATFORMS", "instagram,facebook").split(","))


def load(p, d): return json.load(open(p)) if os.path.exists(p) else d


def link_for(links, key):
    if not key: return ""
    if ":" in key:
        shop, book = key.split(":", 1)
        return (links.get(shop) or {}).get(book, "")
    return links.get(key, "")


def caption_for(entry, links, platform):
    c = entry.get("caption")
    if not c: return ""
    url = link_for(links, c.get("link_key"))
    etsy = link_for(links, "etsy:" + c["link_key"].split(":", 1)[1]) if (c.get("link_key") or "").startswith("amazon:") else ""
    if c.get("link_key") and not url:
        cta = "Coming soon! Follow @color.bloop so you don't miss it."
    elif (platform.startswith("facebook") or platform.startswith("youtube")) and url:
        cta = f"📚 Get it here: {url}" + (f"\n🖨️ Printable PDF on Etsy: {etsy}" if etsy else "")
    elif url:
        cta = "📚 Tap the link in our bio to get it!"
    else:
        cta = "Follow @color.bloop for new books & coloring fun!"
    return c["text"].replace("{cta}", cta)


def run(now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    cal = json.load(open(os.path.join(HERE, "calendar.json")))
    links = load(os.path.join(HERE, "links.json"), {})
    log = load(LOG, {})
    if not log.get("_launch"):
        if not any((links.get("amazon") or {}).values()):
            print("Not launched yet: no Amazon link in links.json -> nothing to post."); return 0
        log["_launch"] = now.astimezone(ET).date().isoformat()
        print("LAUNCH day recorded:", log["_launch"])
    shift = dt.date.fromisoformat(log["_launch"]) - PLAN_START
    escalate = []
    caught_up = set()      # at most one LATE entry per kind per run, so a backlog trickles out instead of flooding
    for e in cal:
        due = (dt.datetime.fromisoformat(e["when_et"]) + shift).replace(tzinfo=ET).astimezone(dt.timezone.utc)
        if now < due: continue
        if e.get("requires_link") and not link_for(links, e["requires_link"]):
            continue                                           # book not live yet -> wait
        row = log.setdefault(e["id"], {})
        late_h = (now - due).total_seconds() / 3600
        done = all(row.get(p, {}).get("status") == "ok" for p in PLATFORMS[e["kind"]] if p.split("_")[0] in ENABLED)
        if not done and late_h > 2:
            if e["kind"] in caught_up: continue
            caught_up.add(e["kind"])
        files = [os.path.join(HERE, "assets", f) for f in e["files"]]
        for platform in PLATFORMS[e["kind"]]:
            if platform.split("_")[0] not in ENABLED: continue
            st = row.get(platform, {"status": "pending", "attempts": 0})
            if st["status"] == "ok": continue
            last = st.get("last_attempt")
            if last and (now - dt.datetime.fromisoformat(last)).total_seconds() < RETRY_COOLDOWN_MIN * 60: continue
            target = files if platform.endswith("carousel") else files[0]
            if platform.endswith("story") and e["kind"] == "story": cap = ""
            else: cap = caption_for(e, links, platform)
            ok, detail = PUB.publish(platform, target, cap)
            st.update(status="ok" if ok else "failed", detail=detail, attempts=st["attempts"] + 1, last_attempt=now.isoformat())
            row[platform] = st
            print(f'{e["id"]} {platform}: {st["status"]}' + ("" if ok else f' ({detail.get("message", "")[:120]})'))
        late = (now - due).total_seconds() / 3600
        bad = [p for p, s in row.items() if s["status"] != "ok" and s.get("detail", {}).get("error") != "not_connected"]
        if late >= STALE_HOURS and bad and not e.get("requires_link"):
            escalate.append((e["id"], round(late, 1), bad))
    json.dump(log, open(LOG, "w"), indent=1, ensure_ascii=False)
    if escalate:
        print("ESCALATE:", escalate); return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
