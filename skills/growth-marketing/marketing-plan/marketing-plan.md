# Marketing plan method

Read this when the request is bigger than one launch: a 90-day or 12-month marketing plan, a go-to-market plan, a growth plan for a client or company, or sequencing an existing audit into action. The deliverable skeleton is [templates/marketing-plan.md](templates/marketing-plan.md); market sizing lives in [market-sizing.md](market-sizing.md); idea selection in [ideas.md](ideas.md).

## Contents
1. Principles the plan must reflect
2. Market-quality gate
3. Intake and evidence
4. Current-state scoring (17 areas)
5. AARRR structure and the binding constraint
6. Variations by business model
7. Budget: two defensible methods
8. Funding-stage tiers
9. Growth shape, S-curves and 70/20/10
10. Team and agency model
11. Measurement and review cadence
12. Drafting order, verification and quality bar

---

## 1. Principles the plan must reflect

- **Portfolio, not calendar.** Favour assets that keep paying (search content, a newsletter, a community, a referral loop, integrations) over one-off spikes. Diversify so no channel carries more than about half of new customers.
- **Many small bets.** No single move fixes growth. Be suspicious of any line item sold as "the" answer.
- **One asset, many returns.** Prefer moves whose output serves several channels: a research report that ranks, earns links, feeds the newsletter, becomes a talk and a sales asset.
- **Attention is earned.** Marketing outcomes are probabilistic; the same input does not guarantee the same output. Run a portfolio of bets, double down on what works, and kill what does not on a schedule.
- **Every move has a mechanism and a leading indicator.** "Post more" is not a move. If a move cannot be tied to a measurable signal, write it as an experiment with a kill criterion.

## 2. Market-quality gate

Before planning how to market, rate the core problem on two axes: size (how costly when it occurs) and frequency (how often the buyer feels it).

| | Rare | Frequent |
|---|---|---|
| **Large problem** | Winnable but costly to stay top of mind; long cycles, nurture and retargeting heavy | Best position: marketing compounds |
| **Small problem** | Weakest; hard to justify attention or spend | Habit-forming but price-sensitive; retention carries the plan |

Name the quadrant in the positioning page. A weak quadrant constrains realistic CAC and channel mix; say so plainly rather than planning as if it were strong. If the question "is this market big enough?" comes up, size it with [market-sizing.md](market-sizing.md).

## 3. Intake and evidence

Read existing material first (positioning doc, decks, analytics snapshots, past audits, voice guide, `.agents/product-marketing.md`), then pull live numbers where tools are connected (web analytics, billing, email platform, search console, CRM). Ask only for what is still missing. Ten intake topics:

1. **Company**: what it sells, to whom, since when, business model.
2. **ICP**: firmographics or demographics, stated vs. real problem, what they actually buy.
3. **Funnel today**: visitors, signups, activation, paid conversion, churn, with dates.
4. **Funding**: stage, runway, next round and timing, what it would unlock.
5. **Team**: every person touching marketing and what they own; gaps.
6. **Budget**: monthly spend split into paid, tools, content, retainers, headcount.
7. **Channels**: what is live, working, not working, never tried.
8. **Already done**: launches, press, content, partnerships the team is proud of (the plan must acknowledge these).
9. **In flight and stuck**: drafted but unshipped items and what blocks each.
10. **Posture**: the one thing to fix this quarter and the one thing to ignore, in the founder's words.

Mark every number you could not confirm as `[TBD: confirm]` and carry it to open decisions. Never invent a metric. Unknown CAC is the highest-impact gap, because every budget and revenue line depends on it.

## 4. Current-state scoring (17 areas)

Score each area 0-5 from evidence, with a one-line note. Total out of 85 (or out of 5 × scored areas when some are N/A). Use `rubric` in [scripts/plan_tool.py](scripts/plan_tool.py) for the total and shape.

