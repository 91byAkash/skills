# Pricing reference

Contents: 1 models · 2 value metrics · 3 tiers and packaging · 4 freemium, trials, enterprise · 5 willingness-to-pay research · 6 price changes · 7 pricing psychology · 8 pricing-page teardown · 9 unit economics · 10 platform cost crossover.

## 1. Pricing models

| Model | How it works | Fits | Watch out for |
|---|---|---|---|
| Flat rate | One price, everything included | Simple single-persona tools, early stage | Leaves money on the table with large customers; no expansion path |
| Per seat | Price × users | Collaboration tools where each user gets value | Seat sharing; penalizes adoption; procurement pushback on large rollouts |
| Usage / metered | Pay per unit consumed (API calls, GB, minutes) | Infra, APIs, AI products where cost and value scale with use | Bill shock, unpredictable revenue; add caps, alerts, committed-use discounts |
| Tiered (good-better-best) | Packages by features + limits | Most SaaS with multiple segments | Too many tiers, unclear differences |
| Feature-based | Tiers differ mainly by capabilities | Products with clear advanced features | Gating core value; feature sprawl |
| Credits / prepaid | Buy a pool, spend across actions | AI/generation products with varied unit costs | Opaque value per credit; expiry resentment |
| Outcome / value-share | % of revenue, savings, or per successful outcome | Measurable results (payments, recovered revenue, leads) | Attribution disputes; revenue volatility |
| Freemium | Free tier + paid upgrades | Viral/network products, low marginal cost | Free users never converting; support cost |

Common hybrids: base platform fee + usage overage; tiers + per-seat inside each tier; tiers + paid add-ons (extra storage, premium support, SSO); credits bundled into tiers. Use a second dimension only when a single one clearly misprices a meaningful segment.

Rules of thumb: perceived value should be around 10× price; very low prices tend to bring higher churn and more support per dollar; customers who hunt for discounts tend to churn roughly twice as often as full-price customers (treat as directional).

## 2. Value metrics

| Product type | Candidate metrics | Usually best when |
|---|---|---|
| Collaboration | active users, workspaces | value scales with people involved |
| CRM / sales | contacts, seats, pipelines | contacts if marketing-led, seats if rep-led |
| Email / marketing | contacts, sends | contacts (predictable); sends for transactional |
| Analytics | events, tracked users, data volume | events with generous tiers |
| Storage / files | GB, files | GB |
| API / infra | requests, compute, bandwidth | requests with volume discounts |
| AI products | credits, generations, tokens, outcomes | credits mapped to plain-language units ("~200 images") |
| Ecommerce tools | orders, GMV, stores | orders or GMV bands |
| Support | agents, tickets, resolutions | agents; resolutions for AI-first |

Good metric checklist: grows with customer value; customer can predict their bill; easy to explain in one line; hard to game; you can meter it reliably; aligns expansion revenue with customer success.

## 3. Tiers and packaging

**Number of tiers**: 2 when segments are clearly two (individual vs team); 3 default; 4 when you need a free or enterprise anchor on top of three paid plans. Beyond 4, choice paralysis.

**Tier roles**
- Entry: removes barriers, proves value, natural limits that serious users hit.
- Middle (recommended): designed for the core customer; where you want most buyers; visually highlighted.
- Top: power users and larger teams; 2-3× middle; makes the middle look reasonable (anchor).
- Enterprise: custom, "from $X", sales-assisted.

**Persona packaging pattern**

| Persona | Needs | Likely tier | Differentiators |
|---|---|---|---|
| Solo / freelancer | do the job, low cost | entry | core features, limited volume |
| Small team | share, collaborate | middle | more seats/usage, integrations, roles |
| Growing company | scale, control | top | advanced features, automation, priority support |
| Enterprise | security, compliance, procurement | enterprise | SSO/SAML, audit logs, SLAs, DPA, custom terms, dedicated CSM |

**Differentiation levers**: usage limits (cleanest), feature gates (advanced, not core), support level, admin/security, integrations, data retention/history, branding removal, API access.

