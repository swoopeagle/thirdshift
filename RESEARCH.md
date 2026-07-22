# thirdshift — Problem-Validation Research
*Compiled 2026-07-21. Every URL below was fetched and verified during this session unless marked otherwise.*

## Executive summary — what's safe on a slide
- **SAFE:** Unplanned downtime costs the world's 500 largest companies ~$1.4T/yr (11% of revenue); automotive lines lose up to $2.3M/hr — Siemens/Senseye "True Cost of Downtime 2024" (STRONG).
- **SAFE:** Deloitte + The Manufacturing Institute (2024): US manufacturing needs up to 3.8M new workers by 2033 and ~1.9M jobs could go unfilled, driven partly by Baby Boomer retirements (STRONG).
- **SAFE with wording care:** Global MRO market ~$700–770B (2025) per multiple research firms; MRO is a canonical "tail spend" category (80% of transactions ≈ 20% of spend, largely unmanaged) (OK — analyst estimates vary widely, cite one firm).
- **SAFE:** CMMS tools (MaintainX et al.) stop at low-stock alerts and PO generation — a human still identifies the part and places the supplier order. Verified against MaintainX's own feature pages (STRONG for MaintainX; say "leading CMMS tools," don't claim we audited all).
- **CAUTION:** McMaster-Carr claim must be softened — they DO have a product-information API, but it is approval-gated (established account, client certificate, subscription caps) and their punchout/cXML/EDI path targets buyers with e-procurement systems. Say "no self-serve ordering API for small buyers," not "no API" (OK). Wrong-part stats exist but only from adjacent industries (WEAK — use as color, not headline).

---

## 1. Cost of unplanned downtime — STRONG
- **Figure:** Unplanned downtime costs the world's 500 largest companies ~**$1.4 trillion/year, 11% of revenues** (up from 8% in 2019). Automotive: idle line costs up to **$2.3M/hour** (+113% since 2019). Average per-facility cost for contract producers/fabricators ~**$260K/hour**; typical large plant loses **27 hours/month**.
- **Source:** Siemens/Senseye, "The True Cost of Downtime 2024." Verified via AEMT's analysis: https://www.theaemt.com/resource/the-true-cost-of-downtime-2024-a-comprehensive-analysis.html and IndexBox summary of the Siemens report: https://www.indexbox.io/blog/network-downtime-costs-manufacturers-billions-analysis-of-2024-siemens-report/
- **Caveats:** Figures describe the Fortune Global 500, not small facilities — frame as "the downtime problem," not "your customer's cost." Siemens' own report page returned 404/403 during this session; the two secondary analyses above agree on the numbers.

## 2. Skilled-trades / maintenance retirement gap — STRONG
- **Figure (current, 2024 study):** US manufacturing may need **3.8M new employees by 2033**; **~1.9M could go unfilled** (more than half of open positions) if the skills/applicant gap isn't addressed. Drivers named: **retiring Baby Boomers** and rising technical-skill demand.
  - Source (fetched): https://themanufacturinginstitute.org/manufacturers-need-as-many-as-3-8-million-new-employees-by-2033/
- **Figure (older, widely quoted):** 2021 study: **2.1M unfilled jobs by 2030**, potential **$1T cost in 2030 alone**; boomer retirement cited by 34% of executives as a reason roles go unfilled.
  - Sources (fetched): https://themanufacturinginstitute.org/2-1-million-manufacturing-jobs-could-go-unfilled-by-2030-11330/ and https://www.prnewswire.com/news-releases/us-manufacturing-skills-gap-could-leave-as-many-as-2-1-million-jobs-unfilled-by-2030--deloitte-and-the-manufacturing-institute-study-finds-301281967.html
- **Caveats:** Use the 2024 numbers (1.9M/3.8M) — the 2.1M figure was superseded. No source found that is specifically about *maintenance technicians* or "tribal knowledge loss"; that framing is ours, supported by the retirement driver. COULD NOT VERIFY a maintenance-tech-specific statistic.