| # | Area | 0 | 2 | 4 | 5 | Stage |
|---|---|---|---|---|---|---|
| 1 | Positioning | None anywhere | Inconsistent; team cannot state it | Clear, mostly consistent | Distinctive, every surface aligned | All |
| 2 | Customer research | Founder intuition only | One-off or stale | Ongoing, language captured | Continuous, feeds copy and product | All |
| 3 | Homepage | Generic or broken | Works, underperforms | Clear, converting | Distinctive, strong conversion | Acq, Act |
| 4 | Product and pricing pages | None | Stale or off-voice | Good for core products | Every plan and add-on covered | Acq, Rev |
| 5 | Campaign and use-case pages | None | One or two | Most needed exist | Full library, converting | Acq, Act |
| 6 | Competitor comparison | Avoided | Weak or hidden | Top 2-3 covered honestly | Full library, ranking | Acq |
| 7 | Content and resources | None | Thin or stale blog | Active, several formats | A moat (original data, pillars) | Acq |
| 8 | Onboarding | None | Exists, leaky | Solid, bottlenecks known | Tested, top-quartile activation | Act |
| 9 | Email lifecycle | None | Drafted or stale | Core flows live | Full, segmented, above benchmark | Ret |
| 10 | Sales material | None | Founder deck only | Self-serve kit | Current, objection library | Acq, Rev |
| 11 | Messaging and voice | Undocumented | In founder's head | Documented, consistent | Distinctive, enforced | All |
| 12 | Pricing | Untested > 1 year | Muddled by discounts or mix | Clear, recently tested | Tested regularly, expansion levers known | Rev |
| 13 | Experimentation | None, no tracking | Ad hoc | Regular cadence | Program with documented wins | Act, Rev |
| 14 | Launches | Soft launches only | Uneven | Playbook exists | Repeatable, coverage on demand | Acq |
| 15 | Paid acquisition | None | Unstructured, wasteful | 2-3 channels, positive economics | Mature, creative iterated weekly | Acq |
| 16 | Search | New or no authority | Brand terms only | Clusters, growing traffic | Moat, thousands of ranking terms | Acq |
| 17 | International | Single market | Users abroad not served | Localised, regional pricing | Multi-region revenue | Acq |

Rules: a low paid or international score for a pre-seed company reflects stage, not failure, so do not treat it as a gap. Subjective areas (1, 2, 7, 11) need a written rationale so the team can push back. If a scored audit already exists, reuse it and note its date.

Read the **shape**, not the total:
- Strong story, weak distribution (1, 2, 11 high; 14, 15, 16 low) → acquisition-heavy plan.
- Traffic without conversion (7, 15, 16 high; 3, 5, 8, 12 low) → activation and revenue first.
- Conversion without retention (3, 8, 12 high; 9, 13 low) → retention first.
- Only positioning and research strong → pre-marketing; first quarter is foundations.
- Paid-carried growth (10, 12, 15 high; 7, 16 low) → build compounding channels before scaling spend.

## 5. AARRR structure and the binding constraint

Organise every move by funnel stage, not by channel. Channel-organised plans hide which leak matters most.

| Stage | Question | Typical indicators |
|---|---|---|
| Acquisition | Do strangers find us? | Visits, signup-page sessions, store page views, CAC by channel |
| Activation | Do new users reach first value? | Signup completion, time to value, key-action rate, trial-to-paid |
| Retention | Do they stay and deepen? | Week 1/4/12 retention, logo and revenue churn, DAU/MAU |
| Referral | Do they bring others? | Invites per user, referred share of signups, review volume |
| Revenue | What do they pay and does it grow? | ARPA, plan mix, expansion, LTV |

Boundary rule: arriving on the signup page is acquisition; completing signup and everything after is activation. Brand and content are cross-cutting; they serve every stage and live in the positioning and operating-model parts, never as a sixth stage.

**Find the binding constraint** and sequence moves there first:
- No users yet → acquisition: the first 100 users.
- Signups but bounce (low activation, poor store conversion, broken onboarding; day-1 paid rate far below day-30) → activation.
- Activation fine but users leave in 7-30 days, retention below category norms → retention.
- Retention strong but growth slow, pricing untested, inbound referrals unstructured → referral and revenue (they often cluster).
- Everything works small → acquisition again, now as scaling.

Assign each move to the stage where its main measurable effect lands; when unsure, ask where removing it would hurt most. Present stages in funnel order regardless of priority, and say which is the priority in the summary. A plan with equal volume across all five stages usually means a weak diagnosis.

