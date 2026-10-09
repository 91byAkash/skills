---
name: retention-and-referrals
description: "Reduce churn and turn customers into an acquisition channel. Use when the user says churn is too high, wants a cancel flow, save offer, pause option, failed-payment recovery or dunning, a health score, win-back, or a referral, affiliate or ambassador program. Not for trial-to-paid activation (use conversion-optimization) or writing the email copy (use email-sequences)."
license: MIT
metadata:
  category: "growth-marketing"
  version: "3.0.0"
---

# Retention and Referrals

Retention compounds everything else: every point of monthly churn removed raises LTV, lowers the acquisition needed to grow, and makes referral programs worth running. Diagnose before you intervene, match every intervention to a reason, and keep leaving easy.

Scope: churn diagnosis (voluntary vs. involuntary, cohorts, GRR/NRR, reason taxonomy), health scores and save plays, cancel flows, pause and downgrade, win-back, failed-payment recovery (retry logic by decline type, dunning, grace periods), renewals, and referral, affiliate and product-embedded viral programs (incentive sizing, K-factor, fraud controls).

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `goal` | required | ask | cut churn, build cancel flow, set up dunning, launch referral/affiliate program |
| `churn_data` | required for churn work | ask | monthly logo churn 5.5%, 1,200 customers, $98k MRR |
| `split` | optional | estimate 60/40 voluntary/involuntary | 41 voluntary, 25 involuntary last month |
| `reasons` | optional | collect via exit survey | cancel-survey export, support tags |
| `billing` | required for dunning/cancel | ask | billing provider, monthly + annual, pause supported? |
| `usage_data` | optional | ask | logins, key feature events, seats, exports |
| `business_type` | required | from context | B2C self-serve, B2B team plans, freemium |
| `economics` | required for offers/referrals | ask | ARPA $79, gross margin 80%, CAC $400, LTV $1,440 |
| `constraints` | optional | none | must allow online cancel; EU customers; brand tone |

Read `.agents/product-marketing.md` first.

## Output

One or more of, depending on `goal`:
- **Churn diagnosis**: metrics (logo churn, gross/net revenue churn, GRR, NRR, quick ratio, involuntary share), cohort table, reason breakdown, top 3 drivers with evidence, prioritized interventions with expected impact and owner ([templates/churn-diagnosis.md](templates/churn-diagnosis.md)).
- **Cancel flow spec**: screens, survey options, reason → primary/fallback offer map, routing by account value, confirmation and post-cancel sequence, tracking events, compliance check ([templates/cancel-flow-spec.md](templates/cancel-flow-spec.md)).
- **Dunning plan**: pre-dunning, retry schedule by decline type, 4-email sequence with copy, grace period and access rules, in-app notices, metrics ([templates/dunning-emails.md](templates/dunning-emails.md)).
- **Referral/affiliate program spec**: fit verdict, mechanism, incentive with sizing math, trigger moments, share flow, fraud rules, terms, launch plan, metrics ([templates/referral-program-spec.md](templates/referral-program-spec.md)).

## Supporting files

- [churn.md](churn.md): metrics and formulas, cohort reading, reason taxonomy, risk signals, health score, proactive plays, renewals, benchmarks. Read for any churn diagnosis.
- [cancel-flow.md](cancel-flow.md): flow structure, exit survey, offer map, offer types and rules, flows by business type and billing interval, segment flows, post-cancel and win-back, tests, compliance. Read when designing or fixing a cancel flow.
- [dunning.md](dunning.md): pre-dunning, decline classification, retry schedules, email copy, grace periods, in-app patterns, provider-neutral setup, metrics. Read for involuntary churn.
- [referrals.md](referrals.md): viral fit spectrum, seven mechanisms, referral loop design, incentives and sizing, affiliate commissions and recruitment, fraud, metrics, disclosure rules. Read for referral or affiliate programs.
- [scripts/retention_tool.py](scripts/retention_tool.py): `metrics`, `cohort` (CSV → retention table), `health` (CSV → scores and bands), `save` (offer economics), `dunning` (recovery value), `referral` (max reward, K-factor, ROI).

## Steps

