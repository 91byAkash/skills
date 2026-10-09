# Platform playbooks

All thresholds are practitioner starting points; recalibrate on your account's first 30 days.

Contents: 1 Google Search · 2 PMax, Shopping and Demand Gen · 3 Meta decision system · 4 Meta lead forms, automation and partnership ads · 5 LinkedIn · 6 ABM · 7 TikTok, X, Bing · 8 audiences, sizes and exclusions.

## 1. Google Search

**Intent ladder** (open each rung only when the one below converts to pipeline): brand (always on, cheapest) → high-intent non-brand (the profit center) → competitor (higher CPC, lower CVR, needs comparison pages) → problem-aware (longer payback) → broad/demand gen (spare budget only).

**Brand**: bid by default (competitors will). If you're the only bidder and organic owns the page, test pausing and watch total brand conversions (paid + organic); if total holds, you were paying for clicks you'd get anyway. Cap brand budget.

**Structure**: brand, non-brand high-intent, competitor and remarketing, each with its own budget (shared budgets let brand starve the rest). Themed ad groups of 5-15 keywords sharing one intent and one promise; 2-3 RSAs per group (max 3). A campaign that can't reach ~15-30 conversions/month can't feed smart bidding: merge it. New campaign defaults: Search Partners and Display off until proven; location "presence" (people in the area), not "presence or interest"; language targets the user's interface language. Route each query to one home with negatives; never run the same keyword and match type in two groups.

**Keywords and match types**: source from how buyers describe the problem (sales calls, search-terms report, competitor ads). 50 clear-intent searches beat 5,000 mixed. Start phrase + exact; add broad only after 30+ conversions/month, smart bidding live and a tight negative list.

