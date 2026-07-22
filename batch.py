#!/usr/bin/env python3
"""
batch.py — de-identified batch benefits screening.

The single-applicant version was the weak one: the senior who most needs this is
the least likely to open a terminal. The real shape is an organization that
already holds a roster of likely-eligible seniors — a food bank with SNAP
outreach, an Area Agency on Aging, a PHA with annually income-verified tenants —
handing over DE-IDENTIFIED records and screening the whole roster at once.

THE PII ARCHITECTURE (the load-bearing idea):
SNAP eligibility is determined by age, household size, income, assets, housing
cost, state, disability status. NONE of those are identifiers. So screening sends
"#47 - 68, CA, household of 1, $1,150/mo, $900 rent" and gets back "likely
qualifies: SNAP, MSP, LIHEAP". The org holds the mapping. The agent never sees a
name, SSN, address, or DOB. There is nothing to protect because the screening
never sees a person.

WHY BATCH FITS THIS STACK: 15-20 min/ticket kills a consumer concierge. It is
irrelevant for overnight back-office work. Tickets run in parallel, so 8 cost
roughly the same wall-clock as 1. The latency stops being an apology and starts
being the thing that selects the use case.

  python3 batch.py fire            # fan out the roster, save ticket ids
  python3 batch.py watch           # live dashboard until all terminal
"""
import json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "batch_state.json")
TARGET = "https://www.benefits.gov/benefit-finder"

ENV = dict(
    l.strip().split("=", 1)
    for l in open(os.path.join(HERE, ".env"))
    if "=" in l and not l.startswith("#")
)
AL_KEY, AL_URL = ENV["ACTIONLAYER_API_KEY"], ENV.get("ACTIONLAYER_API_URL", "https://api.actionlayer.io")

B, D, G, Y, R, C, X = "\033[1m", "\033[2m", "\033[32m", "\033[33m", "\033[31m", "\033[36m", "\033[0m"


def http(url, payload=None, timeout=60):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "lastmile/1.0")  # Python-urllib UA gets 403d
    req.add_header("Authorization", f"Bearer {AL_KEY}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode() or "{}", strict=False)
    except Exception as e:
        return {"_err": str(e)}


def goal_for(rec):
    """Note what is NOT in this string: no name, no SSN, no address, no DOB."""
    d = ", receives disability" if rec["disability"] else ""
    rent = f"${rec['rent']}/mo rent" if rec["rent"] else "no housing cost"
    return (
        f"Complete this benefit finder for a {rec['age']}-year-old in "
        f"{rec['state']}, household of {rec['household']}, ${rec['income']}/month "
        f"income, {rent}, assets {rec['assets']}{d}. "
        f"Return the list of benefits they may qualify for."
    )


def fire_one(rec):
    g = goal_for(rec)
    r = http(f"{AL_URL}/v1/actions/direct.browser_action",
             {"inputs": {"url": TARGET, "instruction": g}})
    return {"id": rec["id"], "rec": rec, "goal": g,
            "ticket": (r.get("payload") or {}).get("ticket_id"), "chars": len(g)}


def cmd_fire():
    roster = json.load(open(os.path.join(HERE, "roster.json")))
    print(f"{B}fanning out {len(roster)} de-identified records…{X}")
    with ThreadPoolExecutor(max_workers=len(roster)) as ex:
        rows = list(ex.map(fire_one, roster))
    json.dump({"started": time.time(), "rows": rows}, open(STATE, "w"), indent=1)
    ok = sum(1 for r in rows if r["ticket"])
    print(f"{G}{ok}/{len(rows)} queued{X}  {D}(goal strings {min(r['chars'] for r in rows)}-{max(r['chars'] for r in rows)} chars){X}")
    print(f"\n{D}example goal — note there is no name, SSN, address, or DOB:{X}")
    print(f"  {rows[0]['goal']}")
    print(f"\nnow: {B}python3 batch.py watch{X}")


def profile(rec):
    d = " dis" if rec["disability"] else ""
    return f"{rec['age']}y {rec['state']} hh{rec['household']} ${rec['income']}/mo{d}"


def cmd_watch():
    st = json.load(open(STATE))
    rows, started = st["rows"], st["started"]
    first = True
    while True:
        with ThreadPoolExecutor(max_workers=8) as ex:
            got = list(ex.map(lambda r: http(f"{AL_URL}/tasks/{r['ticket']}") if r["ticket"] else {}, rows))
        if not first:
            print(f"\033[{len(rows)+7}A", end="")
        first = False
        el = int(time.time() - started)
        done = sum(1 for t in got if t.get("state") in ("completed", "failed", "cancelled"))
        print(f"\033[2K{B}  DE-IDENTIFIED BATCH SCREENING{X}   {D}{len(rows)} records · {el//60}m{el%60:02d}s elapsed · {done}/{len(rows)} terminal{X}")
        print(f"\033[2K{D}  no name · no SSN · no address · no DOB — the agent never sees a person{X}")
        print(f"\033[2K{D}  {'─'*86}{X}")
        print(f"\033[2K  {'REC':<5}{'PROFILE':<30}{'STATE':<16}{'RESULT'}")
        print(f"\033[2K{D}  {'─'*86}{X}")
        for r, t in zip(rows, got):
            s = t.get("state", "?")
            col = {"completed": G, "failed": R, "blocked_on_user": Y}.get(s, D)
            res = (t.get("reason") or t.get("error") or "")[:38].replace("\n", " ")
            if s == "blocked_on_user":
                qs = (t.get("info_request") or {}).get("questions") or []
                res = "⏸ " + (qs[0]["label"][:36] if qs else "waiting")
            print(f"\033[2K  {r['id']:<5}{profile(r['rec']):<30}{col}{s:<16}{X}{res}")
        print(f"\033[2K{D}  {'─'*86}{X}")
        qual = sum(1 for t in got if t.get("state") == "completed")
        print(f"\033[2K  {G}{B}{qual}{X} screened   {D}· one navigator does ~6-8 of these an hour by hand{X}")
        if done == len(rows):
            print(f"\n{G}{B}  batch complete.{X}")
            json.dump({"rows": rows, "results": got}, open(os.path.join(HERE, "batch_results.json"), "w"), indent=1)
            return
        time.sleep(15)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"fire": cmd_fire, "watch": cmd_watch}.get(cmd, lambda: print(__doc__))()
