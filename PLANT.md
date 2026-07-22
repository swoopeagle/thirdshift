# Plant Maintenance Manager — close the work order, not just log it

_Second vertical, same two layers as the SNAP screener, zero new
infrastructure: specificity layer (Novita) → execution layer (ActionLayer).
This file is the sharpened case plus tonight's live validation._

## The gap, in one sentence

CMMS software (MaintainX, Limble, UpKeep) is excellent at *logging* that pump
3 is down — and then it stops, because between "work order opened" and "part
on the bench" sits a human translating a symptom into a catalog spec and
clicking through a supplier site with no self-serve ordering API at this
company's size.

## The buyer

The facility too small for ERP punchout: property management portfolios,
single-line food & beverage plants, machine shops, franchise back-of-house.
No procurement department — **the maintenance manager is procurement**, and
the senior tech who could hear "squealing" and say "6203-2RS, get the sealed
one" is retiring out of the industry. That translation is the product.

## Why this exact stack — each measured property is load-bearing

1. **The specificity thesis transfers at full strength.** We measured tonight
   ([WIN.md](WIN.md)) that browser agents block on under-specification, never
   on credentials, at 15–20 min per block. A work order is maximally vague;
   McMaster-Carr is the most specification-dense catalog on the web (bore,
   OD, width, seal, load rating). The Novita layer isn't decoration here —
   it's the senior tech's two questions, asked in two seconds instead of a
   wasted 20-minute cycle.
2. **The latency selects the use case.** 15–20 min/ticket kills consumer
   concierge. Parts sourced overnight are on the bench for first shift.
3. **The catalog has no self-serve ordering API for this buyer.** McMaster's
   Product Information API is approval-gated, data-only (no ordering); its
   punchout/cXML path assumes an existing e-procurement system. For a small
   buyer the browser is the only way to *order* — precisely ActionLayer's
   territory. (Sources and grades: [RESEARCH.md](RESEARCH.md).)
4. **A work-order queue drains overnight even at concurrency 1.** We measured
   the platform cap tonight (8 simultaneous → failed; 6 staggered →
   cancelled; 1 alone → completed). That cap kills real-time fan-out — but a
   realistic nightly queue of ~20 work orders × 15–20 min each fits inside a
   single night shift running strictly sequentially. Of the shapes we tried
   tonight, this is the one the platform can serve *as it exists today*.

## Problem, validated (sources + honesty grades: [RESEARCH.md](RESEARCH.md))

- Unplanned downtime costs the world's 500 largest manufacturers ~$1.4T/yr
  (~11% of revenue); an automotive line loses up to $2.3M/hr — Siemens
  "True Cost of Downtime 2024". _(Fortune-500 figures; we extrapolate to
  small facilities and say so.)_
- Deloitte + The Manufacturing Institute (2024): up to 3.8M manufacturing
  workers needed by 2033, ~1.9M jobs likely unfilled, boomer retirement a
  named driver. _(The "retiring senior tech" is our framing on top.)_
- Global MRO market ~$700–770B (2025); MRO is textbook unmanaged tail spend.
- Verified on MaintainX's own feature pages: leading CMMS platforms stop at
  low-stock alerts and PO paperwork — none source parts from suppliers. The
  work-order → part-ordered gap is real.

## Pushing ActionLayer to its ceiling (the repositioning)

Read-only price extraction is ActionLayer's *weakest* mode — a scraper could
do it, and 15–20 min for a price check flatters nobody. Its actual
differentiators are the transactional steps other agents quit at: multi-step
checkout incl. 3DS, login walls (it asks the human for credentials mid-flow),
CAPTCHAs, budget-capped spending (`max_budget_usd`), multi-site jobs with
hand-offs (`create_job`). So the deliverable is repositioned:

| Rung | Deliverable | Status |
|---|---|---|
| 1 | Part number, price, stock (read-only) | ticket in flight tonight |
| 2 | **Filled cart + checkout requirements** (stops before the order) | `--cart` mode built; fires when the concurrency slot frees |
| 3 | Placed order under `max_budget_usd`, human go per order | needs an account + explicit approval — designed, not claimed |
| 4 | Multi-site job: McMaster + Grainger + Zoro, buy cheapest in-stock | `create_job` hand-offs — v2 |

`blocked_on_user` gets repositioned too: it's not a failure mode, it's the
escalation channel — the agent asking the maintenance manager the one question
("shielded or sealed?") instead of quitting, exactly like the junior tech
texting the retired one.

## The metric that sells it

Time from **work-order-open → part-on-bench** (and its evil twin: the second
truck roll from ordering the wrong part). Every hour of that interval on a
down line is the most expensive hour in the plant.

## What we validated tonight (live, not claimed)

| Test | Ticket | Result |
|---|---|---|
| Specificity layer: vague work order + tech-answerable facts → one imperative sourcing goal (226 chars) | — | ✅ works, [plant.py](plant.py) `--dry` |
| McMaster-Carr read-only sourcing: sealed 6203-2RS equiv., 17×40×12mm → part number, price, stock | `tkt_os-NZoZVT6Q_-w8vPo7ovA` | _in flight — recorded here when terminal_ |

**Result:** _pending_

## Honest scope

- **Parts sourcing only, read-only.** The ticket returns part number, price,
  stock. Purchasing is a human click on a filled cart — `max_budget_usd` caps
  it when we wire checkout. No checkout evidence yet, and we don't claim any.
- **Symptom→spec is prompted, not yet evaluated.** A pilot needs a facility's
  historical work orders and what was actually ordered as ground truth.

## The pitch

> Your CMMS knows pump 3 is down. Nothing in your stack gets the part on the
> bench. Type what the tech said; overnight, the two questions the senior
> tech would have asked get asked, the exact spec gets compiled, and the
> supplier sites that will never give you an API get driven for you. First
> shift starts with the part number, the price, and the stock status —
> or the filled cart.

```bash
python3 plant.py "bearing on pump 3 is squealing"          # interview mode
python3 plant.py "..." --facts workorder.json              # scripted
python3 plant.py --resume tkt_os-NZoZVT6Q_-w8vPo7ovA       # tonight's ticket
```