**Negatives at build time**: universal junk (free, cheap, jobs, salary, hiring, career, intern, student, course, tutorial, training, certification, pdf, template, wiki, login outside brand); research intent (what is, how to, examples, meaning, definition); category collisions (selling sales engagement → "employee engagement"); your brand in non-brand campaigns. Match mechanics: negative broad needs all its words present (negative broad "free trial" doesn't block "free"); negative phrase blocks the phrase in order; negative exact blocks only that query. Don't over-negative ambiguous terms; get data first.

**Weekly search-terms ritual** per campaign: waste (spend, 3+ clicks, zero conversions, irrelevant → negative), winners (converting terms not yet keywords → add exact/phrase), drift (adjacent wrong meanings → tighten or negative). Remember the report is a sample (tracking-and-audits.md §5).

**Bidding by volume**:

Let conversion volume pick the bid strategy: with fewer than about 15 conversions a month, stay on manual CPC or maximize conversions without a target; from about 15 to 30, maximize conversions; once volume is steady above 30, set a target CPA at or a little above the last 30 days' actual; switch to target ROAS only when real revenue values are being reported back.

Move targets ±10-15% and wait 1-2 weeks. Aggressive targets choke delivery. Daily spend can reach 2× daily budget (balanced monthly). A budget-capped campaign that converts often gets cheaper when you raise budget.

**Quality Score** (expected CTR, ad relevance, landing experience): fix the weak component before raising bids.

**Offline conversions**: import qualified lead / opportunity / closed-won with values via click IDs. B2B clicks close in 60-180 days; in-platform counts never tell the full truth.

**Weekly scorecard (eight numbers)**: spend · leads · CPL · lead→qualified rate (CRM) · qualified leads · cost per qualified · search impression share · top wasted terms. Lost impression share (budget) vs. (rank) tells you whether money or ad rank caps you.

Directional B2B SaaS ranges: brand CTR 8-20%, CVR 15-40%; high-intent non-brand CTR 2-6%, CVR 3-10%, CPC $8-40+, CPL $80-400+.

## 2. PMax, Shopping and Demand Gen

Value order: brand Search > high-intent Search > remarketing > PMax > broad demand gen. Never run PMax first, on weak tracking or tiny budgets. Guardrails: account-level brand exclusions (else it cannibalizes brand and claims credit), first-party audience signals, negatives from day one, offline conversions before scaling, compare lead-to-pipeline rate against Search.

Controls available as of 2026 (check the Help Center before relying on them): campaign-level negative keywords (up to 10,000 per campaign, with match types), brand exclusions, search themes (up to 50 per asset group), the search terms report and channel performance reporting (Search, Shopping, YouTube, Display, Discover, Gmail, Maps split). Use the channel and search-terms reports as evidence before adding negatives.

E-commerce: single source of truth for purchases (no double counting); customer list used for signals and exclusions; feed titles front-load the high-intent keyword in the first ~70 characters; distinctive images; accurate shipping; promotions set up; ratings syncing; disapprovals fixed; check that the whole catalog gets impressions; each segment needs ~30-50 conversions/month; brand split out; brand keywords exact/phrase only; generic queries leaking into brand moved out; enough PMax spend landing in Shopping; Demand Gen read by format and demographics; cold traffic met with comparison pages, advertorials or quizzes, not only product pages; at least one top-of-funnel campaign with a conversion goal.

## 3. Meta decision system

**Anchor: target cost per qualified lead (TCPL)**, where qualified = meets your ICP bar. Set from deal math (target cost per demo × qualified-lead→demo rate), from history (trailing 30-day qualified CPL × 0.8), or for new accounts from CAC × qualified-lead→customer rate; review monthly.

**Ad-count ceiling** = daily budget × 14 ÷ (2 × TCPL). $1,000/day at $500 TCPL → 14; run 6-10. At the ceiling, kill before you launch.

**Two campaigns over the same broad audience**: scaling (~80%, graduated ads only) and testing (~20%, protected budget). New concepts launch as statics first unless inherently video. When the destination is the unknown, run one campaign per persona with one ad set per destination (product page, listicle/advertorial, quiz, demo page) holding creative constant.

**Day-7 delivery check**: fair share = (daily budget ÷ active ads) × 7 × 0.5; below → kill (the system deprioritized it); zero spend → kill. Ongoing: lifetime spend ≥ 1× TCPL and < ~$10/day over 7 days → kill. Iterate delivery-killed ads on hook/visual/format only.

**Weekly quality read (rolling 14 days), stop at first action**:
1. Spend < 3× TCPL → wait. (At true cost = target, 3× spend should yield ~3 qualified leads; zero then has ~5% probability. 2× gives too many false negatives; 5× overpays.)
2. Zero leads at ≥ 3× → swap and abandon the concept.
3. Leads but zero qualified → swap angle, keep format. Qualified rate < 40% → swap and add ICP-filtering language (at 40%, true cost per qualified lead is 2.5× the platform CPL). 40-60% → monitor a week. ≥ 60% → continue.
4. Cost per qualified ≤ TCPL → candidate winner; 1-1.5× → monitor; > 1.5× → swap.

**Graduate** when all: ≥ 5 qualified leads, qualified rate ≥ 60%, cost ≤ TCPL, ≥ 14 days running, ≥ 1 qualified lead in the last 7 days.

**Fatigue bands** (frequency safe / warning / critical): cold 1.0-2.5 / 2.5-4.0 / > 4; retargeting 2-4 / 4-6 / > 6; ABM 2-5 / 5-8 / > 8. Other signals: CTR −20% over 7 days, CPM +30% over 2 weeks (moves first), below-average relevance, CPA up with stable targeting. Scaling ads use a stricter bar: frequency 3.0-3.5 or cost +20% → start 2 iterations now; > 3.5, +40% or > 1.5× TCPL for 2 weeks → swap. B2B lifespans: statics 14-28 days, short video/carousels 21-35, UGC/testimonials 28-42. Retire the concept when CTR is down 30%+ from peak or frequency is critical. Never edit a performing ad (resets learning); add new ads beside it.

**Swap rules**: never pause without a replacement; keep 2-3 iterations staged. Change by cause: delivery kill → hook/visual; quality kill → angle and ICP language; cost kill → offer and audience; fatigue → fresh execution of the same concept.

**Creative math**: test throughput ≈ monthly budget × 0.2 ÷ (3 × TCPL); win rates ~25% for iterations, ~10% for new concepts, ~1 in 6 blended; plan ~6 tests per winner wanted. Proven-ad inventory ≈ monthly budget ÷ ~$5k. You can't scale budget ahead of creative supply. Iteration priority: hook → visual → format → body/CTA. `ads_tool.py meta` computes these.

**Scaling protocol**: preconditions (inventory met, account frequency < 3, cost ≤ TCPL two weeks, 3+ replacements staged); +20% every 5 days; rollback at > 1.5× TCPL (cut 20-30%, stabilize 2 weeks, resume +10%/week).

**Weekly cadence**: Monday decisions (quality reads, fatigue), Wednesday launches (new tests, day-7 checks), Friday scale steps; monthly creative audit and TCPL review.

**Directional B2B SaaS ranges**: CTR 1.0-1.5% (flag < 0.8%), CPM $10-20 (flag > $25), form CPL $20-50 (flag > $75), landing CVR 8-12%.

## 4. Meta lead forms, automation and partnership ads

**Lead forms**: auto-filled forms create leads who don't remember converting. Add deliberate friction: the higher-intent form type with a review step, require work email (can't auto-fill), 1-3 multiple-choice qualifiers ordered easy → hard, a confirmation that says what happens next. Landing page converting ≥ 5% → use it; < ~2% → form; demos/trials → page; content/webinars → form.

