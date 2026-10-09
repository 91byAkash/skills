# Partnerships and co-marketing

Read this when a launch or plan borrows someone else's audience: finding partners, scoring them, planning a joint campaign, pitching a partner, structuring the agreement, or choosing between partnership types. Affiliate commission mechanics, cookie windows and fraud rules live in retention-and-referrals; partner-facing sales collateral in sales-outreach. Proposal skeleton: [templates/co-marketing-proposal.md](templates/co-marketing-proposal.md).

## 1. Five partnership types

Route each request to the right type instead of defaulting to joint content.

| Type | What it is | Main payoff | Start here when |
|---|---|---|---|
| Integrations | Your product connects to another's (native build, automation platform, public API, embedded widget) | Retention, expansion, marketplace discovery | Retention or expansion is the problem; buyers ask "does it work with X?" |
| Resellers and agencies | Partners sell your product and wrap services around it | Distribution plus services revenue | You need distribution without headcount and buyers rely on implementers |
| Affiliates | Promoters earn commission on referred customers | Pay-for-performance reach | Creators and publishers already talk to your buyers |
| Co-marketing | Joint content or campaigns with a non-competing peer | Borrowed audience, credibility | You have content but little reach |
| Marketplaces and app stores | Listing inside a platform's ecosystem | Built-in distribution | One platform owns your buyer's daily workflow |

Notes by type:
- **Integrations**: build in order of buyer intent: first what the product cannot function without (calendar, email, storage), then where revenue teams live (CRM, billing), then top-of-funnel tools (forms, email marketing). Each rung widens who depends on you. Buyers, especially larger ones, often treat a missing integration as a deal-breaker.
- **Resellers**: typical economics give partners a recurring share of software revenue (often 20-40%) while most of their margin comes from services sold around it; enablement (onboarding, certification, collateral, deal registration, co-selling, a partner portal) is the work, not the signing.
- **Affiliates**: commission design, attribution windows, the power-law of promoters and buy-outs are in retention-and-referrals (`referrals.md`); here, treat a top affiliate as a co-marketing partner and use the formats below.
- **Co-marketing**: you do not always need a signed partner. **Permissionless co-marketing** means building something useful for a bigger brand's audience (templates for their workflow, a guide to using both products, a calculator for their users) and publishing it; it can rank and get shared by the partner's community. Showing up consistently in someone else's content ecosystem (their podcast, conference, newsletter) is the low-friction version.
- **Marketplaces**: platforms typically take 15-30% of revenue; treat it as acquisition cost. If one platform maps to your buyer, going deep on it (integration, listing optimisation, co-selling) beats spreading thin.

Programs compound: integrations create marketplace presence, marketplace presence attracts implementers, and implementers and affiliates create case studies for co-marketing.

## 2. Finding partners

Best partners share your buyer but not your budget line: same persona, different problem; adjacent in the workflow (before, after or alongside you); similar stage and customer size.

Questions that surface candidates:
- Which tools do customers already use? What do they use right before and after you?
- Who else sells to the same buyer? Which integrations are requested most?
- Who sponsors the same podcasts and newsletters, exhibits at the same events, or is active in the same communities?
- Whose content does your audience share?

Sources: customer surveys ("what else do you use?"), integration requests, review-site category neighbours, job posts that mention your tool alongside others, account-overlap tools that compare customer lists privately, your own CRM's technographic fields.

## 3. Scoring partners

Score each 1-5 and weight; `partners` in [scripts/plan_tool.py](scripts/plan_tool.py) computes the weighted score and verdict.

| Criterion | Weight | What to check |
|---|---|---|
| Audience fit | 3 | Overlap with your ICP (gate: below 3 → reject) |
| Audience size | 1 | Reach worth the effort |
| Brand alignment | 2 | Would you be proud to stand next to them? (gate: below 3 → reject) |
| Engagement | 2 | Do their emails, posts and events get real responses? |
| Reciprocity | 1.5 | Can you offer comparable value? |
| Ease | 1.5 | Partnerships owner, past co-marketing, decision speed |

Verdicts: ≥ 3.8 pursue, 3.0-3.8 maybe, below 3.0 park. Size matters least: a small engaged audience that matches beats a large loose one.

## 4. Campaign formats

| Format | Effort | Leads | Best for |
|---|---|---|---|
| Co-authored article | Low | Shared byline, links | Search, thought leadership |
| Newsletter swap | Low | Each keeps own | Quick exposure |
| Podcast guest exchange | Low | Each keeps own | Relationship building |
| Joint guide or ebook | Medium | Gated, shared under consent | Lead generation |
| Joint research report | High | Gated, shared | Authority, press |
| Joint webinar or workshop | Medium-High | Shared registrants | Education, demand |
| Virtual summit panel | Medium | Multi-partner | Reach |
| Shared booth or dinner at an event | Medium | Each keeps own | Cost split, relationships |
| Integration launch | Medium | Each keeps own | Existing integration partners |
| Joint case study | Medium | n/a | Shared customers |
| "Better together" page | Low | Each keeps own | Integration discovery, search |
| Bundle or partner discount | Medium | Each keeps own | Conversion, cross-sell |
| In-app cross-promotion | Medium | Each keeps own | Activation of shared users |
| Social takeover, joint live session or AMA | Low | n/a | Exposure |
| Joint giveaway | Low | Shared under consent | List building (qualify the entrants) |

**Lead sharing**: share personal data only with clear consent at the point of capture ("your details go to both companies"), and agree who follows up first.

## 5. Brainstorming with a specific partner

- **Shared moments**: triggers, seasons and industry changes that matter to both audiences.
- **Combined value**: what customers can do with both products that they cannot do with one; which workflow the combination completes.
- **Assets each side brings**: audience size and engagement, content expertise, product capabilities, credibility, customer stories, data.
- **Prompts**: what could we ship together in two weeks? What do both audiences badly need? What would make customers say "finally"? What could only the two of us offer? What data do we both hold that tells a story?

## 6. Pitching a partner

Short cold note:

> Subject: [Your company] × [Their company]: an idea for [shared audience]
>
> Hi [Name], I run [role] at [Your company]; we help [audience] [outcome]. A lot of your customers also use us: [specific overlap evidence]. I have an idea for [format]: [one-sentence pitch with the benefit to their audience]. Open to a 20-minute call next week?

Bring to the call: overlap evidence, 2-3 specific campaign ideas, your audience numbers (list size, traffic, engagement), past partnerships you executed, and a clear ask with what you will provide.

## 7. Agreement essentials

Align in writing (a one-page agreement is enough for most campaigns):
1. Campaign description and goal.
2. Responsibilities: who creates which asset, who approves.
3. Timeline and key dates.
4. Lead handling: capture, consent, sharing, follow-up order.
5. Promotion commitments: minimum sends, posts and placements per side, with dates.
6. Branding: logo use and approval process.
7. Costs: who pays for what.
8. Reporting: which metrics each side shares and when.
9. What happens next if it works.

## 8. Measuring

Quantitative: registrants or leads per partner, lead-to-opportunity rate, revenue attributed (tag every partner link), audience growth, engagement. Qualitative: ease of working together, responsiveness, audience reaction, whether you would do it again. Share results with the partner within two weeks and decide the next step together.

## 9. Checklist

- [ ] Customer tool list and overlap evidence gathered.
- [ ] Top 5 partners scored; past co-marketing researched.
- [ ] Format and goal agreed; lead-sharing and consent defined.
- [ ] Responsibilities, dates and promotion commitments written down.
- [ ] Shared assets built; both teams briefed on talking points.
- [ ] Links tagged per partner; results shared; debrief held.
