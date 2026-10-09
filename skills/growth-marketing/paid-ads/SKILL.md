---
name: paid-ads
description: "Plan, run, audit and scale paid ads on Google, Meta, LinkedIn, TikTok, X and Bing, and write the ad creative. Use when the user wants to run or fix paid ads, asks \"can I afford this channel\", needs ad copy or RSAs, a campaign structure, an account audit or a scaling plan. Not for organic social (use content-strategy) or landing pages (use conversion-optimization)."
license: MIT
metadata:
  category: "growth-marketing"
  version: "3.0.0"
---

# Paid Ads

Paid acquisition should be deterministic: a known amount in, more out, on a clock you can name. Prove the economics, get tracking right, then let creative do most of the targeting. Every live-account change is drafted first and applied only with approval.

Scope: Google Search/Shopping/PMax, Meta, LinkedIn, TikTok, X, Bing; channel affordability (payback, breakeven CPL/CPC/ROAS), budgeting, account structure, keywords and negatives, audiences, bidding, conversion tracking and offline import, kill/keep/scale rules, fatigue, retargeting, ABM, account audits, and creative (angles, hook matrix, statics, short video, RSAs, character limits).

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `mode` | required | inferred | `plan`, `creative`, `rsa`, `audit`, `optimize`, `scale`, `abm` |
| `objective` | required | ask | qualified demos; trial starts; purchases |
| `economics` | required | ask | ACV $3,000, lead→close 10%, gross margin 80%, ARPU per plan |
| `budget` | required | ask | $12k/month |
| `platforms` | optional | chosen in step 2 | Google Search + LinkedIn |
| `offer_and_page` | required | ask | 14-day trial; /agencies landing page |
| `audience` | required | from context file | agency finance leads, 10-80 staff, UK/US |
| `performance_data` | for optimize/audit | ask | 30-day export, search-terms report, CRM stage data |
| `inputs_corpus` | for creative at volume | ask | winning ads, 50-100 reviews, ad comments, brand voice |
| `constraints` | optional | none | regulated category, no competitor names, region rules |

Read `.agents/product-marketing.md` first.

## Output

- **plan**: affordability verdict per plan/segment, channel choice with reasons, budget by stage, account structure with naming, keyword/audience lists with negatives and exclusions, bidding plan, tracking checklist, kill/scale rules, weekly scorecard ([templates/campaign-plan.md](templates/campaign-plan.md)).
- **creative**: concepts as a hook matrix and per-concept briefs (segment, motivation with source, format, hook, copy, visual, grounding), copy checked against platform limits ([templates/creative-brief.md](templates/creative-brief.md)); optional HTML review page.
- **rsa**: ad group structure, ≥ 8 negatives, ≥ 4 sitelinks, ≥ 4 callouts, then RSAs with 15 headlines ≤ 30 chars and 4 descriptions ≤ 90 chars, counts printed ([templates/rsa-output.md](templates/rsa-output.md)).
- **audit / optimize**: findings scored pass/fail/unknown/not applicable with health and evidence coverage reported separately, each fail as a draft change (current → proposed → expected effect → rollback) ([templates/audit-report.md](templates/audit-report.md)).
- **scale**: step plan, preconditions, rollback trigger, creative supply needed.

## Supporting files

- [strategy.md](strategy.md): affordability (payback, breakeven), platform selection, demand lifecycle and budget by stage, leading vs. lagging metrics, structure and naming, brand vs. non-brand, retargeting, landing-page match, scaling discipline, reporting. Read for any plan.
- [platforms.md](platforms.md): Google Search, PMax and Shopping; Meta decision system; LinkedIn; ABM; TikTok, X and Bing notes; audiences, sizes and exclusions. Read before touching a specific platform.
- [creative.md](creative.md): grounded inputs, angles, hook system and diagnostic funnel, static templates with funnel roles, video formats and vertical spec, dramatized and AI-generated formats, copy formulas, AI tells, platform limits, RSA rules, creative roadmap and retro. Read for any creative work.
- [tracking-and-audits.md](tracking-and-audits.md): conversion tracking and server-side events, offline conversion loop, lead quality scoring, audit scoring rules, reading account data without false conclusions, itemized audit checklists, live-account safety. Read before auditing or recommending changes.
- [examples/rsa-agency.md](examples/rsa-agency.md): a complete RSA output for one ad group, linted.
- [scripts/ads_tool.py](scripts/ads_tool.py): `economics`, `limits` (copy vs. platform limits and tells), `zero` (what zero conversions proves), `meta` (ad ceiling, test throughput, verdicts), `scale` (budget steps), `review` (HTML review page from a [concepts.json](templates/concepts.json) file).