**Delivery since 2025**: Meta's system matches ads to people largely by creative and persona, so interest stacking tends to hurt. Practical consequences: target broadly (often just the country), let distinct creatives speak to distinct segments, feed volume (statics are cheap and the system delivers them readily), longer primary text gives more context. Test it: duplicate an interest-targeted winner with broad targeting for 7 days and compare cost per result.

**Identity keyword variants**: duplicate a winner with a niche word in the headline ("dental leads", "agency invoices"); it is both a hook for that viewer and a matching signal. Write variants per segment that keep the original voice and structure. Dead variants you strongly believe in can be relaunched in their own ad set; some revive.

**Automated campaign types**: move a campaign to full automation only after a proven offer, a validated audience and ~50 conversions/week on the optimization event (budget ≈ target CPA × 50 ÷ 7 per day). Below that, optimize a higher-volume upstream event and retarget. Automated audiences conflict with strict ABM.

**Partnership (creator) ads** add net-new reach by inheriting a creator's audience. Pre-test their organic content and promote only pieces already earning saves, shares and watch-through; pick for audience overlap with your ICP, not follower count; contract handle access for ads plus usage rights for a defined window (typically 3-6 months) and paid-amplification rights; pay a flat content fee; also commission a few low-fi statics per creator for mid-funnel. Track rolling month-over-month reach: falling reach is the early warning to add creator/partnership ads before frequency forces it.

## 5. LinkedIn

**Bidding**: week 1 automated to learn CPCs; week 2+ manual CPC ~20% below the automated average. Exceptions: small retargeting/ABM pools stay automated; reset to automated for a week after an objective change. Ad day resets at UTC midnight; daypart to weekday working hours in the audience's zone if budget is tight.

**Audience sizing**: cold 50-300K members (minimum ~15K); if it won't spend, the audience is too small, not the bid too low. Total addressable < ~30K → one campaign with all funnel layers. Retargeting 1-5K per segment workable; < ~300 won't serve.

**Function + seniority vs. titles**: function + seniority usually triples reach at lower cost; run a weekly negative-title exclusion pass for the first ~2 months. Titles and seniority can't be combined. Business Development function contains many founders and executives; filter by seniority instead of excluding it. Audience Expansion off; Audience Network off for lead gen.

**Splits**: intent > persona > region/company size > seniority. Keep the US separate from cheaper regions; DACH needs localized ads; UK/Canada/Australia group fine. Segment by employee count (two bands to start); unsegmented campaigns over-serve the extremes.

**Penetration-based scaling**: 30-day penetration < 25% → room to add budget; 25-35% → hold; 35%+ → scale horizontally. Doubling budget grows penetration ~50-70%. Spend up but reach flat → outbid or weak ads; fix creative before adding money.

**Directional benchmarks** (judge clicks to landing page, not "CTR" that includes social actions): landing CTR cold 0.30-0.55%, mid 0.55-0.80%, retargeting 0.80-1.30%; CPM $33-65; CPC $8-22+; lead-form CPL $50-200; website form CPL $200-500; form fill rate > 8%; cost per qualified lead under ~$500 for enterprise, $50-150 for SMB. Return data lags 3-6 months.

