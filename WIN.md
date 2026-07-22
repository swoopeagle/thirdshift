# The recordable result — benefits.gov, completed 18:55

Ticket `tkt_LclPziYpSgddl0HA-tF3nQ`, fired 18:38, real task framing, senior persona.

**Instruction sent (no name, no SSN, no address, no DOB):**
> Complete this benefit finder questionnaire for a 68-year-old widow living alone
> in California who rents, has $1,150/month Social Security and no other income or
> assets. Return the list of benefits she may qualify for.

**Result — actual federal screener output:**
```
Supplemental Security Income (SSI) for adults: Likely eligible
Retirement benefits: Likely eligible
Tax-advantaged retirement plans information: Likely eligible
Medicare with retirement: Likely eligible
```

## Why the earlier attempts failed (measured, not guessed)

| Attempt | Framing | Result |
|---|---|---|
| 18:20 benefits.gov | "Reconnaissance only… Report: (1) how many steps…" | blocked 2x, then failed |
| 18:20 benefitscal | "Reconnaissance only — map the wall…" | failed, no detail |
| 18:38 benefits.gov | "**Complete** this benefit finder for…" | **completed with real output** |

**ActionLayer executes tasks. It does not write reports about executing tasks.**
Meta-instructions ("report how far you got", "map the wall") fail. Imperative
task instructions succeed. This is the single most useful operating lesson of
the night and it is not in their docs.

## Concurrency limit (measured 18:52)

| Fan-out | Result |
|---|---|
| 8 tickets fired simultaneously | **all 8 failed in 3 min** |
| same goal, 1 ticket alone | completed |
| 6 tickets staggered 20s apart | (in flight 18:55) |

Fast failure (~3 min) is the throttle signature. Slow failure (~5-6 min) or slow
success (~15-20 min) means it actually drove the browser.
