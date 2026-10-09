---
name: content-strategy
description: "Plan what content to make and how to distribute it: topic clusters, keyword-to-stage mapping, calendars, repurposing, social and community strategy. Use when asked what to write or post, for a content calendar or editorial plan, topic clusters, a social media strategy, or a community plan. Not for technical SEO (use seo-optimization), writing a page (use marketing-copy) or email nurture (use email-sequences)."
license: MIT
metadata:
  category: "growth-marketing"
  version: "3.0.0"
---

# Content Strategy

Scope: searchable vs shareable, pillars and clusters, buyer-stage keyword mapping, idea scoring, calendar mix, production standards, link-earning formats, repurposing across owned/rented/borrowed channels, social playbooks and platform limits, short-form video, community models and health metrics.

Treat every piece like a small product launch: a reason to exist (a real customer question or an idea worth spreading), a quality bar, and a distribution plan built in before writing starts.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `goal` | required | ask | traffic, leads, brand authority, community growth, sales enablement |
| `scope` | optional | `full-plan` | `full-plan`, `topic-ideas`, `calendar`, `distribution`, `social`, `community`, `refresh-plan` |
| `audience` | required | from context file | agency finance leads |
| `research` | optional | none | call transcripts, tickets, survey, keyword export, forum threads |
| `existing_content` | optional | none | sitemap or analytics export with top pages |
| `resources` | optional | ask | 1 writer, 8 hours/week, can record video monthly |
| `formats` | optional | written | blog, video, podcast, newsletter, social, templates/tools |
| `platforms` | optional | infer from audience | LinkedIn, X, YouTube, community forum |
| `competitors` | optional | from context file | 3 competitor blogs |
| `horizon` | optional | 90 days | 6 months |

Read `.agents/product-marketing.md` first (audience, pains, language, competitors).

## Output

A content plan ([templates/content-plan.md](templates/content-plan.md)) containing:
1. 3-5 pillars with rationale, subtopic clusters, and how each ties to the product.
2. Ranked idea list: title, searchable/shareable/experimental, content type, keyword + buyer stage, evidence (quote or data), score.
3. Cluster map (hub → spokes, internal links).
4. Calendar for the horizon at the chosen mix, with owners and formats.
5. Distribution plan per flagship (atomization list, channels, reshare schedule) and, if in scope, a social plan ([templates/social-plan.md](templates/social-plan.md)) or community plan ([templates/community-plan.md](templates/community-plan.md)).
6. Metrics and review cadence.
Per piece, a brief: [templates/content-brief.md](templates/content-brief.md).

## Supporting files

- [REFERENCE.md](REFERENCE.md): searchable vs shareable rules, information-gain gate, content types, link-earning formats, pillars, buyer-stage modifiers, ideation sources, scoring, calendar mix, per-format standards, distribution (owned/rented/borrowed, half-lives, flywheel, atomization), content ops and CMS modeling, measurement. Read for any plan.
- [social.md](social.md): platform playbooks and limits, pillars mix, hooks, post templates, carousel frameworks, short-form video scripting, X ranking signals, listening and comment triage, studying top performers, analytics. Read for social scope.
- [community.md](community.md): community models, launch/growth/advocate/support playbooks, platform choice, health metrics, scaling roles. Read for community scope.
- [scripts/content_tool.py](scripts/content_tool.py): `score` (weighted idea ranking), `calendar` (dated calendar honoring the mix), `post` (platform length, fold, link, bait checks). `python3 scripts/content_tool.py score ideas.csv --out ranked.csv`.

## Steps

Run by `scope`: `full-plan` → 1-11; `topic-ideas` → 1, 2, 4-6 (deliver the ranked list); `calendar` → 1, 6, 8 from an existing idea list; `distribution` → 9 for the named pieces; `social` / `community` → 1, 10, 11; `refresh-plan` → 11 plus `editing.md` §6 in the `marketing-copy` skill on the `existing_content` export (rank decaying pages by lost clicks × conversion value).

