---
name: ai-search-optimization
description: "Get a brand cited and recommended in AI answers (Google AI Overviews/AI Mode, ChatGPT, Claude, Perplexity), aka AEO/GEO. Use when asked how to show up in AI answers, why assistants cite competitors, whether to allow GPTBot or other AI crawlers, what llms.txt is, or how to measure AI visibility. Not for classic SEO audits (use seo-optimization)."
license: MIT
metadata:
  category: "growth-marketing"
  version: "3.0.0"
---

# AI Search Optimization

Scope: prompt-based visibility audit with repeat runs, crawler access by purpose (search vs user-fetch vs training), extractable answer blocks, authority and freshness, third-party consensus, llms.txt / pricing.md / Markdown versions, agent readiness, monitoring. Topic planning lives in content-strategy.

AI answers are built by retrieving pages, extracting passages, and choosing which brands to name. Win each stage separately: be **reachable**, be **extractable**, be **trusted**, and be **corroborated** by the rest of the web.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `domain` | required | ask | `example.com` |
| `category` | required | from product context | "expense management software for SMBs" |
| `priority_prompts` | optional | draft 15-25 from the buyer journey | "best expense tool for a 20-person agency" |
| `competitors` | optional | top 3-5 named in AI answers | Brand A, Brand B |
| `engines` | optional | AI Overviews/AI Mode, ChatGPT search, Perplexity, Gemini, Copilot | add others the audience uses |
| `runs_per_prompt` | optional | 3 (5 for decisions) | 5 |
| `brand_stage` | optional | infer: leader vs emerging | emerging (not on analyst/review shortlists) |
| `training_policy` | optional | ask; default allow search crawlers, decide training separately | block training crawlers, allow search |
| `priority_pages` | optional | homepage, pricing, top 5 product/solution pages, top 10 organic posts | `/pricing`, `/vs/brand-a` |

Read `.agents/product-marketing.md` (or the context file from customer-research) first if it exists.

## Output

