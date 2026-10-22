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
  - ETSY-ONLY products use the same per-book plan with "book": "etsy:<key>": the first run that sees
    links.etsy.<key> non-empty records "_live_etsy_<key>" (and "etsy:<key>" in "_live_seq"), same day-0 and
    de-collision rules. Plain "book": "<key>" still means the Amazon link (unchanged).
  - "not_before": "YYYY-MM-DD" on a per-book entry starts that book's plan no earlier than that date (seasonal books
    such as Valentine's / Easter / New Year go live early on the stores but are promoted close to their season);
  - kind "yt" = YouTube-only daily Shorts (absolute dates, 12:00 ET). "related": "amazon:<key>" only picks the
    CTA (Amazon link if live, else "Subscribe"), it never gates. "same_as": "<reel id>" names the reel whose
    video it is a YouTube variant of: that reel then skips YouTube, so a video never lands on the channel twice.
  - YouTube quota guard: at most YT_DAILY_MAX upload attempts per Pacific day (videos.insert = 1600 units of
    the 10k/day quota); anything over waits for the next day (counter "_yt_quota" in publish_log.json).
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
MAX_ATTEMPTS = 8          # after this many failed tries a platform is left alone (no retry, no alarm e-mails)
PLAN_START = dt.date(2026, 10, 19)   # the date calendar.json's absolute entries were written against
PLATFORMS = {
    "post": ["instagram_post", "facebook_post"],
    "carousel": ["instagram_carousel", "facebook_carousel"],
    "reel": ["instagram_reel", "facebook_reel", "youtube_short", "instagram_story", "facebook_story"],
    "story": ["instagram_story", "facebook_story"],
    "yt": ["youtube_short"],
}
YT_DAILY_MAX = 2
PT = ZoneInfo("America/Los_Angeles")    # YouTube quota resets at midnight Pacific
ENABLED = set(os.environ.get("PLATFORMS", "instagram,facebook").split(","))


def load(p, d): return json.load(open(p)) if os.path.exists(p) else d


def link_for(links, key):
    if not key: return ""
    if ":" in key:
        shop, book = key.split(":", 1)
        return (links.get(shop) or {}).get(book, "")
    return links.get(key, "")


def gate_of(book):
    """Calendar "book" value -> link key: "dinosaurs" -> "amazon:dinosaurs", "etsy:bundle_mega" stays."""
    return book if ":" in book else f"amazon:{book}"


def live_key(book):
    """publish_log key of a book's go-live date: "_live_<key>" (Amazon, as before) / "_live_etsy_<key>"."""
    shop, key = gate_of(book).split(":", 1)
    return f"_live_{key}" if shop == "amazon" else f"_live_{shop}_{key}"


ETSY_SHOP_DEFAULT = "https://colorbloop.etsy.com"   # the shop's Share & Save link (Etsy refunds part of the fee on sales from it)


def etsy_shop(links):
    """Every Etsy link we post is the shop's Share & Save link, never a single listing URL.
    Listing URLs in links.etsy.<key> are only the go-live gates for each product's plan."""
    return (links.get("etsy_share") or ETSY_SHOP_DEFAULT).strip()


def _shop_line(link_key, url, links):
    return (f"🖨️ Instant download on Etsy: {etsy_shop(links)}" if link_key.startswith("etsy:") else f"📚 Get it here: {url}")