1. **Set goal and constraints.** Goal decides the mix: traffic/leads → searchable-heavy; authority/category creation → more shareable; retention → implementation content and community. Capacity decides volume; quality beats cadence (one strong piece a week beats five thin ones).
2. **Mine demand.** From research assets: questions → posts/FAQs; pains → problem pieces in their words; objections → proactive content; competitor mentions → comparison pieces; survey themes mentioned by 30%+ → priority. From keyword data: cluster, tag intent and stage, flag quick wins (relevant, decent volume, beatable results) and gaps vs competitors. From forums: questions, misconceptions, debates, terminology. From sales/support: repeated questions, success stories.
3. **Pick 3-5 pillars** where product relevance, audience need, and search/social interest overlap (check product-led, audience-led, search-led, competitor-led angles). Each pillar must support many subtopics.
4. **Map to buyer stages**: awareness (what is, how to, guide), consideration (best, vs, alternatives, comparison), decision (pricing, reviews, demo, trial), implementation (templates, examples, tutorial, setup). Most teams under-serve consideration and implementation; those convert and retain best.
5. **Apply the information-gain gate** to every searchable idea: read the current top results and write one sentence on what yours adds (original data, real process, expert input, better example, tool/template). If you can't → drop or change the angle.
6. **Score and rank** with `content_tool.py score` (customer impact 40%, content-market fit 30%, search potential 20%, resource ease 10%). Pick formats by goal: links → statistics roundups, glossaries, calculators/tools, how-tos; adoption → templates; authority → original data and opinion.
7. **Structure clusters**: hub first, then spokes; interlink spokes ↔ hub and spoke ↔ spoke where useful. Keep everything under `/blog` unless a topic has real layered depth (see `site-architecture.md` in the `seo-optimization` skill).
8. **Build the calendar** at 60% searchable / 30% shareable / 10% experimental by default (`content_tool.py calendar`); adjust: a new site leans searchable, a known brand chasing category leadership leans shareable.
9. **Plan distribution per flagship** before writing: standalone subheads, liftable sections, pre-chosen stats/quotes; atomize into 3-5 social posts, a thread or carousel, 2-4 clips (if video/audio), 1-2 graphics, one email; reshare across the channel's half-life; route attention borrowed → rented → owned (email list, blog, community).
10. **Social / community scope**: follow social.md or community.md to produce platform plans, cadences, templates, engagement routines, or community launch/growth plans.
11. **Define measurement**: per piece (rankings/clicks, assisted conversions, links, AI-answer citations, shares/saves/comments, replies); per program (organic signups, pipeline influenced, content-assisted conversion rate); monthly review of top/bottom pieces; refresh plan for decaying posts (`editing.md` §6 in the `marketing-copy` skill).

## Checkpoints

- After step 3: pillars agreed before listing 30+ ideas.
- After step 6: top 10 ideas reviewed with evidence before scheduling.
- Before publishing a flagship: distribution list exists, not just the article.
- Monthly: compare plan vs results; shift the mix toward what earns conversions.

## Worked example

**Context**: expense tool for agencies; goal: trial signups from organic; 1 writer at ~2 posts/week; research: 40 call notes, ticket export, keyword export.
- Pillars: month-end close (product core), agency spend policy, agency profitability (adjacent, shareable).
- Demand: calls ask "how do other agencies handle client-billable expenses?" (14 mentions); tickets show accounting-sync confusion; keywords: "expense policy template" (1.9k/mo, weak results), "month end close checklist" (2.4k/mo).
- Information gain: checklist built from 1,240 customers' actual close timelines (unique data); policy template with clauses for client-billable spend (no top result covers it).
- Scores: close checklist 8.5, policy template 8.0, alternatives page 7.8, "State of agency spend" data report 6.8, glossary entry 6.2.
- Calendar (8 weeks, 16 slots): 10 searchable, 5 shareable, 1 experimental (short video series).
- Distribution for the data report: 5 LinkedIn posts from key stats, one carousel, one email to 8k subscribers, pitch to two agency newsletters (borrowed), stats page kept updated as a link magnet.
- Metrics: trial signups from organic +30% in 6 months; leading indicators: rankings for 12 target terms, 20 referring domains to the data report.

## Pitfalls

- Topics from brainstorming instead of customer questions and search evidence.
- Me-too articles that add nothing beyond the current top results.
- All top-of-funnel; no comparison, pricing, or implementation content.
- Publishing without distribution, or spraying every platform with no flagship.
- Building only on rented platforms; never converting attention into the email list.
- Calendar commitments the team can't sustain; quality collapses by week 6.
- Social posts with links in the body on link-penalizing platforms, engagement bait, and machine-sounding hooks.
- Vanity metrics (impressions, likes) as the goal instead of signups, pipeline, and retention.
- Communities launched publicly before there's baseline activity.

## Related skills

seo-optimization (keyword mapping, architecture, programmatic pages), ai-search-optimization (citable formats), marketing-copy (writing and refreshing pieces), email-sequences (owned channel and newsletters), customer-research (demand mining), launch-plan (launch content), marketing-plan (channel plan), retention-and-referrals (community and advocacy), paid-ads (amplifying top content).

## Done when

- [ ] Pillars (3-5) with rationale and product tie-in.
- [ ] Ranked ideas, each with stage, type, evidence and information-gain sentence (for searchable pieces).
- [ ] Cluster map and calendar at a stated mix, matched to capacity.
- [ ] Distribution plan for every flagship, routing to owned channels.
- [ ] Social/community plans delivered if in scope.
- [ ] Metrics, review cadence and refresh rules defined.
