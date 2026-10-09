---
name: frontend-visual-direction
description: "Choose and build a deliberate, subject-specific visual direction for a new page, app screen or redesign. Use when building a landing page, marketing site or portfolio, a product UI with no established look, or when a design \"looks AI-generated\" or generic. Not for polishing details (use ui-polish-review) or token setup (use design-system-tokens)."
license: MIT
metadata:
  category: "frontend-design"
  version: "3.0.0"
---

# Frontend Visual Direction

Scope: design read, palette, type, layout, hero, one signature move, real copy, and the build, with a self-review against generic tells.

Decide the look on purpose, review the decision against the brief, then build it consistently. One bold idea, everything else quiet and well made.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `brief` | required | — | "landing page for a bookkeeping app for Indian freelancers" |
| `subject` | optional | inferred from brief, confirmed with user | "GST-ready invoices and expense tracking for solo designers" |
| `audience` | optional | inferred | "freelancers 25–40, mobile-first, price-sensitive" |
| `primary_job` | optional | inferred | "get sign-ups for the free plan" |
| `mode` | optional | `new` | `redesign-preserve`, `redesign-overhaul` |
| `constraints` | optional | none | existing logo/brand colors, framework (React + Tailwind), dark mode required, WCAG AA |
| `dials` | optional | from the dial presets in REFERENCE.md | `variance=6 motion=4 density=4` |
| `directions` | optional | 2 | 3 when the user wants options |
| `content` | optional | you write realistic copy | real headline, pricing, testimonials |

## Output

- A **design plan** (from [templates/design-plan.md](templates/design-plan.md)): design read, dials, palette (4–6 named hex values), type roles and scale, layout concept with ASCII wireframe, the one signature move, principles.
- The implemented UI, tokens first (start from [templates/tokens.css](templates/tokens.css)).
- A short design note saved next to the code (`DESIGN.md` or the plan file) so later work stays consistent.

## Supporting files

- [REFERENCE.md](REFERENCE.md): dial presets, typography and color rules, layout and hero patterns, copy rules, the catalogue of generic tells, redesign protocol, and when to use an established design system. Read at step 3 (dials, patterns) and step 6 (self-review).
- [templates/design-plan.md](templates/design-plan.md): plan skeleton. Fill at step 4.
- [templates/tokens.css](templates/tokens.css): starter custom properties for color (light/dark), type scale, spacing, radii, shadows, motion. Copy at step 7.

## Steps

1. **Ground in the subject.** If `mode` is `redesign-preserve` or `redesign-overhaul`, run the Redesign protocol in REFERENCE.md first (audit screenshots and inventory, list what must not change); it fixes the dial offsets in step 3 and the levers you may pull. If the brief does not say what the product is, who it is for, and the page's main job, propose one concrete answer for each and confirm. A direction for "a SaaS" will be generic; a direction for "bookkeeping for freelance designers in Pune" will not.
2. **Write a one-line design read**: "Trust-first fintech for freelancers; calm, precise, a little warm; mobile-first; sign-up is the goal." If the brief is ambiguous on something that changes the direction (e.g. playful vs serious), ask one question.
3. **Set dials** (1–10): `variance` (symmetry → experimental), `motion` (static → cinematic), `density` (airy → packed). Start from the preset in REFERENCE.md, adjust to the read. Check `constraints`: an existing design system or brand overrides taste.
4. **Draft `directions` plans** using the template. Each needs:
   - **Palette**: 4–6 named hex values (ground, surface, ink, muted ink, accent, optional second accent) with contrast checked: body text ≥ 4.5:1, large text and UI ≥ 3:1. Check each pair with the `design-system-tokens` skill's `scripts/contrast-check.py --pair '#0F766E' '#FBFAF7'` (any WCAG contrast checker works if that skill is not installed). Decorative rules/dividers are exempt; a border that is the only edge of a control (input, checkbox) needs 3:1.
   - **Type**: one or two families with roles; if two, clearly different. Scale from a ratio (1.2–1.333), body 16–18 px, line length ≤ ~75 characters, line height 1.4–1.6 for body.
   - **Layout**: concept in one sentence plus an ASCII wireframe of the first two screens; alignment rule (left-aligned by default for reading).
   - **Hero**: open with the most characteristic thing in the subject's world (a real product view, a live calculator, a striking photo, a sharp headline).
   - **Signature move**: one memorable element. Only one.
