# Churn diagnosis and proactive retention

Contents: 1 metrics · 2 cohorts · 3 reason taxonomy · 4 risk signals · 5 health score · 6 proactive plays · 7 renewals and expansion · 8 benchmarks.

## 1. Metrics

| Metric | Formula | Notes |
|---|---|---|
| Logo churn | customers lost in period ÷ customers at start | Exclude customers acquired mid-period from the denominator |
| Gross revenue churn | (churned MRR + contraction MRR) ÷ start MRR | Never negative |
| Net revenue churn | (churned + contraction − expansion MRR) ÷ start MRR | Negative = net expansion |
| GRR | 1 − gross revenue churn | Ceiling 100%; shows the leak |
| NRR | 1 − net revenue churn | Above 100% means the base grows on its own |
| Quick ratio | (new + expansion MRR) ÷ (churned + contraction MRR) | ≥ 4 strong; < 1 shrinking |
| Involuntary share | failed-payment churn ÷ total churn | Often 20-40% for card-billed products |
| Average lifetime | 1 ÷ monthly churn | 5% → 20 months |
| Save rate | saved ÷ cancel sessions | Only meaningful with saved-customer survival |
| Saved-customer survival | saved customers still paying 90 days later ÷ saved | The honest save metric |

Monthly to annual: annual retention = (1 − monthly churn)^12; 3% monthly ≈ 31% annual churn, 5% ≈ 46%.

`retention_tool.py metrics` computes these from one period's numbers.

## 2. Cohorts

Group customers by start month and track the share still active (or MRR retained) at M1, M2, ... Read:
- **Steep early drop then flat** → a retained core exists; fix early activation to lift the curve.
- **Never flattens** → no durable value for most customers; product/market fit or targeting problem.
- **Newer cohorts above older** → improvements working.
- **Revenue curve above logo curve** → expansion from survivors (good NRR).

Cut by: acquisition channel, plan, billing interval, company size, activation status (did they reach the key action?), first-week usage, cancel reason, which save offer they took. Churn concentrated at renewal dates (annual) needs a renewal process, not a cancel flow.

CSV for `retention_tool.py cohort`: `customer_id,start_month,end_month[,mrr]` where end_month is the first month they were no longer paying (blank if active).

## 3. Reason taxonomy

| Reason | What it usually means | Owner of the fix |
|---|---|---|
| Too expensive | Value not proven, wrong plan, or real budget loss | Pricing/packaging, CS |
| Not using it enough | Never activated or habit faded | Onboarding, lifecycle |
| Missing feature | Product gap or undiscovered feature | Product, docs |
| Switched to a competitor | Competitive gap, price or relationship | Product marketing, product |
| Technical issues/bugs | Quality | Engineering, support |
| Temporary/seasonal | Usage pattern | Pause option |
| Business closed/changed | Unavoidable | Learn and let go |
| Poor support/experience | Service failure | Support |
| Other (free text) | Read monthly; promote recurring themes to options | — |

Triangulate stated reasons with behavior: "too expensive" from someone who never logged in is a usage problem.

## 4. Risk signals

| Signal | Risk | Typical lead time |
|---|---|---|
| Login frequency down 50%+ | High | 2-4 weeks |
| Key feature usage stops | High | 1-3 weeks |
| Support tickets spike, then silence | High | 1-2 weeks |
| Billing/plan page visits rise | High | Days |
| Seats removed | High | 1-2 weeks |
| Data export started | Critical | Days |
| Champion leaves (B2B) | High | 1-3 months |
| Email engagement declines | Medium | 2-6 weeks |
| Satisfaction score drops to detractor (0-6) | Medium | 1-3 months |
| Failed payment | Involuntary risk | Immediate |

Validate on your own history: which signals preceded actual cancels in the last 6-12 months?

## 5. Health score

Weighted 0-100 score from component scores (each normalized 0-100). Starting weights: login frequency 30%, key feature usage 25%, support sentiment 15%, billing health 15%, engagement (email, community, NPS) 15%. Override: data export or seat removal caps the score in "critical".

| Score | Band | Action |
|---|---|---|
| 80-100 | Healthy | Expansion or referral ask |
| 60-79 | Watch | Proactive check-in, feature education |
| 40-59 | At risk | Intervention play |
| 0-39 | Critical | Personal outreach |

Calibrate quarterly: compare scores 30-60 days before churn for churned vs. retained accounts; reweight components that don't separate them. Keep it explainable so CS trusts it. `retention_tool.py health` scores a CSV.

## 6. Proactive plays

| Trigger | Play | Channel / owner |
|---|---|---|
| Usage down > 50% for 2 weeks | "Need a hand with X?" with a specific tip | Email or in-app; lifecycle |
| No login 14 days | What's new + one quick win | Email |
| Approaching plan limit | Upgrade nudge (not a wall) | In-app |
| Detractor score | Personal follow-up within 24h | CS/founder |
| Ticket unresolved > 48h | Escalate and send a status update | Support lead |
| Champion left | Meet the new owner; re-onboard | CS |
| Seats removed / export started | Personal outreach; ask what changed | CS |
| Annual renewal in 30-90 days | Value recap with their usage numbers | CS/email |

## 7. Renewals and expansion (B2B)

- 120 days out: health review, identify risks and stakeholders.
- 90 days: value review / business review with outcomes achieved vs. goals set at onboarding.
- 60 days: renewal proposal; expansion options; address risks.
- 30 days: paperwork; escalate stuck renewals.
- Multi-year or annual prepay offers trade discount for commitment (pricing-and-offers).
- Expansion triggers: seat growth, limit hits, new teams adopting, healthy score + new use case.

## 8. Benchmarks (directional)

- Monthly logo churn: B2C subscriptions often 5-8%; SMB SaaS 3-5%; mid-market 1-2%; enterprise < 1%.
- NRR: SMB-focused SaaS often 90-100%; strong mid-market/enterprise 110-130%.
- Involuntary churn after optimization: roughly 0.5-1.5% of MRR per month for growth-stage companies.
- Cancel flow save rate: 10-15% with a minimal flow, 20-35% with reason-matched offers, higher in B2B with human routing.
