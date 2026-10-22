"""Offline simulation of watchdog.py (no network, nothing is posted).
Amazon links appear one by one on different dates/times (like KDP approvals), the watchdog runs on the real
cron grid (every 30 min, UTC 12-23 + 0-3) for 60 days with publish mocked: YouTube is "not connected"
(missing secrets), other platforms fail ~3% of the time, plus an 8-hour Actions outage.
Checks: no floods, one reel per day, nothing before its book is live, everything eventually posts, exit 0.
Run:  python sim_watchdog.py"""
import collections, datetime as dt, json, os, random, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import watchdog as W

ET = W.ET
UTC = dt.timezone.utc
START = dt.datetime(2026, 10, 19, 0, 0, tzinfo=UTC)
DAYS = 60
# when each book's Amazon link gets pasted into links.json (ET); two books the same day on purpose
GO_LIVE = {
    "xmas_activity": "2026-10-20 13:10", "abc": "2026-10-20 13:10",
    "xmas_coloring": "2026-10-22 09:20", "thanksgiving": "2026-10-22 22:40",
    "preschool": "2026-10-27 11:00", "animals": "2026-10-28 08:00",
    "kindergarten": "2026-11-03 16:00", "sightwords": "2026-11-04 12:00",
    "handwriting": "2026-11-10 10:30", "scissors": "2026-11-10 19:00",
    "numbers": "2026-11-17 09:00", "shapes": "2026-11-18 14:00",
    "cursive": "2026-11-24 10:00", "feelings": "2026-11-24 10:00",
    "space": "2026-12-01 09:00", "dinosaurs": "2026-12-02 15:00",
    # vehicles, unicorns, valentines, easter: not live inside the window -> must never post
}
OUTAGE = (dt.datetime(2026, 11, 5, 14, 0, tzinfo=UTC), dt.datetime(2026, 11, 5, 22, 0, tzinfo=UTC))


def ticks():
    t = START
    while t < START + dt.timedelta(days=DAYS):
        if (t.hour >= 12 or t.hour <= 3) and not (OUTAGE[0] <= t < OUTAGE[1]):
            yield t
        t += dt.timedelta(minutes=30)


def main():
    tmp = tempfile.mkdtemp()
    W.LOG = os.path.join(tmp, "publish_log.json"); W.LINKS = os.path.join(tmp, "links.json")
    W.ENABLED = {"instagram", "facebook", "youtube"}
    base = json.load(open(os.path.join(HERE, "links.json")))
    for shop in ("amazon", "etsy"):          # start from a clean slate: links appear only when the sim says so
        base[shop] = {k: "" for k in base.get(shop, {})}
    cal = json.load(open(W.CAL))
    rnd = random.Random(7)
    posted = collections.defaultdict(list)          # id -> [(tick, platform)]
    started = {}                                     # id -> first tick it published anything
    calls = []

    def fake_publish(platform, target, caption):
        calls.append((now, platform))
        assert "github" not in caption.lower() and "obelix" not in caption.lower(), caption
        if platform.startswith("youtube"):
            return False, {"error": "not_connected", "message": "missing secrets: YT_REFRESH_TOKEN"}
        if rnd.random() < 0.03:
            return False, {"error": "publish_failed", "message": "simulated 500"}
        return True, {"platform_ref": "x"}
    W.PUB.publish = fake_publish

    exits = collections.Counter(); per_tick = []
    for now in ticks():
        links = json.loads(json.dumps(base))
        for k, when in GO_LIVE.items():
            if dt.datetime.fromisoformat(when).replace(tzinfo=ET) <= now:
                links["amazon"][k] = f"https://www.amazon.com/dp/TEST{k.upper()}"
        json.dump(links, open(W.LINKS, "w"))
        before = len(calls)
        exits[W.run(now)] += 1
        new = calls[before:]
        log = W.load(W.LOG, {})
        n_entries = 0
        for e in cal:
            row = log.get(e["id"], {})
            if row and e["id"] not in started and any(isinstance(s, dict) and s.get("status") == "ok" for s in row.values()):
                started[e["id"]] = now; n_entries += 1
        per_tick.append((now, n_entries, len(new)))

    log = json.load(open(W.LOG))
    byid = {e["id"]: e for e in cal}
    print("exit codes:", dict(exits))
    print("max entries started in one run:", max(n for _, n, _ in per_tick),
          "| max publish calls in one run:", max(c for _, _, c in per_tick))
    # one reel per day / per-day load
    day_kind = collections.Counter((t.astimezone(ET).date(), byid[i]["kind"]) for i, t in started.items())
    print("max reels on one ET day:", max([v for (d, k), v in day_kind.items() if k == "reel"] or [0]),
          "| max feed posts on one day:", max([v for (d, k), v in day_kind.items() if k in ("post", "carousel")] or [0]),
          "| max stories on one day:", max([v for (d, k), v in day_kind.items() if k == "story"] or [0]))
    per_day = collections.Counter(t.astimezone(ET).date() for t in started.values())
    print("max entries on one ET day:", max(per_day.values()), "| days with posts:", len(per_day))
    # nothing before live, nothing from books never live
    bad = [i for i, t in started.items() if byid[i].get("book") and
           (byid[i]["book"] not in GO_LIVE or t < dt.datetime.fromisoformat(GO_LIVE[byid[i]["book"]]).replace(tzinfo=ET))]
    print("entries posted before their book was live:", bad or "none")
    # lateness of each entry vs. its scheduled slot
    due = W.schedule(cal, log)
    late = sorted(((started[i] - due[i]).total_seconds() / 3600, i) for i in started)
    print("lateness (h): max %.1f, entries >1h late: %d" % (late[-1][0], sum(1 for h, _ in late if h > 1)))
    for h, i in late[-5:]: print("   %.1f h  %s" % (h, i))
    # everything that should have happened did
    end = START + dt.timedelta(days=DAYS)
    # (YouTube is "not connected" in this sim, so the YouTube-only "yt" Shorts can never post here; see sim_etsy_yt.py)
    # (Etsy links never appear in this Amazon-only sim, so entries gated on an Etsy link can't post here either; see sim_etsy_yt.py)
    missing = [i for i, w in due.items() if w < end - dt.timedelta(hours=6) and i not in started and byid[i]["kind"] != "yt"
               and not (byid[i].get("requires_link") or "").startswith("etsy:")]
    print("due but never posted:", missing or "none")
    print("\nper-book go-live -> plan day 0 and actual post days (ET):")
    for b in log.get("_live_seq", []):
        mine = sorted((started[e["id"]].astimezone(ET), e["id"]) for e in cal if e.get("book") == b and e["id"] in started)
        d0 = dt.date.fromisoformat(log[f"_live_{b}"])
        print(f"  {b:14s} link {GO_LIVE[b]} -> day0 {d0}: " +
              ", ".join(f"{(t.date() - d0).days}{byid[i]['kind'][0]}@{t:%H:%M}" for t, i in mine))
    print("\ntimeline (first 21 days, ET):")
    for d in sorted(per_day)[:21]:
        items = sorted((t.astimezone(ET), i) for i, t in started.items() if t.astimezone(ET).date() == d)
        print(f"  {d}: " + "; ".join(f"{t:%H:%M} {i}" for t, i in items))
    ok = (set(exits) == {0} and not bad and not missing and max(v for (d, k), v in day_kind.items() if k == "reel") == 1)
    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
