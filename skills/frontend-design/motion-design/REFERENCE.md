# Motion Reference

## Contents
- The gate
- Duration budgets
- Easing
- Springs
- Tool ladder
- Properties and performance
- Interruption, enter and exit
- Stagger and sequencing
- Reduced motion and hover gating
- View transitions
- Scroll-driven animation
- Vocabulary

## The gate

Ask in order; stop at the first "no".

1. **Frequency**
   | How often | Verdict |
   |---|---|
   | 100+/day, or keyboard-triggered (shortcuts, palettes, focus moves, core nav) | no animation |
   | tens/day (hover, list navigation, frequent toggles) | none, or near-instant (≤ 120 ms, tiny distance) |
   | occasional (modals, drawers, toasts, settings) | standard |
   | rare / first time (onboarding, success, empty states, celebrations) | delight allowed |
2. **Purpose**: one of feedback, spatial consistency, state indication, preventing a jarring change, explanation (marketing/onboarding), delight (rare only).
3. **Budget**: does it work inside the duration table? If it only works slow, reject.
4. **Function**: does motion help? It hinders when it blocks input, delays information the user needs now, or competes with reading.

## Duration budgets

| Element | Duration |
|---|---|
| Press/tap feedback | 80–150 ms |
| Hover color/shadow change | 120–180 ms |
| Tooltip, small popover | 120–180 ms |
| Dropdown, select, menu | 150–220 ms |
| Toast in / out | 200 / 150 ms |
| Accordion, small expand | 180–260 ms |
| Modal / drawer | 220–350 ms (up to 450 for large sheets) |
| Route/page transition | 200–300 ms |
| Marketing hero / explanatory | 400–1200 ms, once |

Larger distance and larger elements may take slightly longer; tiny elements should be faster.

## Easing

| Situation | Easing |
|---|---|
| Entering or exiting | strong ease-out |
| Moving or morphing on screen | ease-in-out |
| Hover / color | a gentle ease or ease-out |
| Constant motion (progress, marquee) | linear |
| UI default | ease-out |

Built-in `ease-out` is weak; define strong curves once as tokens:
```css
:root {
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);      /* quick start, long settle */
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);   /* symmetric, for on-screen moves */
  --ease-sheet: cubic-bezier(0.32, 0.72, 0, 1);    /* drawers and bottom sheets */
}
```
Never `ease-in` for UI: it delays the moment the user is watching. A 200 ms ease-out feels faster than a 200 ms ease-in.

## Springs

Use for gesture-driven motion (drag, swipe, pull) and elements that should feel alive; they retarget naturally when interrupted.
- Describe by perceptual duration and bounce: e.g. duration 0.35 s, bounce 0–0.15 for UI; 0.2–0.3 only for playful moments.
- Equivalent stiffness/damping starting points: stiffness 400–500, damping 30–40, mass 1.
- Carry gesture velocity into the spring on release.
- No bounce on modals, menus, or anything in a work tool.

## Tool ladder

| Need | Use |
|---|---|
| hover, press, toggled state via class/attribute | CSS `transition` |
| entry on mount without JS | CSS `@starting-style` + `transition` (with `transition-behavior: allow-discrete` for `display`) |
| predetermined motion that must stay smooth while the main thread is busy | CSS `@keyframes` (compositor-driven for transform/opacity) |
| programmatic control (start/stop/reverse, sequence) without a library | Web Animations API `el.animate()` |
| springs, layout/shared-element, exit-on-unmount, gestures | an animation library already in the project |
| page/route transitions | View Transitions API |
Prefer CSS when possible: it keeps running while JS is busy. If the job is a whole component (dialog, toast system, command menu), use the project's component library rather than hand-rolling motion and behaviour.

## Properties and performance

