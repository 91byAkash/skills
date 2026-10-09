# AI Search Optimization: Reference

All platform behavior and percentages below are dated snapshots of fast-moving systems (mostly 2023-2026 studies and practitioner reports). Re-check before quoting a number to a client, and prefer your own monitoring data.

## Contents
1. How engines pick sources
2. Crawler tokens by purpose and a robots policy
3. Authority levers (what research says moves citations)
4. The visibility ladder: retrieved → cited → mentioned → recommended
5. Format volatility
6. Playbooks by content type
7. Off-site surfaces: reviews, communities, video, LinkedIn, podcasts, Wikipedia
8. Machine-readable files and agent readiness
9. Positioning, repositioning and consensus
10. Measurement rigor and attribution

---

## 1. How engines pick sources

Shared prerequisites: be in the engine's index, be crawlable by its discovery crawler, and have passages that stand on their own.

| Engine | Index behind it | What it seems to reward | Priority actions |
|---|---|---|---|
| Google AI Overviews / AI Mode | Google index + Knowledge Graph | Same ranking and quality systems as Search; E-E-A-T; topical coverage (it "fans out" into related sub-queries) | Classic SEO first, cover full topic clusters, author credentials, original info; Google says no special files or markup are required |
| ChatGPT search | Bing-backed index plus its own crawler | Authority/backlinks, freshness (recently updated pages cited far more), content whose structure matches how the assistant answers; recently shifted toward official/primary sources and `site:` lookups | Keep competitive pages fresh, answer-first structure, strong owned pages (product, docs, pricing), named stats |
| Perplexity | Own index + others, multi-stage reranking | Self-contained paragraphs, FAQ structure, public PDFs/research, publishing velocity, fast time-decay (new pages get a chance quickly) | Allow its crawler, publish research openly, clear Q&A sections, Article dates |
| Gemini | Google index + Knowledge Graph | Business-owned sites are a large share of its citations; rarely cites LinkedIn | Owned pages, entity consistency, structured data |
| Copilot | Bing index | Bing indexing, speed (under ~2 s), explicit definitions, LinkedIn content | Bing Webmaster Tools, IndexNow, fast pages, LinkedIn presence |
| Other assistants with web search | Varies (some use independent indexes such as Brave) | Very selective; factual density and precise sourcing | Check your visibility in that engine's index directly; dense, sourced pages |

Where to start: Google AI features (largest reach, uses existing SEO), then ChatGPT (largest standalone assistant for B2B/tech), then Perplexity (researchers, early adopters), then others by audience (enterprise IT → Copilot; developers/analysts → research-oriented assistants).

## 2. Crawler tokens by purpose and a robots policy

Decide by purpose, not "AI yes/no". Confirm current names in each vendor's crawler documentation; they change.

| Purpose | Tokens (examples) | Effect of blocking |
|---|---|---|
| Classic search | `Googlebot`, `Bingbot` | Lose search and the AI features built on it |
| AI search discovery | `OAI-SearchBot`, `Claude-SearchBot`, `PerplexityBot`, other vendors' `*-SearchBot` tokens | Lose citations in that assistant's search answers |
| User-triggered fetch | `ChatGPT-User`, `Claude-User`, `Perplexity-User`, other vendors' `*-User` tokens | Assistant can't open your page when a user pastes or asks for it; some vendors say robots rules may not apply to these |
| Model training | `GPTBot`, `ClaudeBot`, `CCBot`, other vendors' training bots, `Applebot-Extended`, `Meta-ExternalAgent`, `Bytespider` | Opts out of training; does not by itself remove search citations |
| Product control token | `Google-Extended` | Controls certain Gemini training/grounding uses; does not affect Google Search inclusion or ranking |

Template (publisher choice: allow search, block training):
```text
# Search and AI search discovery
User-agent: Googlebot
User-agent: Bingbot
User-agent: OAI-SearchBot
User-agent: Claude-SearchBot
User-agent: PerplexityBot
Allow: /

# Model training (opt-out shown)
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: CCBot
User-agent: Google-Extended
Disallow: /

Sitemap: https://example.com/sitemap.xml
```
Add the equivalent tokens for any other assistant vendors your audience uses. Then check the firewall/CDN bot rules: many block AI agents by default without anyone deciding to. Test with each user-agent string and look for 403/429/challenge pages.

## 3. Authority levers

A 2023 generative-engine-optimization study (tested on an answer engine) compared rewriting tactics. Approximate visibility changes on its own metric:

