#!/usr/bin/env python3
"""
plant.py — thirdshift: the night clerk for the maintenance manager.

Same two layers everywhere: specificity (Novita, seconds) → execution
(ActionLayer, 15-20 min/ticket, concurrency 1 — measured). The work-order
queue drains overnight; first shift finds the results on the bench.

MODES — one queue, four things the night clerk does with it:

  (default)   source a part on a distributor's catalog — part number, price,
              stock. Read-only. --supplier picks the catalog (mcmaster,
              grainger, zoro, motion); nothing else about the run changes.
  --cart      add to cart and drive checkout UP TO but not including placing
              the order; report what the order requires. The executor's real
              differentiator, minus the irreversible click.
  --warranty  fill the manufacturer's warranty/RMA claim from the work order.
              Stops before final submission — a human clicks submit.
  --rebate    find the utility rebate owed for an efficiency replacement —
              program, amount, documentation, deadline. Read-only.

The recovery modes are the point: warranty claims, rebates, and compliance
renewals are money already owed, unclaimed because a portal form stands in
front of it. Slow-tolerant, login-walled, form-heavy — exactly the shape the
executor completed end-to-end tonight (benefits.gov, see WIN.md).

  python3 plant.py "bearing on pump 3 is squealing"
  python3 plant.py "..." --supplier grainger --facts workorder.json --dry
  python3 plant.py "..." --facts workorder.json --dry
  python3 plant.py "pump 3 bearing failed in warranty" --warranty --facts warranty.json --dry
  python3 plant.py "replaced pump 3 motor with premium-efficiency" --rebate --facts rebate.json --dry
  python3 plant.py --resume tkt_xxx

Every mode stops short of the irreversible step (order, submission) by
design. Catalogs and portals at this buyer's size have no self-serve
ordering/filing API — the browser is the only interface. That's the wedge.
"""
import json, sys

from snap import (
    B, D, G, Y, R, C, X, novita, parse_json, al_fire, watch, MODEL,
)

PLANNER = """You are a senior maintenance planner writing an instruction for a
browser agent. {job} Write ONE imperative instruction. Include every fact given.
{stop} Under 450 characters. Output the instruction only."""

# Sourcing is not wired to one catalog. Same goal, same code path, different
# distributor — the executor takes any URL, so the only thing that changes is
# the domain and what that distributor calls its part number.
SUPPLIERS = {
    "mcmaster": ("https://www.mcmaster.com", "mcmaster.com", "McMaster-Carr part number"),
    "grainger": ("https://www.grainger.com", "grainger.com", "Grainger item number"),
    "zoro":     ("https://www.zoro.com",     "zoro.com",     "Zoro part number"),
    "motion":   ("https://www.motion.com",   "motion.com",   "Motion part number"),
}

MODES = {
    "sourcing": {
        "url": "supplier",
        "facts": "equipment, symptom, part_markings_or_dimensions, quantity, urgency",
        "job": "From the work order and facts, infer the exact replacement part the way "
               "an experienced tech would (standard designations, dimensions, seals, "
               "material). Instruct the agent to find that part on {domain} and "
               "return the {idname}, unit price in USD, and whether "
               "it is in stock.",
        "stop": "Read-only — do not add to cart or check out.",
        "flavor": ("\"bearing is squealing\" → wrong part, second truck roll",
                   "exact spec → part number, price, stock — on the bench by first shift"),
    },
    "cart": {
        "url": "supplier",
        "facts": "equipment, symptom, part_markings_or_dimensions, quantity, urgency",
        "job": "From the work order and facts, infer the exact replacement part. "
               "Instruct the agent to find it on {domain}, add the required "
               "quantity to the cart, proceed through checkout up to but NOT including "
               "placing the order, and return the {idname}, unit price, cart total, "
               "and exactly what checkout requires to place the order (login? guest? "
               "payment methods?).",
        "stop": "End the instruction with: Do not submit the order.",
        "flavor": ("read-only lookups are scraper work",
                   "a filled cart at 3am is the executor earning its keep"),
    },
    "warranty": {
        "url": None,  # manufacturer portal — from facts
        "facts": "manufacturer, product_model, serial_number, purchase_date, failure_description, invoice_reference",
        "job": "The failed part is under manufacturer warranty. Instruct the agent to "
               "go to the manufacturer's support site, locate the warranty/RMA claim "
               "form, complete it from the facts, and return the claim reference or "
               "the list of fields the final submission requires.",
        "stop": "End the instruction with: Do not perform the final submission.",
        "flavor": ("a $40 bearing claim nobody files is a donation to the vendor",
                   "the work order already holds everything the claim form asks"),
    },
    "rebate": {
        "url": None,  # utility portal — from facts
        "facts": "utility_provider, facility_state, equipment_replaced, new_equipment_efficiency, install_date",
        "job": "The facility replaced equipment with a higher-efficiency model, which "
               "may qualify for a utility rebate. Instruct the agent to search the "
               "utility's business rebate pages and return the applicable program "
               "name, rebate amount, required documentation, and filing deadline.",
        "stop": "Read-only — do not create accounts or submit applications.",
        "flavor": ("the rebate expires quietly; the utility never reminds you",
                   "same work order, second payout"),
    },
}

