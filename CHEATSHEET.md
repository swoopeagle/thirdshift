# ActionLayer cheat sheet — Last Mile Hackathon, Tue 2026-07-21

Everything below was measured live this afternoon, not read off the docs.

## Hard numbers

| Thing | Measured |
|---|---|
| Trivial read (Wikipedia, their own docs example) | **~20 min** (docs claim 30s–5min) |
| Trivial read (example.com) | ~15 min |
| BenefitsCal (CA CalFresh portal) | **FAILED at ~6 min**, `"The task could not be completed."`, zero detail |
| benefits.gov benefit-finder | reached `blocked_on_user` at ~7 min |

**Budget ~15–20 min per ticket. You get 3–4 attempts in the 75-minute window. Do not start a ticket after 7:40.**

## Gotcha 1 — instructions are truncated (~500 chars)

Long instructions get cut off mid-sentence. The agent then blocks asking what you meant,
burning a full 20-minute cycle. **Keep the instruction to 1–2 short sentences.**

## Gotcha 2 — the blocked question is HIDDEN on the documented endpoint

```
GET /v1/actions/tickets/{id}   → blocked_reason: null, creds_prompt: null   ← useless
GET /tasks/{id}                → info_request: {questions:[{key,label}]}    ← the actual ask
```

`actionlayer_get_action_ticket` (the MCP tool) uses the first one. **Poll `/tasks/{id}` instead**,
or you'll see "blocked" and never learn what it wants.

## Gotcha 2b — it blocks on SPECIFICITY, not credentials

Measured: the benefits.gov ticket blocked TWICE, both times on ambiguity, never on auth.
1. "What information must be reported?" (my instruction was truncated)
2. "Url redirects to a general page. Which specific benefit should be chosen?"

This is the whole pitch, empirically: the last mile is under-specification. Every block costs
a full ~15-20 min cycle, so a vague goal doesn't just degrade quality — it eats the clock.
Front-load the specificity (that's what the Novita layer is for).

## Gotcha 3 — two reply shapes

- `info_request` present → `actionlayer_reply(ticket_id, field_values={"q_0": "..."})`
  keys must EXACTLY match the question keys
- standard block → `actionlayer_reply(ticket_id, field="...", value="...", sensitive=True)` for codes/passwords

Payments are NEVER approved in chat — they go to the user's Link app on their phone.

## Gotcha 4 — hardened gov portals lose

BenefitsCal has real bot defenses and beat it. Don't bet the demo on a state benefits portal.
Federal benefits.gov (softer, mostly static) got further.

## The proven loop

```
invoke_action(direct.browser_action, {url, instruction})  → outcome=queued + ticket_id
  ↓ poll GET /tasks/{id} every 15s
state=pending          → keep polling, no sub-status exists
state=blocked_on_user  → read info_request.questions → actionlayer_reply(field_values=...)
  ↓ back to pending
state=completed        → result / reason has the answer
```

## Don't

- No real application submissions on gov benefits portals with fabricated identities.
- No `usps.create_shipping_label` — charges the saved card, no confirm step.
- Don't re-fire on `queued` — double-charges the session. Use `idempotency_key`.

## Ticket IDs to show the organizers

- `tkt_wf1gX1Hsf9mGA0Wpq3lp7g` — their own docs example, succeeded but ~20min vs documented 30s–5min
- `tkt_3MkSKxB6TtgLpnP6fduh4w` — benefitscal.com, failed with no diagnostic detail
- `tkt_-RBYf2D9U3H3ApP7t0512A` — benefits.gov, blocked with the question only visible via `/tasks/{id}`

## Run order tonight

1. **6:45 sharp** — fire the real ticket FIRST, short instruction. It's the long pole.
2. 6:45–7:05 — build the Novita specificity layer while it cooks (fast, deterministic, yours).
3. 7:05 — first result. Re-fire tighter if needed.
4. 7:25–7:45 — second ticket; this is the one you record.
5. 7:45–8:00 — stop building. Capture the run, 3 slides, rehearse once.

## UPDATE 18:05 — both government portals FAILED

| Target | Result |
|---|---|
| benefitscal.com | failed ~6min, no detail |
| benefits.gov | blocked 2x on specificity, then failed ~5min |

Two for two. The only successes all afternoon were trivial read-only pages
(wikipedia, example.com). **Do NOT stage the demo on a government portal.**
Pick a site you have personally watched succeed, or demo the architecture and
report the portal failures as the finding.

## Gotcha 5 — Python-urllib User-Agent gets 403'd

curl works, `urllib.request` gets `HTTP 403 Forbidden` on POST. Set any UA:
`req.add_header("User-Agent", "lastmile/1.0")`. Cost us 5 min at 18:51.

## Gotcha 6 — Novita models are REASONING models

`reasoning_content` burns the token budget before `content` is emitted.
`max_tokens=400` returns an empty string. Use 3000+.
