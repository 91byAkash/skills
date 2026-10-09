# UI Polish Checklist

## Contents
- Hierarchy
- Layout and spacing
- Typography
- Color and surfaces
- States and feedback
- Interaction details
- Forms
- Responsive
- Copy
- Icons and images
- Perceived performance
- Commonly forgotten

## Hierarchy
- One focal point per view; one primary action per region. Secondary actions visibly quieter (ghost/outline/link).
- Headings step clearly (size and/or weight); not more than 3–4 text sizes in one view.
- Related things grouped by proximity; unrelated things separated by more space than related ones.
- Scan test: blur the screenshot; the most important element should still stand out.

## Layout and spacing
- Spacing from one scale (4 px base: 4, 8, 12, 16, 24, 32, 48, 64). Values off the scale are drift.
- Consistent container padding; content max width (reading text ≤ 75ch; app content 1040–1280 px).
- Align to a grid; left edges line up across sections. Check with a column overlay.
- Optical over geometric: icons in buttons, play triangles, and asymmetric glyphs often need 1–2 px nudges; text next to icons aligned to the cap height or center visually.
- No awkward gaps from mixed margin systems (margin-top on some, margin-bottom on others). Prefer `gap` in flex/grid.

## Typography
- Body ≥ 16 px on mobile (inputs too, or iOS zooms on focus).
- Line height: body 1.4–1.6; headings 1.05–1.25.
- Headings: `text-wrap: balance`; paragraphs: `text-wrap: pretty` to avoid orphans.
- Dynamic numbers (prices, counters, timers, tables): `font-variant-numeric: tabular-nums`.
- Truncation: single line with `text-overflow: ellipsis` and a title/tooltip, or line clamp for previews; never cut text silently.
- Font loading: no invisible text or reflow (`font-display: swap`, metric-matched fallback).
- On macOS-heavy audiences, `-webkit-font-smoothing: antialiased` on the root for light text on dark.

## Color and surfaces
- All colors from tokens. Count distinct greys; more than ~8 means drift.
- Contrast: body ≥ 4.5:1, large text and UI boundaries ≥ 3:1, in every theme.
- Concentric radii: inner radius = outer radius − padding. Radius scale by size, not one value everywhere.
- Shadows for elevation (layered, soft, low opacity, tinted); borders for structure (dividers, inputs, table rules). Do not stack both heavily.
- Images: a subtle 1 px inner outline at ~10% black (light theme) or ~10% white (dark) keeps light images from bleeding into the background.
- Dark theme: elevation via lighter surfaces, not shadows; avoid pure white text on pure black.

## States and feedback
Every interactive element needs: default, hover (pointer devices only: `@media (hover: hover)`), focus-visible, active/pressed, disabled (with reason when possible), loading.
Every data view needs: loading (skeleton matching final layout), empty (what goes here + action), error (what happened + retry), partial, and success confirmation where an action had no visible result.
- Optimistic updates for quick, reversible actions; undo instead of confirm dialogs where possible.
- Toasts for background results; inline messages for field errors.

## Interaction details
- Hit area ≥ 44×44 px on touch (≥ 24×24 minimum anywhere); extend with padding or a pseudo-element, not by enlarging the icon.
- Press feedback: `transform: scale(0.97–0.98)` on `:active` for buttons and cards that act like buttons.
- Transitions: name properties (`transition: background-color 150ms, transform 150ms`), never `transition: all`; animate `transform` and `opacity`, not `width/height/top/left`; 120–200 ms for hover/press; `prefers-reduced-motion` respected.
- Anything beyond hover/press (entrances, overlays, toasts, page transitions): judge it with the motion-design standards (frequency gate, budgets, origin, interruption) in the `motion-design` skill and report the result under this category.
- Cursor: `pointer` on clickable non-links only if the project's convention uses it; never custom cursors.
- Scroll: no scroll-jacking; anchor links offset for sticky headers (`scroll-margin-top`).

## Forms
- Visible labels (placeholders are not labels); helpful hint text below when format matters.
- Correct `type`, `inputmode`, `autocomplete` attributes (email, tel, one-time-code, postal-code).
- Validate on blur or submit, not on every keystroke from the first character; errors next to the field, linked with `aria-describedby`.
- Preserve input on error; focus the first invalid field.
- Primary button states: disabled only with an explanation; show loading in the button during submit; prevent double submit.

## Responsive
- Check 320/360, 390, 768, 1024, 1440 px. No horizontal scroll at any width.
- Navigation collapses intentionally; touch menus open on tap, not hover.
- Tables: horizontal scroll container with sticky first column, or a card layout on small screens.
- Sticky headers/footers not covering inputs when the keyboard opens; `env(safe-area-inset-*)` on notched devices.
- Images responsive (`srcset`/`sizes`), sized to avoid layout shift.

## Copy
- Buttons say what happens ("Save changes"), consistent names across a flow.
- Sentence case; no filler; specific error text with a fix.
- Empty states invite the next action. Numbers formatted for the locale (₹1,24,500 in en-IN).

## Icons and images
- One icon set, one stroke weight matching text weight, consistent sizes (16/20/24).
- State changes via `currentColor`, not separate SVGs.
- Directional icons flip in RTL.
- Icon-only buttons have an accessible name.

## Perceived performance
- Skeletons match final layout; no spinners for < 300 ms operations (delay showing them).
- Reserve space for async content (avoid layout shift).
- Instant feedback on press even if work continues.
- Long lists virtualised; images lazy-loaded below the fold.

## Commonly forgotten
- Favicon, page titles, social preview image.
- 404 and error pages styled like the app.
- Focus styles on custom components (dropdowns, tabs, cards).
- Selection color, scrollbar styling in dark mode.
- Print styles for invoices/receipts.
- Very long names, emails, and numbers in every component.
- Disabled-state contrast still legible.
- Dark mode for embedded content (charts, code blocks, maps).
