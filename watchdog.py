"""Colorbloop posting watchdog (same pattern as the Unshaken engine).
Runs every 30 min from .github/workflows/watchdog.yml. For every calendar.json entry whose time
(US Eastern, DST-safe via zoneinfo) has passed:
  - posts it to every platform for its kind that hasn't succeeded yet (retry with cooldown);
  - NOTHING posts before launch: the first run that finds any Amazon link in links.json records that ET date
    as "_launch" in publish_log.json, and every absolute calendar date ("when_et") is shifted so PLAN_START
    lands on launch day;
  - absolute entries with "requires_link" (e.g. "amazon:abc") wait until links.json has that link;
  - PER-BOOK entries {"book": "<key>", "day": N, "time": "HH:MM"} are scheduled relative to the day that
    book went live: the first run that sees amazon.<key> non-empty records "_live_<key>" (ET date) in the log.
    If that run is already past the book's first day-0 slot, the live date is the NEXT day, so a link added
    in the afternoon never makes day-0 posts fire late. Books go live one by one over weeks, so each book's
    launch plan starts when *its* link appears instead of all its past entries firing at once;
  - slot de-collision (deterministic, recomputed each run): absolute entries keep their time; per-book entries
    are placed after them, books in the order they went live, and an entry whose slot is taken moves +1 day
    until free. Slots: one reel per day, one feed post/carousel per day, one story per day+time.
    So two books going live the same day get the 2nd book's posts shifted, and launch reels never collide;
  - at most one LATE (>2 h) entry per kind per run, so any backlog trickles out instead of flooding;
  - an entry still failing STALE_HOURS after its time -> exit 1 (GitHub emails the repo owner).
    Missing secrets ("not_connected", e.g. YouTube not set up) never escalate.
"""
import datetime as dt, json, os, sys
from zoneinfo import ZoneInfo
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import publish as PUB

ET = ZoneInfo("America/New_York")
LOG = os.path.join(HERE, "publish_log.json")
CAL = os.path.join(HERE, "calendar.json")
LINKS = os.path.join(HERE, "links.json")
STALE_HOURS = 2.5
RETRY_COOLDOWN_MIN = 25
PLAN_START = dt.date(2026, 10, 19)   # the date calendar.json's absolute entries were written against
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


def _at(date, hhmm):
    h, m = map(int, hhmm.split(":"))
    return dt.datetime(date.year, date.month, date.day, h, m, tzinfo=ET)


def _slot(kind, when):
    d = when.date().isoformat()
    if kind == "reel": return ("reel", d)
    if kind in ("post", "carousel"): return ("feed", d)
    return (kind, d, when.strftime("%H:%M"))


def record_live(cal, links, log, now):
    """First sighting of a book's Amazon link -> "_live_<key>" (ET date) + its place in "_live_seq"."""
    now_et = now.astimezone(ET)
    seq = log.setdefault("_live_seq", [])
    books = []
    for e in cal:
        if e.get("book") and e["book"] not in books: books.append(e["book"])
    for b in books:
        if f"_live_{b}" in log or not link_for(links, f"amazon:{b}"): continue
        day0 = [e["time"] for e in cal if e.get("book") == b and int(e["day"]) == 0]
        live = now_et.date()
        if day0 and now_et >= _at(live, min(day0)):
            live += dt.timedelta(days=1)          # too late today for the day-0 posts -> start tomorrow
        log[f"_live_{b}"] = live.isoformat()
        seq.append(b)
        print(f"BOOK LIVE: {b} -> plan day 0 = {live}")


def _tier(e):
    """Placement priority of a per-book entry: launch kit (days 0-2) > page peeks > extra reels (day 9+)."""
    d = int(e["day"])
    return 0 if d <= 2 else (1 if d < 9 else 2)


def schedule(cal, log):
    """Returns {entry_id: due datetime (ET)} for every entry that has a date yet. Deterministic.
    Order of slot claims: entries already started (pinned to the time they really went out) > absolute entries >
    per-book entries by tier, then nominal time, then go-live order. A new book's launch therefore pushes older
    books' not-yet-posted extras later, never the other way round, and nothing already posted ever moves."""
    shift = dt.date.fromisoformat(log["_launch"]) - PLAN_START
    due, taken = {}, set()
    for e in cal:                                              # pinned: already started
        pin = (log.get(e["id"]) or {}).get("_due")
        if pin:
            due[e["id"]] = dt.datetime.fromisoformat(pin); taken.add(_slot(e["kind"], due[e["id"]]))
    for e in cal:                                              # absolute entries: fixed time
        if "when_et" not in e or e["id"] in due: continue
        when = (dt.datetime.fromisoformat(e["when_et"]) + shift).replace(tzinfo=ET)
        due[e["id"]] = when; taken.add(_slot(e["kind"], when))
    seq = log.get("_live_seq", [])
    todo = []
    for b in seq:
        live = dt.date.fromisoformat(log[f"_live_{b}"])
        for e in cal:
            if e.get("book") == b and e["id"] not in due:
                todo.append((_tier(e), _at(live + dt.timedelta(days=int(e["day"])), e["time"]), seq.index(b), e))
    for _, when, _, e in sorted(todo, key=lambda x: x[:3]):
        while _slot(e["kind"], when) in taken:
            when = _at(when.date() + dt.timedelta(days=1), e["time"])
        due[e["id"]] = when; taken.add(_slot(e["kind"], when))
    return due


def run(now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    cal = json.load(open(CAL))
    links = load(LINKS, {})
    log = load(LOG, {})
    if not log.get("_launch"):
        if not any((links.get("amazon") or {}).values()):
            print("Not launched yet: no Amazon link in links.json -> nothing to post."); return 0
        log["_launch"] = now.astimezone(ET).date().isoformat()
        print("LAUNCH day recorded:", log["_launch"])
    record_live(cal, links, log, now)
    due_at = schedule(cal, log)
    escalate = []
    caught_up = set()      # at most one LATE entry per kind per run, so a backlog trickles out instead of flooding
    for e in sorted((e for e in cal if e["id"] in due_at), key=lambda e: due_at[e["id"]]):
        due = due_at[e["id"]].astimezone(dt.timezone.utc)
        if now < due: continue
        gate = e.get("requires_link") or (f"amazon:{e['book']}" if e.get("book") else None)
        if gate and not link_for(links, gate):
            continue                                           # book not live (or link removed) -> wait
        row = log.setdefault(e["id"], {})
        row.setdefault("_due", due_at[e["id"]].isoformat())   # pin: this entry's slot never moves again
        late_h = (now - due).total_seconds() / 3600
        done = all((row.get(p) or {}).get("status") == "ok" for p in PLATFORMS[e["kind"]] if p.split("_")[0] in ENABLED)
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
        bad = [p for p, s in row.items() if p != "_due" and s["status"] != "ok" and s.get("detail", {}).get("error") != "not_connected"]
        if late_h >= STALE_HOURS and bad and not e.get("requires_link"):
            escalate.append((e["id"], round(late_h, 1), bad))
    json.dump(log, open(LOG, "w"), indent=1, ensure_ascii=False)
    if escalate:
        print("ESCALATE:", escalate); return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