5. **Review each plan against the brief.** Ask: would I produce this for any similar brief? Compare against the generic-tells list in REFERENCE.md. Replace any part that is a default rather than a choice. Then present (or pick the best fit and explain why if the user asked you to decide).
6. **Write real copy** from the user's point of view (if `content` was supplied, use it verbatim and only fill gaps; mark any copy you invented so the user can replace it): plain verbs, sentence case, CTAs that say what happens ("Create your first invoice"), the same action name throughout the flow, errors that explain the fix, empty states that invite the next step. No filler verbs ("elevate", "seamless", "unleash").
7. **Build tokens first** (copy templates/tokens.css and replace values; if the project needs themes, multiple brands, or a component library, set up tokens with `design-system-tokens` instead), then layout, then components. Keep selector specificity flat (single classes) so rules do not fight each other.
8. **Build the quality floor without announcing it**: responsive from 360 px to wide screens, visible focus styles, semantic HTML, alt text, `prefers-reduced-motion` respected, dark mode if required, no layout shift from fonts/images (set dimensions, `font-display: swap`).
9. **Motion**: at most one orchestrated moment (a page-load sequence or one reveal) plus purposeful state transitions. Details in `motion-design`.
10. **Critique** with screenshots at 390 px and 1440 px: hierarchy (one focal point per section, one primary action), spacing consistency, contrast, and the tells list. Fix, then write the design note.

## Checkpoints

- After step 1: subject, audience, and primary job confirmed.
- After step 5: user picks a direction (unless they delegated the choice).
- After step 10: screenshots reviewed before calling it done.

## Worked example

Brief: bookkeeping app for freelancers. Read: "calm, precise, warm; mobile-first; sign-ups". Dials: variance 6, motion 4, density 4.

Direction "Ledger paper":
- Palette: Paper `#FBFAF7`, Ink `#1D232B`, Graphite `#5B6573` (5.7:1), Rule `#E3E0D8` (dividers only; input borders use Graphite), Teal `#0F766E` (accent, 5.2:1 on Paper), Marigold `#F2B33D` (highlights only, never text).
- Type: a humanist sans for UI and body (16/1.55), tabular numerals for amounts; display 44/1.1 at desktop from a 1.25 scale.
- Layout: left-aligned 12-column grid, 1120 px max; hero is a real invoice being filled in, with GST auto-calculated as the user types.

```
[logo]                      [Pricing] [Log in] [Start free]
Send a GST-ready invoice     ┌──────── live invoice ───────┐
in two minutes.              │ Client  Studio Kavya         │
[Start free]  no card needed │ Logo design      ₹18,000     │
                             │ GST 18%           ₹3,240     │
                             └──────────────────────────────┘
```
- Signature: the live invoice. Everything else stays plain: no gradients, cards only where content is a discrete object.

Self-review caught: a centred three-card feature row (default) → replaced with a two-column "what you do / what the app does" list tied to the invoice.

## Pitfalls

- Mixing several directions on one page.
- Picking typefaces and colors you would use on any project; they are defaults, not choices.
- Decoration that encodes nothing: numbered eyebrows, hairline grids, status dots, ALL-CAPS labels over every heading.
- Fake product UI built from grey divs; use a real screenshot, a real interactive component, or nothing.
- Placeholder names and perfect numbers ("John Doe", "99.9%"); use realistic, local content.
- Shipping desktop-only, or skipping dark mode when it was required.
- Contrast sacrificed for mood.

## Done when

- [ ] Subject, audience, primary job, and design read are written down.
- [ ] A plan with palette (contrast-checked), type roles/scale, layout wireframe, and one signature move exists and was reviewed against the generic-tells list.
- [ ] Tokens are defined before components and used everywhere (no stray hex values or ad-hoc spacing).
- [ ] Copy is real, specific, and consistent in action names.
- [ ] Works at 360–1440+ px, keyboard focus visible, reduced motion respected, no layout shift.
- [ ] Design note saved for future work.
