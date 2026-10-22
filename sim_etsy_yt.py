"""Offline simulation of watchdog.py for the Etsy-only products + YouTube daily Shorts (nothing is posted).
75 days on the real cron grid with publish mocked:
  - Amazon links appear on various days (like sim_watchdog.py), all 9 Etsy links appear on day 3,
  - YouTube secrets present (uploads "succeed"), other platforms fail ~3% of the time, plus an Actions outage.
Checks: <=2 YouTube uploads per Pacific/ET day, <=1 reel/day on IG/FB, no floods, nothing before its gate,
no video uploaded to YouTube twice (reel + its yt variant), titles <=100 chars, Etsy/YouTube CTAs, exit 0.
Also checks that with no Etsy links the Amazon/brand plan posts EXACTLY as the previous watchdog did.
Run:  python sim_etsy_yt.py"""
import collections, datetime as dt, importlib.util, json, os, random, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import watchdog as W
import publish as P

ET, UTC = W.ET, dt.timezone.utc
PT = W.PT
START = dt.datetime(2026, 10, 19, 0, 0, tzinfo=UTC)
DAYS = 75
GO_LIVE = {
    "xmas_activity": "2026-10-20 06:20", "abc": "2026-10-23 13:10",
    "xmas_coloring": "2026-10-22 09:20", "thanksgiving": "2026-10-22 22:40",
    "preschool": "2026-10-27 11:00", "animals": "2026-10-28 08:00",
    "kindergarten": "2026-11-03 16:00", "sightwords": "2026-11-04 12:00",
    "handwriting": "2026-11-10 10:30", "scissors": "2026-11-10 19:00",
    "numbers": "2026-11-17 09:00", "shapes": "2026-11-18 14:00",
    "cursive": "2026-11-24 10:00", "feelings": "2026-11-24 10:00",
    "space": "2026-12-01 09:00", "dinosaurs": "2026-12-02 15:00",
    "vehicles": "2026-12-15 10:00", "unicorns": "2026-12-20 10:00",
}
ETSY_KEYS = sorted({(e.get("book") or e.get("requires_link") or "").split(":", 1)[1] for e in json.load(open(W.CAL))
                    if str(e.get("book") or e.get("requires_link") or "").startswith("etsy:")})
ETSY_LIVE = "2026-10-22 14:00"        # day 3: all 9 Etsy listings go live at once
OUTAGE = (dt.datetime(2026, 11, 5, 14, 0, tzinfo=UTC), dt.datetime(2026, 11, 5, 22, 0, tzinfo=UTC))


def et(s): return dt.datetime.fromisoformat(s).replace(tzinfo=ET)


def ticks(days=DAYS):
    t = START
    while t < START + dt.timedelta(days=days):
        if (t.hour >= 12 or t.hour <= 3) and not (OUTAGE[0] <= t < OUTAGE[1]):
            yield t
        t += dt.timedelta(minutes=30)


def simulate(mod, go_live, etsy_live, enabled, yt_ok, days=DAYS, fail=0.03, seed=7):
    tmp = tempfile.mkdtemp()
    mod.LOG = os.path.join(tmp, "publish_log.json"); mod.LINKS = os.path.join(tmp, "links.json")
    mod.ENABLED = set(enabled)
    base = json.load(open(os.path.join(HERE, "links.json")))
    for shop in ("amazon", "etsy"):          # start from a clean slate: links appear only when the sim says so
        base[shop] = {k: "" for k in base.get(shop, {})}
    rnd = random.Random(seed)
    calls = []
    state = {}

    def fake_publish(platform, target, caption):
        r = _fake(platform, caption)
        calls.append((state["now"], platform, os.path.basename(target if isinstance(target, str) else target[0]), caption, r[0]))
        return r

    def _fake(platform, caption):
        low = caption.lower()
        assert "github" not in low and "obelix" not in low, caption
        if platform.startswith("youtube"):
            if not yt_ok: return False, {"error": "not_connected", "message": "missing secrets: YT_REFRESH_TOKEN"}
            assert len(P.yt_title(caption)) <= 100
        if rnd.random() < fail:
            return False, {"error": "publish_failed", "message": "simulated 500"}
        return True, {"platform_ref": "x"}
    mod.PUB.publish = fake_publish
    exits = collections.Counter(); per_run = []
    for now in ticks(days):
        state["now"] = now
        links = json.loads(json.dumps(base))
        for k, when in go_live.items():
            if et(when) <= now: links["amazon"][k] = f"https://www.amazon.com/dp/TEST{k.upper()}"
        if etsy_live and et(etsy_live) <= now:
            for k in ETSY_KEYS: links["etsy"][k] = f"https://www.etsy.com/listing/TEST_{k}"
        json.dump(links, open(mod.LINKS, "w"))
        before = len(calls)
        exits[mod.run(now)] += 1
        per_run.append(len(calls) - before)
    return calls, exits, per_run, json.load(open(mod.LOG))


