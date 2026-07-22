# MVP Scope — SNAP screening for seniors

_Locked 2026-07-21 18:22 PDT. Build window 18:45–20:00 (75 min). Judging 20:00._

## Problem Hypothesis

Capable browser agents don't fail because they can't act — they fail because the human
didn't say precisely enough what they wanted. **Evidenced this afternoon, measured, not
assumed:** our benefits.gov ticket blocked twice, both times on ambiguity ("which specific
benefit should be chosen?"), never once on credentials or CAPTCHA. Each block cost a full
~15–20 minute cycle. Under-specification isn't a UX annoyance; it's the dominant failure
mode and it's expensive.

## Target User

Anyone handing a real-world task to an agent — but concretely, the person who types
"get me something for tonight" and expects it to work.

## Core Interaction

An organization that already holds a roster of likely-eligible seniors hands over
**de-identified** records. We screen the whole roster at once — 8 in parallel, same
wall-clock as 1 — and hand back which records likely qualify. The org holds the mapping.

**The PII architecture (load-bearing):** SNAP eligibility is determined by age, household
size, income, assets, housing cost, state, disability status. None of those are identifiers.
Screening sends `#47 — 68, CA, household of 1, $1,150/mo, $900 rent` and gets back
`likely qualifies: SNAP, MSP, LIHEAP`. The agent never sees a name, SSN, address, or DOB.
Asked about privacy on stage, the answer is the demo: there is nothing to protect, because
the screening never sees a person. Identified data appears only later, in the low-volume,
consented, human-supervised application step (SNAP's authorized-representative provision).

**Why batch, not single-applicant:** the senior who most needs this is the least likely to
open a terminal. And 15–20 min/ticket kills a consumer concierge but is irrelevant for
overnight back-office work. The latency stops being an apology and becomes the thing that
*selects* the use case.

**Buyers, ranked by roster × income data × incentive × speed-to-pilot:** food banks with
existing SNAP outreach (fastest) → Area Agencies on Aging → PACE → senior housing/PHAs
(income-verified annually) → D-SNP plans (biggest, slowest; they reduce their own medical
spend when members enroll). Hospitals have the data, brutal compliance drag. Churches are a
weak data channel but the strongest trust channel — pair church-as-consent with
food-bank-as-data.

## The demo — SNAP screening for seniors

**The wow number:** ~9 million adults 65+ are eligible for SNAP but not enrolled
(16M among adults 50+). Only ~42% of eligible seniors participate vs 83% of all
eligible people. The barrier cited first in the research is **"perceived or real
burdens of applying."** The number-one thing keeping nine million eligible seniors
from food assistance IS THE FORM. That is exactly what this stack removes.

Judging fit: two of four judges are ClarityCare AI (healthcare) — senior benefits
is directly their world.

**Arc:** "my mom needs help with groceries" → Novita asks the 4 facts that actually
determine eligibility (age, state, household size, income) → specified goal →
ActionLayer completes the benefits.gov screener → `blocked_on_user` if it fires →
result: what she qualifies for.

**Surface: benefits.gov/benefit-finder.** It failed once this afternoon, but that
test was flawed — we asked it to *write a report about navigating* rather than to
*complete the screener*. Re-fired 18:38 with a real task framing.

## In Scope

- Novita-powered "specificity interrogator": vague ask in → 2–3 clarifying questions →
  precisely-specified goal string out. Fast, deterministic, fully ours, demos instantly.
- A visible **before/after diff** of the goal string. This is the differentiation — do not
  rush past it in the demo.
- One `direct.browser_action` call to benefits.gov via `snap.py`, with the
  `blocked_on_user` round trip handled interactively.
- A recorded run (screen capture) as the primary artifact.
- 3 slides: the 9-million number, the architecture, the result.

## Out of Scope

- Real PII. Synthetic applicant only. No application is ever submitted.
- Slack integration / clew wiring. Needs a Railway deploy; would eat the entire window.
  It's the product this implies, not tonight's build.
- Any payment, booking, account creation, or PII.
- More than **two sequential rounds** of ActionLayer tickets. Parallel fan-out within a
  round is free (same wall-clock), so the cap is on rounds, not count.
- A live on-stage ActionLayer run as the spine of the demo. Record it; narrate the recording.
- Retry-on-failure logic, error taxonomy, persistence, tests. Not a product tonight.

## Timeline (hard)

| Time | Action |
|---|---|
| 18:45 | Fire ticket #1 immediately — short instruction, before writing any code |
| 18:45–19:05 | Build the Novita interrogator while it cooks |
| 19:05 | Ticket #1 lands. Re-fire tighter if it blocked. |
| 19:25–19:45 | Ticket #2 — **this is the one you record** |
| 19:40 | **Last possible fire.** Nothing after this returns in time. |
| 19:45–20:00 | Stop building. Capture, 3 slides, rehearse once. |

## Amendment Criteria

Add scope only if:
- [ ] A workshop reveals a capability that removes the 15–20 min latency (would reopen
      live on-stage execution)
- [ ] Ticket #1 succeeds before 19:05 AND the Novita layer is done (buys one extra surface)
- [ ] An organizer confirms a faster/sandbox tier exists for attendees

## Change Log

| Date | Proposed | Decision | Evidence Provided |
|------|----------|----------|-------------------|
| 07-21 18:00 | Benefits-enrollment demo surface | **Cut** | benefitscal + benefits.gov both failed, no diagnostics |
| 07-21 18:22 | Funny surface over serious one | **Accepted** | 3-min slot, 8pm room; comedy is in the measured finding itself |
| 07-21 18:22 | imgflip meme generator | **Accepted** | ActionLayer's own docs cite it; benign; visual artifact |
| 07-21 18:45 | Pivot to SNAP/seniors over bees + meme | **Accepted** | 9M eligible seniors unenrolled; #1 barrier is application burden; ClarityCare judges are healthcare |
| 07-21 18:50 | Pivot single-applicant → de-identified batch | **Accepted** | Latency flips from liability to fit; parallel fan-out costs no extra wall-clock so the two-ticket cap (a time constraint, not a count) is not violated; orgs already staff this work manually |
