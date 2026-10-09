# Content strategy reference

Contents: 1 searchable vs shareable · 2 content types · 3 link-earning formats · 4 pillars and clusters · 5 buyer-stage keyword modifiers · 6 ideation sources · 7 scoring · 8 calendar mix and capacity · 9 per-format standards · 10 distribution · 11 content operations and CMS modeling · 12 measurement.

## 1. Searchable vs shareable

Every piece must be searchable, shareable, or both. Search is the compounding base; shareable work creates demand and earns links and mentions.

**Searchable** (captures existing demand)
- One primary query or question; match intent exactly (format and depth the results page rewards).
- Title mirrors the query; headings mirror sub-questions; key terms in title, first paragraph, a heading, and URL.
- Complete answer: don't leave the obvious follow-up unanswered; include data, examples, and links to authoritative sources.
- Information-gain gate: before committing, read the top results and write one sentence on what yours adds (first-party data, a real process with screenshots, expert quotes, a better worked example, a tool or template, a fresher date). No sentence → no piece.
- Make it citable by AI answers: direct answer near the top, stable definitions, tables, consistent positioning across the web (see ai-search-optimization).

**Shareable** (creates demand)
- Lead with a new insight, original data, or a well-argued contrarian view.
- Name something everyone feels but nobody has labeled.
- Stories with real stakes; honest lessons, including failures.
- Gives readers something that makes them look smart or helpful when they share it.
- Ties to a current shift or emerging problem.

## 2. Content types

| Type | What it is | Notes |
|---|---|---|
| Use-case pages/posts | [persona] + [use case] ("project tracking for architects") | Long-tail, high intent; often programmatic-ready |
| Hub and spoke | Comprehensive hub + deep subtopic spokes | Build the hub first; dedicated URL trees only for big layered topics |
| Template/tool libraries | Free templates, calculators, generators | High intent; show how the product makes the template better |
| How-to/tutorials | Step-by-step tasks | Screenshots, time estimates, prerequisites |
| Comparison/alternatives | vs and alternatives pages | Consideration stage; fair and dated (see seo-optimization) |
| Glossary/definitions | Short canonical definitions | Easy links and AI citations |
| Statistics roundups | Curated, maintained stats with sources | Strong link magnet if kept current |
| Original research/data | Surveys, product-data analysis, experiments | Big shareable bet; plan distribution |
| Thought leadership | Named concepts, contrarian arguments with evidence | Needs a real point of view |
| Expert roundups | One narrow question put to a panel of roughly 15-30 practitioners | Contributors share it, so it arrives with an audience |
| Case studies | Challenge → solution → results → lessons | Sales enablement and proof |
| Meta/behind-the-scenes | "How we reached our first $5k MRR" | Transparency builds trust |

## 3. Link-earning formats

When links are the goal, format matters more than effort. One 2026 vendor study of B2B SaaS sites (single source, treat as directional) compared each format's share of backlinks with its share of pages.

In that study, statistics and data roundups pulled in roughly four times the links their page count would predict. Glossary pages, interactive calculators and step-by-step tutorials each earned about one and a half times their share. Original research, long "ultimate" guides, opinion pieces and template or framework pages all came in below their share, at roughly 0.7-0.8×.

Read: writers link to whatever makes citing easiest. A maintained, well-sourced statistics page is citation infrastructure; original research earns links mainly when it's distributed hard and its key numbers are easy to quote.

## 4. Pillars and clusters

