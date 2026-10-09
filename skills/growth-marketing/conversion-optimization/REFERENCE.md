# Conversion Optimization: Reference

## Contents
1. Page analysis by type
2. Landing / sales page audit (paid traffic)
3. Forms
4. Signup and registration
5. Onboarding and activation
6. Popups, slide-ins, banners
7. Paywalls and upgrade prompts
8. Checkout, order bumps, post-purchase upsells
9. Funnel shapes, page specs, benchmarks
10. Research methods for finding "why"

---

## 1. Page analysis by type

Seven dimensions in impact order: value-proposition clarity → headline → CTA (placement, copy, hierarchy) → visual hierarchy/scannability → trust and proof → objection handling → friction.

Headline patterns that work: outcome without pain ("Get [outcome] without [pain]"), specificity (numbers, timeframes), proof-led ("Join 10,000+ teams who…"). Weak CTAs: Submit, Sign up, Learn more. Strong: Start free trial, Get my report, See pricing, Book a 20-min demo.

| Page | What must be true |
|---|---|
| Homepage | Cold visitor understands category, audience and outcome; one fast path to the main conversion; secondary path for researchers (tour, pricing, case studies) |
| Landing page | Message match with its traffic; one CTA; nav removed or minimal; complete argument on one page (problem → solution → proof → objections → CTA) |
| Pricing | Plans comparable at a glance; recommended plan marked; "which plan is right for me?" answered (who each is for, toggle effects, FAQ on billing, limits, cancellation); annual savings shown honestly |
| Feature page | Feature → benefit → use case → proof → path to try |
| Blog post | Contextual CTA matched to the topic (template, tool, trial) inline at natural break points plus end-of-post; not a generic newsletter box only |
| Demo request | Short form, what happens next (who calls, when, how long), calendar booking on the confirmation, routing by size |

## 2. Landing / sales page audit (paid traffic)

Inputs in priority order, and what each unlocks: URL (rendered DOM) → traffic source + sample ad (message match) → 14-30 days of sessions and conversions (real vs noise) → step drop-offs (which step to audit) → device split (paid social is commonly 70-90% mobile).

Checks in revenue-impact order:
- **A. Message match**: headline repeats the ad's promise in its words; page delivers the specific offer (not a homepage version); offer visible without scrolling at 390×844.
- **B. Mobile first viewport**: one promise, one CTA (count competing primaries); CTA reachable without scrolling past a hero; something meaningful painted by ~2.5 s.
- **C. Offer clarity**: what, for whom, cost, what happens on click; price shown unless high-ticket/call-booking; risk reversal (guarantee, trial, cancel anytime, shipping/returns).
- **D. Form friction**: field count, each justified now vs after payment; checkout on the same page or one click away; payment methods and wallets visible; inline validation.
- **E. Trust at payment**: guarantee, secure-payment mark, real named reviews, return policy next to the button; anonymous filler testimonials hurt.
- **F. After the button**: upsell/bump/thank-you with instructions rather than a dead end; confirmation sets delivery expectations (prevents refunds and chargebacks).
- **G. Measurement**: conversion event fires; click id carried to the order; server-side purchase reporting.

Report rules: no lift percentages; ≤ 7 "ship now" items; if volume is low (sessions < ~1,000 or conversions < ~30), rank by friction.

## 3. Forms

Field cost (rule of thumb vs a 3-field baseline): 4-6 fields ≈ 10-25% fewer completions; 7+ ≈ 25-50%+ fewer. For each field: needed before you can help? obtainable another way (enrichment, email domain)? askable later?

| Field | Rules |
|---|---|
| Email | One field, no confirm field, inline format check, typo suggestion (gmial → gmail), `type="email"` |
| Name | Single "Full name" unless split is used immediately; test |
| Phone | Optional unless calling/SMS is the service; say why if required; auto-format, country code |
| Company | Infer from email domain or enrich after submit; autosuggest |
| Role / size | Dropdown if used for routing; otherwise defer |
| Message | Optional, expands on focus |
| Selects | Radio buttons if < 5 options; searchable if many; "Other" with text |

