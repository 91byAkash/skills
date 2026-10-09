---
name: analytics-and-experiments
description: "Set up trustworthy tracking and run sound A/B tests. Use when the user wants a tracking plan, UTM conventions, GA4 or tag-manager setup, asks \"are my events firing\", sees ad platforms under-report conversions, or asks how long to run a test or whether a result is significant. Not for deciding what to change on a page (use conversion-optimization)."
license: MIT
metadata:
  category: "growth-marketing"
  version: "3.0.0"
---

# Analytics and Experiments

Measurement exists to change decisions. Track the few events that answer real questions, make the money events impossible to lose, and only call experiments you powered in advance.

Scope: decision-driven tracking plan (events, properties, naming, UTMs), tag-manager and GA4 implementation, consent mode, server-side conversion APIs, attribution views, and A/B test design and analysis (hypothesis, sample size, duration, significance, sample-ratio checks, experiment backlog). Campaign setup belongs to paid-ads.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `mode` | required | inferred from the ask | `tracking-plan`, `audit`, `server-side`, `test-design`, `test-analysis`, `program` |
| `business_model` | required | ask | SaaS self-serve, B2B demo-led, ecommerce, marketplace, content/ads |
| `decisions` | required for tracking | ask; propose 3-5 | "Which channel brings paying users?", "Where does onboarding stall?" |
| `stack` | optional | GA4 + tag manager on web | GA4, GTM, product analytics tool, CDP, server framework |
| `ad_platforms` | optional | none | Meta, Google Ads, TikTok, Bing Ads, LinkedIn |
| `consent_regions` | optional | assume EU/UK visitors exist | EU, UK, California, none |
| `baseline_rate` | required for test design | ask; never use site-wide average | 0.04 (signup start → signup complete) |
| `daily_traffic` | required for test design | ask | 1,800 eligible visitors/day |
| `mde` | optional | 10-20% relative for mature pages, 20-50% for bold redesigns | 0.15 relative |
| `alpha` / `power` | optional | 0.05 two-sided / 0.80 | 0.05 / 0.9 for high-stakes |
| `results` | required for analysis | ask | control 9,800 users / 412 conv; variant 9,750 / 468 |

If `.agents/product-marketing.md` (or a similar product-context file written by customer-research) exists, read it first and only ask for what it lacks.

## Output

Pick the deliverable(s) that match `mode`:

- **Tracking plan**: [templates/tracking-plan.md](templates/tracking-plan.md) filled in: decisions → metrics → events table (name, trigger, properties, destination, owner), user identity rules, conversions with counting method, UTM convention, consent notes, QA checklist.
- **Audit**: findings table (issue, evidence, impact, fix, owner) ranked by revenue impact, plus a click-id coverage and order-reconciliation result if ads run.
- **Server-side plan**: the 7-link chain (capture → persist → carry → attach → report → dedupe → verify) with what exists, what is missing, and payload specs per platform.
- **Test plan**: [templates/test-plan.md](templates/test-plan.md) with the calculator output pasted in.
- **Test readout**: [templates/test-results.md](templates/test-results.md) with a verdict of win / lose / inconclusive and the next action.
- **Program**: backlog with ICE scores and cadence from [templates/experiment-backlog.md](templates/experiment-backlog.md).

## Supporting files

- [REFERENCE.md](REFERENCE.md): statistics (formulas, corrected sample-size table, sequential tests, multiple variants, SRM, novelty), attribution views, GA4 and tag-manager setup details, UTM rules, server-side payload and hashing rules, consent, debugging matrix. Read when implementing or when a number looks wrong.
- [event-library.md](event-library.md): ready event names and properties for marketing sites, SaaS product, monetization, ecommerce, B2B accounts, plus standard funnels. Read when drafting the events table.
- [scripts/abtest.py](scripts/abtest.py): sample size, duration, minimum detectable effect, significance with confidence interval, and sample-ratio-mismatch check. Run instead of guessing: `python3 scripts/abtest.py duration --baseline 0.04 --mde 0.15 --daily 1800`.
- Templates: [tracking-plan](templates/tracking-plan.md), [test-plan](templates/test-plan.md), [test-results](templates/test-results.md), [experiment-backlog](templates/experiment-backlog.md).

## Steps

### A. Tracking plan or audit