**Thought-leader ads** (promoted from a person's profile) often get several times the CTR of company-page ads at lower CPC; creator/non-employee posts can beat employee posts. Promote posts that already earned ~2-3% organic CTR; let a post run organically ~3 days, then add the CTA and promote. Document, conversation and thought-leader formats face less auction competition than single-image ads.

**Build order** (fund each before the next): product value (direct response) → remarketing → content that can't be consumed in-feed → social proof → thought leadership.

**Formats**: document ads 1080×1350, 5-7 slides (hook → pain → shift → solution → differentiators → CTA), each slide adding something new. Conversation ads: 2-4 word subject, 3-5 short lines, specific numbers, soft CTA routed to a lead form; open rates 35-50%+. CTV: awareness only, auto-bid, worth it only above ~$15k/month total spend.

**Retargeting audiences only collect from creation**: create site-visitor, video-viewer, ad-engager, form-opener and page-visitor audiences before launch.

**Audit shortlist**: expansion/network left on; audiences too small; < 4 ads per campaign; < ~10 results/week per campaign (consolidate); creative older than 3 months; no retargeting audiences; lead quality never reconciled; expensive and cheap geos mixed.

## 6. ABM

**Go/no-go**: run paid ABM when the account list is ≥ ~1,000 companies (or you accept 1:1/1:few economics), deals ~$25k+, cycles 60+ days, sales and marketing agree on the list. Skip below ~500 accounts without enrichment, under ~$3k/month, or with short transactional cycles.

**LinkedIn**: 1:1 (named company, bespoke creative), 1:few (10-20 accounts sharing a pain), 1:many (uploaded list). Needs 300 matched members to serve; company lists beat contact lists for most teams. Split mixed lists into homogeneous bands or the largest enterprises absorb delivery. Use the per-company engagement report to find under-served priority accounts. Cap ~3 impressions/person/week by excluding accounts that crossed ~500 impressions in 7 days (tune 300-750). Account-named creative can lift CTR sharply; check local privacy law before personalizing with company names (Germany is a known exception).

**Account pages**: send 1:1/1:few clicks to a page for that account or segment (personalization layer, CMS template filled from a list, or a dynamic route from the CRM). Keep them noindex, out of the sitemap, built only from public or first-party facts, human-reviewed before publishing.

**Meta**: no company targeting; raw work-email uploads match poorly (often < 5%); identity-resolution enrichment can raise match rates to roughly 40-85%. Minimums: ~1,000 companies for list audiences, ~100 for retargeting slices, 500+ seeds for lookalikes. Meta provides cheap committee coverage; LinkedIn provides precision. Default split ~60% LinkedIn / 30% Meta / 10% other, LinkedIn first.

**Acceleration**: upload open opportunities by stage weekly; awareness/reach objective (don't ask booked accounts to book a demo); stage-matched case studies and objection handlers; budget scales with deal value.

**Cross-channel UTM remarketing**: tag all paid traffic consistently; on Meta, build a site audience where URL contains `utm_source=linkedin` and retarget it at Meta prices. The reverse (search clickers → LinkedIn) needs substantial search volume.

**Sales orchestration**: pipe engagement spikes to the CRM and reach out within ~48 hours; post new leads to a shared channel with a quick quality reaction; review the list monthly with sales. Expect 7-10 touches before a conversation.

**Measure accounts, not clicks**: list penetration ~40-60%; cost per engaged account ~$100-300; account→opportunity 10-20%; influenced pipeline 3-5× spend; hold out ~20% of the list for 21+ days to measure incrementality.

## 7. TikTok, X, Bing

- **TikTok**: broad targeting, native vertical video, sound-off captions, trends and creator formats; promote proven organic posts (boosted-post format keeps the creator's handle). Interest targeting is coarse; creative dominates.
- **X**: follower-lookalikes of relevant accounts and keyword/conversation targeting work; lower CPMs, less precision; conversational tone, 0-2 hashtags.
- **Bing**: import Google Search campaigns, then fix bids, negatives and audiences separately; often cheaper clicks with an older, desktop-heavy and B2B-skewed audience; LinkedIn profile targeting is available on its network.

## 8. Audiences, sizes and exclusions

Where audience knowledge goes (directional): Meta ~80% into creative / 20% into targeting; PMax/Demand Gen ~70/30; TikTok ~70/30; X ~50/50; Google Search and LinkedIn ~40/60 (keywords and firmographics still dominate).

Putting knowledge into creative: demographics and niche identity → headline keywords ("for dentists"); pains and fears in the customer's words → headline and first line; desired outcomes → transformation copy and CTA; objections → retargeting objection ads; vocabulary → overall voice; best customers by LTV → lookalike seeds.

Building blocks: customer lists (match 30-70% on Meta), site visitors (up to 180 days on Meta), engagement audiences (video 25/50/75/95%, form openers), lookalikes (seed on high-LTV customers, 100 minimum, 1,000+ ideal; 1% closest, 1-3% balance, 3-5% scale, 5-10% awareness), Google custom-intent from converting keywords, in-market and affinity audiences (observation mode first, then targeting for winners), remarketing lists for search (bid up returning searchers). LinkedIn combinations: enterprise = 1000+ employees + VP/CXO + industry; SMB = 11-200 + manager/director + function; developer tools = skills + function.

Sizes (minimum / ideal): Google Display 100K / 500K-5M; Meta 100K / 500K-10M; LinkedIn 50K / 100-500K; X 50K / 100K-1M; TikTok 100K / 1M+; Search keywords 1,000+ searches/month combined.

Always exclude: existing customers (unless upsell), recent converters (7-14 days), employees, bounced visitors, careers/support visitors, identifiable competitors. Avoid overlapping ad sets competing for the same people.

Policy: declare special ad categories (housing, credit, employment, social/political issues) where required; they restrict targeting options.
