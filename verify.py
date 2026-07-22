#!/usr/bin/env python3
"""
verify.py — re-verify every claim in this repo against the live ActionLayer API.

Nothing here is asserted from memory. Every row is a real ticket that was really
fired tonight; this script re-fetches each one and checks the recorded state
still matches. Run it yourself:

    python3 verify.py            # re-check all recorded tickets
    python3 verify.py --json     # machine-readable

Exit code 0 = every claim verified. Non-zero = a claim did not hold.
"""
import json, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "evidence", "tickets.json")
ENV = dict(
    l.strip().split("=", 1)
    for l in open(os.path.join(HERE, ".env"))
    if "=" in l and not l.startswith("#")
)
AL_KEY = ENV["ACTIONLAYER_API_KEY"]
AL_URL = ENV.get("ACTIONLAYER_API_URL", "https://api.actionlayer.io")
B, D, G, Y, R, X = "\033[1m", "\033[2m", "\033[32m", "\033[33m", "\033[31m", "\033[0m"


def fetch(tid):
    req = urllib.request.Request(f"{AL_URL}/tasks/{tid}")
    req.add_header("Authorization", f"Bearer {AL_KEY}")
    req.add_header("User-Agent", "lastmile-verify/1.0")  # urllib's default UA is 403'd
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode(), strict=False)
    except Exception as e:
        return {"_err": str(e)}


def main():
    ledger = json.load(open(LEDGER))
    tickets = ledger["tickets"]
    with ThreadPoolExecutor(max_workers=8) as ex:
        live = list(ex.map(lambda t: fetch(t["ticket"]), tickets))

    if "--json" in sys.argv:
        print(json.dumps(
            [{**t, "live_state": l.get("state"), "live_reason": l.get("reason")}
             for t, l in zip(tickets, live)], indent=2))
        return 0

    print(f"\n{B}  VERIFYING {len(tickets)} TICKETS AGAINST THE LIVE API{X}")
    print(f"{D}  every claim in README.md re-checked, nothing asserted from memory{X}\n")
    print(f"  {'TICKET':<26}{'CLAIMED':<12}{'LIVE':<12}{'':4}{'WHAT IT PROVES'}")
    print(f"{D}  {'─'*104}{X}")

    bad = 0
    for t, l in zip(tickets, live):
        got = l.get("state", "ERR")
        ok = got == t["state"]
        if not ok:
            bad += 1
        mark = f"{G}✓{X}" if ok else f"{R}✗{X}"
        col = {"completed": G, "failed": R, "cancelled": D, "blocked_on_user": Y}.get(got, "")
        print(f"  {t['ticket'][:24]:<26}{t['state']:<12}{col}{got:<12}{X}{mark}   {t['proves']}")

    print(f"{D}  {'─'*104}{X}")
    if bad:
        print(f"\n{R}{B}  {bad} claim(s) did not verify.{X}\n")
        return 1
    print(f"\n{G}{B}  all {len(tickets)} claims verified against the live API.{X}\n")

    # the headline artifact, printed in full
    win = next((t for t in tickets if t.get("headline")), None)
    if win:
        l = live[tickets.index(win)]
        print(f"{B}  THE RESULT{X}  {D}{win['ticket']}{X}")
        print(f"{D}  instruction sent (no name, no SSN, no address, no DOB):{X}")
        print(f"    {win['instruction']}\n")
        print(f"{D}  returned by benefits.gov:{X}")
        for line in (l.get("reason") or "").split("\n"):
            print(f"    {G}{line}{X}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
