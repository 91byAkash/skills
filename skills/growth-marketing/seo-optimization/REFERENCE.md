# SEO Audit: Reference

## Contents
1. Technical checklist
2. On-page checklist and title patterns
3. Content quality and E-E-A-T
4. Traffic-drop triage
5. Rankings push (striking distance and low CTR) and new-page launch
6. International SEO
7. Migration runbook
8. Common issues by site type
9. Tools

---

## 1. Technical checklist

**robots.txt**
- Reachable at `/robots.txt`, returns 200 (a 5xx can make crawlers pause the whole site).
- No accidental `Disallow: /` or blocks on key sections, CSS, JS or images needed to render.
- Block only private/infinite spaces (`/admin/`, `/cart/`, internal search `?q=`, endless filter combinations).
- `Sitemap:` line with absolute URL.
- AI crawler policy is a separate decision (see ai-search-optimization).

**XML sitemaps**
- Only canonical, indexable, 200 URLs; no redirects, 404s, noindex or parameter duplicates.
- ≤ 50,000 URLs and ≤ 50 MB uncompressed per file; sitemap index for more; split by page type (products, categories, posts) to read indexing rates per type.
- `lastmod` only when content really changed; `changefreq`/`priority` are ignored by Google.
- Submitted in Google Search Console and Bing Webmaster Tools.

**Indexation and canonicals**
- Every indexable page has a self-referencing canonical (absolute URL, https, preferred host, consistent trailing slash).
- Variants (http, www/non-www, uppercase, trailing slash, `index.html`) 301 to the canonical in one hop.
- Paginated series: each page self-canonical; never canonical page 2+ to page 1.
- Parameters for tracking/sorting: canonical to the clean URL; filters with real demand can be indexable landing pages.
- Noindex + canonical to another URL = conflicting signals; pick one.
- Don't block a URL in robots.txt if you need search engines to see its noindex.
- Search Console statuses: "Discovered, not indexed" → crawl priority/internal links; "Crawled, not indexed" → quality or duplication; "Duplicate, Google chose different canonical" → consolidate or differentiate; "Soft 404" → thin/empty page or bad redirect.

**Redirects and status codes**
- Permanent moves: 301/308. Temporary: 302/307. Chains ≤ 1 hop; no loops.
- Removed content with no replacement: 404/410 (not a redirect to the homepage).
- Out-of-stock products: keep the page (200) with alternatives if returning; 301 to the closest category if discontinued forever.

**Site speed and Core Web Vitals** (field data, 75th percentile, mobile first)
| Metric | Good | Needs improvement | Poor |
|---|---|---|---|
| LCP | ≤ 2.5 s | 2.5-4 s | > 4 s |
| INP | ≤ 200 ms | 200-500 ms | > 500 ms |
| CLS | ≤ 0.1 | 0.1-0.25 | > 0.25 |
Common fixes: preload/prioritize the LCP image, serve modern formats sized to the viewport, cut render-blocking JS/CSS, reserve space for images/ads/embeds (CLS), break up long tasks and defer third-party scripts (INP), CDN and caching, font-display swap with preloaded fonts.

**Mobile**: responsive layout with `width=device-width`; same main content, links and structured data as desktop; 16 px base font; tap targets ≥ 48×48 px; no intrusive interstitials on entry.

**Security**: HTTPS sitewide, valid certificate, no mixed content, HTTP→HTTPS 301, HSTS.

**URLs**: lowercase, hyphens, readable, short (aim < 75 chars), reflect hierarchy, no session IDs, no dates in evergreen blog URLs, no IDs where a slug works.

**Crawl budget** (sites > ~10k URLs): control faceted navigation (only index facets with demand), paginate infinite scroll with real URLs, fix soft 404s and redirect chains, keep server fast, monitor crawl stats.

**JavaScript rendering**: main content, links (`<a href>`), titles, canonicals and structured data present in server HTML or reliably rendered; no content behind user interaction only; don't rely on hash URLs.

## 2. On-page checklist and title patterns

**Title tag**: start from the results page for the target query (format that wins, words searchers expect, the gap). Structure: `[primary query] + [reason to click] + [brand if it helps]`. Keep the key words in the first ~50 characters; unique per page; match the H1's topic; use a year/number/"free" only if the page delivers.

