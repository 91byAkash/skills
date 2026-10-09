# Visual Direction Reference

## Contents
- Dials and presets
- Typography
- Color
- Layout patterns
- Hero patterns
- Surfaces, cards, depth
- Imagery and icons
- Copy in the interface
- Generic tells to avoid
- Redesign protocol
- When to use an established design system
- Pre-flight checklist

## Dials and presets

| Dial | 1–3 | 4–6 | 7–10 |
|---|---|---|---|
| **variance** | symmetric, centred or strict grid | asymmetric accents on a regular grid | broken grids, overlap, unexpected scale |
| **motion** | static; state transitions only | one entrance sequence, hover/press feedback | scroll-linked scenes, physics, choreographed sequences |
| **density** | gallery-like, big whitespace | balanced marketing/product | dashboards, data tables, dense controls |

Starting points, written as variance / motion / density; adjust after seeing the brief and references:
- **Quiet and trustworthy**: public-sector, regulated or accessibility-critical services 2–3 / 1–2 / 5; internal admin dashboards 2–3 / 2 / 7–8.
- **Balanced**: developer portfolios and documentation 5–6 / 3–4 / 4–5; editorial sites and blogs 5–6 / 3 / 3; a mainstream SaaS landing page 6–7 / 5–6 / 4.
- **Expressive**: premium consumer products 7 / 5–6 / 3; agency or creative portfolios 8–9 / 7–8 / 3.
- **Redesigns**: when the brief says preserve, keep the current variance and density and allow motion one step higher; when it says overhaul, raise variance and motion by about two and keep density.

## Typography

- One or two families. If two, they must contrast clearly (serif display + sans text, or grotesque + mono for data); two similar sans faces look like a mistake.
- Choose for the subject: a precise grotesque for finance tools, a warm humanist sans for consumer services, a high-contrast serif for editorial or luxury, a mono for developer tools. Avoid reaching for the same face on every project.
- Scale from a ratio: 1.2 (dense UI), 1.25 (general), 1.333 (marketing). Example at 1.25 from 16 px: 13, 16, 20, 25, 31, 39, 49.
- Body 16–18 px; line height 1.4–1.6 (serif body slightly more); line length 45–75 characters (`max-width: 65ch`).
- Headlines: line height 1.05–1.2, tighten tracking slightly at large sizes (−0.01 to −0.03 em). Control hierarchy with weight and color, not just size.
- Numbers in tables and prices: tabular figures (`font-variant-numeric: tabular-nums`).
- Load at most 2 families × 2–3 weights; subset; `font-display: swap`; size-adjusted fallbacks to avoid layout shift.
- Avoid as defaults: one italic/colored word in every headline, ALL-CAPS tracked labels above every heading, `<br>`-split headlines for drama.

## Color

- Structure: ground, surface, ink, muted ink, border/rule, one accent, optional second accent, semantic (success, warning, danger, info).
- Neutrals carry the page; the accent marks actions and key data. If everything is accented, nothing is.
- Avoid pure `#000`/`#fff` on large areas; slightly tinted neutrals feel finished. Desaturate accents that vibrate against neutrals.
- Contrast: body text ≥ 4.5:1; large text (≥ 24 px, or ≥ 19 px bold) and UI boundaries ≥ 3:1. Check both themes.
- Dark mode: not an inversion. Raise surface lightness for elevation, reduce accent saturation, keep text off pure white (around 90–95% lightness).
- Prefer defining palettes in OKLCH for predictable lightness steps; output hex for compatibility.

## Layout patterns

Pick one primary structure per page:

| Pattern | Good for |
|---|---|
| Long-form document (single readable column with asides) | editorial, docs, manifestos |
| Feature stack (alternating text/visual rows) | product marketing with 3–6 capabilities |
| Bento grid (unequal tiles, deliberate sizes) | showing many small capabilities at once |
| Workbench (product UI as the page) | tools where the demo is the pitch |
| Stat-led (one big number, then proof) | outcomes-driven B2B |
| Quote-led | services and agencies with strong client voices |
| Catalogue / index-first | many items: templates, products, articles |
| Narrative workflow (step through a process with one visual) | onboarding, "how it works" |
| Split studio (fixed side panel + scrolling content) | portfolios, case studies |
| Specimen (type or product shown large with specs) | fonts, hardware, physical goods |
| Photographic (full-bleed imagery leads) | travel, food, fashion, places |
| Conversational FAQ | considered purchases with many objections |

Grid: 12 columns desktop, 4–6 mobile; max content width 1040–1280 px; spacing scale on a 4 px base (4, 8, 12, 16, 24, 32, 48, 64, 96). Use fewer, larger gaps between sections than within them.

## Hero patterns