Pillars: the 3-5 topics you aim to own. Find them from four angles: product-led (problems you solve), audience-led (what the ICP must learn), search-led (topics with demand), competitor-led (what they rank for and where they're thin). A good pillar aligns with the product, matters to the audience, has search and/or social interest, and is broad enough for 10-30 pieces.

```
Pillar hub
├── Cluster A: article, article, article
├── Cluster B: article, article, article
└── Cluster C: article, article, article
```

Linking: hub ↔ every spoke; spokes ↔ siblings where the reader would naturally continue; product pages from the most commercial spokes. Most sites keep everything under `/blog`; only build `/guides/topic/...` trees for deep, layered topics.

## 5. Buyer-stage keyword modifiers

| Stage | Modifiers | Example pieces |
|---|---|---|
| Awareness | what is, how to, guide to, why, examples of | "What is a month-end close" |
| Consideration | best, top, vs, alternatives, comparison, review of category | "Best expense tools for agencies", "X vs Y" |
| Decision | pricing, cost, reviews, demo, trial, discount, implementation time | "Expense software pricing compared" |
| Implementation | template, example, tutorial, how to use, setup, integration | "Expense policy template", "How to sync receipts with your ledger" |

Intent labels: informational, commercial, transactional, navigational. Match format to intent (list vs guide vs tool vs comparison).

## 6. Ideation sources

| Source | Extract | Output |
|---|---|---|
| Keyword exports | Clusters, intent, stage, quick wins (relevant + decent volume + beatable), competitor gaps | Table: keyword, volume, difficulty, stage, type, priority |
| Sales/customer calls | Questions, pains, objections, exact phrases, competitor mentions | Ideas with supporting quotes |
| Surveys | Open-ended themes (30%+ mention = high priority), resource requests, format preferences | Prioritized topics |
| Forums and Q&A sites (`site:<forum> <topic>`) | Top questions, misconceptions, debates, upvoted answers, terminology | FAQ and opinion pieces |
| Competitor content (`site:<competitor>/blog`) | Top posts, repeated topics, gaps, outdated pieces, structure | "Do it better" and "angle they missed" list |
| Sales and support teams | Objections, repeated questions, ticket patterns, success stories, feature requests | Enablement and implementation content |
| Product data | Aggregated, anonymized usage patterns | Data reports and benchmarks |

Prompts for the team: patterns in the last 10 customer conversations; recurring sales questions; where competitors' content falls short; unique insights we hold; which existing pieces drive conversions and why.

## 7. Scoring

Score each idea 1-10 on four factors and weight:
- Customer impact (40%): frequency in research, share of customers affected, emotional intensity, value of customers with this need.
- Content-market fit (30%): ties to problems we solve, unique insight available, customer stories exist, leads naturally to the product.
- Search potential (20%): volume, competitiveness, long-tail breadth, trend direction.
- Resource ease (10%): expertise in-house, research needed, assets needed (10 = easy).

Example: impact 8, fit 9, search 7, ease 6 → 3.2 + 2.7 + 1.4 + 0.6 = 7.9. `scripts/content_tool.py score ideas.csv`.

## 8. Calendar mix and capacity

Default 60% searchable / 30% shareable / 10% experimental (new formats, channels or bets). New sites lean further toward searchable; established brands pursuing category leadership push shareable. Plan to real capacity: a solo writer sustains roughly 1-2 quality posts a week plus distribution; add a refresh slot (about 1 in 5 slots) once 30+ posts exist.

## 9. Per-format standards

- **Blog post**: 10 title options before drafting; brief with query, intent, information-gain sentence, outline, sources, internal links, CTA; ~5 editing passes (structure, clarity, evidence, line edit, title/meta); visuals planned; publish with schema where relevant.
- **Long-form guide (pillar)**: table of contents, jump links, links to every spoke, updated at least yearly.
- **Video**: script the hook first and deliver the payoff early; plan short clips at scripting time; chapters and full transcript for search.
- **Podcast**: each episode designed to be atomized: transcript, 3-5 clips, quote graphics, recap post, newsletter section.
- **Email/newsletter**: one idea per send; write several subject lines; see email-sequences.
- **Tools/templates**: ungated where possible for links; gate only for lead capture with a clear value exchange.

## 10. Distribution

**Create once, distribute many.** One exceptional flagship cut into channel-native pieces beats a fresh mediocre post per platform. Design for distribution while writing: subheads that work as standalone posts, modular sections, pre-chosen stats and quotes.

**Owned / rented / borrowed as a funnel**

| Layer | Channels | Role | You control |
|---|---|---|---|
| Borrowed | Podcasts, guest posts, partner newsletters, PR, communities you don't run | Discovery | Nothing |
| Rented | Social platforms, ad networks, marketplaces | Engagement and reach | The content, not the audience or algorithm |
| Owned | Email list, blog, community, product | Conversion and retention | Everything |

Route attention from borrowed and rented into owned. The common trap: ~90% of effort on channels you don't control while the list and site stagnate. Platform risk is real: organic reach on one major social network dropped from roughly 20% to under 2% of followers over a decade.

**Half-lives**

| Channel | Rough half-life | Implication |
|---|---|---|
| X posts | minutes to hours | Frequency, reposts, threads |
| Facebook/Instagram feed | ~1 day | Frequent cadence; stories are ephemeral |
| LinkedIn posts | ~1 day (longer for strong posts) | Fewer, higher-effort posts |
| Short video | days to weeks (resurfacing) | Evergreen hooks can resurface |
| YouTube | months to years | Search-driven; compounds |
| Blog/SEO | years | The compounding asset |
| Email | one send, archive reusable | Harvest into other formats |

**Flywheel**: create flagship → atomize → distribute (owned first, then rented, borrowed) → engage and collect questions → feed the next flagship and double down on top-performing atoms.

**Atomization checklist per flagship**: 3-5 standalone social posts; 1 thread or carousel; 2-4 short clips (if video/audio); 1-2 stat/quote graphics; 1 email; reshare schedule across the channel's half-life; outreach to 3-10 people cited or likely to cite; community posts where genuinely useful; internal links from related pages.

Failure modes: spray-and-pray (everywhere, no flagship, no system); platform dependency (no list); one-and-done posting.

## 11. Content operations and CMS modeling

Workflow: idea → brief → draft → edit → SEO/fact check → design → publish → distribute → measure → refresh. Roles: author (create, edit own), editor (edit all, publish), admin (everything incl. delete). Keep a content inventory (URL, pillar, stage, owner, publish/update date, primary query, conversions).

CMS choice: traditional/monolithic CMS when non-technical editors need to ship fast on one website; headless when content feeds several channels (site, app, docs), developers want full front-end control, or content must be reused. Checklist: multi-channel? developer capacity? editor experience? time to launch? localization? preview needs?

Model marketing content as structured types, not pages of rich text:

| Type | Key fields |
|---|---|
| Landing page | title, slug, hero, sections[], seo |
| Blog post | title, slug, body, author, category, tags, published/updated dates, seo |
| Case study | customer, industry, challenge, solution, results, metrics[], logo, quote |
| Testimonial | quote, name, role, company, avatar, permission status |
| FAQ | question, answer, category |
| Author | name, bio, credentials, avatar, profile links |
| CTA block | heading, body, button text, URL, variant |

SEO fields on every page type: meta title, meta description, canonical, noindex toggle, social image, schema type, updated date. Reusable blocks (testimonial, CTA, FAQ) keep proof consistent across pages and make updates one-step.

## 12. Measurement

| Level | Metrics |
|---|---|
| Piece (search) | Impressions, clicks, average position for target query, AI-answer citations, assisted conversions |
| Piece (shareable) | Referring domains, mentions, shares/saves, comments, newsletter signups |
| Program | Organic signups/trials, pipeline and revenue influenced, content-assisted conversion rate, email list growth |
| Health | Publishing vs plan, % of pieces with distribution done, decaying pages count |

Review monthly: top and bottom 5 pieces (why?), mix vs results, refresh candidates (traffic down 20%+ over 3-6 months, stats > 12 months old, product changed).
