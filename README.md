# lastmile — the last mile isn't authentication, it's specification

_Last Mile Agent Hackathon, AWS Builder Loft SF, 2026-07-21. Novita (inference)
+ ActionLayer (browser execution). Everything below is measured tonight, live —
ticket IDs included so it can be checked._

## Why it matters

Capable browser agents don't fail because they can't act. They fail because
the human didn't say precisely enough what they wanted. We went in expecting
the wall to be OTPs, CAPTCHAs, login walls. We measured something else:

- Our benefits.gov ticket blocked **twice, both times on ambiguity** ("which
  specific benefit should be chosen?") — **never once on credentials**.
- Each block costs a full **15–20 minute** execution cycle.
- The same task, re-fired with a fully specified imperative goal, **completed
  with real federal screener output** (`tkt_LclPziYpSgddl0HA-tF3nQ`, see
  [WIN.md](WIN.md)).

Under-specification isn't a UX annoyance. It's the dominant failure mode, and
it's expensive. That reframes what the "last mile" product actually is.

## What the tech can do

**ActionLayer** drives a real browser end-to-end on sites with no API —
including form-heavy government sites — but only when the goal uniquely
identifies what's wanted, and only at 15–20 min per success. **Novita** serves
fast, cheap open models (glm-5.2 et al.) in milliseconds-to-seconds.

The economics write the architecture: never spend a 20-minute browser cycle
discovering an ambiguity a 2-second model call could have caught.

```
vague human ask
   → Novita: interview — ask only what's missing, like the expert would
   → Novita: compile facts into ONE imperative, fully-specified goal
   → ActionLayer: execute (slow, expensive, but doesn't quit)
```

Operating lessons we measured that aren't in anyone's docs ([WIN.md](WIN.md)):
- **Imperative goals succeed; meta-instructions fail.** "Complete this
  screener for…" works. "Report how far you got…" dies.
- **Concurrency is capped at ~1.** 8 simultaneous → all failed in ~3 min.
  6 staggered 20s apart → **all cancelled**. 1 alone → completed, 4/4.
  Fast failure (~3 min) = throttled; slow failure or slow success = it really
  drove a browser.
- Instructions truncate around ~500 chars — compile tight goals.
- **`blocked_on_user` detail is only on `GET /tasks/{id}`** — the documented
  `/v1/actions/tickets/{id}` and its MCP tool return nulls.
- Python-urllib's default User-Agent gets 403'd; curl doesn't. Set any UA.
- Novita models are reasoning models — `reasoning_content` eats the token
  budget before `content` exists. `max_tokens=400` returns `""`; use 3000+.

### The contradiction worth reporting

15–20 min/ticket makes ActionLayer unusable for a consumer concierge and
**ideal for overnight back-office batch work** — nobody is watching, and the
alternative is a human on hold for 45 minutes. That is the use case the latency
selects for. But the platform cancels or fails concurrent tickets. **The one
shape that fits the latency is the shape it can't do today.** Raise per-account
concurrency and the batch use case opens up.

## How we solved it — two verticals, one architecture

### 1. Plant maintenance manager ([PLANT.md](PLANT.md), [plant.py](plant.py))

Unplanned downtime is the most expensive thing in a plant, and the bottleneck
between "machine is down" and "part is ordered" is a human translating a symptom
into a catalog spec. That translation is tribal knowledge, and it is retiring.
Small facilities never had that person: the maintenance manager IS procurement.

Same two layers, zero new infrastructure, pointed at
industrial maintenance. "Bearing on pump 3 is squealing" → the specificity
layer asks what the retiring senior tech would ask → exact spec → ActionLayer
sources it on McMaster-Carr, which has **no API for small buyers**. Read-only
by design: part number, price, stock — a human approves the filled cart.

**Measured:** `"bearing on pump 3 is squealing"` → `6203-2RS double rubber-sealed
ball bearing (17 mm bore, 40 mm OD, 12 mm width), qty 2, return part number, unit
price, and stock; do not add to cart or check out.` — 240 chars, generated in
seconds by Novita. That is the retiring tech's translation, done by a model.

- Live validation ticket: `tkt_os-NZoZVT6Q_-w8vPo7ovA` — result in
  [PLANT.md](PLANT.md), honestly recorded either way.
- What we deliberately do NOT claim yet (checkout, an evaluated symptom→spec
  corpus) is listed there too.
- The concurrency cap doesn't hurt this vertical: a realistic nightly queue
  of work orders drains **sequentially** — 15–20 min × 20 work orders fits
  inside a single night shift with the cap exactly as it is today.

### 2. De-identified batch SNAP screening for seniors ([SCOPE.md](SCOPE.md), [batch.py](batch.py))

The vertical where we have a **completed end-to-end run**. ~9M adults 65+ are eligible for SNAP and not enrolled; the #1 cited barrier is
the burden of applying. An org that already holds a roster (food bank, Area
Agency on Aging, PHA) hands over **de-identified** records — eligibility is
determined by age/household/income/rent/state, none of which identify anyone —
and we screen the whole roster overnight, in parallel.

- Single-record proof: **completed**, real screener output ("SSI: Likely
  eligible; Medicare with retirement: Likely eligible…") — [WIN.md](WIN.md).
- Batch fan-out is **built and blocked, not proven**: both fan-out attempts
  (8 simultaneous, then 6 staggered) were killed by the concurrency cap. The
  dashboard runs against real sequential tickets. We are not claiming batch
  throughput we did not achieve.
- The PII answer is structural: **the agent never sees a person.**
- The 15–20 min latency that kills consumer concierge is irrelevant overnight
  — the latency *selects* the use case.

## Prove it

```bash
python3 verify.py
```

Re-fetches every ticket cited in this repo from the live ActionLayer API and
checks the recorded state still matches. **Nothing here is asserted from
memory** — successes, failures, and cancellations alike. Exit 0 = every claim
holds. The ledger is [evidence/tickets.json](evidence/tickets.json).

```
  all 10 claims verified against the live API.
```

## Run it

```bash
python3 plant.py "bearing on pump 3 is squealing"      # maintenance vertical
python3 plant.py "..." --dry                           # specificity layer only, ~4s, no ticket
python3 snap.py  "my mom needs help with groceries"    # benefits vertical, interview mode
python3 verify.py                                      # re-verify every claim, live
```

Zero dependencies — Python stdlib only. Needs `.env` with `NOVITA_API_KEY`,
`ACTIONLAYER_API_KEY`.

## The one-sentence pitch

> Agents don't need a better browser. They need the two questions an expert
> would have asked first — so the slow, expensive executor only ever runs a
> goal that can't block.