1. **Write the decisions first.** List 3-5 decisions the data must inform. For each, name the metric and the events needed to compute it. If an event does not feed a decision → drop it.
2. **Inventory what exists.** Tags, data layer pushes, server events, ad pixels, product analytics calls. If auditing → open the tag-manager preview / analytics debug view and click through the main funnel, recording what fires (event, params, duplicates).
3. **Name events `object_action`, snake_case, past tense** (`signup_completed`, `plan_selected`). Put variation in properties, not names (`cta_clicked` + `cta_location=hero`, not `hero_cta_clicked_v2`). Reuse the analytics tool's recommended names where they exist (`sign_up`, `purchase`, `begin_checkout`) so built-in reports work.
4. **Choose properties.** Every event gets a standard context set (page, user/account ids, plan, campaign). No PII (emails, names, phone numbers) in analytics properties. Keep custom dimensions under the tool's quota; register only the ones you will segment by.
5. **Define identity.** Anonymous id on first visit → `user_id` (and `account_id` for B2B) on signup/login; never set `user_id` to an email. If the product is B2B → track at both user and account level.
6. **Define conversions and counting.** Leads/signups: once per session. Purchases: every event, with `transaction_id`, `value`, `currency`. Mark only true business outcomes as conversions (5 or fewer key events per property is a good ceiling).
7. **Set the UTM convention** (REFERENCE.md §UTMs): lowercase, fixed vocab for `utm_medium`, a shared sheet for every tagged link, never UTMs on internal links.
8. **Plan consent.** If EU/UK/similar visitors → load tags behind a consent manager with consent mode; analytics may model unconsented traffic but ad pixels must respect the choice. Server-side events are not a way around consent.
9. **Decide client vs server per event.** Money and lifecycle events (purchase, subscription start/renew/cancel, refund, qualified lead) → send from the backend. UI interactions → client. If ads run → do section B.
10. **QA** with the checklist in the template; then compare one week of analytics conversions with the source-of-truth table (orders, CRM). If the gap is > 10-15% and not explained by consent opt-outs → treat as a bug.

### B. Server-side conversion reporting (ads running)

11. Build the chain in order; skipping early links is why "we already have server-side" still under-reports:
    1. **Capture** click ids (`fbclid`, `gclid`/`wbraid`/`gbraid`, `ttclid`, `msclkid`, `li_fat_id`) plus all `utm_*`, landing URL, referrer, user agent and the visitor's real IP on the first hit, before any redirect.
    2. **Persist** them server-side against a first-party session (browser-script storage can be capped at about 7 days on some browsers).
    3. **Carry** them across every step; on a cross-domain hop forward them explicitly in the redirect and re-persist.
    4. **Attach** them to the lead/order record.
    5. **Report** from a queue with retries (never inline in checkout): event name, time, `event_id`, value, currency, click id, hashed identifiers normalized per REFERENCE.md.
    6. **Dedupe**: browser and server events for the same conversion share one `event_id`.
    7. **Verify**: platform test-event tools, then weekly reconciliation.
12. **Health metric: click-id coverage** = paid orders with a click id ÷ paid orders. If it is far below the paid-traffic share → links 1-4 are broken. Track the platform-reported ÷ actual ratio weekly; a stable ratio is healthy, a swinging one means dropped events.

### C. Experiment design

13. **Is this worth testing?** If the change is a clear bug fix, legal requirement, or traffic is too low (step 15 says > 8 weeks) → ship it and monitor instead. Otherwise continue.
14. **Write the hypothesis**: "Because [evidence], we believe [change] for [audience] will [move primary metric by ≥ MDE]. We will know when [metric definition]." One primary metric, 2-3 secondary metrics, 1-3 guardrails (revenue per visitor, refunds, support tickets, unsubscribe rate).
15. **Size it**: `python3 scripts/abtest.py duration --baseline B --mde M --daily D --exposed E --variants K`. Decision on the verdict:
    - ≤ 4 weeks → proceed.
    - 4-8 weeks → proceed only for high-impact changes.
    - > 8 weeks → raise the MDE (test a bolder change), move upstream where traffic is higher, pool similar pages, cut variants, or decide qualitatively.
    - If you plan segment readouts → size for the smallest segment.