Layout: single column; easy fields first, sensitive last; visible labels above fields (placeholders are examples, not labels); 44-48 px tap targets; mobile keyboards per field type; autofill attributes.

Multi-step when > 5-6 fields, distinct sections, or conditional paths: progress indicator, one topic per step, easy → sensitive, back navigation, save progress, required/optional marked. Progressive commitment: email → name/company → qualifying questions → preferences.

Errors: validate on blur (not every keystroke); specific messages with fix ("Enter an email like name@company.com"); next to the field; focus first error on submit; never clear inputs.

Submit button: first-person, outcome copy ("Send me the guide", "Get my quote"); state what happens next under it ("We'll reply within 1 business day"); privacy line near email field.

Measure: form start rate, completion rate, field-level drop-off, time to complete, error rate per field, mobile vs desktop.

## 4. Signup and registration

- Essential: email (or phone) + password, or passwordless (magic link / social). Usually deferrable: company, role, team size, phone, address.
- Show value before commitment where possible (try before account, demo data, calculator results before email).
- Social auth prominent: B2C Google/Apple; B2B Google/work-account SSO.
- Password: show/hide toggle, requirements shown up front and checked live, allow paste, strength meter over rigid rules.
- Single-step when ≤ 3 fields or high intent; multi-step for B2B segmentation: email → password+name → optional customization.
- Trust at form: "No credit card required" (if true), trial length, privacy line, one testimonial.
- Post-submit: clear success state and one next step; delay email verification until needed; magic link alternative; let users explore while unverified; resend + change-email options.
- Mobile: correct keyboard types, autofill, sticky CTA, real-device testing.

## 5. Onboarding and activation

**Activation**: the earliest action that best predicts retention (compare retained vs churned cohorts). Examples: project tool = create project + invite teammate; analytics = install tracking + see first report; design tool = create + export/share; marketplace = first transaction. Judge onboarding by activation rate, time-to-activation, and 30/90-day retention, not signups.

**Activation models** (market decides, not preference):
| Model | Notes |
|---|---|
| Freemium | Free tier must hook, then limit; generous free that satisfies kills upgrades |
| Free trial (3/7/14/30 days) | Shorter = urgency, needs fast time-to-value. Card required up front typically cuts signups 50-70% but converts 2-3× better |
| Paid trial (e.g., $7-10 for 7 days) | Filters tire-kickers, pre-collects payment |
| Money-back guarantee | Full price up front; product must prove value inside the window |
| Consultation / white-glove | Human-gated access for complex or high-price products |

**Minimum path to value**: inventory every screen, field, click, permission and empty state between signup and the value moment → remove/defer/pre-fill/skip anything not required now → rebuild value-first and measure. Context: 40-60% of trial signups often never return after session one, and most trial abandonment happens on day one, so session one must reach value.

**Psychology**: endowed progress (start checklist partly complete; one pre-completed item notably raises completion), peak-end (engineer a win and end sessions positively), Goldilocks difficulty, behavior = motivation × ability × prompt (find which is missing), add boosters (templates, sample data, quick wins) and remove blockers (required fields, dead ends).

**Components** (use the fewest that reach value): welcome question (1-2 for personalization), first-run screen with one action, checklist (3-7 items, value-ordered, quick wins first, progress %, celebration, dismissible), empty states (explain, show example, one primary action, optional sample data), interactive tours (≤ 3-5 steps, skippable, not repeated), data import, videos/docs, onboarding calls for high-value accounts, triggered emails.

**First 30 seconds**: product-first (simple/B2C/mobile; risk blank slate), guided setup (needs personalization; adds friction), value-first with demo data (may feel unreal).

