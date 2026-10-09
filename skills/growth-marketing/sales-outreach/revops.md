# Revenue operations reference

The system connecting marketing, sales and customer success: shared definitions, routing, scoring, pipeline hygiene and handoffs. Fix process before buying tools; automate only what works manually.

Contents: 1 lifecycle stages · 2 MQL and SLAs · 3 lead scoring · 4 routing · 5 pipeline stages · 6 metrics · 7 automations · 8 deal desk · 9 data hygiene · 10 motion differences.

## 1. Lifecycle stages

| Stage | Entry criteria | Owner | Exit to |
|---|---|---|---|
| Subscriber | Opted in to content | Marketing | Lead on any meaningful engagement |
| Lead | Known contact with some engagement | Marketing | MQL when fit + engagement threshold met |
| MQL | Score above threshold (fit and engagement both) | Marketing → sales | SQL or recycled |
| SQL | Sales accepted and qualified (need, authority, timing) | Sales (SDR/AE) | Opportunity or recycled |
| Opportunity | Active deal with amount and close date | AE | Closed won / lost |
| Customer | Signed | CS / account management | Evangelist |
| Evangelist | Referring, reviewing, case study | CS / marketing | — |

Every stage needs written entry/exit criteria, an owner, and a recycle path (lost or unresponsive leads return to nurture with a reason code, not deleted).

## 2. MQL definition and SLAs

MQL = fit AND engagement, not either alone. A perfect-fit company with no engagement is a target account; an engaged non-fit is not a lead.

SLAs (written, measured weekly):
- Marketing → sales: MQL delivered with context (source, score breakdown, key activities).
- Sales acceptance: first contact within 4 business hours (demo/contact requests: minutes); accept or reject within 48 hours with a reason.
- Rejected MQLs go back with reason codes; review rejection reasons monthly to fix scoring.
- Speed matters: responding within 5 minutes to inbound demo requests converts dramatically better than responding in an hour.

## 3. Lead scoring

Three components:

| Component | Examples with typical points |
|---|---|
| Explicit (fit) | Title/seniority match (+15-25), company size in range (+10-20), target industry (+10), target geography (+5)|
| Implicit (engagement) | Pricing page view (+15-20), demo request (+30-50, often auto-MQL), product signup/usage (+20-30), case study view (+10), webinar attended (+10), email click (+3-5), blog view (+1-2)|
| Negative | Student/personal email (−20), competitor (−50/disqualify), job seeker visiting careers (−30), unsubscribed (−20), no activity 30+ days (decay −5 to −10 per period)|

- MQL threshold usually 50-80 points depending on the model; demo requests often bypass to MQL.
- Product-led: weight product signals (activation milestones, team invites, limit hits) above content.
- Calibrate: compare score distributions of closed-won vs. closed-lost; adjust weights quarterly; a score that doesn't separate wins from losses is noise.
- Keep the model explainable; reps ignore black boxes.

`outreach.py score` implements a configurable points model for outbound lists.

## 4. Routing

| Method | When |
|---|---|
| Round-robin | Equal reps, similar territories; simple |
| Territory | Geography, industry or segment specialists |
| Account-based | Existing account owner gets all contacts from that account |
| Skill/tier | Enterprise to senior AEs, SMB to inside sales; language |

Rules: match leads to existing accounts first (avoid two reps on one company); fallback owner when no match; route within minutes; alert on unworked leads after the SLA; reassign after 2× SLA breach.

## 5. Pipeline stages

| Stage | Exit criteria (required fields) |
|---|---|
| Discovery | Pain confirmed, decision process known, next meeting booked |
| Qualification | Budget range, authority mapped, timing, champion identified |
| Solution/demo | Demo done, success criteria agreed |
| Proposal | Proposal sent, pricing discussed, decision date |
| Negotiation | Terms in review, legal/procurement engaged |
| Closed won/lost | Signed / loss reason code |

Required fields per stage are enforced in the CRM; stage probability set from historical conversion, not optimism.

## 6. Metrics

- Lead → MQL, MQL → SQL, SQL → opportunity, opportunity → won conversion by source.
- Pipeline velocity = (opportunities × average deal size × win rate) ÷ cycle length.
- Pipeline coverage: 3-4× the quota for the period.
- Average deal size, sales cycle length, win rate by segment and competitor.
- Speed-to-lead, SLA compliance, MQL rejection rate and reasons.
- Forecast accuracy (forecast vs. actual).

## 7. Automations

Lead assignment and notification; SLA breach alerts; lifecycle stage updates on criteria; task creation on high-intent actions (pricing visit by an open opportunity, usage spike); recycle to nurture after a lost reason; renewal reminders 90/60/30 days out; handoff notes from sales to CS on close; stale opportunity alerts (no activity 14+ days).

## 8. Deal desk

Triggered for non-standard deals: above a size threshold (e.g., $25k ACV), custom terms, multi-year, or discounts beyond rep authority.

| Discount | Approver |
|---|---|
| 0-10% | Rep |
| 10-20% | Sales manager |
| 20-40% | VP/head of sales |
| 40%+ | Deal desk / finance / CEO |

Rules: trade discounts for something (multi-year, prepayment, case study, faster signature); standard non-standard terms list (payment terms, liability caps, SLAs) with approved fallback positions; turnaround target 24-48 hours; log all exceptions and review quarterly. See pricing-and-offers for discount strategy.

## 9. Data hygiene

- Required fields at each stage; picklists over free text.
- Dedup rules: match on email for contacts, domain for accounts; merge weekly; prevent creation of duplicates at entry.
- Enrichment on entry (size, industry, location); re-verify emails before campaigns.
- Owner on every record; no orphan leads.
- Quarterly audit: stale records, invalid emails, missing fields, conflicting lifecycle stages.

## 10. Motion differences

- Product-led: product-qualified leads (activation, usage thresholds, team growth) drive routing; sales-assist triggers on limit hits; scoring weights usage.
- Sales-led: MQL/SQL handoffs, SDR qualification, longer stages, stronger deal desk.
- Hybrid: separate tracks by segment (self-serve below a size, sales above), with clear rules for when self-serve accounts get a rep.
