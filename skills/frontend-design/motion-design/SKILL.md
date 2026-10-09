---
name: motion-design
description: "Decide whether something should animate, then build or review UI motion that is fast, interruptible and respects reduced-motion. Use when adding transitions or animations, reviewing animation code, \"make it feel smoother\", or finding where motion would help. Not for general visual polish (use ui-polish-review) or a page's overall look (use frontend-visual-direction)."
license: MIT
metadata:
  category: "frontend-design"
  version: "3.0.0"
---

# Motion Design

Scope: purpose test, durations and easing, enter/exit and spatial transitions, GPU-friendly properties, reduced motion, and an animation review.

Motion is a tool with a purpose, not decoration. The best animation for a 100-times-a-day action is none.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `target` | required | — | `src/components/Dropdown.tsx`, a PR diff, or "the settings page" |
| `mode` | optional | inferred | `build` · `review` (judge existing motion) · `find` (look for opportunities) |
| `stack` | optional | detected | plain CSS; React + Framer Motion; Svelte transitions |
| `personality` | optional | from the product | `crisp` (tools, dashboards) · `soft` (consumer) · `playful` (games, kids, celebration) |
| `budget` | optional | UI ≤ 300 ms | marketing hero may run 600–1200 ms |
| `motion_level` | optional | from design dials, else 4/10 | 2 for regulated/public-sector, 7 for creative portfolio |

## Output

- **build**: the animation code, using the cheapest tool that works, with reduced-motion and hover gating.
- **review**: a findings table (from [templates/motion-review.md](templates/motion-review.md)) with standard violated, location, before/after, and a verdict.
- **find**: an opportunities table (moment, frequency, purpose, proposed motion, duration) plus rejected candidates with reasons.

## Supporting files

- [REFERENCE.md](REFERENCE.md): the four-question gate, duration budgets, easing curves, tool ladder, springs, interruption, reduced motion, view transitions, scroll-driven animation, performance, and vocabulary. Read at step 2 (gate) and when choosing easing/tools.
- [examples/recipes.css](examples/recipes.css): working CSS recipes (press, popover from trigger with `@starting-style`, dialog, toast, accordion height, skeleton, stagger, reduced motion). Copy and adapt in `build`.
- [templates/motion-review.md](templates/motion-review.md): review/opportunity report format.

## The ten standards

1. **Justified**: names its purpose (feedback, spatial consistency, state indication, preventing a jarring change, explanation, or delight on rare moments).
2. **Frequency-appropriate**: keyboard-triggered and 100+/day actions get no animation; tens/day get near-instant motion; occasional gets standard; rare gets delight.
3. **Responsive easing**: enters/exits use a strong ease-out; never `ease-in` on UI.
4. **Fast**: UI animations under 300 ms (see budgets).
5. **Physically correct**: popovers grow from their trigger (`transform-origin`), never from `scale(0)`; start at 0.92–0.97 with opacity.
6. **Interruptible**: rapidly triggered or gesture-driven motion uses transitions or springs that retarget, not keyframes that restart.
7. **GPU-friendly**: animate `transform`, `opacity` (and `clip-path`/`filter` sparingly); never width/height/top/left/margin.
8. **Accessible**: `prefers-reduced-motion` keeps fades but drops movement; hover motion gated by `@media (hover: hover) and (pointer: fine)`.
9. **Asymmetric**: deliberate actions (hold, destructive confirm) are slower; system responses snap; exits shorter than enters.
10. **Cohesive**: matches the product's personality and the rest of the UI.

## Steps

1. **Read the context**: stack, existing motion tokens (durations, easings), animation libraries already installed. Do not add a library if CSS can do it.
2. **Gate each candidate** (REFERENCE.md): frequency → purpose → can it fit `budget` → is it allowed at `motion_level` (table in step 5) → does motion help here? Reject anything that fails; record why.
3. **Branch by mode.**