| Tactic | Approx. effect | Apply as |
|---|---|---|
| Cite sources | +30-40% | Link primary sources inline for claims |
| Add statistics | +30-40% | Specific numbers with date and source |
| Add quotations | ~+30% | Named expert, role, organization |
| Authoritative tone | ~+25% | Show first-hand expertise; no hedging fluff |
| Easier to understand | ~+20% | Short sentences, defined terms |
| Technical terms | ~+18% | Use the field's vocabulary correctly |
| Fluency | +15-30% | Clean, readable prose |
| Keyword stuffing | about -10% | Avoid |

Best combination in that study: fluency plus statistics. Lower-ranked sites gained the most from adding citations. Effects are not additive and the numbers are not forecasts.

Freshness: visible "last updated" dates that reflect real edits; refresh competitive pages monthly to quarterly; remove outdated stats.

E-E-A-T: author bios with relevant credentials, first-hand experience (screenshots, data you collected, "we tested"), transparent methodology, clear ownership (About, contact, company info).

Domain-specific signals:
- Technology: version numbers, dates, links to official docs, code samples.
- Health: peer-reviewed sources, clinician reviewer, "last reviewed" date, limitations.
- Finance: regulator references, time-bound figures, "educational, not advice" note.
- Legal: statutes, jurisdiction, consult-a-professional note.
- Business/marketing: case studies with measured results and timeframes.

## 4. The visibility ladder

| Rung | Meaning | Governed by | How to see |
|---|---|---|---|
| Retrieved | Read while composing the answer | Crawlability, parseable structure, relevance | Server logs (bot hits) |
| Cited | Linked as a source | Usefulness: structure, stats, clarity, freshness | Prompt tracking, AI Overview sources |
| Mentioned | Brand named in the text | Entity recognition, how the web describes you | Prompt tracking |
| Recommended | On the shortlist the buyer acts on | Web-wide consensus: reviews, analysts, communities, press, video | Prompt tracking + framing |
| Recommended against | Named as a poor fit | Repeated negative consensus | Framing review on requirement-heavy prompts |

Key finding from 2026 B2B research: self-promotional "best [category]" guides from emerging brands were often cited in answers that then recommended competitors (in one 100-query study, roughly 7 in 10 such citations). The model harvests your category research and recommends from consensus. Leaders benefit from definitive guides; emerging brands should expect citation and category framing, not shortlist placement, and shift investment off-site. A middle path: name the category leader first, say honestly what it does well, then show where you go further.

Repairing a repeated weakness ("slow implementation"): address it publicly and specifically over months: a concrete timeline on the relevant page, posts from real people about the process, customer stories with dates.

## 5. Format volatility

- In mid-2026 a major chat assistant cut citations of listicles by about half and comparison pages by about a third, while `site:` and "official" lookups rose. These were the two formats most scaled for AI visibility.
- Comparison and best-of pages still convert humans, still appear in Google's AI features (which follow rankings), and had no reported demotion on some other engines.
- Rising everywhere: owned primary sources (product, docs, pricing, original research).

| Format | Chat assistant (post-shift) | Google AI features | Gemini | Perplexity |
|---|---|---|---|---|
| Listicles / best-of | Demoted | Depends on rankings | No reported change | No reported change |
| Comparison / vs | Demoted | Depends on rankings | No reported change | No reported change |
| Original research | Strong | Strong | Strong | Strong |
| Product / docs / pricing | Rising | Strong | Dominant | Strong |
| How-to guides | Steady | Strong | OK | Strong |

Do not mass-publish one page per fan-out query; that is the scaled pattern engines demote.

## 6. Playbooks by content type

- **Product pages**: what it does and for whom in the first paragraph; specific metrics instead of adjectives; feature table vs the category; customer counts with numbers; visible pricing plus `/pricing.md`; buyer FAQ.
- **Blog posts**: one target question per post; definition first for "what is"; original data or expert quotes; updated date; author bio; links to related product pages.
- **Comparison / alternatives pages**: tables with explicit criteria; fair (engines and readers discount obvious bias); current prices and features with a "checked on" date. Build mechanics in seo-optimization.
- **Segment / industry pages**: one per segment you truly serve, with segment-specific workflows, integrations, compliance and proof; never templated pages that only swap the industry name.
- **Docs / help**: numbered steps, prerequisites, expected outcome, code, alt text, HowTo-style structure.
- **Local and ecommerce**: current product feed (price, stock, attributes), complete business profile (hours, services, photos, answered Q&A), recent reviews with responses, service-area markup.