def old_watchdog():
    """watchdog.py and calendar.json as they were before this change (git HEAD~ of these files)."""
    rev = os.environ.get("OLD_REV", "HEAD")
    tmp = tempfile.mkdtemp()
    for fn in ("watchdog.py", "calendar.json"):
        src = subprocess.run(["git", "show", f"{rev}:{fn}"], cwd=HERE, capture_output=True, text=True, check=True).stdout
        open(os.path.join(tmp, fn), "w").write(src)
    spec = importlib.util.spec_from_file_location("watchdog_old", os.path.join(tmp, "watchdog.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.CAL = os.path.join(tmp, "calendar.json")
    return m


def main():
    ok = True
    cal = json.load(open(W.CAL)); byid = {e["id"]: e for e in cal}
    byfile = {}
    for e in cal:
        byfile.setdefault(e["files"][0], e["id"])

    # ---------------- 1) equivalence: no Etsy links, YouTube off -> identical IG/FB posting to the old watchdog
    old = old_watchdog()
    a, _, _, _ = simulate(old, GO_LIVE, None, {"instagram", "facebook"}, False)
    b, ex_b, _, _ = simulate(W, GO_LIVE, None, {"instagram", "facebook"}, False)
    strip = lambda cs: [(t, p, f, g) for t, p, f, _c, g in cs]   # captions changed on purpose (Etsy shop link); timing/files must not
    same = strip(a) == strip(b)
    print(f"[equivalence] old watchdog {len(a)} calls, new {len(b)} calls -> {'IDENTICAL' if same else 'DIFFERENT'}")
    ok &= same

    # ---------------- 2) full scenario: Amazon links over time, all Etsy links on day 3, YouTube connected
    calls, exits, per_run, log = simulate(W, GO_LIVE, ETSY_LIVE, {"instagram", "facebook", "youtube"}, True)
    print("exit codes:", dict(exits))
    ok &= set(exits) == {0}
    oks = []                      # successful (time, platform, entry id)
    for t, p, f, c, good in calls:
        if good: oks.append((t, p, byfile[f], c))
    started = {}
    for t, p, i, c in oks:
        started.setdefault(i, t)
    # YouTube per day (each call is an upload attempt = quota)
    yt_pt = collections.Counter(t.astimezone(PT).date() for t, p, *_ in calls if p == "youtube_short")
    yt_et = collections.Counter(t.astimezone(ET).date() for t, p, *_ in calls if p == "youtube_short")
    print(f"YouTube uploads: total {sum(yt_pt.values())} | max per Pacific day {max(yt_pt.values())} | max per ET day {max(yt_et.values())}")
    ok &= max(yt_pt.values()) <= 2
    # IG/FB reels per day
    reels = collections.Counter((t.astimezone(ET).date(), p) for t, p, i, c in oks if p in ("instagram_reel", "facebook_reel"))
    print("max IG/FB reels on one ET day (per platform):", max(reels.values()))
    ok &= max(reels.values()) == 1
    feed = collections.Counter((started[i].astimezone(ET).date()) for i in started if byid[i]["kind"] in ("post", "carousel"))
    print("max feed posts/carousels started on one ET day:", max(feed.values()))
    ok &= max(feed.values()) == 1
    print("max publish calls in one run:", max(per_run), "| runs with >6 calls:", sum(1 for n in per_run if n > 6))
    ok &= max(per_run) <= 12
    # nothing before its gate
    bad = []
    for i, t in started.items():
        e = byid[i]
        if e.get("book"):
            shop, k = W.gate_of(e["book"]).split(":", 1)
            gate_t = et(ETSY_LIVE) if shop == "etsy" else (et(GO_LIVE[k]) if k in GO_LIVE else None)
            if gate_t is None or t < gate_t: bad.append(i)
    print("entries posted before their gate:", bad or "none")
    ok &= not bad
    # no video on YouTube twice
    yt_ids = [i for t, p, i, c in oks if p == "youtube_short"]
    twins = {e["same_as"]: e["id"] for e in cal if e.get("same_as")}
    dup = [i for i in yt_ids if i in twins and twins[i] in yt_ids]
    print("videos uploaded to YouTube twice:", dup or "none", "| repeated entry uploads:",
          [i for i, n in collections.Counter(yt_ids).items() if n > 1] or "none")
    ok &= not dup and len(set(yt_ids)) == len(yt_ids)
    # captions / CTAs
    cta_bad = []
    for t, p, i, c in oks:
        e = byid[i]; lk = (e.get("caption") or {}).get("link_key") or ""
        if lk.startswith("etsy:"):
            if p.startswith(("facebook", "youtube")) and "🖨️ Instant download on Etsy: https://colorbloop.etsy.com" not in c and c: cta_bad.append((i, p))
            if p.startswith("instagram") and c and ("http" in c or "link in our bio" not in c): cta_bad.append((i, p))
        if c and ("etsy.com/listing" in c or "etsy.com/shop/" in c): cta_bad.append((i, "listing-link"))
        if e["kind"] == "yt":
            rel = e.get("related", "")
            live = rel.startswith("amazon:") and rel.split(":")[1] in GO_LIVE and et(GO_LIVE[rel.split(":")[1]]) <= t
            if "Subscribe for daily coloring videos!" not in c: cta_bad.append((i, "no-subscribe"))
            if "https://colorbloop.etsy.com" not in c: cta_bad.append((i, "no-etsy-shop"))
            if live != ("amazon.com" in c): cta_bad.append((i, "amazon-link-mismatch"))
    print("CTA problems:", cta_bad or "none")
    ok &= not cta_bad
    # everything due got done
    due = W.schedule(cal, log)
    end = START + dt.timedelta(days=DAYS)
    missing = []
    yt_twins = {e["same_as"] for e in cal if e.get("same_as")}
    for i, w in due.items():
        if w >= end - dt.timedelta(hours=6): continue
        row = log.get(i, {})
        need = [p for p in W.platforms_for(byid[i], yt_twins)]
        if not all((row.get(p) or {}).get("status") == "ok" for p in need): missing.append(i)
    print("due but not fully posted:", missing or "none")
    ok &= not missing
    # Etsy plans
    print("\nEtsy go-live -> plan day 0 and actual post days (ET):")
    for b in [x for x in log["_live_seq"] if x.startswith("etsy:")]:
        d0 = dt.date.fromisoformat(log[W.live_key(b)])
        mine = sorted((started[e["id"]].astimezone(ET), e["id"]) for e in cal if e.get("book") == b and e["id"] in started)
        print(f"  {b:22s} day0 {d0}: " + ", ".join(f"{(t.date() - d0).days}{byid[i]['kind'][0]}@{t:%m-%d %H:%M}" for t, i in mine))
    print("\nfirst 10 YouTube Shorts (yt kind):")
    for t, p, i, c in [x for x in oks if byid[x[2]]["kind"] == "yt"][:10]:
        print(f"  {t.astimezone(ET):%a %Y-%m-%d %H:%M} ET  {i:38s} title: {P.yt_title(c)}")
    n_yt = sum(1 for t, p, i, c in oks if byid[i]["kind"] == "yt")
    n_reel_yt = sum(1 for t, p, i, c in oks if p == "youtube_short" and byid[i]["kind"] == "reel")
    print(f"\nYouTube: {n_yt} daily Shorts + {n_reel_yt} reels (launch reels etc.) in {DAYS} days; "
          f"days with 2 uploads: {sum(1 for v in yt_et.values() if v == 2)}")
    print("log keys:", sorted(k for k in log if k.startswith("_")))
    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
