---
name: conversion-optimization
description: "Diagnose and fix conversion leaks on pages and flows (landing, pricing, forms, signup, onboarding, popups, paywalls, checkout) and design funnels. Use when conversion is low, paid traffic isn't converting, signups don't activate, users don't upgrade, or asked to review a landing page. Not for writing pages (use marketing-copy), price levels (use pricing-and-offers) or test stats (use analytics-and-experiments)."
license: MIT
metadata:
  category: "growth-marketing"
  version: "3.0.0"
---

# Conversion Optimization

Scope: homepage, landing/sales, pricing and feature pages, lead and demo forms, signup, onboarding and activation, popups, paywalls and upgrade prompts, checkout, order bumps and upsells (average order value), multi-step funnels. Output is a ranked fix list, copy alternatives and test ideas.

Find where people drop, figure out why, fix the biggest leak first. Every finding names the element, the failure mode, and the exact change.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `surface` | required | ask | `landing`, `homepage`, `pricing`, `feature`, `blog`, `form`, `signup`, `onboarding`, `popup`, `paywall`, `checkout`, `upsell`, `funnel-design` |
| `url_or_mockup` | required (except funnel-design) | ask | `https://example.com/lp/receipts` or screenshots |
| `goal` | required | ask | trial start, demo request, purchase, email opt-in, upgrade |
| `traffic_source` | optional | ask; assume mixed | paid social (cold, ~80% mobile), search ad with keyword, email list |
| `sample_ad_or_keyword` | optional | none | ad headline "Stop chasing receipts" |
| `funnel_numbers` | optional | none; findings marked as estimates | 12,000 LP views → 900 checkout starts → 380 purchases (30 days) |
| `device_split` | optional | assume mobile-first for paid social | 78% mobile |
| `research` | optional | none | recordings, heatmaps, survey answers, support tickets |
| `activation_event` | onboarding/paywall only | ask; propose from retention data | "created first report and shared it" |
| `offer_and_price` | funnel/upsell only | ask | $49 course; $29 workbook add-on |

Read `.agents/product-marketing.md` (or the customer-research context file) first if present.

## Output

A **conversion audit** in the shape of [templates/audit-report.md](templates/audit-report.md):
- **Diagnosis**: does the leak sit on the page/flow itself, or upstream of it (traffic, offer, price)?
- **Ship now**: no more than 7 changes, highest expected revenue impact first, each a table row of element, what goes wrong and the evidence, the change, effort (S/M/L) and confidence (H/M/L).
- **Copy alternatives**: 2-3 options for headline, subhead and primary CTA, each with its rationale.
- **A/B test first**: judgment calls that deserve a test instead of a straight swap, each with its primary metric.
- **Checked and fine**: what you looked at and found working, so nobody re-fixes it.
- **Blind spots**: inputs you never received and how their absence limits the findings.

For `funnel-design`: a funnel spec from [templates/funnel-spec.md](templates/funnel-spec.md). For `onboarding`: [templates/onboarding-plan.md](templates/onboarding-plan.md). For `popup`/`paywall`: screen specs from [templates/screens.md](templates/screens.md).

## Supporting files

- [REFERENCE.md](REFERENCE.md): checks and rules per surface (page dimensions, landing audit A-G, forms, signup, onboarding and activation models, popups, paywalls, checkout and upsells, funnel shapes and benchmarks). Read the section for the surface you're auditing.
- [experiments.md](experiments.md): test ideas by surface. Read when filling "A/B test first".
- [scripts/funnel.py](scripts/funnel.py): step conversion, biggest leak, value of a lift, and upsell/AOV math. `python3 scripts/funnel.py --steps "Landing:12000" "Checkout start:900" "Purchase:380" --value 49`.
- Templates: [audit-report](templates/audit-report.md), [funnel-spec](templates/funnel-spec.md), [onboarding-plan](templates/onboarding-plan.md), [screens](templates/screens.md).

## Steps

1. **Collect evidence and note gaps.** URL (read the rendered page on a 390×844 viewport and on desktop), traffic source + sample ad, 14-30 days of sessions and conversions, step drop-offs, device split, research. List anything missing under "Blind spots".
2. **Locate the leak before auditing.** If you have step counts → run `funnel.py`; audit the step with the worst drop relative to its benchmark. If sessions < ~1,000 or conversions < ~30 in the window → say the data can't separate a real problem from noise and rank by friction instead.
3. **Rule out upstream causes.** If the ad promises something the page doesn't deliver, the audience is wrong, or the price/offer can't work for the traffic temperature (e.g., $2,000 instant checkout on cold social) → say so in the diagnosis; page edits won't fix it. Route offer problems to pricing-and-offers.
4. **Audit the surface** with the matching REFERENCE.md section. For any page, in impact order:
   1. **Message match**: headline repeats the ad/keyword promise in the same words; the specific thing promised is visible above the fold.
   2. **Value clarity in 5 seconds**: what it is, who it's for, what it costs (or why not shown), what happens on click.
   3. **Primary CTA**: one primary action, visible in the first viewport, value-stating copy ("Start my free trial", not "Submit"); secondary CTA visibly lesser.
   4. **Hierarchy and speed**: scannable headings, LCP ≤ 2.5 s on mobile, no slow hero video on paid social.
   5. **Proof near the decision**: specific, attributed testimonials, logos, numbers, ratings beside CTAs and after claims.
   6. **Objections**: price, "will it work for me", effort to switch/set up, risk → FAQ, guarantee, comparison, process steps.
   7. **Friction**: fields, steps, redirects, surprises (shipping, card required), mobile tap targets, errors.
   8. **After the click**: next step, expectations, upsell or onboarding instead of a dead end.
   9. **Measurement**: conversion event fires; click ids carried to the order (see analytics-and-experiments).
