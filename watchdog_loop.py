"""Keeps the watchdog running on time even when GitHub's cron fires hours late.

One Actions job runs watchdog.run() at every :02 and :32 (like the old */30 cron) for ~5h40m, committing
publish_log.json after each pass, then re-dispatches itself (workflow_dispatch with GITHUB_TOKEN is allowed
to start a new run). The cron triggers stay as a backup; the workflow's concurrency group keeps it to one
running + one queued job, so nothing ever posts twice.

Exit code: 1 if the LAST pass escalated (so the failure e-mail still reaches Mohamed), else 0.
"""
import datetime as dt, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "publish_log.json")
BUDGET_MIN = int(os.environ.get("LOOP_MINUTES", "340"))      # Actions job limit is 6 h; leave margin


def git(*a, check=True):
    return subprocess.run(["git", *a], cwd=HERE, check=check, capture_output=True, text=True)


def commit_log(base):
    """Commit publish_log.json; if someone else pushed meanwhile, merge per-entry (our touched rows win)."""
    ours = json.load(open(LOG))
    if ours == base:
        return
    for attempt in range(4):
        git("add", "publish_log.json")
        if git("diff", "--cached", "--quiet", check=False).returncode == 0:
            return
        git("commit", "-m", "watchdog: " + dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M"))
        if git("push", check=False).returncode == 0:
            return
        # someone pushed: take theirs, re-apply only the rows this pass changed
        git("fetch", "origin", "main")
        theirs = json.loads(git("show", "origin/main:publish_log.json").stdout)
        for k, v in ours.items():
            if base.get(k) != v:
                theirs[k] = v
        git("reset", "--hard", "origin/main")
        json.dump(theirs, open(LOG, "w"), indent=1, ensure_ascii=False)
        ours = theirs
    print("WARNING: could not push publish_log.json after 4 tries")


def next_tick(now):
    """Next :02 or :32 after now."""
    t = now.replace(second=0, microsecond=0)
    m = 2 if t.minute < 2 else 32 if t.minute < 32 else 62
    return t.replace(minute=0) + dt.timedelta(minutes=m)


def main():
    start = dt.datetime.now(dt.timezone.utc)
    stop = start + dt.timedelta(minutes=BUDGET_MIN)
    rc = 0
    while True:
        git("pull", "--rebase", "--autostash", check=False)          # pick up new pins / calendar / links
        import importlib, publish, watchdog as W
        importlib.reload(publish); importlib.reload(W)   # pick up code pushed while the loop runs
        base = json.load(open(LOG)) if os.path.exists(LOG) else {}
        try:
            rc = W.run()
        except Exception as ex:                                     # never let one bad pass kill the loop
            print("watchdog pass crashed:", repr(ex)); rc = 1
        commit_log(base)
        nxt = next_tick(dt.datetime.now(dt.timezone.utc))
        if nxt >= stop:
            break
        time.sleep(max(0, (nxt - dt.datetime.now(dt.timezone.utc)).total_seconds()))
    # hand over to a fresh run so the loop never depends on GitHub's cron
    if os.environ.get("GITHUB_ACTIONS") and os.environ.get("NO_CHAIN") != "1":
        r = subprocess.run(["gh", "workflow", "run", "watchdog.yml", "--ref", "main"], cwd=HERE,
                           capture_output=True, text=True)
        print("re-dispatch:", r.returncode, r.stderr.strip()[:200])
    return rc


if __name__ == "__main__":
    sys.exit(main())