def _caption_raw(entry, links, platform):
    c = entry.get("caption")
    if not c: return ""
    shop = etsy_shop(links)
    if entry.get("kind") == "yt":                       # YouTube-only Short: related link (never a gate) + Etsy shop + subscribe
        rel = entry.get("related") or ""
        url = link_for(links, rel)
        cta = (_shop_line(rel, url, links) + "\n" if url else "")
        if not rel.startswith("etsy:"):
            cta += f"🖨️ Printable PDFs on Etsy: {shop}\n"
        cta += "🔔 Subscribe for daily coloring videos!"
        return c["text"].replace("{cta}", cta)
    if (c.get("link_key") or "").startswith("etsy:"):    # Etsy-only product
        url = link_for(links, c["link_key"])
        if not url:
            cta = "Coming soon! Follow @color.bloop so you don't miss it."
        elif platform.startswith("facebook") or platform.startswith("youtube"):
            cta = f"🖨️ Instant download on Etsy: {shop}"
        else:
            cta = "🛍️ Instant download: tap the link in our bio (colorbloop.etsy.com)"
        return c["text"].replace("{cta}", cta)
    url = link_for(links, c.get("link_key"))
    on_etsy = (c.get("link_key") or "").startswith("amazon:") and bool(link_for(links, "etsy:" + c["link_key"].split(":", 1)[1]))
    if c.get("link_key") and not url:
        cta = "Coming soon! Follow @color.bloop so you don't miss it."
    elif (platform.startswith("facebook") or platform.startswith("youtube")) and url:
        cta = f"📚 Paperback on Amazon: {url}" + (f"\n🖨️ Printable PDF on Etsy: {shop}" if on_etsy else "")
    elif url:
        cta = ("🖨️ Printable PDF: tap the link in our bio\n📚 Paperback: search 'Colorbloop' on Amazon" if on_etsy
               else "📚 Search 'Colorbloop' on Amazon to get it!")
    else:
        cta = f"Follow @color.bloop for new books & coloring fun! 🖨️ Printables: {shop}" if (platform.startswith("facebook") or platform.startswith("youtube")) else "Follow @color.bloop for new books & coloring fun! 🖨️ Printables: link in bio"
    return c["text"].replace("{cta}", cta)


HASHTAG_CAP = {"instagram": 5, "facebook": 3}   # Instagram allows max 5 hashtags; on Facebook 2-3 read best


GENERIC_TAGS = {"#coloringbook", "#kidsactivities", "#preschoolactivities", "#toddleractivities", "#coloringpages",
                "#homeschool", "#coloring", "#coloringforkids", "#satisfying", "#printables"}


def _cap_hashtags(text, n):
    """Keep at most n hashtags: topic-specific tags first (they rank posts in niche searches), then generic ones."""
    import re
    tags = []
    for t in re.findall(r"#\w+", text):
        if t.lower() not in [x.lower() for x in tags]: tags.append(t)
    specific = [t for t in tags if t.lower() not in GENERIC_TAGS]
    generic = [t for t in tags if t.lower() in GENERIC_TAGS]
    keep = specific[:max(n - 2, 1)]
    keep += generic[:n - len(keep)]
    keep += [t for t in specific if t not in keep][:n - len(keep)]
    body = re.sub(r"#\w+", "", text)
    body = "\n".join(re.sub(r"[ \t]{2,}", " ", ln).rstrip() for ln in body.split("\n")).rstrip()
    ordered = [t for t in tags if t in keep]
    return body + ("\n\n" + " ".join(ordered) if ordered else "")


def caption_for(entry, links, platform):
    text = _caption_raw(entry, links, platform)
    n = HASHTAG_CAP.get(platform.split("_")[0])
    return _cap_hashtags(text, n) if (n and text) else text


def _at(date, hhmm):
    h, m = map(int, hhmm.split(":"))
    return dt.datetime(date.year, date.month, date.day, h, m, tzinfo=ET)


def _slot(kind, when):
    d = when.date().isoformat()
    if kind == "reel": return ("reel", d)
    if kind in ("post", "carousel"): return ("feed", d)
    return (kind, d, when.strftime("%H:%M"))


def record_live(cal, links, log, now):
    """First sighting of a book's link -> "_live_<key>" / "_live_etsy_<key>" (ET date) + its place in "_live_seq"."""
    now_et = now.astimezone(ET)
    seq = log.setdefault("_live_seq", [])
    books = []
    for e in cal:
        if e.get("book") and e["book"] not in books: books.append(e["book"])
    for b in books:
        if live_key(b) in log or not link_for(links, gate_of(b)): continue
        day0 = [e["time"] for e in cal if e.get("book") == b and int(e["day"]) == 0]
        live = now_et.date()
        if day0 and now_et >= _at(live, min(day0)):
            live += dt.timedelta(days=1)          # too late today for the day-0 posts -> start tomorrow
        log[live_key(b)] = live.isoformat()
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
        live = dt.date.fromisoformat(log[live_key(b)])
        for e in cal:
            if e.get("book") == b and e["id"] not in due:
                start = max(live, dt.date.fromisoformat(e["not_before"])) if e.get("not_before") else live
                todo.append((_tier(e), _at(start + dt.timedelta(days=int(e["day"])), e["time"]), seq.index(b), e))
    for _, when, _, e in sorted(todo, key=lambda x: x[:3]):
        while _slot(e["kind"], when) in taken:
            when = _at(when.date() + dt.timedelta(days=1), e["time"])
        due[e["id"]] = when; taken.add(_slot(e["kind"], when))
    return due


