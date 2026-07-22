# Plant Maintenance Manager — the generality proof

_The second vertical. Same architecture as the SNAP screener, zero new
infrastructure: specificity layer (Novita) → execution layer (ActionLayer).
If the thesis is real, it should transfer. This file records the transfer._

## Why it's important

- **Unplanned downtime is the most expensive thing in a plant.** Commonly
  cited estimates put it around $50B/yr for industrial manufacturers, and a
  large share of incidents trace to a part that wasn't on the shelf when the
  machine went down. The bottleneck between "machine is down" and "part is
  ordered" is a human translating a symptom into a catalog spec.
- **That translation is tribal knowledge, and it's retiring.** The senior tech
  who hears "squealing" and says "6203-2RS, get the sealed one" is the single
  most-cited loss in the skilled-trades gap. Small facilities — property
  managers, franchises, single-line shops — never had that person at all: the
  maintenance manager *is* the procurement department.
- **The long tail of MRO buying has no API.** McMaster-Carr's integration
  path (punchout) is enterprise-ERP only. Grainger/Zoro similar. TaskRabbit
  and labor marketplaces: no API, period. For a small buyer, the browser is
  the only interface — which is exactly ActionLayer's territory.

## Why this stack specifically

1. **A work order is the purest form of the specificity thesis.** We measured
   tonight (see [WIN.md](WIN.md)) that browser agents block on
   under-specification, not credentials — and each block costs a 15–20 min
   cycle. "Bearing on pump 3 is squealing" is maximally vague; McMaster is
   the most specification-dense catalog on the internet (bore, OD, width,
   seal type, load rating). The specificity layer has real, hard work to do
   here — it's not decoration.
2. **The latency profile selects this use case.** 15–20 min/ticket kills
   "order me a coffee." It is irrelevant when parts are sourced overnight and
   on the bench for first shift. Same argument that made batch screening the
   right shape for SNAP.
3. **Batch is the native shape.** A CMMS work-order queue is a roster. The
   fan-out we built in [batch.py](batch.py) — stagger 20s, poll, dashboard —
   is the same machine pointed at a different queue.

## What we validated tonight (live, not claimed)

| Test | Ticket | Result |
|---|---|---|
| McMaster-Carr read-only part sourcing — "sealed deep-groove bearing equiv. 6203-2RS, 17mm bore, 40mm OD, 12mm width → part number, price, stock" | `tkt_os-NZoZVT6Q_-w8vPo7ovA` | _in flight — result recorded below when terminal_ |

**Result:** _pending_

## What we have NOT validated (and won't claim)

- **TaskRabbit.** Browsing taskers typically hits a signup wall; booking one
  spends money and touches a real person's calendar. The labor half of the
  demo is a design, not a result, until a read-only rate-extraction ticket
  succeeds. Deliberately not fired tonight — the SNAP batch owns the
  concurrency budget.
- **Checkout.** All sourcing tickets are read-only by design. Purchasing is a
  human click on a filled cart (with `max_budget_usd` as the cap when we do
  wire it). We have no evidence yet on McMaster's checkout flow.
- **Real work-order corpus.** The symptom→spec translation is prompted, not
  evaluated. A real pilot needs a facility's historical work orders + what
  was actually ordered, as ground truth.

## The pitch shape

> A maintenance manager types what the tech said. The specificity layer asks
> the two questions the senior tech would have asked, produces the exact
> spec, and overnight the execution layer comes back with part number, price,
> and stock — across catalogs that have no API for buyers this size. The
> human approves; the cart is already full.

Run it:

```bash
python3 plant.py "bearing on pump 3 is squealing"          # interview mode
python3 plant.py "..." --facts workorder.json              # scripted
python3 plant.py --resume tkt_os-NZoZVT6Q_-w8vPo7ovA       # tonight's ticket
```