16. **Design**: one meaningful change per test (bold enough to plausibly hit the MDE); randomize by user, not pageview; 50/50 default, 90/10 or ramp 10→50% for risky changes; server-side assignment if flicker or pricing is involved.
17. **Pre-launch**: QA every variant on mobile and desktop, verify the primary metric fires in both arms, record planned sample and stop date. Run whole weeks (minimum 7 days, ideally 2 business cycles for B2B).
18. **During**: check daily for breakage, SRM (`abtest.py srm`) and guardrails only. Do not stop for a "win" before the planned sample; stopping for a significantly harmful guardrail is allowed. If peeking is a must → pre-register a sequential method (REFERENCE.md).

### D. Analysis and program

19. **Analyze** with `abtest.py analyze --control N C --variant N C --planned P`. Read in order: SRM → sample reached → significance → CI vs MDE → secondary consistency → guardrails → segments (exploratory only).
20. **Decide**: significant win and guardrails flat → ship; significant loss → keep control and log why; inconclusive → do not call it; ship only if cheaper/simpler and the CI rules out meaningful harm; mixed → follow-up test, not a segment-mined "win".
21. **Log** every test (win or not) in the backlog file with the reusable pattern and where else to apply it.
22. **Program mode**: keep 20+ scored hypotheses (ICE 1-10 each, averaged), aim for 4-8 launches/month, expect a 20-30% win rate (sustained higher usually means timid hypotheses), weekly guardrail check, biweekly readouts, monthly re-score.

## Checkpoints

- After step 1: the user agrees with the decision list before you write 40 events.
- After step 10: analytics vs source-of-truth gap measured and explained.
- After step 12 (ads): click-id coverage number reported.
- Before step 17: hypothesis, primary metric, MDE, sample and stop date written down and agreed.
- Before calling any result: SRM passed and planned sample reached.

## Worked example

**Ask**: "Trial signups from our pricing page feel low. Should we test a new layout?"
- Baseline: pricing view → trial start = 4.0%; 1,800 pricing views/day; MDE 15% relative.
- `abtest.py duration --baseline 0.04 --mde 0.15 --daily 1800` → 17,943 per variant, 20 days → run 21 days (3 full weeks). Feasible.
- Hypothesis: "Because session recordings show 38% of visitors toggling annual/monthly and leaving, we believe defaulting to annual with monthly price shown beside it will raise trial starts ≥ 15% for new visitors. Primary: `trial_started` ÷ users with `pricing_viewed`. Guardrails: paid conversion at day 14, refund rate."
- Day 10 readout request from stakeholders: 9,800/412 vs 9,750/468 → p = 0.044 but sample 54% of plan → reported as "preliminary, no decision"; test continues.
- Day 21: SRM p = 0.79, 18,100/740 vs 18,050/846 → +14.6% relative, p = 0.006, CI roughly +4% to +25%, guardrails flat → ship; log pattern "default to annual on pricing" for the checkout page.

## Pitfalls

- Tracking everything, answering nothing; 200 events with no owner rot within a quarter.
- Event names with embedded variants (`signup_clicked_header_v3`) that make funnels impossible.
- PII in event properties or URLs (`?email=`), which violates analytics terms and privacy law.
- UTMs on internal links: they overwrite the real source and start a new session.
- Calling tests on a peek, on a site-wide baseline, or on a segment you found after the fact.
- Using 90% confidence silently to make a test "fit"; if you lower the bar, write it down.
- Removing the server event to "fix" double counting instead of adding a shared `event_id`.
- Treating ad-platform conversion counts as truth; they overlap and each claims credit. Your order table is truth.
- Ignoring SRM: a 50/50 test landing at 52/48 on 20k users is broken, not lucky.

## Related skills

conversion-optimization (what to test), paid-ads (campaigns that consume these conversions), email-sequences (lifecycle events as triggers), pricing-and-offers (price tests), retention-and-referrals (churn and cohort metrics).

## Done when

- [ ] Every tracked event maps to a stated decision, follows `object_action` naming, and has an owner.
- [ ] Conversions have counting rules; money events are server-side with a shared `event_id`.
- [ ] UTM convention and consent handling are written down.
- [ ] Analytics totals reconciled against the source of truth (and click-id coverage measured if ads run).
- [ ] Any test has a hypothesis, primary/guardrail metrics, calculator output and a fixed stop date before launch.
- [ ] Any readout states SRM result, sample vs plan, effect with CI, guardrails, and a ship / keep / retest decision, and is logged.
