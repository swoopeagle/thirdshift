# MVP Scope — "Be More Specific" (working title)

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

## The demo

Comedy comes from the finding itself: an extremely capable agent, stopped cold by a human
being vague. The Novita layer plays the exasperated concierge that refuses to act until it
knows exactly what you mean.

**Surface: imgflip meme generator.** Chosen because it is ActionLayer's own documented
example ("make a meme" → imgflip.com), so it's the highest-probability-of-success surface
available; it's read/write but benign (no account, no payment, no PII); and it produces a
**visual artifact** we can put straight on a slide. Payoff: the meme it generates is about
agents dying at the last mile. Self-referential, and the artifact IS the punchline.

## In Scope

- Novita-powered "specificity interrogator": vague ask in → 2–3 clarifying questions →
  precisely-specified goal string out. Fast, deterministic, fully ours, demos instantly.
- A visible **before/after diff** of the goal string. This is the differentiation — do not
  rush past it in the demo.
- One `direct.browser_action` call to imgflip via `./al.sh`, with the `blocked_on_user`
  round trip handled if it fires.
- A recorded run (screen capture) as the primary artifact.
- 3 slides: the measurement, the architecture, the meme.

## Out of Scope

- Any government or benefits portal. 0 for 2 this afternoon.
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
