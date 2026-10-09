---
name: prototype-to-decide
description: "Build throwaway code that answers one named design question: a single-file HTML logic prototype for a state model, or 3-5 UI variants behind a switcher. Use when a workflow, state machine or data shape is hard to judge on paper, or nobody can pick a layout without seeing it (\"mock up options\", \"prototype this\"). Not for production features (use implement-plan)."
license: MIT
metadata:
  category: "plan-and-decide"
  version: "3.0.0"
---

# Prototype to Decide

A prototype is disposable code that answers a question. Name the question first; it decides the shape of the artifact.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `question` | yes | – | "Can an order be refunded after partial shipment?" |
| `branch` | optional | inferred: backend module → `logic`, page/component → `ui` | `logic`, `ui` |
| `variants` | optional (ui) | 3, max 5 | `4` |
| `host_route` | optional (ui) | the existing page the piece lives on | `/settings` |
| `location` | optional | next to the code it informs, named with `prototype` | `src/billing/refund.prototype.html` |
| `capture_branch` | optional | `prototype/<slug>` | `prototype/refund-rules` |

## Output

- **Logic**: one self-contained HTML file (inline CSS/JS, no build, opens by double-click) with a pure logic module, a live state panel, free-play action buttons, and tabbed guided scenarios.
- **UI**: N variants rendered on one route, switched via `?variant=` and a floating switcher bar (arrows + keys), hidden in production builds.
- Always: a short verdict note (question, what was tried, answer, chosen variant and why) posted to the issue/spec/commit, and the prototype preserved on `capture_branch`, not on main.

## Supporting files

- [templates/logic-prototype.html](templates/logic-prototype.html): starting file for the logic branch (state panel, actions, scenario tabs), pre-filled with the refund example below. Copy it to `location`, then replace `Logic.step`, the `actions` list and the `scenarios` list (scenario `steps` are indexes into `actions`; each scenario resets to `Logic.initial`).
- [templates/variant-switcher.html](templates/variant-switcher.html): framework-free switcher bar with keyboard support; shows the element whose `data-variant` matches `?variant=`. Paste into a plain page as-is, or port its behaviour to the project's framework for the UI branch.

## Steps

1. **Name the question.** Write it at the top of the prototype in visible text. If the user is unavailable and the branch is ambiguous, pick by surrounding code and state the assumption at the top.
2. **Pick the branch.** "Does this logic/state model feel right?" → logic. "What should this look like?" → UI. Getting this wrong wastes the whole prototype.

### Logic branch
3. **Write a pure module** in one `<script>` block of the copied template at `location` that could be lifted into the real code. Choose the shape that fits the question:
   - reducer `(state, action) => state` for discrete events on one state value;
   - explicit state machine when "which actions are legal now" is part of the question;
   - a few pure functions over plain data when there is no current state;
   - a small class only when the logic truly owns ongoing internal state.
   No DOM access inside the module; the page calls in, nothing calls out.
4. **Build the page** top to bottom: title + one-line question; current state as labelled fields (not raw JSON), re-rendered after every click with the changed field highlighted; one free-play button per action (illegal actions show why they were rejected); one tab per scenario with a plain-language setup, what to watch for, and the ordered buttons to press. Include the happy path, a tricky edge case, and an attempt at something that should be illegal. Use domain words, not code words. One accent colour, no animation.
5. **Hand it over**: send the file. The useful feedback is "wait, that shouldn't be possible".

### UI branch
3. **Find the host.** Use `host_route` if given. Otherwise prefer rendering variants inside the existing page (real header, real data, real density). Use a new throwaway route only if nothing could host it, and follow the project's routing convention with `prototype` in the path.
4. **Choose directions.** List `variants` variants (default 3, never more than 5), each with a name and the axis it explores (layout, information hierarchy, density, primary affordance, interaction model, motion). If two differ only in colour or copy, replace one.
5. **Build variants** as separate components (`VariantA`...) sharing the page's data fetching. Realistic copy and numbers, working interactions, project tokens. Read-only; point any mutation at a stub.
6. **Add the switcher**: fixed bottom-centre pill; prev/next arrows wrap around; label shows key and name ("B - Sidebar"); `←`/`→` cycle except when focus is in an input, textarea or contenteditable; updates the URL param via the router so reloads and links keep the variant; rendered only when not a production build.
7. **Verify yourself**: flip through every variant, check the console is clean, screenshot each if tooling exists.
8. **Present and stop**: a table of variant, axis, when it wins, what it costs. Do not pre-pick. Expect "header from B with the list from C".

### Both
9. **Capture**: record the verdict; commit the whole prototype to `capture_branch` and link that branch from the issue; fold only the validated decision into main, rewritten to production standard (tests, error handling). Remove the switcher and losing variants from main.

## Rules

1. Marked throwaway (file name, banner) and placed near the code it informs.
2. Starts with one command or a double-click.
3. No persistence unless persistence is the question; then use a scratch DB/file named "PROTOTYPE - wipe me".
4. No tests, no abstractions, only the error handling needed to run.
5. Show the full relevant state after every action or switch.

## Checkpoints

- Question written in the artifact before any code.
- Logic: the module has zero references to `document` or event handlers.
- UI: every variant has a distinct axis; no two share a layout skeleton.
- Before hand-off: you clicked through every scenario/variant yourself.

## Worked example

Question: "Can an order be refunded after partial shipment, and what amount?"
- Module: state machine with states `placed → partially_shipped → shipped → delivered`, actions `ship(items)`, `refund(items)`, `cancel()`. `refund` in `partially_shipped` allowed only for unshipped items; amount = item prices + proportional shipping.
- Scenarios: (1) happy path: ship all, deliver; (2) ship 1 of 3, refund the other 2 → state shows refund 2 × price + 2/3 shipping; (3) try `cancel()` after partial shipment → rejected with reason "items already shipped".
- PM clicks scenario 2 and says "shipping should not be refunded on partial refunds" → decision recorded on the issue; reducer lifted into `billing/refunds.ts` with the corrected rule; HTML kept on `prototype/refund-rules`.

## Pitfalls

- Prototyping without a question: you get a demo, not a decision.
- One polished option instead of several rough ones.
- Variants that share a layout component, so they cannot really differ.
- Mixing logic into click handlers, so nothing can be lifted.
- Reaching for a framework, bundler, or server for a logic demo.
- Letting the prototype become production code, or leaving the switcher on main.

## Done when

- [ ] The question is answered in writing with the evidence (scenario or variant) that answered it.
- [ ] The decision is recorded where the implementation will read it (issue, spec, ADR).
- [ ] Prototype preserved on `capture_branch` with a pointer from the issue; main holds only the validated decision.
- [ ] Nothing prototype-only (switcher, scratch DB, throwaway route) remains on main.
