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

A user makes a **deliberately vague** request. The Novita layer interrogates it into a goal
that uniquely identifies what they want. ActionLayer executes it. The user sees the
before/after — the vague ask that would have burned 20 minutes, and the specified ask that
completed.

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
- More than **two** ActionLayer tickets during the window. At 15–20 min each that is the
  hard budget.
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
