---
name: pricing-and-offers
description: "Design and change pricing, packaging and offers: value metric, tiers, freemium vs trial, willingness-to-pay research, price increases, guarantees and bonuses. Use when asked \"what should I charge\", how to structure tiers, whether to raise prices, why an offer isn't converting, or how to price a course, service or SaaS. Not for page layout (use conversion-optimization) or sales copy (use marketing-copy)."
license: MIT
metadata:
  category: "growth-marketing"
  version: "3.0.0"
---

# Pricing and Offers

Scope: value metric, pricing model (flat, usage, tier, seat, credit, outcome, hybrid), good-better-best, freemium vs trial, enterprise tier, WTP research (Van Westendorp, MaxDiff, Gabor-Granger), price increases, pricing-page teardown, offer construction (value equation, bonuses, guarantees, honest scarcity, payment plans, upsell ladders), unit economics.

Price on value, between the next-best alternative (floor for differentiation) and the customer's perceived value (ceiling). Cost is a floor, never the basis. Most "we need better copy" problems are offer problems.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `mode` | required | inferred | `new-pricing`, `repackage`, `price-increase`, `pricing-page-teardown`, `offer-design`, `offer-diagnosis`, `wtp-research` |
| `business_type` | required | ask | self-serve SaaS, sales-led SaaS, course, coaching, service/agency, info product, ecommerce, marketplace |
| `current_pricing` | optional | none | Starter $29 / Pro $79 / Business $199 per month |
| `customer_segments` | optional | from product context | freelancers, 2-10 person teams, 50+ seat companies |
| `alternatives` | required for new pricing | ask | spreadsheets + a $99 competitor |
| `value_evidence` | optional | ask | "saves 6 hours/month per finance lead" |
| `metrics` | optional | ask | conversion 3.1%, ARPA $79, monthly churn 3%, CAC $450 |
| `motion` | optional | self-serve | self-serve, sales-assisted, enterprise sales |
| `goal` | optional | revenue growth | growth, revenue, profitability, move upmarket |
| `constraints` | optional | none | must keep a free plan, annual contracts only |

Read `.agents/product-marketing.md` (or the customer-research context file) first.

## Output

