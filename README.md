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
- **Concurrency throttle:** 8 simultaneous tickets → all fail in ~3 min.
  Staggered 20s apart → they run. Fast failure = throttled; slow = real.
- Instructions truncate around ~500 chars — compile tight goals.

## How we solved it — two verticals, one architecture

### 1. De-identified batch SNAP screening for seniors ([SCOPE.md](SCOPE.md), [batch.py](batch.py))

~9M adults 65+ are eligible for SNAP and not enrolled; the #1 cited barrier is
the burden of applying. An org that already holds a roster (food bank, Area
Agency on Aging, PHA) hands over **de-identified** records — eligibility is
determined by age/household/income/rent/state, none of which identify anyone —
and we screen the whole roster overnight, in parallel.

- Single-record proof: **completed**, real screener output ("SSI: Likely
  eligible; Medicare with retirement: Likely eligible…") — [WIN.md](WIN.md).
- Batch fan-out: 6 de-identified records staggered 20s apart —
  [batch_results.json](batch_results.json).
- The PII answer is structural: **the agent never sees a person.**
- The 15–20 min latency that kills consumer concierge is irrelevant overnight
  — the latency *selects* the use case.

### 2. Plant maintenance manager ([PLANT.md](PLANT.md), [plant.py](plant.py))

The generality proof: same two layers, zero new infrastructure, pointed at
industrial maintenance. "Bearing on pump 3 is squealing" → the specificity
layer asks what the retiring senior tech would ask → exact spec → ActionLayer
sources it on McMaster-Carr, which has **no API for small buyers**. Read-only
by design: part number, price, stock — a human approves the filled cart.

- Live validation ticket: `tkt_os-NZoZVT6Q_-w8vPo7ovA` — result in
  [PLANT.md](PLANT.md), honestly recorded either way.
- What we deliberately do NOT claim yet (TaskRabbit, checkout) is listed
  there too.

## Run it

```bash
python3 snap.py "my mom needs help with groceries"     # single applicant, interview mode
python3 batch.py fire && python3 batch.py watch        # de-identified roster fan-out
python3 plant.py "bearing on pump 3 is squealing"      # maintenance vertical
```

Zero dependencies — Python stdlib only. Needs `.env` with `NOVITA_API_KEY`,
`ACTIONLAYER_API_KEY`.

## The one-sentence pitch

> Agents don't need a better browser. They need the two questions an expert
> would have asked first — so the slow, expensive executor only ever runs a
> goal that can't block.