## 3. MRO market size & tail spend — OK
- **Figure:** Global MRO market ≈ **$765.6B (2025) → $970.5B (2035), 2.4% CAGR** (Expert Market Research, fetched: https://www.expertmarketresearch.com/reports/maintenance-repair-operations-mro-market). Other firms: $699.4B (IMARC, 2025) — estimates range roughly $450–770B depending on scope.
- **Tail spend:** Classic pattern — **~80% of purchase transactions represent ~20% of spend** and are largely unmanaged; MRO parts are a textbook tail-spend category. Better tail-spend management yields **~7.1% average savings** (Hackett Group, cited in Fairmarkit, fetched: https://www.fairmarkit.com/blog/what-is-tail-spend-and-how-can-we-manage-it).
- **Caveats:** These are paywalled-analyst topline numbers, not audited figures; cite one firm and say "estimates vary." The 80/20 stat is a heuristic (Pareto), not a measured MRO-specific finding.

## 4. CMMS gap: work order → part ordered — STRONG (for the claim as scoped)
- **Finding:** MaintainX's own parts-inventory page describes low-stock alerts, PO generation, vendor records, and ERP PO sync — **it does not source, identify, or place orders with external suppliers**. "Generate purchase orders automatically to restock parts when they fall below a certain level" — the PO still goes out via a human/ERP. Fetched: https://www.getmaintainx.com/use-cases/parts-inventory-management (see also https://www.getmaintainx.com/use-cases/vendor-management).
- **Interpretation:** The gap we claim — translating a symptom into a part spec and executing the supplier purchase — sits outside what the CMMS automates. Verified directly for MaintainX; Limble and UpKeep marketing describes the same inventory/PO scope but was not individually fetched this session.
- **Caveats:** Say "leading CMMS platforms stop at inventory alerts and PO paperwork" — do NOT say "no CMMS does procurement" (unauditable). Grade: STRONG for MaintainX, OK generalized.

## 5. McMaster-Carr integration options — OK (claim needs softening)
- **Finding:** McMaster-Carr's integration paths are **punchout catalog, OCI, cXML/EDI** — designed to plug into a buyer's e-procurement/ERP system, with a dedicated implementation team (contact eProcurement@mcmaster.com). Fetched: https://www.mcmaster.com/help/punchout-catalog/ and https://www.mcmaster.com/eprocurement/
- **Important correction:** They **do have a Product Information API** (https://www.mcmaster.com/help/api — fetched) but it is **not self-serve**: approval required, established account, per-user client certificate + password, product "subscription" caps and rate limits — and it retrieves **product data only, not ordering**.
- **Safe slide wording:** "McMaster-Carr's integrations (punchout/cXML/EDI, gated data API) assume you already run an e-procurement system — there is no self-serve ordering API for a 10-person facility."
- **Grade:** OK — the spirit of the claim holds; the literal "no API" version is falsifiable in one Google search.

## 6. Cost/frequency of ordering the wrong part — WEAK
- **Figures found:**
  - **~19.4% of parts ordered online are returned** (attributed to Motor.com 2023), often from misidentification; rush orders cost **15–30% more** than planned purchases. Fetched: https://www.wickedfile.com/blogs/5-common-parts-ordering-mistakes-that-are-costing-your-shop-money/ (auto-repair context).
  - Field-service **truck rolls cost ~$150–$500 each** (SightCall; TSIA estimates ~$1,000 fully loaded), and **~25% are avoidable/non-value-added**. Fetched: https://www.smarty.com/articles/truck-roll-costs
- **Caveats:** Both are vendor blogs in adjacent industries (auto repair, telecom/field service) — no peer-reviewed or industrial-MRO-specific figure found for wrong-part frequency in plant maintenance. COULD NOT VERIFY an industrial-maintenance-specific wrong-part statistic. Use as supporting color ("in adjacent industries, ~1 in 5 parts ordered online is returned"), never as a headline stat.

---

*Sections 7–10 added later the same session, for the dollar model ("The money" in README.md).*

## 7. Downtime cost per hour, small/mid facilities — OK
- **Figures:** Aberdeen Research average across sectors ~**$260K/hr**; by sector: discrete manufacturing **$10K–$50K/hr**, food & beverage **$30K–$50K/hr**, heavy industry ~$187.5K/hr, automotive $2.3M/hr; a **small job shop ~$5K/hr**. Fetched: https://reliamag.com/articles/cost-unplanned-downtime-manufacturing/
- **Caveats:** Trade-press compilation of analyst figures, not primary research. For the model we use the **$10K/hr discrete floor** — the bottom of every published range. A "~$25K/hr mid-size" figure circulates in trade content but was not individually verified.

## 8. Warranty recovery rates under manual tracking — WEAK (directionally consistent)
- **Figures:** HVAC service companies recover only **12–18% of eligible warranty claims**; fleet operations report a similar share of eligible repairs going unclaimed annually (missed 30–60-day filing windows, missing documentation); fleets moving from manual tracking to systematic coverage checks report recovery rising from **~30–35% to 85–95%**.
- **Sources (search-surfaced vendor content, not independently fetched):** oxmaint.com, fleetrabbit.com, buscmms.com warranty-recovery guides.
- **Caveats:** All CMMS/fleet-software vendor blogs in adjacent industries; specific numbers vary and even conflict between sources. The safe claim is directional: **under manual tracking, most eligible claims are never filed; systematic filing recovers the majority.** Use the 30%→85% span for modeling, labeled as vendor-reported.

## 9. Maintenance labor cost and wrench time — STRONG (BLS) / OK (wrench time)
- **BLS May 2024 medians:** industrial production managers **$121,440/yr (~$58/hr)**; general maintenance and repair workers **$48,620/yr**. Source: https://www.bls.gov/ooh/management/industrial-production-managers.htm (STRONG; no BLS series exists for "maintenance manager" specifically — the small-facility role sits between these two).
- **Wrench time:** industry average **25–35%** of technician time is hands-on; one pharmaceutical-plant study found **26% hands-on, 74%** consumed by travel, **waiting for parts**, tool location, and admin. Sources: MaintainX/Reliable Plant/vendor learning-center content (OK as color — parts-searching is consistently named a top wrench-time killer, but no isolated parts-only percentage exists).

## 10. MRO spend share and utility motor rebates — OK / WEAK
- **MRO spend:** published benchmarks range **0.5%–10% of revenue** depending on source and industry (BCG, Verdantis, procurement consultancies); heavy industry at the top. Cite as a range; we model at 3%.
- **Motor rebates:** Otter Tail Power lists prescriptive motor rebates of **$40–$7,000 per motor** by HP and type (page returned 403 this session — figure from search results, WEAK); a PG&E industrial guidebook example shows a **$7,293 incentive for a 125 hp premium-efficiency motor upgrade** (search-surfaced, not fetched). Safe wording: "hundreds of dollars for small motors, thousands for large ones, per qualifying swap."
