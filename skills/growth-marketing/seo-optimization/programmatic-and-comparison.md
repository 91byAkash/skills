# Programmatic Pages and Competitor Comparison Pages

## Part A: Programmatic SEO

### Principles
1. **Unique value per page.** Each page must answer its query with information specific to that page; swapping one variable into boilerplate is a doorway page.
2. **Data defensibility** (strongest first): proprietary (you created it) → product-derived (aggregated usage data) → user-generated (community) → licensed/exclusive → public (anyone can copy; weakest).
3. **Subfolders on the main domain** (`/templates/resume/`) rather than a separate subdomain, unless you can link the subdomain strongly.
4. **Intent match.** Look at what ranks for 5 sample queries in the pattern; if results are tools and you plan articles, stop.
5. **Quality over quantity.** 100 strong pages beat 10,000 thin ones; thin sets can drag the whole site.

### The 12 playbooks
| Playbook | Query pattern | Example | Value bar (what each page must have) | URL |
|---|---|---|---|---|
| Templates | "[type] template" | invoice template | Actually usable template, variations, easy copy/download | `/templates/{type}` |
| Curation | "best [category]" | best website builders | Real criteria, testing/expertise, dated updates, not pay-to-rank | `/best/{category}` |
| Conversions | "[X] to [Y]" | 100 kg to lbs | Working fast tool, accurate data, related conversions | `/convert/{x}-to-{y}` |
| Comparisons | "[X] vs [Y]" | notion vs coda | Honest analysis, real feature data, recommendation by use case | `/compare/{x}-vs-{y}` |
| Examples | "[type] examples" | SaaS landing page examples | Real examples with screenshots, categorization, why each works | `/examples/{type}` |
| Locations | "[service] in [city]" | coworking in san diego | Real local data (providers, prices, regulations), not a swapped city name | `/{service}/{city}` |
| Personas | "[product] for [audience]" | CRM for real estate | Segment-specific workflows, features, proof and FAQs | `/for/{audience}` |
| Integrations | "[A] [B] integration" | slack asana integration | Real integration, setup steps, use cases | `/integrations/{tool}` |
| Glossary | "what is [term]" | what is churn rate | Clear definition, example, formula, related terms linked | `/glossary/{term}` |
| Translations | same content, other languages | qué es CRM | Native-reviewed translation, localized examples, hreflang | `/{lang}/{page}` |
| Directory | "[category] tools" | AI writing tools | Comprehensive, filterable, maintained listings | `/tools/{category}` |
| Profiles | "[entity]" | company or person facts | Accurate structured facts, sources, freshness | `/{entity-type}/{slug}` |

Pick by asset: proprietary data → directories/profiles; integrations → integration pages; design/creative product → templates/examples; several segments → personas; local footprint → locations; utility → conversions; expertise → glossary/curation; crowded market → comparisons. Layer playbooks when demand exists ("best coworking in San Diego").

### Build steps
1. **Pattern research**: define the repeating structure and variables; count combinations; pull volume for a sample; check distribution (a few heads + long tail) and trend.
2. **Data**: list the fields each page needs, the source for each, refresh frequency, and who owns updates.
3. **Template design**: H1 with the target query; unique intro generated from data (not one sentence with a swapped noun); data-driven sections with conditional blocks (show a section only when data exists); unique insight per page (comparisons, stats, rankings computed from data); related-page links; intent-appropriate CTA; FAQ from real questions.
4. **Linking**: hub page per pattern (listing/filtering all spokes); spokes link back to the hub and to 3-5 related spokes; breadcrumbs; separate XML sitemap per page type.
5. **Indexation gates**: publish/index only pages that pass a data threshold (e.g., ≥ N listings, ≥ M unique data points); noindex or don't generate thin combinations; roll out in batches (e.g., 50 → 500 → all) and watch the indexing rate per batch. If a batch indexes poorly (< ~50% after 4-6 weeks) → improve the template before expanding.
6. **Platform**: must handle page count, data refresh, server-rendered HTML, conditional sections and per-page indexation control. Prefer the existing CMS; otherwise serve on a subpath.

