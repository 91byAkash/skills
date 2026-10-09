# Paid strategy reference

Contents: 1 affordability · 2 platform selection · 3 demand lifecycle and budget by stage · 4 leading vs. lagging metrics · 5 structure and naming · 6 budget allocation · 7 brand vs. non-brand · 8 retargeting · 9 landing-page match · 10 scaling discipline · 11 reporting and attribution · 12 measurement maturity.

## 1. Affordability

**Why not LTV:CAC alone.** A blended ratio hides four things: (1) it assumes every customer eventually churns, which undervalues the compounding core; (2) it smooths churn evenly, though churn is front-loaded in the first months; (3) it averages cheap and expensive plans into a number that describes neither; (4) it ignores revenue delay from trials, free plans and long cycles. A "healthy 3:1" can sit on a channel that runs you out of cash.

**Payback period** = CAC ÷ monthly gross-margin ARPU, per plan or cohort. Aim for 3-12 months: under 3 usually means under-investing, over 12 means financing customers longer than most balance sheets can. Retention-adjusted (crude): CAC ÷ (ARPU × margin × annual retention). Same $300 CAC: $9 plan → 33 months (don't buy with paid), $99 → 3 months (scale), $999 → under 1 month (pour budget in).

**Breakeven CPL** = average deal value × lead-to-close rate ($3,000 × 10% = $300). **Breakeven CPC** = CPL × landing-page conversion ($300 × 5% = $15). Set targets below breakeven by your required margin. **Breakeven ROAS** (e-commerce) = 1 ÷ gross margin for first-order economics, lower if repeat purchases are reliable.

Gate: turn a channel on only where payback ≤ 12 months; re-run monthly as CAC rises with scale. Breakeven tells you the most you can pay; payback tells you how long cash is tied up. You need both.

## 2. Platform selection

| Platform | Best for | Use when |
|---|---|---|
| Google Search / Bing | Harvesting existing demand | People search for the solution or problem |
| Google Shopping / PMax | E-commerce catalogs | Feed quality is good; Search basics already work |
| Meta (Facebook/Instagram) | Creating demand, visual products, broad B2C and SMB B2B | Strong creative supply; conversion volume reachable |
| LinkedIn | B2B precision by title, function, company | ACV supports high CPCs; small, defined buyer set |
| TikTok | Younger audiences, native video | You can make native-feeling video at volume |
| X | Tech and timely audiences | Audience is active there; cheaper reach, less precision |
| Review-site listings | High-intent software buyers | Category pages exist on major review directories |
| Sponsorships (newsletters, podcasts, creators) | Borrowed trust in a niche | A publisher's audience overlaps your ICP |
| Programmatic (display, CTV, audio, native) | Reach and retargeting at scale | Measurement is in place; budget is large |

Evaluate any channel on four axes: can it target your ICP, media cost, reach at that targeting, and industry policy restrictions. Search harvests demand; it can't create it. If category search volume is near zero, put budget upstream on social.

Out-of-home only pays when it is designed to be photographed and amplified on social; on its own it has no measurable loop.

## 3. Demand lifecycle and budget by stage (B2B)

| Stage | Goal | Typical offers | KPIs | Budget / time to ROI |
|---|---|---|---|---|
| Create | Affinity with unaware/problem-aware buyers | Education, point of view | Cost per engaged view, blended cost per opportunity | High / 90+ days |
| Capture | Convert in-market buyers | Demo, trial | Pipeline per dollar, cost per opportunity | Moderate / < 45 days |
| Accelerate (sales-led) / Activate (product-led) | Speed open deals / convert free users | Case studies, webinars, events | Velocity, paid conversions | Low / tracks cycle |
| Revive | Restart closed-lost | Incentivized demo, guided trial | Re-opened opportunities | Low / < 45 days |
| Expand | Grow accounts | New features, referral | Expansion revenue | Low / < 60 days |

Build bottom-up for fastest return (expand → revive → accelerate → capture → create). Product-led motions lean create + capture; sales-led with small markets lean create + accelerate. Fund stages whose pipeline share exceeds budget share and whose audience isn't saturated.

## 4. Leading vs. lagging metrics

You can't optimize daily on revenue that closes in six months. Leading (moves within a month; optimize on these): CTR, engagement, CPL, cost per qualified lead, accounts reached. Lagging (monthly/quarterly truth): pipeline per dollar, influenced revenue, time to close, expansion. A proxy is only worth optimizing if it predicts the lagging metric; if CPL falls while pipeline doesn't move, fix the proxy, not the ads.

| Objective | Primary metrics |
|---|---|
| Awareness | CPM, reach, view rate, rolling reach |
| Consideration | CTR, CPC, landing engagement |
| Conversion | CPA/cost per qualified lead, ROAS, conversion rate |

## 5. Structure and naming

Account → campaigns (objective × audience/product) → ad sets/groups (targeting or theme) → 3+ ads each. Naming: `[PLATFORM]_[Objective]_[Audience]_[Offer]_[Date]`, e.g. `GOOG_Search_NonBrand-Rebilling_Trial_2026Q4`, `META_Conv_Broad-US_FounderStatic_Oct26`, `LI_LeadGen_FinanceOps-Agencies_Guide_Oct26`. Fewer, well-fed campaigns beat elaborate structures at low volume.

## 6. Budget allocation

Testing phase (first 2-4 weeks): ~70% proven/safe, ~30% new audiences and creative. Scaling phase: consolidate into winners; raise budgets ~20% at a time with 3-5 days between steps (bigger jumps reset learning). Seasonality: Q1 auction prices are usually the lowest of the year; Q4 consumer auctions can run far higher, so B2B advertisers often bank budget for January.

## 7. Brand vs. non-brand

Split before evaluating anything. Branded queries harvest demand you already own; a cheap brand CPA reflects awareness, not campaign skill. Report blended efficiency as the business view; set targets, bids and budgets on non-brand. Never present a low brand CPA as a win unless a brand holdout measured incrementality.

## 8. Retargeting

| Stage | Audience | Message | Window | Frequency |
|---|---|---|---|---|
| Hot | Cart/checkout abandoners, trial users | Objection handling, help, honest urgency | 1-7 days | Higher is fine |
| Warm | Pricing/feature/demo page visitors | Case studies, demos, comparisons | 7-30 days | 3-5/week |
| Cold | Any visit, content readers, video viewers | Education, proof | 30-90 days | 1-2/week |

Exclusions: customers (unless upsell), recent converters (7-14 days), bounced visitors (< 10 s), careers/support visitors, employees.

**Retarget with a different offer**, not the same one louder: the most common reason someone didn't buy is that the offer didn't fit. Pricing viewer who didn't sign up → free audit or assessment; lead-magnet downloader who didn't book → a related second resource; product A viewer → product B.

Run four retargeting ad types together: (1) an objection-handling ad built from real reasons non-buyers gave (call or survey them); (2) a proof carousel of testimonials and results; (3) other strong offers in one campaign; (4) a value-first audit or assessment that leaves them with something useful either way.

## 9. Landing-page match

Treat ad headlines as a high-volume headline test: run 20-40 headline variations, pick the winner by CTR and downstream conversion, and mirror its exact promise in the page H1, subhead and opening copy. Pages that pivot to a different angle lose the visitor regardless of quality. Keep 3+ tests running across ad, page, offer and post-conversion at any time. Page rules: message match with ad and query, one job and one CTA, fast load (< 3 s), mobile-ready, proof above the fold. Form length is an intent gate: short forms buy volume, longer qualifying forms buy quality; match it to the conversion you feed back.

## 10. Scaling discipline

- Judge headroom on net cash and blended business efficiency, optimize on non-brand. Falling ROAS with much higher spend can mean far more profit; refusing to scale a 10× ROAS on $5k/month is a common, expensive mistake.
- Find the ceiling: maximum CAC that stays profitable (or inside payback) is the line; scale until you approach it.
- Scaling quadrant by constraint:

| | Low effort | High effort |
|---|---|---|
| Budget available | Audiences: bigger, more segments, more frequency | New geographies (localization) |
| Budget capped | New creative, angles, formats | Objective and bid changes that buy cheaper |

- Hitting the wall (account frequency > ~3.5, rolling reach flat): new seed audiences, broader lookalikes, broad targeting, creator/partnership ads, cross-channel UTM audiences.
- Founders: block a few hours a month to review the raw numbers yourself; and call non-converting leads to learn the blocker. Their words become objection ads.

## 11. Reporting and attribution

Weekly: spend vs. pacing; cost per result vs. target (brand and non-brand separately); top/bottom ads; audience breakdown; frequency; landing conversion; lead quality from the CRM. Platform attribution overlaps and inflates; use consistent UTMs, compare against analytics and the CRM, and track blended CAC. Never add conversions across platforms with different windows or definitions; report side by side.

## 12. Measurement maturity

Score 1-3 each: blended pipeline dashboard; per-channel dashboard; conversion tracking (1 none, 2 pixel only, 3 offline conversions flowing); web analytics; agreed attribution process. Under ~6 of 15: fix visibility before adding budget, lowest score first.