5. **Surface-specific decisions** (details in REFERENCE.md):
   - Form/signup: each field must be needed now; ≤ 3 fields single-step; > 5-6 fields → multi-step easiest-first with progress; social sign-in prominent; keep labels visible.
   - Onboarding: define the activation event from retention data; inventory every step to it; cut, defer, pre-fill; checklist of 3-7 value-ordered items with one pre-completed; triggered emails at 24 h / 72 h for stalled users.
   - Popup: click-triggered > exit intent > scroll 25-50% > time ≥ 30-60 s; never on entry for mobile; once per session, suppress 7-30 days after dismissal, never for converted users or on checkout.
   - Paywall: show after the activation moment, at a real limit or locked feature; always an honest "not now"; cooldown in days after a dismissal.
   - Checkout/upsell: one-page checkout with wallets; post-purchase one-click upsell before any order bump; complementary offer ≤ base price to start; chain ≤ 2 decisions; honest decline link.
6. **Rank** by (traffic through the element × expected effect × confidence) ÷ effort. Cap "Ship now" at 7. Never promise a % lift; give expected direction and relative rank.
7. **Write copy alternatives** for headline/subhead/CTA (use marketing-copy rules): one benefit-led, one specificity-led, one proof-led.
8. **Split fixes vs tests**: clear errors (broken mobile layout, 11-field form, mismatch) → ship now; judgment calls (headline angle, price display, page length) → test with analytics-and-experiments; check traffic is enough to test, else ship and monitor.
9. **For `funnel-design`**: pin offer/price, traffic source, awareness, fulfilment, existing assets → pick a standard shape → spec every page → price ladder → instrumentation blockers → build order (checkout first) → open assumptions.

## Checkpoints

- After step 3: if the diagnosis is "upstream", confirm with the user before producing a page fix list.
- After step 6: the list is ≤ 7 items and every item names element, failure and change.
- Before recommending a popup, paywall or upsell: frequency rules and an honest decline path are specified.
- Before declaring a test winner: planned sample reached (analytics-and-experiments).

## Worked example

**Ask**: "Facebook ads to our receipt-scanning landing page. CPA $96, target $60." Data: 12,000 LP views → 900 trial starts (7.5%) → mobile 81%.
- Message match: ad says "Stop chasing receipts from your team"; page H1 says "The modern spend platform". → Fix 1: H1 "Stop chasing receipts. Your team snaps, Acme files." | S | high.
- Mobile first viewport: hero video 4.2 MB, CTA below the fold, LCP 4.8 s. → Fix 2: static product shot, CTA in first viewport | S | high.
- Form: 7 fields (incl. phone, company size, role). → Fix 3: email + password + Google sign-in; ask role in onboarding | M | high.
- Proof: logos only in footer. → Fix 4: one agency testimonial with name, photo and "saved 6 hours a month" next to CTA | S | med.
- Objection "do my staff need training?" unanswered → Fix 5: 3-step "how it works" + FAQ | S | med.
- A/B test first: price shown on page vs not (primary: trial start rate; guardrail: trial→paid).
- Blind spot: trial→paid by source (needed to judge lead quality).
- Re-measure after 3 weeks: trial start 7.5% → 11.2%, CPA $64 ($96 × 7.5 ÷ 11.2, same spend and click volume).

## Pitfalls

- Generic advice ("add social proof") without element, failure and replacement.
- 30-item fix lists that never ship; cap at 7.
- Auditing the page when the ad, audience or offer is the problem.
- Claiming case-study lift percentages for a fix; they don't transfer.
- Removing fields the sales team actually uses without agreeing an enrichment or later-step replacement.
- Popups on entry, on mobile full-screen, or reappearing after dismissal; intrusive interstitials also hurt search.
- Paywalls before users reach value, guilt-trip decline copy, hidden close buttons, fake countdown timers.
- Order bumps added without watching base conversion as a guardrail.
- Upsells that need card re-entry, create separate orders, or lack idempotency (double charges → chargebacks).

## Related skills

marketing-copy (rewrites), analytics-and-experiments (tracking and test design), pricing-and-offers (price, tiers, guarantees, bump and upsell pricing), email-sequences (onboarding and trial emails), paid-ads (message match from the ad side), retention-and-referrals (cancel flows and save offers).

## Done when

- [ ] Evidence used and gaps listed; leak located with numbers or friction reasoning stated.
- [ ] Diagnosis says page vs upstream.
- [ ] ≤ 7 ranked fixes, each with element, failure mode, specific change, effort, confidence.
- [ ] 2-3 copy alternatives for headline and CTA with rationale.
- [ ] Test list with primary metric per test; "checked and fine" and "blind spots" sections filled.
- [ ] For popups/paywalls/upsells: triggers, frequency caps and decline path specified; for funnels: page specs, price ladder and instrumentation blockers delivered.