INTERVIEW = """You triage industrial maintenance work orders. Technicians are vague;
portals and catalogs are not. Return ONLY minified JSON, no prose, no code fences.

Given a vague work order, return:
{{"missing": ["fact", ...], "questions": ["short question", ...]}}

Ask ONLY about these facts, and only ones the work order does not already answer:
{facts}.
Max 4 questions. Each answerable by a technician in a few words."""

URLSYS = """From these facts, return ONLY the most likely https:// homepage URL of the
{kind}, nothing else. No prose."""


def main():
    args = sys.argv[1:]
    if args and args[0] == "--resume":
        return watch(args[1])
    if not args:
        raise SystemExit(__doc__)

    mode = next((m for m in MODES if f"--{m}" in args), "sourcing")
    cfg = MODES[mode]
    ask = args[0]
    facts_path = args[args.index("--facts") + 1] if "--facts" in args else None

    sup = args[args.index("--supplier") + 1].lower() if "--supplier" in args else "mcmaster"
    if sup not in SUPPLIERS:
        raise SystemExit(f"unknown supplier {sup!r} — choose from: {', '.join(SUPPLIERS)}")
    sup_url, domain, idname = SUPPLIERS[sup]

    print(f"\n{B}{'═'*60}{X}")
    print(f"{R}{B}  THE WORK ORDER{X}  {D}[{mode}]{X}")
    print(f"  \"{ask}\"")

    if facts_path:
        facts = json.load(open(facts_path))
    else:
        print(f"\n{C}{B}  NOVITA — what would the senior tech ask?{X}  {D}({MODEL}){X}")
        plan = parse_json(novita(INTERVIEW.format(facts=cfg["facts"]), ask, 3000))
        print(f"{D}  missing: {', '.join(plan.get('missing', []))}{X}\n")
        facts = {}
        for q in plan.get("questions", [])[:4]:
            facts[q] = input(f"  {q}\n  {B}▸ {X}").strip()

    print(f"\n{C}{B}  SPECIFIED {mode.upper()} GOAL{X}")
    # recovery-mode prompts run longer chains of reasoning — 3000 sometimes
    # comes back empty (reasoning_content eats the budget; see snap.py note)
    job = cfg["job"].format(domain=domain, idname=idname)
    goal = novita(PLANNER.format(job=job, stop=cfg["stop"]),
                  f"Work order: {ask}\nFacts: {json.dumps(facts)}", 6000)
    goal = goal.strip().strip('"')
    print(f"{G}  {goal}{X}")
    print(f"{D}  {len(goal)} chars{X}")

    url = cfg["url"]
    if url == "supplier":
        url = sup_url
        print(f"{D}  target: {url}{X}")
    elif url is None:
        kind = "manufacturer's site" if mode == "warranty" else "utility provider's site"
        url = novita(URLSYS.format(kind=kind), json.dumps(facts), 2000).strip()
        print(f"{D}  target: {url}{X}")

    lo, hi = cfg["flavor"]
    print(f"\n{B}{'═'*60}{X}")
    print(f"  {R}{lo}{X}")
    print(f"  {G}{hi}{X}")
    print(f"{B}{'═'*60}{X}")

    if "--dry" in args:
        return
    tid = al_fire(url, goal)
    print(f"\n{D}fired. resume anytime: python3 plant.py --resume {tid}{X}")
    watch(tid)


if __name__ == "__main__":
    main()