Stage sequencing principles:
- **Acquisition**: build the organic base first (search, founder-led social, content, PR, ambassadors); add paid on top of a working baseline, because paid amplifies whatever conversion rate exists.
- **Activation**: shorten the path to first felt value; every step between opening the product and the converting experience is a candidate to cut.
- **Retention**: ship lifecycle flows in order of content stability (flows referencing UI that may change go last); reconcile churn definitions across billing and analytics first.
- **Referral**: launch with whoever already raises a hand (five eager advocates are a program), then build share moments into the product.
- **Revenue**: audit what is actually charged (discounts, trials, plan mix) before testing price changes; listed and effective price often differ.

## 6. Variations by business model

| Model | Acquisition leans on | Activation event | Retention driver | Referral | Revenue lever |
|---|---|---|---|---|---|
| B2B SaaS | Search, content, comparison pages, founder LinkedIn, outbound, events for high ACV | Signup → first key action, or demo → pilot | Feature adoption, success team for high ACV | Advocacy, reviews, champion moves | Expansion and NRR, seats, tiers |
| Consumer subscription app | Store optimisation, paid social, creators, PR | Onboarding completion, first session, paywall | Lifecycle email and push, preference center | Share mechanics, two-sided rewards | Annual default, tiers, in-app upsell |
| Hardware + software | Store SEO, marketplaces, PR, visual paid social | Unboxing and app setup (two activations) | Companion software, community | Gifting, reviews | Blended LTV, bundles (device + months of premium) |
| Marketplace | Two funnels: supply via outbound/partners, demand via search/paid; location pages | First listing (supply), first transaction (demand) | Repeat frequency, supply utilisation | Same-side referrals | Take rate × volume, premium placement |
| Developer tool | Docs search, technical content, developer relations, community forums | First build or integration; time to hello world | Depth of integration, team adoption | Forum recommendations, talks | Usage limits, team and enterprise plans, support tiers |
| Deep tech / clinical | Publications, conference talks, advisor intros | Pilot or proof of concept, high-touch setup | Success team, co-publication | Named references | Pilot to contract, multi-year, compliance add-ons |

## 7. Budget: two defensible methods

Pick one and show the arithmetic. Use `budget` in [scripts/plan_tool.py](scripts/plan_tool.py).

**Blended CAC first.** Divide all acquisition cost in a period by new customers: marketing salaries (loaded), ad spend, tools, content production, agency and contractor fees, SDR cost. A company that "runs no ads" still has a CAC hidden in people and content. With no history, start from one year of revenue on the cheapest paid plan as a placeholder and replace it with measured CAC after one quarter.

**Method A: revenue-based (budget → goal).** Spend a share of ARR, then forecast what it buys.

| Posture | Share of ARR | Fits |
|---|---|---|
| Conservative | ~5% | Profitable or bootstrapped, protecting margin |
| Standard growth | 15-25% | Most healthy seed to Series A companies |
| Aggressive | up to ~40% | Just raised, mandate to deploy |

Example: $600k ARR at 20% → $120k. At $400 blended CAC → 300 customers; at $60/month → $216k gross new ARR; at 80% annual retention → about $173k net. A founder spending 5% while promising the board a tripling is sending two incompatible signals; make the share match the ambition.

**Method B: goal-based (goal → budget).** Budget = (new ARR ÷ (ARPC × 12)) × CAC ÷ annual retention.

Example: add $300k ARR at $60/month ARPC, $400 CAC, 80% retention → $720 per customer per year → 417 customers → $166.7k → ÷ 0.8 = $208k. Best for early companies, fundraising asks, or a fixed board target. It forces the question "is this goal funded?"; if the result is above ~40% of ARR, lower the goal, fix CAC or retention, or name the funding source.

**Always add a 10-20% experimental layer.** CAC is the main uncertainty; the buffer also funds the next channel before the current one plateaus.

**Venture benchmark** for venture-backed companies past $1M ARR: triple, triple, then double for several years (1 → 3 → 9 → 18 → 36). Few hit it; anchor against it only to say explicitly whether the plan matches it or deliberately does not. Bootstrapped companies plan linear additions instead.