## 7. Off-site surfaces

- **Review platforms** (category-relevant ones): complete profiles in the same words as your About page; steady flow of real reviews; respond to reviews.
- **Analyst and roundup pages**: get listed accurately; supply data and customer references.
- **Communities and forums**: genuine participation by named people; never sockpuppets. Citation share from any single forum can collapse overnight; treat as one surface in a portfolio.
- **Wikipedia / Wikidata**: only if you meet notability; keep facts accurate via proper editing rules; never write your own promotional article.
- **YouTube**: engines read the text layer, not the footage. In order of leverage: transcript with answers spoken as complete sentences and key entities said aloud → corrected captions → question-shaped title → chapters titled by sub-question → description restating key points as bullets → pinned comment with the numbered summary and links → thumbnail for clicks. Ungate product demos.
- **LinkedIn**: cited heavily for professional queries but by surface and engine: one assistant moved from long-form articles to feed posts; others still cite articles and company pages; Gemini barely cites LinkedIn. Publish both posts and articles, keep the company page complete, front-load the target phrase (it becomes the URL slug), and check articles aren't served `noindex` to crawlers.
- **Podcasts**: transcripts and show notes get crawled; guest appearances become durable mentions.
- **Press**: check that syndicated release pages are actually indexed before paying.

## 8. Machine-readable files and agent readiness

The stack (complementary, not competing): `sitemap.xml` (which URLs exist) → `robots.txt` with explicit AI policy → `llms.txt` (signpost to the pages that matter) → `llms-full.txt` (whole-site content in one file) → `/pricing.md` (agent-comparable plans) → per-page JSON-LD → Markdown versions of pages.

Agent readiness audit:
- **Access**: core content in the initial HTML (most agents don't run JS); no bot challenge on discovery paths; real status codes, no soft 404s; stable canonicals.
- **Discovery**: explicit robots stance, valid sitemap, llms.txt, optional content-usage statements.
- **Parseability**: valid JSON-LD; a Markdown representation via `Accept: text/markdown` at the same URL (with `Vary: Accept`) or a `Link: <…md>; rel="alternate"; type="text/markdown"` header; one H1; headings that answer sub-questions.
- **Actionability (emerging)**: the 2-4 highest-intent actions (trial, demo, contact) work without JS-only flows, have labeled fields and return machine-readable confirmation; emerging standards let pages declare forms as callable tools with input schemas. Reuse existing validation, spam protection, consent and CRM routing; test that bad input is rejected.
- Experimental knowledge-bundle formats (a folder of cross-linked Markdown files with frontmatter) exist; no engine has confirmed using them. Skip unless llms.txt and schema are already maintained and the site allows custom paths. Generating one doubles as an orphan-page audit.

## 9. Positioning and consensus

- Models associate a brand with a category, a segment (SMB/mid-market/enterprise) and strengths/weaknesses; this moves slowly.
- Repositioning or rebrand: baseline prompts for both the old and new segment; warn that old-segment visibility may dip first; move off-site profiles, reviews and listings first, then stage the site rewrite; keep pages that still win old prompts until the new association shows up.
- Profile consistency: every directory, review, data and social profile states the same category, segment and differentiators. Cheapest high-leverage fix available.
- Aggregators' "cons": if a listed con reinforces a weakness models repeat, ask the publisher to use a different true con. Never ask for false claims.
- Head terms owned by incumbents: run both a solution page and a buyer's guide, amplify earned third-party proof (review grid placements, analyst mentions), occupy several result types (video, reviews, press).
- Never: invented awards, brand-run "independent" review sites, fake or incentivized-without-disclosure reviews (consumer protection rules on reviews apply).

## 10. Measurement rigor and attribution

- Track prompts like keywords; one core prompt per intent; 3-5 runs per engine in fresh sessions; report rate with n.
- Compare over months, not runs. 4/5 → 3/5 is noise; sustained 0/5 is signal.
- Record framing (favorable, neutral, hedged, against), not just presence.
- Most traffic influenced by AI recommendations arrives as branded search or direct (one 2026 journey study saw under ~10% as visible AI referrals). Use the triad: prompt tracking + self-reported attribution ("AI assistant" option with "what did you ask?") + sales-call notes. Watch branded search volume for unexplained lifts.
- Google provides no AI-specific reporting; use standard search performance data for its features, third-party tracking for the rest.
- AI referral sessions in analytics: create a channel group matching known assistant referrer domains.