**Email + in-app triggers**: welcome (immediate); incomplete setup (24 h, 72 h); activation reached (celebrate + next step); feature discovery (day 3, 7, 14); stalled (X days inactive → value reminder, blocker help, human outreach for high-value). Emails reinforce in-app actions with one CTA back to the exact step (see email-sequences).

**Patterns**: B2B SaaS: setup wizard → first value action → invite team → deep setup. Marketplace: profile → browse → first transaction → repeat. Mobile app: quick win → permission asks in context → notifications → habit loop. Content: follow/customize → consume → create → engage.

## 6. Popups, slide-ins, banners

| Trigger | Use | Notes |
|---|---|---|
| Click-triggered | Lead magnets, gated content | Zero annoyance; often 10%+ conversion |
| Exit intent (desktop) | Ecommerce, lead gen last chance | Mobile alternative: back-button/scroll-up detection or bottom slide-up |
| Scroll 25-50% | Blogs, long content | "Halfway through? Get the checklist" |
| Time on page 30-60 s | General | Never 5 s |
| Page count / session | Research behavior | "Comparing plans? Get a summary" |
| Behavior | Cart abandon, pricing visitors, repeat visits | High intent |

Types: email capture (benefit + frequency, email only), lead magnet (show cover, instant delivery), discount (clear amount, deadline only if real, single use), exit intent (different offer than entry, address an objection), announcement bar (one message, dismissible, time-limited), slide-in (corner/bottom, non-blocking).

Copy: headline benefit/question/curiosity/proof; subhead sets expectations ("one email a week, 5-minute read") or handles an objection; CTA first-person specific ("Send me the checklist", "Claim my 10% off"); decline polite ("No thanks"), never shaming ("No, I don't like saving money").

Rules: max once per session; remember dismissals 7-30 days; exclude converted users, checkout and signup flows; target by source/page/new vs returning; desktop 400-600 px wide; mobile bottom sheet not full screen; visible close (top right) + click outside + Esc; keyboard accessible with focus trap; consent language and unticked boxes; intrusive mobile interstitials hurt search.

Benchmarks: email popups 2-5%; exit intent 3-10%; click-triggered 10%+. Track views, form focus, submits, close clicks, outside clicks, Esc, time to close.

## 7. Paywalls and upgrade prompts

Principles: value before ask (after activation); show what they're missing; frictionless upgrade; respect "no".

Triggers: feature gate (click on paid feature: explain, preview, unlock path, continue option), usage limit (clear limit reached, what upgrade gives, alternative action like delete/archive), trial expiry (warnings at 7/3/1 days, what happens, value summary), time-based nudges (gentle, highlight unused paid features).

Screen components: headline ("Unlock [feature] to [benefit]"), value demo (preview/before-after), comparison with current plan marked, price with annual/monthly, one proof line, specific CTA, clear escape ("Continue with Free").

Timing: not during onboarding or mid-task; not repeatedly after dismissal; per-session cap and multi-day cooldown; track annoyance (rapid dismissals, support tickets).

Upgrade flow: in-context checkout, pre-filled, immediate access after payment, confirmation + guide to new features.

Measure: paywall views, click-to-upgrade, payment completion, revenue per user, post-upgrade churn/refunds.

## 8. Checkout, order bumps, post-purchase upsells

**Checkout**: one page where possible; guest checkout; wallets (Apple Pay, Google Pay, PayPal) above the card form; total cost including shipping/tax before the last step; trust and guarantee beside the pay button; address autocomplete; minimal fields; inline errors; no surprise account creation.

**Pre-purchase bump vs post-purchase upsell**
| | Order bump (on checkout) | Post-purchase upsell |
|---|---|---|
| Risk to base conversion | Real | None (order already captured) |
| Seen by | All checkout visitors | Buyers only |
| Typical price | Small add-on (10-30% of base) | Up to 2-5× base for tier upgrades |
| Needs | Nothing extra | Stored payment credential for one-click |
Default: build post-purchase first; add a bump only behind a test with base conversion as guardrail.

