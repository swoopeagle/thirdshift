# lastmile — Last Mile Agent Hackathon (Tue 2026-07-21)

Novita AI + ActionLayer, AWS Builder Loft SF. Doors 5:30 · workshops 6:00–6:45 ·
**hacking 6:45–8:00 (75 min)** · judging 8:00. $7K+ prizes incl. **FDE interviews**.
Judges: Nathan Handler (Reddit), Oscar Courbit + Simon Lefort (ClarityCare AI),
Aditya Salian (Atlas).

## The stack

- **Novita** — inference only. OpenAI-compatible, `https://api.novita.ai/openai/v1`,
  `Authorization: Bearer`. Verified working. Serves kimi-k3, glm-5.2, minimax-m3, hy3.
- **ActionLayer** — browser-agent concierge, ships as an MCP server (`pip install actionlayer`,
  NOT the orphaned `actionlayer-mcp`). `https://api.actionlayer.io`. Registered at user scope.
  Keys are `ak_…` (the dashboard copy button prepends a `key` label — strip it).

## What we measured (2026-07-21 afternoon, live)

| Target | Result |
|---|---|
| Wikipedia (their own docs example) | ✅ succeeded, **~20 min** (docs say 30s–5min). Output accurate + cited. |
| example.com | ✅ succeeded, ~15 min |
| **benefitscal.com** (CA CalFresh) | ❌ **failed** ~6 min — `"The task could not be completed."`, zero detail |
| **benefits.gov/benefit-finder** | ❌ blocked twice on specificity, then **failed** ~5 min after both were answered |

**Both government benefit portals failed. Two for two.** The two successes were trivial
read-only pages. We have no evidence it completes a real form-heavy government flow, and
that is precisely the category their marketing calls out as a strength.

Failures carry no diagnostic detail — you cannot distinguish bot-detection from
element-not-found from timeout.

## The finding worth pitching

The benefits.gov ticket blocked **twice, both times on ambiguity, never on credentials**:

1. "What information must be reported?" — our instruction was truncated (~500 char limit)
2. "Url provided redirects to general page… which specific benefit should be chosen?"

We went in expecting the wall to be an OTP or a login. It was **under-specification**, every
time — and each block cost a full ~15–20 min cycle. That's the thesis, measured:

> The last mile isn't authentication. It's specification.

Which is what makes the Novita half load-bearing rather than decorative: it front-loads
specificity before the ask ever reaches the slow, expensive executor.

## Architecture we're pitching

```
vague human ask
  → Novita (fast, cheap, deterministic, ours): interrogate into a goal that
    uniquely identifies the want
  → ActionLayer: execute on the live site
  → blocked_on_user: ask for exactly one thing
  → completed
```

Product it implies: **`clew` + ActionLayer.** Clew already finds grants, opens a Slack war
room per prospect, and drafts a competitive application — then stops at the apply link.
ActionLayer is the missing "submit". Both `clew` and `ece-agents` already state the design
principle *"agents draft and prepare; humans approve and send"* — `blocked_on_user` IS that
approval gate expressed as a protocol. Slack is the right surface because it's async (a
20-min ticket is fine in a channel, intolerable in a chat UI) and threaded (free audit trail).

## Hard constraints

- **~15–20 min per ticket** → 3–4 attempts in the 75-min window. Nothing fired after 7:40.
- **Live on-stage demo is off.** Record the run (`showrunner`) and narrate it.
- Instructions truncate ~500 chars.
- `blocked_on_user` detail is ONLY on `GET /tasks/{id}` — the documented action-ticket
  endpoint and its MCP tool show nulls. Use `./al.sh`, which always hits `/tasks/{id}`.

## Boundaries

- No real applications submitted to government benefits portals with fabricated identities.
- No `usps.create_shipping_label` — charges the saved card with no confirm step.
- Never re-fire on `queued` (double-charges the session); use idempotency keys.
- Rotate both API keys after the event — they were pasted into a chat transcript.

## Files

- `CHEATSHEET.md` — the one-pager to open at the venue
- `al.sh` — CLI helper (fire / task / watch / get / reply); works around the info_request gap
- `check_keys.sh` — verifies both keys
- `.env` — keys, gitignored, chmod 600

## Ticket IDs for the organizers

- `tkt_wf1gX1Hsf9mGA0Wpq3lp7g` — their docs example, succeeded but ~20min vs documented 30s–5min
- `tkt_3MkSKxB6TtgLpnP6fduh4w` — benefitscal.com, failed, no detail
- `tkt_-RBYf2D9U3H3ApP7t0512A` — benefits.gov, blocked twice on specificity then failed;
  the question text was invisible on `/v1/actions/tickets/{id}`