def platforms_for(e, yt_twins):
    """Platforms of an entry; a reel whose video has a YouTube-only variant ("same_as") skips YouTube."""
    return [p for p in PLATFORMS[e["kind"]] if not (p == "youtube_short" and e["id"] in yt_twins)]


def yt_quota(log, now):
    day = now.astimezone(PT).date().isoformat()
    q = log.get("_yt_quota") or {}
    if q.get("date") != day:
        q = {"date": day, "n": 0}
    log["_yt_quota"] = q
    return q


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
    yt_twins = {e["same_as"] for e in cal if e.get("kind") == "yt" and e.get("same_as")}
    escalate, capped = [], set()
    caught_up = set()      # at most one LATE entry per kind per run, so a backlog trickles out instead of flooding
    for e in sorted((e for e in cal if e["id"] in due_at), key=lambda e: due_at[e["id"]]):
        due = due_at[e["id"]].astimezone(dt.timezone.utc)
        if now < due: continue
        gate = e.get("requires_link") or (gate_of(e["book"]) if e.get("book") else None)
        if gate and not link_for(links, gate):
            continue                                           # book not live (or link removed) -> wait
        row = log.setdefault(e["id"], {})
        row.setdefault("_due", due_at[e["id"]].isoformat())   # pin: this entry's slot never moves again
        late_h = (now - due).total_seconds() / 3600
        plats = platforms_for(e, yt_twins)
        done = all((row.get(p) or {}).get("status") == "ok" for p in plats if p.split("_")[0] in ENABLED)
        if not done and late_h > 2:
            if e["kind"] in caught_up: continue
            caught_up.add(e["kind"])
        files = [os.path.join(HERE, "assets", f) for f in e["files"]]
        for platform in plats:
            if platform.split("_")[0] not in ENABLED: continue
            st = row.get(platform, {"status": "pending", "attempts": 0})
            if st["status"] == "ok": continue
            if st.get("attempts", 0) >= MAX_ATTEMPTS: continue
            last = st.get("last_attempt")
            if last and (now - dt.datetime.fromisoformat(last)).total_seconds() < RETRY_COOLDOWN_MIN * 60: continue
            if platform == "youtube_short":
                q = yt_quota(log, now)
                if q["n"] >= YT_DAILY_MAX:
                    capped.add((e["id"], platform))     # waiting for quota is not a failure: never escalate it
                    print(f'{e["id"]} {platform}: waiting (YouTube daily cap {YT_DAILY_MAX} reached)'); continue
            target = files if platform.endswith("carousel") else files[0]
            if platform.endswith("story") and e["kind"] == "story": cap = ""
            else: cap = caption_for(e, links, platform)
            ok, detail = PUB.publish(platform, target, cap)
            if platform == "youtube_short" and detail.get("error") != "not_connected":
                q["n"] += 1
            st.update(status="ok" if ok else "failed", detail=detail, attempts=st["attempts"] + 1, last_attempt=now.isoformat())
            row[platform] = st
            print(f'{e["id"]} {platform}: {st["status"]}' + ("" if ok else f' ({detail.get("message", "")[:120]})'))
        bad = [p for p, s in row.items() if p != "_due" and s["status"] != "ok" and s.get("detail", {}).get("error") != "not_connected"
               and (e["id"], p) not in capped
               and (3 if p == "youtube_short" else 2) <= s.get("attempts", 0) < MAX_ATTEMPTS]   # YT often waits hours for quota first      # one failure right after an outage isn't an alarm; a failed retry is
        if late_h >= STALE_HOURS and bad and not e.get("requires_link"):
            escalate.append((e["id"], round(late_h, 1), bad))
    json.dump(log, open(LOG, "w"), indent=1, ensure_ascii=False)
    if escalate:
        print("ESCALATE:", escalate); return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
