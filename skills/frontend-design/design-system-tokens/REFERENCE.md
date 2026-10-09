# Design Tokens Reference

## Contents
- Layers and naming
- Color ramps
- Contrast targets
- Type, spacing, radius, shadow, motion, breakpoints, z-index
- Dark mode and themes
- Source format and build
- Framework wiring
- Enforcement
- Component library rules

## Layers and naming

| Layer | Purpose | Example | Who uses it |
|---|---|---|---|
| Primitive | raw palette and scales | `blue.600 = #2563eb`, `space.4 = 16px` | semantic tokens only |
| Semantic | roles, switch per theme | `color.text.muted → gray.600` | all components |
| Component | rare, specific overrides | `button.primary.bg → color.accent` | one component |

Naming: `category.role.variant.state` in source (`color.text.muted`, `color.accent.hover`); CSS output `--color-text-muted`. Use roles (`muted`, `subtle`, `strong`), never appearance (`light-grey`). Add a component token only when a component genuinely diverges from the semantic role.

Starter semantic color roles:
`bg`, `bg.subtle`, `surface`, `surface.raised`, `overlay`, `text`, `text.muted`, `text.subtle`, `text.inverse`, `border`, `border.strong`, `accent`, `accent.hover`, `accent.text`, `accent.subtle`, `focus`, `success`, `success.subtle`, `warning`, `warning.subtle`, `danger`, `danger.subtle`, `danger.text`, `info`.

## Color ramps

- Build ramps in OKLCH: hold hue (and roughly chroma), step lightness. Neutral ramp: 50 (≈ 98% L) to 950 (≈ 15% L), 11 steps.
- Tint neutrals slightly toward the brand hue (chroma 0.005–0.02) so they do not look dead.
- Reduce chroma at the extremes (very light and very dark steps) to stay in gamut.
- Accent: pick the step where white text passes 4.5:1 as the default `accent` (often 600); hover = one step darker (light theme) or lighter (dark theme).
- Status colors: same lightness logic as the accent; keep text-on-status and status-on-bg pairs checked.

## Contrast targets (WCAG 2.x)

| Pair | Minimum |
|---|---|
| body text on its background | 4.5:1 |
| large text (≥ 24 px, or ≥ 18.7 px bold) | 3:1 |
| UI component boundaries, icons, focus indicators vs adjacent colors | 3:1 |
| disabled controls | exempt, but keep legible |
| placeholder text | treat as text: 4.5:1 |
Check every pair in every theme. APCA can guide fine-tuning, but ship against WCAG 2.x thresholds unless your target says otherwise.

## Type, spacing, radius, shadow, motion, breakpoints, z-index