Depending on `mode`:
- **Pricing recommendation** ([templates/pricing-recommendation.md](templates/pricing-recommendation.md)): value metric + model, tier table (price, limits, features, who it's for), free/trial decision, enterprise trigger, annual discount, price-page notes, unit-economics check, test/rollout plan, risks.
- **Price-increase plan**: break-even math, segment rollout waves, grandfathering decision, customer email draft.
- **Pricing-page teardown**: 10-dimension scorecard (6 human, 4 machine-readability) with prioritized fixes.
- **Offer sheet** ([templates/offer-sheet.md](templates/offer-sheet.md)): value-equation scores, the six components (core, bonuses, guarantee, scarcity/urgency, name, price/payment), upsell/downsell ladder, and copy-ready guarantee and scarcity lines.
- **Research plan**: survey questions, sample size, analysis method, decision rule.

## Supporting files

- [REFERENCE.md](REFERENCE.md): pricing models, value metrics, tiers and personas, freemium/trial, enterprise, research methods, price-increase rollout, pricing psychology, teardown rubric, unit-economics benchmarks, platform cost crossover. Read for any pricing work.
- [offers.md](offers.md): value equation, offer anatomy, 8 guarantee types and decision tree, bonus stacking, honest scarcity, formats by business type, SaaS offers and the discount trap, ladders. Read for offer work.
- [scripts/pricing_calc.py](scripts/pricing_calc.py): LTV/CAC/payback, price-increase break-even, discount break-even, annual-plan math, platform crossover, Van Westendorp analysis, guarantee refund stress test. `python3 scripts/pricing_calc.py increase --old 49 --new 59 --customers 1200`.
- Templates: [pricing-recommendation](templates/pricing-recommendation.md), [offer-sheet](templates/offer-sheet.md), [price-change-email](templates/price-change-email.md).

## Steps

1. **Classify.** If self-serve SaaS or marketplace → pricing levers dominate (metric, tiers, packaging); offer construction is secondary. If course, coaching, service, info product, high-ticket B2B or direct response → offer construction dominates; also read offers.md.
2. **Gather value and alternatives.** Quantify the outcome (time, money, risk) per segment; list the next-best alternatives and their cost. Aim for perceived value ≈ 10× price. If you can't articulate that → the problem is positioning or offer, not the number.
3. **Pick the value metric.** Test: "as usage of X grows, does the customer get more value?" and is it easy to understand, predictable, hard to game. Seats only if value grows with headcount (otherwise logins get shared). Usage if consumption tracks value (add caps/alerts). Then choose the model (REFERENCE.md §1); layer a second model only if one clearly misprices a real segment.
4. **Set the first price (if none exists).** Pick the order of magnitude by customer: ~$10/month prosumer, ~$100/month SMB team, ~$1,000/month mid-market/business-critical. Round and slightly high beats clever and cheap; avoid ultra-low "$9" pricing that creates false traction. Treat it as a bet to learn from, with a date to revisit.
5. **Package tiers.** Default 3 tiers (good-better-best): entry removes barriers; middle is the recommended plan where most land; top is 2-3× the middle. Differentiate by usage limits, advanced features, support level, and admin/security (SSO, audit logs). Never gate the core value; gate what separates casual from serious use. Map features with MaxDiff results if available (top 20% in all tiers, 20-50% differentiators, 50-80% higher tiers, bottom 20% cut or add-on).
6. **Decide free vs trial.** Freemium if network/viral effects, low marginal cost, large market, natural upgrade limits; the free tier must hook, then limit. Free trial if value needs setup time or buyers are committees: 7-14 days simple, 14-30 complex; card up front → fewer trials, much higher trial-to-paid. Consider a reverse trial (full access, then drop to free).
7. **Enterprise.** Add "Contact sales" (ideally "from $X") when deals exceed ~$10k ARR, or need custom contracts, security review, SSO/SAML, SLAs, onboarding or procurement.
8. **Check unit economics** with `pricing_calc.py unit`: LTV:CAC ≥ 3, CAC payback ≤ 12 months (SMB) / ≤ 18 (mid-market) / ≤ 24 (enterprise); gross margin ≥ 70-80% for software.
9. **Research when stakes are high.** If changing price for > 20% of revenue or entering a new segment → run Van Westendorp (100-300 respondents per segment) + MaxDiff or Gabor-Granger; analyze with `pricing_calc.py vw`. Otherwise test on new signups.
10. **Price increases.** Signals: prospects don't flinch, "so cheap" feedback, trial-to-paid or close rates very high (> ~40%), monthly churn < ~3%, major value shipped. Run `pricing_calc.py increase` for the revenue-neutral loss. Roll out: new customers first → 5-10% of existing → staggered waves; announce 30-90 days ahead (3-6 months for big jumps) with the why and a soft landing (lock old price by switching to annual, grace period, one-time credit). Don't grandfather forever by reflex; price the subsidy.
11. **Offer design/diagnosis** (offers.md): state the offer plainly → score the four value-equation levers 1-10 → audit the six components → fix the lowest-scoring lever only this iteration → draft the changed component → expect honest single-change lifts (roughly 10-40%), not multiples.
12. **Pricing page.** Run the 10-dimension teardown; prices in HTML text (not images), recommended tier marked, "who it's for" per tier, annual toggle with savings (typically 15-20%), FAQ on billing/limits/cancellation, guarantee near CTAs, Product/Offer markup (see seo-optimization schema.md), `/pricing.md` (see ai-search-optimization).
13. **Plan the test/rollout.** Price tests: server-side, consistent per user, measure revenue per visitor and downstream churn/refunds, not just conversion (analytics-and-experiments). Discount only for upgrades, cross-sells or real seasonal windows.

## Checkpoints

- After step 2: value and alternatives agreed; no pricing from cost or competitor-matching alone.
- After step 5: tier table reviewed for "which plan is for me" clarity before setting final numbers.
- Before step 10 rollout: break-even loss computed and the communication drafted.
- Before shipping an offer: every bonus maps to an objection, the guarantee passes the 10%-refund stress test, and any scarcity is real and enforceable.

## Worked example

**Context**: B2B expense tool, flat $49/month per company, 1,200 customers, churn 2.1%/month, trial-to-paid 46%, customers range 3-150 employees.
- Diagnosis: one price for a 3-person studio and a 150-person agency; high conversion and low churn signal under-pricing; value grows with number of spenders.
- Value metric: active card holders (spenders), not seats (approvers shouldn't pay).
- Tiers: Starter $39 (up to 5 spenders, receipts + cards) · Growth $129 (up to 25 spenders, approvals, accounting sync; recommended) · Scale $349 (up to 100 spenders, multi-entity, SSO, audit log) · Enterprise from $12k/year.
- Economics: Growth ARPA $129, margin 0.82, churn 2%, CAC $900 → LTV ≈ $5,290, LTV:CAC 5.9, payback 8.5 months.
- Rollout: new signups first for 4 weeks (watch trial-to-paid and revenue per trial); then existing customers mapped to tier by spender count; 3-person studios stay on Starter at $39 (a cut); others get 90 days' notice plus "lock today's price for 12 months by switching to annual". `increase --old 49 --new 129` → revenue-neutral up to 62% loss among moved accounts; plan expects < 10%.
- Offer layer for the upgrade: "Painless switch" bonus (we import last 12 months of receipts) addressing the top objection from cancellation surveys.

## Pitfalls

- Pricing from cost-plus or copying a competitor's number (you inherit their strategy, not their economics).
- Ultra-low launch prices that attract the wrong customers and are hard to raise 5-10× later; low prices also tend to churn more.
- Per-seat pricing on a product whose value doesn't scale with seats.
- Too many tiers (5+), tiers that blur together, or gating the core value.
- "Contact us" on every tier; prices only in images or JavaScript.
- Discounting to acquire: discount-seekers churn faster and anchor the product as cheap.
- Bonus inflation ($25k of "value" on a $497 product), unconditional guarantees on high-touch offers, fake countdown timers or "3 spots left" that never changes.
- Grandfathering forever without pricing the subsidy; or raising prices for everyone at once with no notice.
- Judging a price test on conversion alone instead of revenue per visitor and retention.

## Related skills

conversion-optimization (pricing page, paywalls, checkout and upsell flows), marketing-copy (pricing and offer copy, psychology), customer-research (value language, alternatives, WTP interviews), analytics-and-experiments (price tests), retention-and-referrals (save offers, failed payments), sales-outreach (deal desk, proposals).

## Done when

- [ ] Value metric and model chosen with the test stated.
- [ ] Tier table complete: price, limits, key features, who it's for, recommended tier; free/trial and enterprise decisions made.
- [ ] Unit economics computed (LTV:CAC, payback) and within benchmarks or flagged.
- [ ] Any price change has break-even math, rollout waves, and a drafted customer message.
- [ ] Any offer has all six components, value-equation scores, objection-mapped bonuses, a stress-tested guarantee and honest scarcity.
- [ ] Test or rollout plan names metrics (revenue per visitor, churn/refunds) and a decision date.
