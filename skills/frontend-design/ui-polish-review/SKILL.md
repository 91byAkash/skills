---
name: ui-polish-review
description: "Review an existing UI for craft and usability problems and report or apply prioritised fixes with before/after evidence. Use when asked to review, critique or polish a UI, \"make this feel better\", before shipping a UI change, or when something \"feels off\". Not for a new direction (use frontend-visual-direction), WCAG audits (use accessibility-audit) or animation (use motion-design)."
license: MIT
metadata:
  category: "frontend-design"
  version: "3.0.0"
---

# UI Polish Review

Scope: hierarchy, spacing, alignment, typography, color, surfaces, states, interaction details, responsiveness, copy, icons, perceived performance.

Small details compound. Walk every state slowly, find what is off, and fix the highest-impact issues first without changing the design's direction.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `target` | required | — | `http://localhost:3000/settings` or `src/components/Pricing.tsx` |
| `mode` | optional | `full` | `quick` (primary path, HIGH/MEDIUM only, max 5 findings) |
| `action` | optional | `report` | `fix` (apply changes), `report+fix` |
| `viewports` | optional | `390`, `768`, `1440` px | add `320` for small Android |
| `themes` | optional | every theme the app ships | `light,dark` |
| `stack` | optional | detected | React + Tailwind v4; plain CSS |
| `finding_cap` | optional | 15 (`full`) / 5 (`quick`) | 25 for a whole app |

## Output

A report from [templates/review-report.md](templates/review-report.md):
- scope and coverage table (each category: what was inspected, result, or "not reviewed" and why)
- findings grouped by category: **Severity**, **Location** (`file:line` or screen › component), **Before**, **After**, **Why**
- considered-but-rejected items, and a verdict
With `action=fix`: the changes applied in the priority order below, plus before/after screenshots.

## Supporting files

- [REFERENCE.md](REFERENCE.md): the detail checklist per category with concrete values (radii, hit areas, transitions, type, states, forms, responsive rules, copy) and the "commonly forgotten" list. Read while inspecting.
- [templates/review-report.md](templates/review-report.md): report skeleton.
- [scripts/css-audit.py](scripts/css-audit.py): static scan of CSS/JSX/TSX/Vue/Svelte files for token drift and polish smells (distinct colors, font sizes, radii, z-index, `transition: all`, removed outlines, `!important`). Run first: `python3 scripts/css-audit.py src/`.

## Boundary with accessibility-audit

Polish review records the accessibility problems it meets while walking the UI (missing focus style, text contrast below 4.5:1, targets under 24×24 px, icon buttons without names, placeholder-only labels) as **HIGH**, citing the WCAG criterion number. It does not run screen-reader passes, walk every success criterion, or state conformance. Recommend a full `accessibility-audit` in the verdict when the review finds 3 or more such issues, or when the user mentions compliance, public-sector, or a launch to a regulated audience. For contrast numbers use the `design-system-tokens` skill's `scripts/contrast-check.py --pair FG BG` (or any WCAG contrast checker).

## Severity

- **HIGH**: makes something inaccessible, unreadable, misleading, or repeatedly disruptive (no focus style, text under 4.5:1, layout jump on every load, tap target 24 px on mobile primary action).
- **MEDIUM**: noticeable usability or consistency problem (three button styles for one role, missing loading state, misaligned grid).
- **LOW**: isolated polish (optical alignment of one icon, heading orphan).

## Steps

1. **Scope**: confirm target, mode, action. Note the stack and styling conventions; you will work within them.
2. **Static scan**: `python3 scripts/css-audit.py <src dir>`. Note token drift (e.g. 23 distinct greys, 11 font sizes) as systemic findings.
3. **Walk the UI** at each viewport and theme. For every component on the primary path, exercise states: default, hover, focus (keyboard), active/pressed, disabled, loading, empty, error, success, long content, very short content. Replay motion at 10–25% speed in devtools.
4. **Inspect by category** using REFERENCE.md: hierarchy, layout and spacing, typography, color and surfaces, states and feedback, interaction details, forms, responsive, copy, icons and images, perceived performance.
5. **Write findings**: one row per issue, or one row per systemic issue listing every location. Before and After must be concrete (code or exact values), not "improve spacing". Respect `finding_cap`; never pad.
6. **Prioritise fixes** (when `action` includes fix), highest visual impact and lowest risk first:
   1. typography (family/scale/line length) and color cleanup (clashing or off-token values)
   2. focus, hover, active states
   3. layout and spacing (grid, max width, consistent padding)
   4. loading, empty, error states
   5. component consistency (one button style per role, consistent radii)
   6. fine details (optical alignment, tabular numbers, text wrapping)
7. **Fix within the stack**: no framework or styling-library migration; check dependencies before adding any library; check the Tailwind major version before touching config. Small focused commits; test after each change.
8. **Verify**: re-screenshot the same views; re-run the static scan; confirm nothing regressed (keyboard path, other viewports, other theme).

## Checkpoints

- Before fixing in `report+fix`: share the findings table and confirm the priorities.
- Any change that alters layout structure, copy meaning, or brand colors → ask first.

## Worked example

Target: pricing page, `mode=quick`, `action=report`.

| Severity | Location | Before | After | Why |
|---|---|---|---|---|
| HIGH | `Pricing.tsx:88` button | `outline: none` with no replacement | `:focus-visible { outline: 2px solid var(--color-focus); outline-offset: 2px }` | keyboard users cannot see focus |
| HIGH | `PlanCard.tsx:41` price | price digits proportional; toggling monthly/annual shifts layout | `font-variant-numeric: tabular-nums` | text jumps on every toggle |
| MEDIUM | `PlanCard.tsx:12`, `Badge.tsx:5` | card radius 16 px, inner badge 16 px with 8 px inset | inner radius 8 px (outer − padding) | non-concentric corners look off |
| MEDIUM | all CTAs (4 files) | three hover treatments (darken, underline, scale 1.05) | one: background shade step + `scale(0.98)` on press | inconsistent feedback |
| LOW | `Pricing.tsx:20` h2 | orphan word at 1440 px | `text-wrap: balance` | ragged heading |

Verdict: ship after the two HIGH fixes.

## Pitfalls

- Reviewing only the default state on a desktop screen.
- Vague findings ("spacing feels off") with no location or replacement.
- Redesigning while polishing; keep the existing direction.
- `transition: all` and animating layout properties (width, height, top) instead of transform/opacity.
- Removing focus outlines for looks.
- Padding the report with LOW items to look thorough, or hiding uninspected areas.

## Done when

- [ ] Coverage table lists every category with evidence or "not reviewed" plus reason.
- [ ] Every finding has severity, exact location, concrete before/after, and the user impact.
- [ ] Systemic issues are consolidated with all locations listed.
- [ ] (fix) Changes applied in priority order within the existing stack; before/after screenshots at each viewport/theme.
- [ ] Keyboard path and reduced-motion behaviour re-checked after fixes.
- [ ] Verdict recommends `accessibility-audit` when 3+ accessibility findings appeared.