- **Type**: families (`font.sans`, `font.serif`, `font.mono`), sizes from a ratio (1.2 or 1.25) rounded to whole px, line heights per size (tight 1.1–1.2 for display, 1.5 for body), weights (400/500/600/700 at most), letter spacing per size (negative for large display).
- **Spacing**: 4 px base: 0, 1 (4), 2 (8), 3 (12), 4 (16), 5 (20), 6 (24), 8 (32), 10 (40), 12 (48), 16 (64), 20 (80), 24 (96). Optional named layout tokens (`space.section = 96px`).
- **Radius**: `none 0`, `sm 4`, `md 8`, `lg 12`, `xl 16`, `full 9999`. Nested elements: inner = outer − padding.
- **Shadow**: 3 levels (`sm`, `md`, `lg`) layered and tinted; dark theme uses surface lightness instead.
- **Motion**: `duration.fast 120ms`, `duration.base 200ms`, `duration.slow 300ms`; `ease.out`, `ease.in-out`.
- **Breakpoints**: `sm 640`, `md 768`, `lg 1024`, `xl 1280`, `2xl 1536` (match the framework's defaults if one is used).
- **Z-index layers**: `base 0`, `dropdown 1000`, `sticky 1100`, `overlay 1200`, `modal 1300`, `popover 1400`, `toast 1500`, `tooltip 1600`. Components never invent their own numbers.

## Dark mode and themes

- Each theme maps the same semantic roles to different primitives. Components do not change.
- Dark: background around gray.950, surfaces step lighter for elevation (`surface` gray.900, `surface.raised` gray.800), text gray.50/100 rather than pure white, accents one or two steps lighter and slightly less saturated.
- Switching: `[data-theme="dark"]` on `<html>` for explicit choice, with `prefers-color-scheme` as the default; set `color-scheme: light dark` so form controls and scrollbars follow.
- Avoid a flash of the wrong theme: set the attribute in a tiny inline script in `<head>` before CSS paints, reading the stored preference.
- Brands: same pattern; a brand file overrides accent primitives and maybe type families.

## Source format and build

Keep a JSON source in the Design Tokens Format Module 2025.10 (the first stable DTCG spec, Oct 2025): `$value`, `$type`, references in `{braces}`. In 2025.10, color values are objects (`{"colorSpace": "srgb", "components": [r, g, b], "hex": "#rrggbb"}`) and `dimension`/`duration` values are `{"value": 16, "unit": "px"}`; plain strings like `"#fff"` or `"16px"` are pre-2025 drafts. `scripts/build-css.py` and `scripts/contrast-check.py` accept both, so older files still build. Use `hex` (or srgb components) for anything these scripts read; for other color spaces, build with a tool that supports them.
```json
{ "gray": { "600": { "$value": { "colorSpace": "srgb", "components": [0.345, 0.38, 0.424], "hex": "#58616c" }, "$type": "color" } },
  "themes": { "light": { "color": { "text-muted": { "$value": "{gray.600}" } } } } }
```
`themes`, `component` and `contrast_pairs` are this pack's layout conventions, not part of the spec. Spec-native theming uses the separate DTCG Resolver module (one file per theme/mode plus a resolver); if the project already uses that, keep it and point the scripts at a resolved single-theme file.
Generate CSS variables with `scripts/build-css.py`. Use a token build tool (e.g. Style Dictionary or Terrazzo) when you also need platform outputs (Android/iOS resources, TypeScript constants). Commit the source; generate outputs in the build or commit them marked "generated".

## Framework wiring

**Plain CSS**: custom properties on `:root` and `[data-theme]` (see templates/tokens.css).

**Tailwind v4** (CSS-first config):
```css
@import "tailwindcss";
@import "./tokens.css";              /* defines --color-bg, --color-text-muted, ... per theme */
@theme inline {
  /* Tailwind maps --color-* to utilities. Re-declaring --color-bg: var(--color-bg)
     would be a self-reference (invalid), so point utility names at the semantic vars
     under a different name: bg-canvas, text-ink, text-ink-muted, bg-brand,
     rounded-card, font-body. Every left-hand name must differ from its var(). */
  --color-canvas: var(--color-bg);
  --color-ink: var(--color-text);
  --color-ink-muted: var(--color-text-muted);
  --color-brand: var(--color-accent);
  --radius-card: var(--radius-md);
  --font-body: var(--font-sans);
}
@custom-variant dark (&:where([data-theme="dark"], [data-theme="dark"] *));
```
`@theme inline` is required here: it inlines `var(--color-bg)` into each utility so the value switches with `[data-theme]` at use time. If you prefer utility names identical to the semantic roles, rename the generated variables instead (e.g. `--bg`, `--text-muted`) and map `--color-bg: var(--bg)`.

**Tailwind v3** (`tailwind.config.js`):
```js
module.exports = {
  darkMode: ["class", '[data-theme="dark"]'],
  theme: { extend: { colors: { bg: "var(--color-bg)", text: { DEFAULT: "var(--color-text)", muted: "var(--color-text-muted)" }, accent: "var(--color-accent)" } } },
};
```
Check which major version the project uses before editing; the config models differ.

**CSS-in-JS**: export a theme object whose values are `var(--…)` references so runtime theming stays in CSS.

**Native apps**: generate platform files (Android XML/Compose, iOS asset catalogs/Swift) from the same JSON.

## Enforcement

- Stylelint: `declaration-strict-value` (plugin) for `color`, `background-color`, `border-color`, `fill`, `z-index`, with tokens/`var(--…)` allowed.
- Simple CI grep for components: `rg -n '#[0-9a-fA-F]{3,8}\b|rgb\(' src/components` should return nothing.
- Utility frameworks: disallow arbitrary values in components (`bg-[#…]`, `p-[13px]`) via lint plugin or review checklist.
- Track adoption: count raw values over time; replace highest-traffic components first.

## Component library rules

For copy-in component libraries built on headless primitives (and in-house kits alike):
- Check for an existing component before writing custom markup (alerts, badges, separators, skeletons, empty states, toasts).
- Use built-in variants and sizes before custom classes; add a variant to the component when a pattern repeats.
- Pass layout classes (margin, width, grid placement) from outside; do not override the component's colors or typography with utility classes. Change tokens instead.
- Use `gap` on flex/grid containers rather than per-child spacing utilities.
- Overlay components (dialog, popover, sheet) manage their own stacking; no manual z-index.
- Dialogs and sheets always have a title (visually hidden if needed); avatars have fallbacks; grouped items live inside their group component.
- Forms: one field wrapper that wires label, control, description, and error with `aria-describedby` and `aria-invalid`; use toggle groups for 2–7 exclusive options.
- Merge conditional classes with a class-merge helper, not string ternaries.
- When updating copied-in components from upstream, diff first and preserve local token changes.