- **Real product view** (screenshot or live component) next to a direct headline.
- **Interactive moment**: a working calculator, editor, or search the user can try immediately.
- **Photographic fold**: one strong image, short headline overlay with sufficient contrast.
- **Statement**: a large, precise sentence with one CTA; works when the copy is genuinely sharp.
- **Stat-led**: one verified number with its source.
Rules: one primary CTA (plus at most one secondary); headline ≤ 2 lines at desktop; the first screen must say what it is and for whom.

## Surfaces, cards, depth

- Use a card only when content is a discrete, repeatable object (a product, a post). Not every section needs a box.
- Vary radius by size and role (small controls 6–8 px, cards 12–16 px, sheets 20+ px) rather than one radius everywhere, or go square deliberately.
- Shadows: 2–3 elevation levels, tinted toward the ground hue, soft and low-opacity; borders often work better than shadows in dense UI.
- Gradients: only when they mean something (light source, brand mark), never as filler wash.

## Imagery and icons

- Real screenshots beat illustrations of screenshots. Crop to the relevant part; add a subtle frame only if needed.
- Photography: consistent treatment (same color grade, aspect ratios from a small set). Placeholders: descriptive seeded image services or flat color blocks with labels, never broken stock links.
- Icons: one library, one stroke weight, one size scale; label icons that are not universally understood. No emoji as UI icons unless the brand voice calls for it.
- Do not hand-draw complex SVG illustrations in code as a default; use real assets or generated images when available.

## Copy in the interface

- Name things by what users understand ("Notifications", not "Webhook config").
- Buttons say what happens: "Save changes", "Send invoice", not "Submit".
- Keep the action name consistent: "Publish" → toast "Published".
- Errors: what happened + how to fix, no apology, no vagueness. Empty states: what goes here + the action to start.
- Sentence case, plain verbs, no filler. Each piece of text does one job.
- Realistic content: local names, real-looking numbers (₹18,240, 47.2%), believable company names.

## Generic tells to avoid

These are fine when a brief truly calls for them, but they appear as defaults on generated pages regardless of subject:

**Palette and surface**
- cream background + high-contrast serif + terracotta accent
- near-black background + single acid-green or vermilion accent
- purple-to-blue gradients, glassmorphism everywhere, neon glows
- identical rounded cards with the same soft grey shadow on every section

**Type and labels**
- ALL-CAPS tracked eyebrow above every heading
- numbered section labels (01 / 02 / 03, "001 · Capabilities") that encode nothing
- one word in a headline italicised or colored
- meta strings joined with middle dots ("A · B · C · D"), labels built as "WORD — fragment"

**Layout**
- centred hero → three equal feature cards → testimonial carousel → CTA band, by reflex
- broadsheet hairline rules and zero radius used as instant "editorial"
- decorative grid lines, crosshairs, rotated vertical text

**Content**
- fake dashboards/terminals built from grey divs
- version stamps in heroes ("v2.0 BETA"), fake build footers, live-stock counters
- "Trusted by" logo strips of invented companies; "John Doe" testimonials; 99.9% uptime claims with no source
- scroll cues, city/time/weather strips, poetic section labels

The test: if you would have produced the same element for a different product, it is a default. Replace it with something that comes from this subject.

## Redesign protocol

1. **Detect the mode**: preserve (evolve the existing look) or overhaul (new direction). Ask if unclear.
2. **Audit first**: screenshot key pages at 390 and 1440 px; inventory colors, type, spacing values, components; note what users and the brand rely on (logo, brand color, nav labels, URLs).
3. **Preserve** without asking: information architecture and URLs, brand marks, accessibility wins, content meaning.
4. **Levers in priority order**: typography (scale, family, rhythm) → spacing and grid → color refinement → component consistency → imagery → motion.
5. **Targeted evolution vs full redesign**: if more than half the audit items need changing, propose a full redesign; otherwise evolve.
6. **Never change silently**: navigation labels, pricing presentation, legal text, form fields and their order.

## When to use an established design system

If the brief is a product with an existing system, or a domain with a mandated one (government services, a platform's app ecosystem), use the official system's packages and tokens instead of inventing a look:
- government/public services → the national design system (e.g. GOV.UK Frontend, USWDS)
- enterprise data apps → a mature enterprise system (Carbon, Fluent, Atlassian, Material 3)
- platform extensions → that platform's own component kit
- generic React product with headless primitives → Radix or similar, themed with your tokens (never ship component kits in their default look)
Apply visual direction only within the system's theming affordances.

## Pre-flight checklist

- [ ] One-line design read and dials written
- [ ] Palette contrast checked in every theme
- [ ] Type scale from a ratio; body ≥ 16 px; line length ≤ 75ch
- [ ] One primary CTA per view; one focal point per section
- [ ] One signature move; nothing from the tells list by default
- [ ] Real copy and realistic content
- [ ] 360 / 768 / 1440 px checked; no horizontal scroll
- [ ] Focus visible; reduced motion honoured; images sized; fonts swap without shift