**Packaging from MaxDiff utility**: top ~20% of features → every tier (they're why people buy); 20-50% → differentiators for middle; 50-80% → top tier; bottom 20% → cut, add-on, or bury.

**Add-ons**: when a feature is valuable to a minority across all tiers (extra storage, premium support, a module). Keep to a handful.

**Tier table must show**: name, price (monthly and annual), who it's for (one line), 3-6 headline features/limits, CTA, recommended badge, full comparison table below.

## 4. Freemium, trials, enterprise

**Freemium works when**: viral or network effects, low marginal cost to serve, large addressable market, natural usage limits that growing users hit, product teaches its value without sales. Design: generous enough to form a habit, constrained on the dimension that grows with success (usage, collaborators, history, branding).

**Free trial works when**: value needs setup/data before it's visible, buyers are teams or committees, there's no cheap way to serve free users.

| Trial choice | Effect |
|---|---|
| No card required | Many more trials; trial-to-paid often ~15-25% |
| Card required | Far fewer trials (often half or less); trial-to-paid often ~40-60% |
| Length 7-14 days | Simple products with fast first value |
| Length 14-30 days | Complex setup, team rollout, integrations |
| Reverse trial | Full premium access for the trial, then drop to free tier instead of locking out; captures both freemium reach and premium exposure |
| Usage-based trial | Free until N units; good when time-limited trials expire before use |

Benchmarks vary widely by product and traffic quality; treat these as starting expectations, not targets.

**Enterprise tier** when any apply: deals > ~$10k ARR, security reviews/questionnaires, SSO/SCIM, audit logs, data residency, custom contracts/MSA/DPA, SLAs, invoicing/PO, dedicated onboarding. Show "from $X" or "starts at" when you can; it pre-qualifies.

## 5. Willingness-to-pay research

**Van Westendorp price sensitivity meter** (4 questions, asked after describing the product concretely):
1. At what price would this be so cheap you'd doubt its quality? (too cheap)
2. At what price would it be a bargain, a great buy? (cheap)
3. At what price would it start to feel expensive, but you'd still consider it? (expensive)
4. At what price would it be too expensive to consider? (too expensive)

Analysis: plot cumulative curves (too cheap and cheap falling with price; expensive and too expensive rising). Intersections:
- PMC (point of marginal cheapness): too cheap × expensive
- OPP (optimal price point): too cheap × too expensive
- IDP (indifference price point): cheap × expensive
- PME (point of marginal expensiveness): cheap × too expensive

Acceptable range PMC-PME; most products price between OPP and IDP, premium brands toward PME. Sample 100-300 per segment; drop illogical answers (out-of-order); segment results (they differ more than you expect). `scripts/pricing_calc.py vw --csv answers.csv`.

**MaxDiff** (feature value): 8-15 features, shown in sets of 4-5, respondent picks most and least valuable; repeat so each feature appears 3+ times. Output: relative utility scores → packaging (see §3).

**Gabor-Granger** (demand at price points): "Would you buy at $X?" with price varied up/down; produces a demand curve and revenue-maximizing price. Good for a single product, weaker for tiers.

**Conjoint** (trade-offs between features and price): most rigorous for packaging; needs larger samples and tooling.

**Cheaper signals**: sales-call objection logs, discount request rate, win/loss notes, close rate by price band, competitor price moves, upgrade/downgrade flow, "too expensive" in cancel reasons (often really "not enough value").

Survey caveats: stated WTP overstates real behavior; anchor respondents with a real description; never treat survey output as the final number; validate with a live test on new traffic.

## 6. Price changes

**Signals you're under-priced**: little price resistance; "that's cheap" comments; trial-to-paid or close rate very high (> ~40%); monthly churn very low (< ~3%) with strong engagement; competitors charge much more for less; you've shipped substantial value since last change; customers expand quickly.

**Signals of over-pricing or bad packaging**: long cycles stuck at price, high discount rates, low trial-to-paid with good activation, churn citing price from active users, heavy downgrades.

**Rollout options**
- New customers only (lowest risk; test first).
- Existing customers at renewal, with notice.
- Staggered waves: 5-10% of base, observe a billing cycle (churn, tickets, downgrades), then expand.
- Grandfathering: time-limited (6-12 months) beats forever. A legacy base paying $50 next to new customers at $250 is a $2,400/year gap per account that compounds; decide deliberately.

**Communication**: 30-90 days' notice (longer for large jumps or annual contracts); explain what's improved and why; show the new price and effective date plainly; offer a soft landing (lock current price by prepaying annual, grace period, credit, or a lighter plan); give a contact for questions; prepare support macros and a save path. Draft with [templates/price-change-email.md](templates/price-change-email.md).

**Measure**: churn and downgrades by cohort for 2-3 cycles, net revenue retention, support volume and sentiment, new-customer conversion and revenue per visitor.

## 7. Pricing psychology

- Anchoring: show the top tier or the annual total first; strike the monthly equivalent next to annual.
- Decoy: a tier that's close in price to the target but clearly worse makes the target look better; use sparingly and honestly.
- Center-stage effect: buyers drift to the middle of three options; put the plan you want chosen there.
- Charm vs round: $49/$99 signals value; round numbers ($50/$100/$500) signal premium/simplicity; pick one style.
- Rule of 100: under $100 express discounts as %, over $100 as absolute amount.
- Price per unit framing: "$1.60 per active user" or "less than one hour of a contractor"; frame against the alternative's cost.
- Annual discounts: 15-20% (two months free ≈ 16.7%) is standard; show the saving in currency.
- Pain of paying: annual prepay reduces repeated pain; usage pricing increases it (caps help).
- Defaults: preselect annual only if you're clear about it; dark defaults erode trust.

## 8. Pricing-page teardown (10 dimensions, score 0-2 each)

Human (6):
1. Clarity: can a visitor say what each plan costs and includes within 10 seconds?
2. Plan-fit: does each tier say who it's for; is one recommended?
3. Value framing: outcomes and limits stated in customer terms; value metric explained.
4. Objection handling: FAQ on billing, limits, overages, cancellation, refunds, data, security.
5. Proof and risk reversal: logos/testimonials near plans; guarantee/trial terms near CTAs.
6. Friction: CTA copy matches action; monthly/annual toggle; currency; no forced "contact us" for self-serve tiers.

Machine readability (4):
7. Prices and limits as HTML text, not images or client-only rendering.
8. Paste test: copy the page text into a plain doc; is it still understandable (tier names, prices, limits in order)?
9. Structured data: Product/Offer or SoftwareApplication markup with price and currency.
10. A plain-text/Markdown pricing file (`/pricing.md`) and consistent pricing across docs, comparisons and third-party listings.

Scoring: 16-20 strong; 10-15 fix the zeros first; < 10 rebuild. Typical failures: all-features table without a recommendation, prices behind "contact sales", usage units undefined ("credits"), toggle defaulting to annual with monthly-looking prices, FAQ missing cancellation.

Report format: score table → top 5 fixes (impact × effort) → rewritten tier blurbs → what to test.

## 9. Unit economics benchmarks

| Metric | Formula | Healthy (directional) |
|---|---|---|
| ARPA | MRR ÷ paying accounts | rising over time |
| Gross margin | (revenue − COGS) ÷ revenue | software 70-85% |
| LTV | ARPA × gross margin ÷ monthly churn | cap lifetime at 3-5 years |
| LTV:CAC | LTV ÷ fully loaded CAC | ≥ 3 (≫ 5 may mean under-investing) |
| CAC payback | CAC ÷ (ARPA × gross margin) | SMB ≤ 12 mo, mid-market ≤ 18, enterprise ≤ 24 |
| Net revenue retention | (start MRR + expansion − contraction − churn) ÷ start MRR | SMB 90-100%+, mid-market 100-110%, enterprise 110%+ |
| Discount rate | avg discount on closed deals | < ~15%; rising = packaging or value issue |

`scripts/pricing_calc.py unit --arpa 79 --margin 0.8 --churn 0.03 --cac 450`.

## 10. Funnel/landing platform cost crossover

When picking a platform for funnels, landing pages or checkout, don't compare list prices or feature grids; compute the cost curve for the specific case.

Inputs that flip the answer: monthly GMV through the funnel (the biggest factor), number of funnels/clients/workspaces, contact list size and growth, where catalog and orders must live (existing store?), who maintains it (no technical owner → hosted), and exit tolerance (does the business survive if pages go dark 30 days after cancelling?).

Cost formulas:
- Hosted flat fee: plan fee + contact overage + transaction fees
- %-of-revenue: base fee + rate × GMV
- Self-hosted: hosting + database + maintenance hours × hourly cost (+ PCI and payment setup)
- CMS plugin: licence + hosting + your time
- Store-native app: app fee (often GMV-tiered) + store platform fee

Crossover GMV = (flat fee − base fee) ÷ rate. Example: $49 + 2% vs $199 flat → crossover at $7,500/month; above it the % plan costs more, with no ceiling. `scripts/pricing_calc.py crossover --flat 199 --base 49 --rate 0.02`.

Also price: email sending, per-transaction platform fees, and migration labor when leaving (rebuilding pages, domains, tracking).

Matching: solo non-technical and low GMV → hosted all-in-one; existing CMS store → plugin that reuses the store's checkout; existing hosted store wanting upsells → app inside that store's checkout; high GMV with a developer → self-hosted; agency → no per-workspace fees and a licence that permits client work (read the licence text); data ownership needs → self-hosted; one page, one product → static page + hosted checkout link.

If "open source" is a selling point, verify: OSI-approved licence vs source-available with commercial limits; the repository exists and contains the product; tagged releases exist; it can take payments without a paid key. Always state the trade-off: self-hosting means you own upgrades, backups, uptime, PCI scope and support; hosted means cost grows with the business, pages stop when payment stops, and data access is on their terms.
