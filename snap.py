#!/usr/bin/env python3
"""
snap.py — the specificity layer.

Thesis, measured this afternoon: agents don't die at the last mile on
credentials or CAPTCHAs. They die on under-specification. Every block costs a
full 15-20 minute ActionLayer cycle.

So: Novita (fast, cheap, deterministic) turns a vague human ask into a goal
that uniquely identifies what's wanted. THEN ActionLayer executes.

  python3 snap.py "my mom needs help with groceries"
  python3 snap.py "..." --facts facts.json     # skip the interview (for recording)
  python3 snap.py --resume tkt_xxx             # re-attach to a running ticket

Zero dependencies — stdlib only.
"""
import json, os, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))


def load_env():
    env = {}
    with open(os.path.join(HERE, ".env")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v
    return env


ENV = load_env()
NOVITA_KEY = ENV.get("NOVITA_API_KEY", "")
NOVITA_URL = ENV.get("NOVITA_BASE_URL", "https://api.novita.ai/openai/v1")
AL_KEY = ENV["ACTIONLAYER_API_KEY"]
AL_URL = ENV.get("ACTIONLAYER_API_URL", "https://api.actionlayer.io")
MODEL = ENV.get("NOVITA_MODEL", "zai-org/glm-5.2")

B, D, G, Y, R, C, X = (
    "\033[1m", "\033[2m", "\033[32m", "\033[33m", "\033[31m", "\033[36m", "\033[0m",
)

# The six facts that actually determine SNAP eligibility. A senior applicant
# knows none of these are being asked for, which is exactly why the form wins.
FACTS = ["age", "state", "household_size", "monthly_income", "assets", "housing_cost"]

SYSTEM = """You triage benefit-screening requests. Callers are vague; eligibility
screeners are not. Return ONLY minified JSON, no prose, no code fences.

Given a vague request, return:
{"missing": ["fact", ...], "questions": ["short question", ...]}

Ask ONLY about these facts, and only ones the request does not already answer:
age, state, household_size, monthly_income, assets, housing_cost.
Max 4 questions. Each question must be answerable by a non-expert in a few words."""

GOALSYS = """Write ONE imperative sentence instructing a browser agent to complete a
public benefits eligibility screener for this applicant. Include every fact given.
No preamble, no quotes, no explanation. Under 300 characters. Output the sentence only."""


def http(url, payload=None, headers=None, method=None, timeout=90):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url, data=data, method=method or ("POST" if data else "GET")
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "lastmile/1.0")  # Python-urllib UA gets 403d
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode() or "{}", strict=False)
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400]
        raise SystemExit(f"{R}HTTP {e.code} from {url}{X}\n{body}")


def novita(system, user, max_tokens=3000):
    # NOTE: these are reasoning models — reasoning_content burns the token
    # budget before `content` is emitted. Starve it and you get "" back.
    # Keep max_tokens generous.
    if not NOVITA_KEY:
        raise SystemExit(f"{R}NOVITA_API_KEY missing from .env{X}")
    out = http(
        f"{NOVITA_URL}/chat/completions",
        {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.2,
        },
        {"Authorization": f"Bearer {NOVITA_KEY}"},
    )
    msg = out["choices"][0]["message"]
    return (msg.get("content") or "").strip()


def parse_json(text):
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```")[1]
        t = t[4:] if t.startswith("json") else t
    i, j = t.find("{"), t.rfind("}")
    return json.loads(t[i : j + 1], strict=False)


# ---------- ActionLayer ----------

def al_fire(url, instruction):
    if len(instruction) > 480:
        print(f"{Y}!! instruction {len(instruction)} chars — truncates ~500{X}")
    r = http(
        f"{AL_URL}/v1/actions/direct.browser_action",
        {"inputs": {"url": url, "instruction": instruction}},
        {"Authorization": f"Bearer {AL_KEY}"},
    )
    return (r.get("payload") or {}).get("ticket_id")


def al_get(tid):
    # /tasks/{id}, NOT /v1/actions/tickets/{id} — the latter hides info_request
    return http(f"{AL_URL}/tasks/{tid}", headers={"Authorization": f"Bearer {AL_KEY}"})


def al_reply(tid, key, value):
    return http(
        f"{AL_URL}/tasks/{tid}/reply",
        {"sensitive": False, "info": {key: value}},
        {"Authorization": f"Bearer {AL_KEY}"},
    )


def watch(tid):
    print(f"\n{C}ticket {tid}{X}  {D}(15-20 min is normal){X}")
    t0 = time.time()
    while True:
        t = al_get(tid)
        st = t.get("state")
        el = int(time.time() - t0)
        print(f"\r  {st}  {el}s ", end="", flush=True)

        if st == "blocked_on_user":
            ir = t.get("info_request") or {}
            qs = ir.get("questions") or []
            print(f"\n\n{Y}{B}  ⏸  IT'S ASKING YOU:{X}")
            for q in qs:
                print(f"     {q['label']}")
            if not qs:
                print(f"     {D}(no question text — check info_request){X}")
                return t
            ans = input(f"\n  {B}your answer ▸ {X}").strip()
            al_reply(tid, qs[0]["key"], ans)
            print(f"  {G}sent — resuming{X}")
            t0 = time.time()
            continue

        if st in ("completed", "failed", "cancelled"):
            print(f"\n\n{B}{'─'*60}{X}")
            print(f"{G if st=='completed' else R}{B}  {st.upper()}{X}  {D}after {el}s{X}\n")
            print(t.get("reason") or json.dumps(t.get("result") or {}, indent=2) or t.get("error"))
            return t
        time.sleep(15)


# ---------- main ----------

def main():
    args = sys.argv[1:]
    if args and args[0] == "--resume":
        return watch(args[1])
    if not args:
        raise SystemExit(__doc__)

    ask = args[0]
    facts_path = args[args.index("--facts") + 1] if "--facts" in args else None
    target = "https://www.benefits.gov/benefit-finder"

    print(f"\n{B}{'═'*60}{X}")
    print(f"{R}{B}  THE VAGUE ASK{X}")
    print(f"  \"{ask}\"")
    print(f"{D}  → a browser agent handed this blocks on ambiguity, ~20 min per block{X}")

    if facts_path:
        facts = json.load(open(facts_path))
    else:
        print(f"\n{C}{B}  NOVITA — what's actually missing?{X}  {D}({MODEL}){X}")
        plan = parse_json(novita(SYSTEM, ask, 3000))
        print(f"{D}  missing: {', '.join(plan.get('missing', []))}{X}\n")
        facts = {}
        for q in plan.get("questions", [])[:4]:
            facts[q] = input(f"  {q}\n  {B}▸ {X}").strip()

    print(f"\n{C}{B}  SPECIFIED GOAL{X}")
    goal = novita(GOALSYS, f"Vague: {ask}\nFacts: {json.dumps(facts)}", 3000)
    goal = goal.strip().strip('"')
    print(f"{G}  {goal}{X}")
    print(f"{D}  {len(goal)} chars{X}")

    print(f"\n{B}{'═'*60}{X}")
    print(f"  {R}vague{X} → blocks, ~20 min wasted, no answer")
    print(f"  {G}specific{X} → executes")
    print(f"{B}{'═'*60}{X}")

    if "--dry" in args:
        return
    tid = al_fire(target, goal)
    print(f"\n{D}fired. resume anytime: python3 snap.py --resume {tid}{X}")
    watch(tid)


if __name__ == "__main__":
    main()