## Steps

1. **Affordability first.** Compute breakeven CPL (ACV × lead→close) and CPC (CPL × page conversion), or breakeven ROAS (1 ÷ gross margin), and payback per plan (CAC ÷ gross-margin ARPU, retention-adjusted) with `ads_tool.py economics`. If payback for a plan exceeds 12 months → don't buy that plan's customers with paid; route them to organic/product-led. If tracking can't see conversions → stop and fix tracking (step 4) before spending.
2. **Pick channels by demand state.** If people already search for the solution → Google Search (and Bing) first, climbing the intent ladder brand → high-intent → competitor → problem-aware → broad. If demand must be created or the product is visual → Meta/TikTok. If job title and company decide fit and ACV supports $8-20+ CPCs → LinkedIn. Before committing to a new channel, run a ~$100 test to learn real CPC/CPM for your targeting.
3. **Budget by stage.** B2B: build bottom-up (expand → revive → accelerate/activate → capture → create). Keep ~70% on proven campaigns and ~30% on tests early. Give every campaign enough budget to reach the platform's learning bar; if it can't, consolidate.
4. **Tracking before launch** (tracking-and-audits.md): browser tag + server-side events with shared event IDs, conversions firing on confirmed outcomes, values set, consent handled, test conversion observed. B2B: plan offline conversion import from the CRM (qualified lead, opportunity, closed-won) because the bidder optimizes toward whatever you call a conversion.
5. **Structure** (strategy.md, platforms.md): separate brand, non-brand, competitor and remarketing with independent budgets; themed ad groups (5-15 keywords, one promise); on Meta, a scaling campaign (~80%) and a protected testing campaign (~20%) over the same broad audience; naming `[PLATFORM]_[Objective]_[Audience]_[Offer]_[Date]`.
6. **Targeting.** Search: phrase + exact on high-intent terms, starter negatives, broad only after 30+ conversions/month with smart bidding and a tight negative list. Social: audience knowledge goes mostly into creative, broad targeting plus exclusions (customers, recent converters, employees). LinkedIn: function + seniority, 50-300K cold audiences, Audience Expansion and Audience Network off.
7. **Creative** (creative.md): ground in winning ads, reviews and ad comments; define 3-5 angles; build a hook matrix across segment × motivation × format; produce low-fidelity first and save high production for validated angles; check every line with `ads_tool.py limits`. If the inputs corpus is empty → ask for it rather than inventing claims.
8. **Landing match.** The page headline repeats the winning ad's promise; one job and one CTA; fast; proof above the fold. If CTR is high but conversion low → fix the page or offer (conversion-optimization), not the ad.
9. **Operate on rules, not mood.** Judge only after the data gate (e.g., spend ≥ 3× target cost per qualified lead, or enough clicks that zero conversions is meaningful, `ads_tool.py zero`). Respect learning phases; never edit a performing ad in place; never pause a producer without a replacement staged. Weekly: search-terms pass (waste, winners, drift), fatigue check, lead quality from the CRM.
10. **Scale** only when cost per qualified result ≤ target for 2+ weeks, frequency is healthy and replacements are staged: +20% every ~5 days (`ads_tool.py scale`); judge headroom on net cash and blended efficiency, optimize on non-brand. Out of audience → horizontal moves (new audiences, geographies, partnership/creator ads), not more budget on the same people.
11. **Audits and live changes** (tracking-and-audits.md): score only what you verified; report health and evidence coverage separately; no invented negatives without a search-terms report; never sum conversions across platforms with different windows; draft every change with a rollback and apply only after approval.

