#!/usr/bin/env python3
"""
plant.py — the specificity layer, pointed at plant maintenance.

Same architecture as snap.py, different vertical — this is the generality
proof. A maintenance work order is the purest form of the thesis:

  the human says   "the bearing on pump 3 is squealing"
  the catalog wants "6203-2RS, 17mm bore, 40mm OD, 12mm width, double sealed"

That translation is tribal knowledge that walks out the door when the senior
tech retires. Novita does the translation (fast, cheap); ActionLayer executes
against catalogs with no self-serve ORDERING API for small buyers —
McMaster-Carr's data API is approval-gated and order-less; punchout assumes
an ERP. For everyone else the browser is the only way to order.

Why the 15-20 min/ticket latency is fine HERE and fatal for consumer
concierge: parts sourced overnight are on the bench for tomorrow's first
shift. Same latency-selects-the-use-case argument as batch.py.

  python3 plant.py "bearing on pump 3 is squealing"
  python3 plant.py "..." --facts workorder.json   # skip interview
  python3 plant.py "..." --dry                    # show goals, don't fire
  python3 plant.py --resume tkt_xxx

Sourcing tickets are READ-ONLY by design: part number, price, stock — no
checkout, no login, no spend. Purchasing is a human click on a filled cart.
"""
import json, sys

from snap import (
    B, D, G, Y, R, C, X, novita, parse_json, al_fire, watch, MODEL,
)

PARTS_TARGET = "https://www.mcmaster.com"

# What a work order needs before a catalog search can succeed. The interview
# only asks for what the vague ask didn't already answer.
FACTS = ["equipment", "symptom", "part_markings_or_dimensions", "quantity", "urgency"]

SYSTEM = """You triage industrial maintenance work orders. Technicians are vague;
parts catalogs are not. Return ONLY minified JSON, no prose, no code fences.

Given a vague work order, return:
{"missing": ["fact", ...], "questions": ["short question", ...]}

Ask ONLY about these facts, and only ones the work order does not already answer:
equipment (make/model), symptom, part_markings_or_dimensions, quantity, urgency.
Max 4 questions. Each answerable by a technician in a few words."""

GOALSYS = """You are a senior maintenance planner writing a parts-sourcing instruction
for a browser agent on mcmaster.com. From the work order and facts, infer the exact
replacement part the way an experienced tech would (standard designations, dimensions,
seals/material). Write ONE imperative sentence: find that part and return the
McMaster-Carr part number, unit price in USD, and whether it is in stock. Read-only —
do not add to cart or check out. Include every spec. Under 400 characters.
Output the sentence only."""

# --cart mode: push the executor to its actual differentiator — the checkout.
# Still stops short of the irreversible click; placing a real order needs a
# human go, an account, and max_budget_usd on the ticket.
CARTSYS = """You are a senior maintenance planner writing an instruction for a browser
agent on mcmaster.com. From the work order and facts, infer the exact replacement part
(standard designations, dimensions, seals/material). Write ONE imperative instruction:
find that part, add the required quantity to the cart, and proceed through checkout up
to but NOT including placing the order; return the part number, unit price, cart total,
and exactly what checkout requires to place the order (login? guest? payment methods?).
End with: Do not submit the order. Under 450 characters. Output the instruction only."""


def main():
    args = sys.argv[1:]
    if args and args[0] == "--resume":
        return watch(args[1])
    if not args:
        raise SystemExit(__doc__)

    ask = args[0]
    facts_path = args[args.index("--facts") + 1] if "--facts" in args else None

    print(f"\n{B}{'═'*60}{X}")
    print(f"{R}{B}  THE WORK ORDER{X}")
    print(f"  \"{ask}\"")
    print(f"{D}  → a catalog search on this blocks or buys the wrong part{X}")

    if facts_path:
        facts = json.load(open(facts_path))
    else:
        print(f"\n{C}{B}  NOVITA — what would the senior tech ask?{X}  {D}({MODEL}){X}")
        plan = parse_json(novita(SYSTEM, ask, 3000))
        print(f"{D}  missing: {', '.join(plan.get('missing', []))}{X}\n")
        facts = {}
        for q in plan.get("questions", [])[:4]:
            facts[q] = input(f"  {q}\n  {B}▸ {X}").strip()

    cart = "--cart" in args
    print(f"\n{C}{B}  SPECIFIED {'CART' if cart else 'SOURCING'} GOAL{X}")
    goal = novita(CARTSYS if cart else GOALSYS,
                  f"Work order: {ask}\nFacts: {json.dumps(facts)}", 3000)
    goal = goal.strip().strip('"')
    print(f"{G}  {goal}{X}")
    print(f"{D}  {len(goal)} chars{X}")

    print(f"\n{B}{'═'*60}{X}")
    print(f"  {R}\"bearing is squealing\"{X} → wrong part, second truck roll")
    print(f"  {G}exact spec{X} → part number, price, stock — on the bench by first shift")
    print(f"{B}{'═'*60}{X}")

    if "--dry" in args:
        return
    tid = al_fire(PARTS_TARGET, goal)
    print(f"\n{D}fired. resume anytime: python3 plant.py --resume {tid}{X}")
    watch(tid)


if __name__ == "__main__":
    main()