Starting shapes by page type (examples use a made-up invoicing brand; adapt, don't fill in blindly):
- Feature or product page: what it is, who it is for, then the brand: "Invoicing software for freelancers | Ledgerly".
- Pricing page: brand, the word "pricing", and what a searcher wants to learn: "Ledgerly pricing: plans from $9 a month".
- Head-to-head comparison: both names plus the difference that decides it: "Ledgerly vs Tallybook: which handles multi-currency better".
- Alternatives roundup or best-of list: a count, the competitor or category, the audience, and the year only if you refresh it every year.
- Task guide: start with "How to" and the task; add "without" and the obstacle when that is what people search.
- Definition: ask the question ("What is accrual accounting?") and add a short promise of the answer.
- Pillar guide: the topic plus who it serves ("…for first-time founders").
- Free template or calculator: lead with "Free", name the thing, put the file format in brackets.
- Error or problem page: quote the error, then promise its meaning and the fix.

Rewrite triggers (Google substitutes its own title): far too long, keyword-stuffed or repeated boilerplate ("| Brand | Brand Blog"), mismatched with H1/content, generic ("Home"). Fixes: tighten and align with the H1. Don't change URL slugs to chase a year.

Bulk audit output:
```markdown
| URL | Title now | Suggested title | Why |
|---|---|---|---|
| /features/recurring | Get Paid Faster | Recurring invoices for freelancers \| Ledgerly | Names the feature people search for; "get paid faster" matches no query |
```
Give 2-3 options for top revenue pages; one proposal for the long tail.

**Meta description**: ~150-160 characters (a lint proxy; snippets vary), unique, states the specific outcome, includes the query naturally, has a reason to click. Google often rewrites; still write them for priority pages.

**Headings**: one clear primary H1 (multiple H1s in valid HTML are not a failure by themselves, but one is cleaner); no skipped levels; headings describe sections, not styling.

**Body**: answer the query in the first two sentences; query and close variants used naturally in the first 100 words; covers sub-questions from "People also ask" and rivals' subheadings; original data, examples, visuals.

**Images**: descriptive file names, alt text describing the image (decorative images `alt=""`), width/height set, compressed WebP/AVIF, lazy-load below the fold only.

**Internal links**: descriptive anchors (not "click here"); roughly 5-10 contextual links per 1,000 words; link from strong pages to pages you want to rise; fix broken internal links; no hundreds of footer links.

**Keyword mapping**: one primary query (plus close variants) per URL; no two URLs targeting the same intent; maintain the map in [templates/keyword-map.md](templates/keyword-map.md).

## 3. Content quality and E-E-A-T

- **Experience**: first-hand use, original photos/screenshots, "we tested" with method, case data.
- **Expertise**: author pages with credentials; reviewed-by for medical/financial/legal topics.
- **Authoritativeness**: cited and linked by others in the field; consistent entity info.
- **Trust** (most important): accurate claims with sources, clear ownership, contact details, policies, secure checkout, honest reviews.
- Thin content: tag/category pages with no unique text, doorway pages, near-duplicate location or industry pages, auto-generated text with no added value. Fix by consolidating, enriching or removing (404/410 or noindex) rather than hiding.
- Freshness: update facts and screenshots; change the visible date only when content changed.
- Writing quality: cut filler openers and stock phrases ("in today's fast-paced world", "delve", "it's important to note") that signal low-effort generated text; see marketing-copy for the full pattern list.

## 4. Traffic-drop triage

1. **Confirm it's real**: compare analytics organic sessions with Search Console clicks; check tracking changes (consent banner, tag removed, GA property switch).
2. **Date it**: day of the drop vs deploys, migrations, CMS/plugin updates, robots/sitemap changes, known core/spam updates, seasonality (same period last year).
3. **Shape it**:
   - Sitewide, sudden → technical (robots, noindex, canonical, server errors, DNS/CDN), manual action, or migration.
   - One section/template → template change (canonicals, rendering, internal links removed from nav).
   - Gradual across content → quality/helpfulness update or competitors improving.
   - Impressions flat, clicks down → CTR loss: SERP features/AI answers, rewritten titles, rich result lost.
   - One country/device → hreflang, mobile rendering, local SERP changes.
4. **Prove the cause** with page-level before/after (indexing status, rendered HTML, positions per query).
5. **Fix, then monitor** weekly; recoveries from quality updates often wait for the next update cycle.

## 5. Rankings push and new-page launch

**Find candidates** (Search Console, last 28 days vs previous):
| Bucket | Filter | Fix |
|---|---|---|
| Striking distance | Avg position 8-20, meaningful impressions (often 100+/month) | Content + internal links |
| Weak CTR | Position 1-5, CTR well below your own pages at the same position | Title + meta only |
| Near the top | Position 4-7 on revenue queries | Content, links, snippet-friendly format |
Prioritize by business value, not impressions. Check cannibalization first.

**Diagnose against the top 3**: for each, name the concrete reason it beats you: intent match, a missing section, freshness, format (table/steps/tool), or links. If you can't name one, the gap is probably authority → links, not rewrites.

**Smallest change that closes the gap**: answer in the first two sentences; add the missing section (don't rewrite a ranking page); align title/H1 with the query if natural; add 3+ internal links from strong related pages with descriptive anchors; refresh stale facts. For weak CTR change only title/meta so the effect is attributable. Record baseline position/impressions/CTR, wait 3-4 weeks. Two rounds with no movement → stop editing; it's intent or authority.

**New page launch checklist**
- [ ] ≥ 3 internal links from relevant existing pages
- [ ] Unique title and meta matching the target query; one H1
- [ ] Self-referencing canonical; indexable; not blocked by robots
- [ ] In the XML sitemap
- [ ] Structured data where the type applies
- [ ] Main content in server HTML
- [ ] Connected to the conversion path
- [ ] Request indexing once; if not indexed after a few weeks, diagnose instead of resubmitting

## 6. International SEO

**Hreflang** (in HTML head, HTTP headers, or sitemap; if more than one method, they must agree; prefer sitemap for 10+ locales):
- Every page lists itself and all alternates (self-reference required).
- Reciprocal: A→B requires B→A or the pair is ignored.
- Codes: ISO 639-1 language + optional ISO 3166-1 alpha-2 region (`en`, `en-GB`, `es-MX`, `pt-BR`); `en-UK` is invalid.
- `x-default` points to the fallback (selector or default locale).
- Targets return 200, are indexable and self-canonical; canonical URL must be in the hreflang set.
- Large sites: sitemap alternates don't count toward the 50k URL limit but the 50 MB limit bites; plan ~2-5k URLs per file. Bing treats hreflang weakly; add `<html lang>` and content-language.
- Some frameworks' locale alternates omit the self-referencing entry; check generated output.

**Canonicals**: each locale self-canonical; never canonical French to English. Canonical beats hreflang when they conflict.

**URL structure**: subdirectories (`/de/`) recommended; subdomains or ccTLDs acceptable; `?lang=` parameters not recommended. Prefix all locales consistently. Never auto-redirect by IP or Accept-Language without a crawlable path (crawlers mostly come from US IPs without Accept-Language).

**Content**: translate main content, not just navigation; machine translation is allowed if reviewed and useful; don't create locale pages you can't make genuinely useful (thin locales can drag sitewide quality); localize currency, units, phone/address formats.

## 7. Migration runbook

**Before**: crawl the old site (all URLs + titles + canonicals + status); export top pages by traffic, conversions and backlinks; build a one-to-one redirect map (old → closest new equivalent; never mass-redirect to home); keep content, titles, meta, structured data and internal links at parity for top pages; staging blocked from indexing by authentication (not just robots).
**Launch day**: deploy redirects with the switch; remove staging blocks from production; submit new sitemaps and keep the old sitemap reachable briefly so crawlers see the redirects; spot-check top 50 URLs (200, title, canonical, schema, content); confirm analytics, conversion tracking and forms.
**After**: Search Console 404s and coverage daily for 2 weeks, then weekly; fix missing redirects; update internal links to new URLs; compare traffic by page vs the same period. A few weeks' dip is common; sustained page-specific losses mean a missing redirect or lost content.

## 8. Common issues by site type

- **SaaS**: thin feature pages, blog not linking to product pages, no comparison/alternative pages, no integration pages, glossary missing, docs on a subdomain with no links to marketing.
- **Ecommerce**: thin category pages (add intro, buying guidance, FAQs), duplicate manufacturer descriptions, faceted duplicates, missing Product/Offer markup, discontinued product handling.
- **Publisher/blog**: outdated posts, cannibalization, no topic clusters, weak internal links, missing author pages.
- **Local**: inconsistent name/address/phone, missing LocalBusiness markup, thin or duplicate location pages, incomplete business profile, few recent reviews.
- **Multilingual**: hreflang errors, cross-locale canonicals, partial translation, IP redirects.

## 9. Tools

Search Console and Bing Webmaster Tools (essential); PageSpeed Insights / Lighthouse / WebPageTest (speed); Rich Results Test and the schema.org validator (renders JavaScript); a desktop crawler with JS rendering for large sites; backlink tools for authority; `scripts/seo_page_check.py` for quick raw-HTML checks.