- Animate `transform` and `opacity`. `clip-path` and `filter: blur()` are acceptable in small areas; measure.
- Never animate `width`, `height`, `top`, `left`, `margin`, `padding`. For height, animate `grid-template-rows: 0fr → 1fr` or use `interpolate-size: allow-keywords` where supported, or a FLIP technique.
- `translate` percentages are relative to the element: `translateY(100%)` moves by its own height.
- In JS libraries, prefer a full `transform` string over separate `x`/`y`/`scale` values when the page is busy.
- Do not drive many children's transforms from a CSS variable on a parent; it triggers style recalculation for each child.
- `will-change: transform` only right before an animation; remove after. Too many layers cost memory.
- Test with CPU throttling (4–6×) in devtools; watch for dropped frames.

## Interruption, enter and exit

- Toggles, hovers, toasts: transitions (retarget from current value). Keyframes restart from zero and stutter when re-triggered.
- Exits: 20–30% shorter than enters; smaller distance (4–8 px instead of 16); same edge they came from (spatial consistency).
- Deliberate actions (hold-to-confirm, destructive confirm): slower progress, instant release/snap back.
- Popovers, dropdowns, tooltips: scale from trigger (`transform-origin` at the anchor). Modals scale from center. Start at `scale(0.94–0.97)` with opacity 0, never `scale(0)`.
- Do not animate on initial page render for content that is already present.
- Crossfades between very different states can look muddy; a short blur (2–4 px) during the swap or a slight scale helps bridge.

## Stagger and sequencing

- Stagger list/group entrances by 30–60 ms per item; cap total at ~300 ms (stagger only the first 5–8 items).
- One orchestrated page-load sequence beats separate effects on every section.
- Do not stagger routine updates (search results refreshing, list re-sorts).

## Reduced motion and hover gating

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 1ms !important; animation-iteration-count: 1 !important;
                           transition-duration: 1ms !important; scroll-behavior: auto !important; }
}
```
That blanket rule is a safety net. Better: per component, keep opacity and color transitions but remove translation, scaling, parallax, and auto-playing loops. Pause or remove background videos.
Gate hover-only motion so touch devices do not get sticky hover states:
```css
@media (hover: hover) and (pointer: fine) { .card:hover { transform: translateY(-2px); } }
```

## View transitions

- Same-document: `document.startViewTransition(() => updateDOM())`; style `::view-transition-old(root)` / `::view-transition-new(root)`.
- Cross-document (MPA): `@view-transition { navigation: auto; }` in both pages' CSS.
- Shared elements: give matching elements the same `view-transition-name` (unique per page at a time).
- Keep them short (200–300 ms); disable under reduced motion; feature-detect and fall back to instant updates.
- In component frameworks, wrap the state update that changes the view inside the transition callback; avoid async gaps inside it.

## Scroll-driven animation

- CSS `animation-timeline: view()` / `scroll()` runs on the compositor; prefer it over scroll listeners.
- Reveal-on-scroll: subtle (opacity + 8–16 px translate), once per element, never hide essential content until scrolled.
- No scroll-jacking, no horizontal hijack of vertical scroll on content pages, no heavy parallax for reading.

## Vocabulary

| Term | Meaning |
|---|---|
| Fade / fade-through | opacity change; fade-through dips to transparent between two states |
| Scale-in | grow from slightly smaller (0.95) with fade |
| Slide / push | translate in from an edge; push moves the old content out at the same time |
| Morph / shared element | one element animates into another's position and size across states |
| FLIP | First-Last-Invert-Play: measure, apply inverse transform, animate to identity |
| Stagger | sequential delays across a group |
| Orchestration | timing several elements into one sequence |
| Ease-out / ease-in-out | fast-then-slow / slow-fast-slow speed curves |
| Spring | physics-based motion defined by stiffness, damping, mass (or duration + bounce) |
| Overshoot / bounce | passing the target and settling back |
| Anticipation | small opposite movement before the main one (use rarely in UI) |
| Skeleton / shimmer | placeholder shapes with a subtle moving highlight while loading |
| Parallax | layers moving at different scroll speeds |
| Scroll-linked | progress tied to scroll position |
| Micro-interaction | small feedback tied to one action (press, toggle, like) |
| Reduced motion | OS-level user preference to minimise movement |