## Checkpoints

- After step 1: affordability verdict and target CPL/CPA/ROAS agreed.
- Before launch: tracking test conversion observed; negatives and exclusions in place; copy passes `limits`.
- Day 7 and day 14: delivery and quality reads against the rules; no changes inside learning without a verified break.
- Monthly: target cost per qualified lead re-set, creative retro, CRM reconciliation (the CRM wins disagreements).

## Worked example

**Context**: expense tool for agencies; ACV $1,550 (Growth plan $129/month), lead→close 10% from trial-qualified demos, landing page converts 6%; budget $12k/month; US/UK.
- `economics --acv 1550 --close 0.1 --lp-cvr 0.06 --margin-target 0.3`: breakeven CPL $155, target $108; breakeven CPC $9.30. With `--cac 900 --arpu 39 129 --plan Starter Growth --gross-margin 0.8`: Starter pays back in 28.8 months (no paid for Starter), Growth in 8.7 months (fund).
- Channels: Google Search (category terms exist: "expense software for agencies") at $8k; LinkedIn function + seniority to agency finance/ops at $3k; $1k Meta test of founder-message statics.
- Search: brand / non-brand (3 ad groups: agency expense software, client rebilling, receipt automation) / competitor; phrase + exact; negatives (free, template, jobs, personal, reimbursement form, brand name in non-brand). RSA linted (examples/rsa-agency.md).
- Week 3: one non-brand term has 41 clicks and 0 leads. `zero --clicks 41 --cpc 11 --target-cpa 108`: break-even CVR is 10.2%, and 41 clicks with zero conversions already rules out CVR ≥ 7.0% (about 28 clicks were enough). So the term is below break-even: check its intent in the search-terms report, then add it as a negative. A sibling term with 9 clicks stays live, because 9 clicks proves nothing.
- Week 6: offline import of "demo qualified" live; Search cost per qualified demo $96. LinkedIn $240, so cut to $1.5k and moved to thought-leader ads. Meta founder static at $88 per qualified lead with 62% qualified rate graduated.
- Scale: `scale --start 270 --target 400` gives Search $270 → $324 → $389 → $400/day over ~15 days; rollback if cost per qualified demo goes above 1.5× target ($162).

## Pitfalls

- Spending before tracking works; optimizing to raw form-fills (cheap junk leads).
- Judging on blended LTV:CAC, or on brand ROAS, instead of per-plan payback and non-brand efficiency.
- Too many campaigns and ads for the budget, so nothing exits learning.
- Interest-stacking narrow audiences to rescue generic creative.
- Broad match without conversion volume, smart bidding and negatives; negatives invented without a search-terms report.
- Killing on small samples or inside learning; editing live winners (resets learning); pausing without a replacement.
- One ad per ad set; creative never refreshed; headlines that only work in one combination.
- Invented stats, testimonials or "found footage" framing; unlicensed press logos; regulated claims without review.

## Related skills

analytics-and-experiments (tracking plans, attribution, holdouts), conversion-optimization (post-click conversion), marketing-copy (landing pages, copy quality), customer-research (voice of customer, competitor ads), pricing-and-offers (offers that make ads work), launch-plan (paid as a launch channel), sales-outreach (ABM follow-up, lead routing), content-strategy (organic posts worth promoting).

## Done when

- [ ] Affordability verdict per plan/segment with breakeven and target numbers.
- [ ] Tracking verified with a real test conversion; offline conversion plan for B2B.
- [ ] Structure, targeting, negatives/exclusions and bidding documented with reasons.
- [ ] Creative grounded in sources, varied across angles and formats, and passes platform limits.
- [ ] Kill, graduation, fatigue and scaling rules written with numbers.
- [ ] Audit findings separate health from coverage; every change drafted with a rollback and awaiting approval.