**Forecast honestly.** Below public-company scale nobody hits monthly forecasts. Commit to an annual direction, the budget that makes it plausible, quarterly KPIs and kill criteria; label month-by-month projections as illustrative.

## 8. Funding-stage tiers

Tie every recommendation to what the company can fund now, and show what the next round unlocks. Ranges are anchors; consumer and e-commerce spend more, deep tech less.

| Tier | Paid media / month | Tools / month | People | Channels live | Unlocks |
|---|---|---|---|---|---|
| Pre-seed / bootstrapped | $0 | ~$0.5-2k | Founders, maybe a generalist, fractional help | Search, content, store organic, founder social, events, word of mouth, ambassadors, founder-pitched PR | Nothing hired; plan runs on current team and tooling |
| Seed close | ~$5-15k test | ~$1-3k | First marketing hire | + small paid pilots, funding PR, first big launch | Lifecycle/content marketer or growth marketer |
| Seed deployment | ~$20-50k | ~$2-5k | + designer (often fractional), second marketer | + paid on 2-3 channels, weekly content cadence, full lifecycle | Brand creative velocity, structured launch motion |
| Series A | ~$50-150k | ~$5-10k | Team forming: performance lead, content lead, designer | Full surface; brand campaigns possible; international considered | Agency partners, attribution, possibly a permanent CMO |
| Series B+ | $150k+ | ~$10-25k | 10+ person org | Category-level sponsorships, PR firm, media acquisitions | VP/CMO, regional leads |

Name tier skips explicitly (a well-known founder raising a large first round, a hardware product with a breakout PR moment, enterprise contracts funding a pilot) instead of forcing the ladder. Never plan paid spend that depends on money not yet raised without labelling it "post-round".

## 9. Growth shape, S-curves and 70/20/10

**Phases** (each has a different binding constraint):
- $0-10k ARR: slow and grinding, often 6-12 months, with repositioning likely. Constraint: finding a repeatable channel and message.
- $10k-100k: the dangerous middle; enough revenue to prove the idea, not to fund a team. Founders can usually go full-time around $8-10k MRR. Constraint: activation and focus.
- $100k-1M: acceleration as word of mouth and references kick in; the next doubling is often much faster than the first. Constraint: retention, referral and repeatable acquisition.
- $1M+: layering channels, segments and products.

**Shape**: healthy growth is mostly linear (a predictable amount of new MRR per month from working channels) with step jumps from deliberate events (a new segment, a big release, a channel breakthrough). Do not promise exponential curves; the founder will hold the plan to them.

**Layer S-curves** on three axes. Channels mature at different speeds: search takes 6-12 months then runs for years; paid gives quick results with diminishing returns; content compounds slowly; partnerships are episodic; outbound plateaus at team capacity; PR spikes. Products saturate their first use case. Markets saturate their first segment (SMB → mid-market → enterprise; one vertical → adjacent; domestic → international). Start the next curve while the current one is still growing.

**70/20/10**: about 70% of effort and budget on what works now, 20% on the next curve being built (graduates to the 70% within 2-4 quarters), 10% on experiments. The 10% is the experimental buffer from section 7.

**Plateau signals** (two on the same curve → shift weight to the 20%): weekly additions flat despite equal or more effort; CAC rising on a formerly cheap channel; top-of-funnel engagement softening; effort up, output flat. Review leading indicators weekly, allocation monthly, the plan quarterly.

## 10. Team and agency model

- **Keep strategy in-house**: direction, customer understanding, positioning, institutional knowledge. **Outsource execution** where scope is clear: specialist implementation (paid media, technical search, video, design), burst capacity, well-defined programs, fresh eyes.
- Three functions exist at any size: **growth** (demand engine: channels, funnel, tooling, testing), **product marketing** (story engine: positioning, launches, enablement, pricing communication), **content** (trust engine: voice, editorial, education, customer stories). Name an internal owner for each, even if one person holds all three.
- **First hire is a strategist who can execute**, ideally deep in two of the three functions (product marketing + growth, product marketing + content, or growth + content). A deep specialist alone (paid, search, design) needs a strategic owner above them.
- **Title conservatively**: manager or lead, not VP or CMO, so the org can grow above them.
- **External help ladder**: individual contractors (most flexible, best for most pre-Series A work) → small specialist agencies (full programs with some complexity) → small generalist agencies (convenience, higher cost) → large agencies (rarely right for startups: minimums, junior teams, slow).
- **Make outsourcing work**: specific briefs with deliverables and success metrics, weekly tactical and monthly strategic check-ins, shared data, reviews against agreed metrics. Red flags: scope creep beyond their speciality, team turnover on your account, missed deadlines, reporting activity instead of outcomes.