1. **Split the churn.** Get logo and revenue churn for 3-6 months; separate voluntary from involuntary (failed payments). If involuntary is > 25% of churn → start with dunning (fastest, least controversial win); else → voluntary first. Run `retention_tool.py metrics`.
2. **Find where it happens.** Build cohorts (`cohort`) by signup month, then cut by plan, channel, tenure, activation status. If most churn happens in the first 30-60 days → it's an activation problem: hand to conversion-optimization and add onboarding saves; if churn is spread across tenure → value/fit/price problem; if one channel or plan dominates → targeting or packaging problem.
3. **Learn why.** Pull reasons from exit surveys, support tags, interviews with recent churners (customer-research), and usage before cancel. Group into the reason taxonomy (churn.md §3). If reason data is missing → ship a minimal exit survey first (one question, 5-8 options, free text) and collect 4-6 weeks.
4. **Prioritize interventions** by (churned MRR in that reason × plausible fix rate) ÷ effort. Typical order: dunning → cancel flow with reason-matched offers → proactive health plays → product fixes for top reasons → win-back.
5. **Fix involuntary churn** (dunning.md): card-expiry reminders, card updater, retry by decline type (soft: retry over ~7-10 days; hard: ask for a new card; authentication: send to authenticate), 4 plain-text emails over ~10 days with a no-login update link, grace period, in-app banner. Size the value with `dunning`.
6. **Design the cancel flow** (cancel-flow.md): trigger → one-question survey → one primary offer + one fallback matched to the reason → clear confirmation with access end date → post-cancel path. If account value is high (B2B above a threshold) → route to a human before cancel completes, never block online cancellation where law requires it. Discounts ≤ 30% for 2-3 months, at most one discount per customer per year; pause 1-3 months; downgrade framed as right-sizing. Check offer economics with `save`.
7. **Add proactive saves**: health score from usage, support, billing and engagement (`health`); triggers (usage −50% for 2 weeks, no login 14 days, seats removed, data export, billing page visits, detractor score, renewal in 30-90 days) mapped to plays and owners.
8. **Plan post-cancel**: confirmation email, data retention notice, nothing for a week, then reason-specific win-back when something relevant changes (email-sequences writes the copy).
9. **Referral fit check** (referrals.md): if retention is weak or NPS/CSAT is low → fix that first; referrals amplify happy customers only. Place the product on the viral spectrum: if natural (collaboration, communication, visible outputs) → build product-embedded loops first; if limited → reward-based referrals, affiliates, partnerships.
10. **Design the program**: trigger at the aha moment or milestone; one-click share with a pre-written message; double-sided reward sized under `LTV × margin − target CAC` (`referral`); reward paid after the referred customer qualifies (paid and past refund window); fraud controls; terms; disclosure rules for affiliates.
11. **Measure and iterate**: churn by cohort monthly; save rate and 90-day survival of saved customers; dunning recovery by decline type; referral participation, conversion, referred-customer retention, cost per referred customer vs. other channels. Test one variable at a time with a holdout (analytics-and-experiments).

## Checkpoints

- After step 3: diagnosis with top 3 drivers reviewed before designing interventions.
- Before launching a cancel flow: compliance check (online cancel path, visible "continue cancelling", no forced calls) and event tracking in place.
- Before launching referrals: reward sizing math and fraud rules approved; terms drafted.
- 30 and 90 days after any change: save rate, saved-customer survival, recovery rate reviewed against baseline.

## Worked example

**Context**: B2C-leaning subscription tool, 1,200 customers, $98k MRR, ARPA ~$79, monthly logo churn 5.5% (66 customers: 41 voluntary, 25 failed payments), no cancel flow, default billing retries only.
- `metrics`: GRR 93.8%, NRR 96.9%, quick ratio 2.1, involuntary 38% of churn → dunning first.
- Cohorts: M1 retention 78% vs. M6 flattening at 52%; customers who never connected a bank feed churn 3× more → activation fix handed to conversion-optimization.
- Exit reasons (6 weeks of survey, n=74): too expensive 31%, not using enough 27%, missing feature 15%, temporary 12%, switching 9%, other 6%.
- Dunning: failed MRR ~$6,000/month, recovery 32% → target 60% with card updater, decline-based retries, 4 emails, read-only grace. `dunning --failed-mrr 6000 --current 0.32 --target 0.6 --monthly-churn 0.055` → +$1,680 MRR recovered per month, ~$108k first-year cash.
- Cancel flow: price → 25% off 3 months (fallback: Starter plan at $29); not using → 1-2 month pause (fallback: setup call); missing feature → roadmap + workaround; temporary → pause; switching → ask which tool + feedback call. `save --mrr 79 --monthly-churn 0.055` → ~$208 expected value per cancel session at 20% acceptance, assuming 60% of accepters survive the discount.
- Results after 90 days: save rate 23%, 90-day survival of saved customers 64%, recovery 57%; logo churn 5.5% → 4.1%.
- Referral (month 4): LTV $1,440, margin 80%, target CAC $400 → max reward $752; chose $50 credit each side, paid after the friend's second paid month. K = 2.2 invites × 12% = 0.26 (amplifier, not engine).

## Pitfalls

- Treating churn as one number; no cohorts; mixing voluntary and involuntary.
- Discounting everyone at cancel; 50%+ discounts; re-offering discounts to repeat cancellers (trains bargaining).
- Hidden cancel buttons, forced calls, guilt-trip copy: dark patterns, bad reviews, and legal exposure.
- Counting a "save" that churns 30 days later; never measuring saved-customer survival.
- Ignoring failed payments; retrying hard declines; dunning emails that require login or blame the customer.
- Pauses longer than 3 months (rarely return); downgrades buried behind support.
- Launching referrals before customers are happy; rewards at signup (fraud magnet); rewards bigger than the economics allow; affiliates without disclosure rules.

## Related skills

conversion-optimization (activation and onboarding, paywalls), email-sequences (win-back, dunning and referral email copy), customer-research (churn interviews, exit-survey synthesis), pricing-and-offers (downgrade tiers, annual plans, discount policy), analytics-and-experiments (events, cohorts, cancel-flow tests), launch-plan (announcing a referral program), marketing-plan (co-marketing partnerships), sales-outreach (renewal and expansion handoffs).

## Done when

- [ ] Churn split into voluntary/involuntary with cohorts and a reason breakdown.
- [ ] Interventions prioritized with expected impact, owner and metric.
- [ ] Cancel flow maps every reason to an offer or a graceful exit, keeps cancellation easy, and tracks each step.
- [ ] Dunning covers pre-dunning, decline-based retries, emails, grace period and in-app notice.
- [ ] Referral program (if any) passes the fit check, has sized rewards, qualification-based payout, fraud rules and terms.
- [ ] Measurement plan includes saved-customer survival and a holdout or baseline comparison.