**Offer rules**: complementary, not "more of the same"; one decision per screen; one-tap yes; honest, easy no; first upsell at or below base order value unless it's a clear tier upgrade; scarcity only if structurally true ("only on this page" is true; fake timers are not).

**Chain**: payment → upsell 1 → (accept) optional upsell 2 / (decline) downsell (smaller commitment: single unit, lite, payment plan) → thank-you. Max two decisions for most funnels.

**Upsell page copy**: headline names the gap the purchase left; 3-5 lines on one benefit referencing what they bought; one proof line; reference price only if real elsewhere; button "Add the strap – $19"; plain decline link "No thanks, continue to my order"; confirmation that it's added to the same order and card.

**Technical requirements**: off-session-capable stored payment method; merged order (one shipment/receipt); push to store/ERP after the chain ends; per-charge refunds; purchase event value updated after upsells; idempotent accept (double taps); SCA/3DS fallback screen when an off-session charge needs authentication. Test end-to-end with a real low-value order, including decline path and refund, before sending traffic.

**Measure**: take rate per offer, AOV before/after, refund rate upsold vs base orders (guardrail), base conversion unchanged, monthly chargeback rate. One variable at a time; don't call winners on a few dozen conversions.

## 9. Funnel shapes, page specs, benchmarks

Inputs that decide the shape: offer and price (< ~$50 direct single step; $50-500 landing + checkout + upsell; $500+ lead capture + call), traffic source (cold social needs full pitch; search warmer; email shortest; affiliates need a pre-sell), awareness (problem-unaware needs education first), fulfilment (digital/physical/service), existing assets (list, store, pixels). Flag conflicts (high price + cold traffic + instant checkout) before designing.

| Shape | Steps | Fits |
|---|---|---|
| Direct offer | LP with offer → checkout → thank-you | Impulse price, solution-aware traffic, single product |
| Tripwire → core | LP → low-price checkout → one-click upsell to core → thank-you | Cold paid traffic |
| Lead magnet → nurture | Opt-in → delivery/thank-you → email sequence → offer page | Long consideration, trust needed |
| VSL / long-form | Video sales page → checkout → upsell chain | Info products $100-2,000, cold traffic |
| Application | LP → qualification form → booking → confirmation | $500+ services closed on calls |
| Store funnel | Ad → product page → checkout → post-purchase upsell → confirmation | Ecommerce catalog |
| SaaS self-serve | LP → signup → onboarding → activation → paywall/trial end | Product-led software |
| SaaS sales-led | LP → demo request → qualification → call → proposal | High ACV |

Starting benchmarks (cold paid traffic; replace with your own history): LP → checkout start 5-15%; checkout start → purchase 30-60%; LP → purchase overall 1-5%; post-purchase upsell take 10-30%; lead-magnet opt-in 20-40%. Far outside these → look for a structural cause (traffic, offer, tracking) before page tweaks.

Price ladder: entry price (beats click friction) → immediate one-click upsell (complementary, often 2-5× entry) → downsell on decline → back end (subscription, service, high-ticket) sold later; capture the data the back end needs now.

Launch blockers: conversion event per step with stable names; click id captured and carried to order; server-side purchase event with value and currency; one A/B test slot defined. Build order: checkout first (it constrains what the landing page can promise).

## 10. Research methods for finding "why"

- Session recordings: watch 20-30 sessions of non-converters on the leaking step; log hesitation, rage clicks, dead clicks, form re-entry.
- Heatmaps/scroll maps: does attention reach the CTA, proof and price?
- On-page poll on exit or after 30 s: "What's stopping you from [action] today?" (free text).
- Post-conversion survey: "What almost stopped you?" and "What convinced you?"
- Support/sales tickets and chat logs for repeated questions.
- 5-second test with 5-10 target users: what is it, who for, what next?
- Field-level form analytics for drop-off and errors.