### Pre-launch checklist
- [ ] Each sample page offers unique, useful information for its query
- [ ] Unique titles/meta generated from data; one H1; logical headings
- [ ] Structured data generated from the same data
- [ ] Fast pages, server-rendered
- [ ] Hub, breadcrumbs, related links; no orphans
- [ ] Sitemap for the set; indexation gates in place
- [ ] Monitoring: indexing rate, impressions per page, conversions per page

Post-launch: watch "Crawled, not indexed" share, impressions per page after 8-12 weeks, and prune/merge pages with zero impressions after 6 months.

## Part B: Competitor comparison and alternatives pages

### Formats
| Format | Intent | URL | Structure |
|---|---|---|---|
| [Competitor] alternative (singular) | Ready to switch from one product | `/alternatives/{competitor}` | Why people leave (validate the pain) → you as the alternative → detailed comparison → who should switch and who shouldn't → migration path → switcher proof → CTA |
| [Competitor] alternatives (plural) | Researching options | `/alternatives/{competitor}-alternatives` | Common pains → criteria to judge alternatives → 4-7 real options (you included, honestly placed) → summary table → each option in detail → recommendation by use case → CTA |
| You vs [Competitor] | Direct comparison | `/vs/{competitor}` | TL;DR (2-3 sentences) → at-a-glance table → detail by category (features, pricing, support, ease of use, integrations) → who you're best for → who they're best for → switcher quotes → migration support → CTA |
| [A] vs [B] (two competitors) | Comparing two others | `/compare/{a}-vs-{b}` | Overview of both → comparison by category → who each fits → the third option (you) → three-way table → CTA |

Keyword targets: "[competitor] alternative(s)", "alternative to [competitor]", "switch from [competitor]", "[you] vs [competitor]" and reverse order, "[a] vs [b]".

### Essential sections
- **TL;DR** for scanners.
- **Paragraph comparisons** per dimension: how each handles it, when the difference matters.
- **Feature comparison** per category: strengths and limitations for both, bottom line.
- **Pricing comparison**: tier by tier, what's included, hidden costs (seats, add-ons, overages, onboarding fees), and total cost for a sample team (e.g., 10 users, annual).
- **Support comparison**: docs, channels, response SLA, onboarding, success manager tier.
- **Who should choose each**: specific use cases, team types, budgets.
- **Migration**: what transfers, what needs reconfiguring, import tools, help offered, time required, switcher quote.
- Tables organized by category with notes, not just checkmarks.

### Evidence discipline (every page must survive the competitor reading it)
- "Not observed" ≠ "doesn't have". Write "not listed on their pricing page (as of Mar 2026)" unless docs or a trial confirm absence.
- Date every competitor fact; re-verify before republishing.
- One visit is a snapshot; claims about history need dated sources (changelog, archives).
- State what changed, not why (no guessed motives).
- Separate their facts, your interpretation, and your recommendation.

### Centralized competitor data
Keep one data file per competitor (see [templates/competitor-data.md](templates/competitor-data.md)) and generate or update every page and sales asset from it, so a price change is fixed once.

### Research process per competitor
1. Sign up/trial; document features, UX, limits.
2. Pricing: tiers, inclusions, hidden costs, date checked.
3. Review mining on major review sites: top 5 praise themes, top 5 complaint themes, with counts.
4. Talk to customers who switched (both directions).
5. Their positioning, their own comparison pages, changelog.
Update quarterly (pricing/features), when a customer reports a change, and fully once a year.

### Claim audit (for existing pages, battle cards, decks)
1. List each competitor claim with asset and location.
2. Re-verify against current site/docs/changelog; record check date (if you can't browse, mark "unchecked").
3. Mark: **Current** (true, source/date updated) · **Changed** (now wrong; note what's true) · **Unverifiable** (soften to "not listed (as of date)" or remove) · **Overclaimed** (no source; rewrite or remove).
4. Fix public pages first, then rep talk tracks, then internal docs.
5. Report: assets audited, claims checked, counts by status, fix list with replacement wording.

### Linking and markup
Hub pages for alternatives and comparisons, linked from the footer; feature pages link to relevant comparisons; comparison pages link to each other. Mark up FAQs honestly; no fake review stars.

### AI-answer expectation
These pages often earn citations in AI answers, but whether assistants recommend you depends on off-site consensus; for emerging brands, a self-ranked list can surface competitors instead (see ai-search-optimization).