An **AI Visibility Report** built from [templates/visibility-report.md](templates/visibility-report.md):
1. Prompt scorecard: each prompt × engine with cited / mentioned / recommended rates over n runs, competitors named, and the sources cited.
2. Diagnosis per gap, labeled **technical** (can't reach/parse), **comprehension** (described wrongly or vaguely), or **trust** (understood but not chosen).
3. Access findings: robots and firewall behavior per crawler purpose, rendering, machine-readable files.
4. Page fixes: for each priority page, the failed extractability checks and rewritten answer blocks.
5. Off-site plan: the third-party sources engines cite for your prompts, ranked, with an owner.
6. Monitoring setup: tracking sheet ([templates/prompt-tracker.csv](templates/prompt-tracker.csv)), cadence, and the attribution field.

## Supporting files

- [REFERENCE.md](REFERENCE.md): how each engine picks sources, crawler tokens by purpose and a robots policy template, research-backed authority levers, the visibility ladder, format volatility, content-type playbooks, agent readiness, YouTube/LinkedIn/podcast text layers, measurement rigor. Read before giving platform-specific advice.
- [templates/answer-blocks.md](templates/answer-blocks.md): fill-in patterns (definition, steps, comparison, pros/cons, FAQ, stat, quote, evidence sandwich). Use when rewriting pages.
- [templates/llms.txt](templates/llms.txt) and [templates/pricing.md](templates/pricing.md): machine-readable files to publish at the site root.
- [templates/prompt-tracker.csv](templates/prompt-tracker.csv): the monitoring sheet.
- [scripts/ai_access_check.py](scripts/ai_access_check.py): checks robots rules per crawler, llms.txt / llms-full.txt / pricing.md / sitemap presence, how much text is in the raw HTML (no JS), JSON-LD types and Markdown negotiation. Run `python3 scripts/ai_access_check.py https://example.com /pricing /blog/post`.

## Steps

1. **Build the prompt set.** 15-25 prompts across stages, written the way people type into a chat box:
   - problem-aware: "how do I stop employees losing receipts"
   - solution-aware: "best expense software for a 20-person agency", "what is spend management"
   - product-aware: "Brand vs Competitor", "is Brand good for agencies"
   - decision: "Brand pricing", "does Brand integrate with [accounting tool]"
   Collapse wording variants into one prompt per intent. Drop prompts that would not change revenue (generic glossary questions). If a chat assistant exposes its background searches, record the fan-out queries; they reveal sub-topics and which third-party domains get searched.
2. **Run the baseline.** Each prompt × engine × `runs_per_prompt`, fresh session, logged-out where possible. Record per run: brand cited (link)? mentioned (named)? recommended (on the shortlist)? framing (favorable / neutral / hedged / against)? competitors named, cited URLs. Report rates with n ("mentioned 2/5"). One run is an anecdote.
3. **Check access** (`scripts/ai_access_check.py`):
   - If search-discovery crawlers are blocked in robots or by the firewall/CDN → fix first; nothing else matters until then.
   - If raw HTML has little text (the script flags pages under 200 words without JavaScript, or compare with what the browser shows) → server-render or pre-render the main content.
   - Decide training crawlers separately per `training_policy`; blocking training does not by itself block citations.
   - Confirm the site is indexed in both Google and Bing (several assistants use Bing-backed indexes); submit sitemaps to both; use IndexNow for fast updates where supported.
4. **Diagnose each gap** with the label rule:
   - Not cited and pages not retrieved → **technical** (access, indexing, rendering) or coverage (no page answers the prompt).
   - Mentioned but facts wrong or vague → **comprehension**: the page that should state the fact doesn't say it plainly → fix that page.
   - Cited but not recommended, or competitors recommended from your own guide → **trust**: web consensus doesn't support you yet → off-site plan (step 7).
5. **Fix extractability on priority pages.** Score each page with the checklist in the report template. Rules:
   - Lead each section with a direct, self-contained answer of 40-60 words under a heading phrased like the question.
   - Use the right block for the intent (definition, numbered steps, comparison table, pros/cons, FAQ) from [templates/answer-blocks.md](templates/answer-blocks.md).
   - State specifics: numbers with units and dates, named sources, prices, limits, integrations, implementation time.
   - One idea per paragraph; tables for comparisons; no key facts only in images, PDFs behind forms, tabs that need JS, or video without transcript.
   - Write for people with normal headings and paragraphs; do not create separate "AI versions" or chop pages into fragments (scaled-content risk in Google's systems).
6. **Add authority and freshness.** Named author with credentials, visible "Updated [date]" that reflects real edits, cited primary sources, original data (surveys, benchmarks, usage stats), expert quotes with name and role. Structured data per page type (Organization, Article with dates, Product/Offer, SoftwareApplication, HowTo, FAQPage where answers are real), coordinated with seo-optimization. Refresh competitive pages at least quarterly, monthly for fast-moving categories.
7. **Build consensus off-site.** From step 2's cited URLs, list the third-party sources engines rely on for your prompts (review sites, analyst pages, community threads, comparison articles, videos, LinkedIn, Wikipedia/Wikidata, directories, podcasts). Then:
   - Make every profile say the same category, segment and differentiators as your About page.
   - Pursue accurate inclusion in cited roundups and comparisons (outreach, PR, partnerships).
   - Earn reviews from real customers on the platforms that get cited.
   - Participate genuinely in communities; never astroturf or fabricate reviews/awards.
   - If `brand_stage` = emerging → weight effort toward off-site corroboration over publishing more self-ranked "best X" lists; if leader → publish the definitive buyer's guide for the category.
8. **Publish machine-readable files.** `/llms.txt` (summary + key links), `/pricing.md` (plans, prices, limits in plain text), optional `/llms-full.txt`, Markdown versions of key pages via `Accept: text/markdown` negotiation or a `Link` header. Google's AI features don't need these; other assistants and buying agents can use them. If the site has < 10 pages or a closed platform → skip optional bundles.
9. **Make high-intent actions agent-usable.** Pricing, specs, contact and signup visible in HTML; semantic forms with labels; no JS-only flows for demo/trial; clean accessibility tree.
10. **Set up monitoring.** Re-run the prompt set monthly (weekly for launches) with the same n; track the ladder (cited → mentioned → recommended) and framing; add "AI assistant" with "what did you ask?" to the signup/demo "How did you hear about us?" field; watch branded search volume and AI referral sessions. Treat a 4/5 → 3/5 move as noise and a sustained drop to 0/5 as signal.

## Checkpoints

- After step 2: share the baseline scorecard before recommending fixes; it is the yardstick.
- After step 3: crawler policy confirmed with the user (especially training opt-outs).
- After step 4: every gap has a label; fixes map to labels.
- Before step 7 outreach: no tactic involves fake reviews, owned "independent" review sites, or undisclosed paid mentions.

## Worked example

**Context**: B2B expense tool, emerging brand, 3 competitors.
- Baseline (20 prompts × 4 engines × 3 runs): cited 9%, mentioned 14%, recommended 3%. Competitor A recommended 61%.
- Access check: firewall returned 403 to one assistant's search crawler; pricing rendered by JS with 40 words in raw HTML. → technical fixes, week 1.
- Comprehension: two assistants said "no mobile app" (false). Product page buried the app in a carousel → added a plain sentence plus FAQ "Does Brand have a mobile app?" with store links.
- Trust: for "best expense software for agencies", engines cited the brand's own listicle but recommended A and B. Cited third-party sources: two review platforms, one analyst roundup, one forum thread. → review drive targeting agencies, profile text aligned to "expense management for agencies and studios", pitch to the roundup author with a customer case.
- 90 days later (same prompts, n=3): cited 27%, mentioned 31%, recommended 12%; "no mobile app" claim gone; demo-form "AI assistant" answers rose from 2% to 9%.

## Pitfalls

- Reporting single-run screenshots as "we rank #1 in ChatGPT".
- Blanket-blocking every AI user agent (or letting a CDN do it by default) and wondering why citations vanished.
- Writing a separate keyword-stuffed "AI page"; stuffing measurably lowers visibility in generative engines.
- Fake freshness (changing the date without changing content).
- Gating the most authoritative content (research, demos, pricing) behind forms.
- Betting on one third-party surface; citation mixes shift overnight with retrieval updates.
- Quoting vendor statistics as stable facts; every share-of-citation number is a dated snapshot.
- Assuming citation equals recommendation; a self-ranked listicle can hand the shortlist to competitors.

## Related skills

seo-optimization (indexing, schema, site architecture), content-strategy (topic clusters and formats), marketing-copy (answer blocks that still sell), customer-research (category language and review mining), launch-plan and marketing-plan (directories and PR that create corroboration), analytics-and-experiments (self-reported attribution, referral tracking).

## Done when

- [ ] Baseline scorecard exists with rates and n per prompt × engine, plus competitors and cited sources.
- [ ] Crawler access verified per purpose (robots and firewall), and the training policy is an explicit decision.
- [ ] Each gap is labeled technical / comprehension / trust with a mapped fix and owner.
- [ ] Priority pages pass the extractability checklist, with rewritten answer blocks delivered.
- [ ] Off-site source list ranked from real citations, with profile-consistency edits listed.
- [ ] llms.txt and pricing.md drafted (or skipped with a reason).
- [ ] Monthly monitoring cadence and the self-reported attribution option are in place.