## 11. Measurement and review cadence

**North star**: one metric that captures the business model, moves slowly and improves only when the business improves. Revenue totals are outcomes, not north stars.

| Model | North star | Alternative |
|---|---|---|
| B2B SaaS | Net revenue retention | Logo retention × expansion ARR |
| Consumer subscription | Blended LTV ÷ blended CAC | Paid users at day 35 per cohort × LTV |
| Hardware + software | Blended LTV ÷ CAC across both | Device-buyer-to-subscriber rate × blended margin |
| Marketplace | Liquidity (share of listings or requests that transact) × take rate | Monthly transacting users × frequency × take rate |
| Developer tool | Weekly active developers × paid conversion | Weekly active orgs × seats × ARPA |
| Media / content | Daily active readers × revenue per session | Subscribers × retention × ARPU |
| One-off commerce | Repeat purchase rate × order value × frequency | LTV ÷ CAC with payback |

Leading indicators per stage: acquisition (organic visits per cluster, store visit-to-install, social-to-subscriber conversion, CAC per paid channel); activation (day 1/7 paid conversion, onboarding completion, key action rate); retention (day 30/60/90 retention, gross and net churn, lifecycle engagement, reactivation); referral (referred signups, share rate, review volume, NPS if surveyed); revenue (ARPA by cohort, annual-plan share, plan mix, expansion).

**Cadence**: weekly 30-minute scoreboard (indicators vs. last week, ships, blockers); monthly 60-90 minute review (indicators vs. quarterly targets, learnings, idea reprioritisation, hiring calls); quarterly 2-3 hour recalibration (plan vs. outcomes, channel analysis, funding-tier check, next 90 days, new plan version).

**Quarterly KPI targets** (3-5 per quarter, specific, measurable from a connected source, stretch but plausible, each with what a miss triggers):
- Q1 foundations: fix leaks and lay tracks ("signup completion 41% → 55%", "4 search clusters published"); avoid bold growth numbers.
- Q2 validation: does it work? ("blended CAC under $X", "organic visits 2-4k/month", Q2 cohort retention vs. Q1).
- Q3 scaling: how far does it go? ("paid at $Y/month with CAC flat", "first partner-sourced customers").
- Q4 compounding: is the flywheel turning? ("over half of new customers from non-paid channels", "LTV/CAC above 3").

## 12. Drafting order, verification and quality bar

**Drafting order**: positioning → baseline → the five stages → 90-day timeline and year view → operating model → ideas backlog → measurement and open decisions → leadership brief last (it summarises decisions already made). Review each section with the owner before moving on; keep approved sections as separate files so work can resume after an interruption.

**Verification pass before delivery**:
- Every idea or skill referenced exists and is named correctly.
- Every tool mentioned is in the company's stack or flagged "not yet connected".
- No machine paths, internal file names or private links in the deliverable.
- Voice check against the company's rules.
- Every TBD is listed in open decisions, not buried in prose.
- Every item from "already done" is acknowledged somewhere.

**Good plan signals**: every move tagged to a stage and an owner; anchored in the company's real budget, team and channels; the 90-day timeline has owners and dates; the funding section says what changes after the round; skipped ideas listed with reasons; the summary can be pasted into an investor update; open decisions explicit.

**Failure modes**: tactics without sequence; moves the team cannot staff; paid spend before the money exists; glossing over bad metrics; generic lines ("build community", "improve SEO"); ignoring voice rules; padding with ideas that do not fit; ignoring work the team already shipped.

**Length**: comprehensive plans run long (often 8-12k words) because founders share them with teams and investors; be dense, not bloated. If a section has nothing to say, write that and why ("international: out of scope for 12 months").