**build**
4. Pick the cheapest tool: CSS transition (state changes) → `@starting-style` (entry without JS) → CSS keyframes (predetermined, must stay smooth under load) → Web Animations API (programmatic) → an animation library (springs, layout/shared-element, exit animations, gestures).
5. Pick properties (transform/opacity), origin (trigger for anchored UI, center for modals), easing and duration from the budget table, or a spring for gesture-driven motion. Tune by `personality` and cap by `motion_level`:

   | `personality` | Duration within budget | Easing / spring | Distance |
   |---|---|---|---|
   | `crisp` | lower third | `--ease-out`; springs bounce 0 | 2–4 px, scale ≥ 0.97 |
   | `soft` | middle | `--ease-out`; bounce ≤ 0.1 | 4–8 px, scale 0.95–0.97 |
   | `playful` | middle; delight moments may exceed | bounce 0.2–0.3 on rare moments only | 8–16 px |

   | `motion_level` | Allowed |
   |---|---|
   | 1–3 | state transitions and feedback only; no entrance or scroll motion |
   | 4–6 | plus one entrance sequence per page and enter/exit on overlays |
   | 7–10 | plus scroll-linked or choreographed scenes, on marketing surfaces only (`budget` applies) |
6. Handle interruption and exit: transitions over keyframes for toggles; exits 20–30% shorter than enters, smaller distance.
7. Add reduced-motion and hover gating. Test at 10% speed in devtools, then at full speed with rapid repeated triggering.

**review**
4. List every animation in the diff/target with its trigger, frequency, properties, duration, easing.
5. Check each against the ten standards; flag on sight: `transition: all`, `scale(0)`, `ease-in` on UI, motion on keyboard actions, UI > 300 ms without reason, center-origin popovers, keyframes on toasts/toggles, layout-property animation, missing reduced-motion, ungated hover motion.
6. Propose fixes in this order of preference: delete → reduce → fix easing → fix origin → make interruptible → move to GPU properties → asymmetric timing → polish (stagger, blur bridge) → accessibility/cohesion.
7. Verdict: approve, approve with fixes, or block (any HIGH: motion on high-frequency/keyboard paths, inaccessible motion, jank on core interactions).

**find**
4. Hunt where change is currently abrupt: elements appearing/disappearing, list insert/remove, route/tab changes, expanding content, async results, success/error moments, onboarding, empty states.
5. Gate each; keep only survivors. Report rejected candidates too.

## Checkpoints

- After the gate: share kept/rejected candidates before building more than one animation.
- Review mode: any block-level finding is raised before smaller polish.

## Worked example

`mode=review`, diff adds a dropdown and a command palette.

| Severity | Location | Standard | Before | After |
|---|---|---|---|---|
| HIGH | `CommandPalette.tsx:22` | frequency | 250 ms scale+fade on ⌘K open | remove animation; open instantly |
| MEDIUM | `Dropdown.css:8` | origin, physicality | `transform: scale(0); transform-origin: center` | `scale(0.96)` + `opacity: 0`, `transform-origin: var(--trigger-origin, top left)` |
| MEDIUM | `Dropdown.css:9` | easing | `transition: all 300ms ease-in` | `transition: opacity 160ms var(--ease-out), transform 160ms var(--ease-out)` |
| LOW | `Dropdown.css` | accessibility | no reduced-motion rule | under `prefers-reduced-motion: reduce`, keep opacity, drop scale |

Verdict: approve after removing the palette animation.

## Pitfalls

- Animating because it "feels premium" on something users see constantly.
- Long, symmetric, `ease-in-out` transitions on everything; the UI feels sluggish.
- Page-load entrance animations on content that is already there, delaying reading.
- Keyframe toasts that restart when a second toast arrives.
- Library springs or `x/y` shorthands that drop frames while the page is busy; prefer full `transform` strings or CSS.
- Forgetting reduced motion, or removing *all* feedback for it (keep opacity/color changes).
- Scroll-jacking and parallax on content pages.

## Done when

- [ ] Every animation names its purpose and passed the frequency gate.
- [ ] Durations within budget; easing ease-out (enter/exit) or ease-in-out (on-screen movement); no `ease-in` on UI.
- [ ] Only transform/opacity (or justified clip-path/filter) animate; no `transition: all`.
- [ ] Anchored UI grows from its trigger; nothing starts from `scale(0)`.
- [ ] Rapid re-triggering does not stutter or restart; exits are shorter than enters.
- [ ] Reduced motion and hover gating in place, verified in devtools.
