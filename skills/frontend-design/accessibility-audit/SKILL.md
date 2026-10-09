---
name: accessibility-audit
description: "Audit a web UI against WCAG 2.2 AA with scans, keyboard and screen-reader passes, then fix issues at the source. Use when asked for an \"a11y audit\", \"WCAG compliance\", screen-reader or keyboard support, before a public launch, or when building dialogs, menus, tabs or forms. Not for visual polish (use ui-polish-review)."
license: MIT
metadata:
  category: "frontend-design"
  version: "3.0.0"
---

# Accessibility Audit

Scope: WCAG 2.2 A/AA success criteria, automated and static scans, keyboard and screen-reader walkthroughs, ARIA patterns for common widgets, and a findings report. Supports, but does not replace, a formal conformance review or legal opinion. Legal baselines differ by region: EU European Accessibility Act (applies since June 2025, via EN 301 549), US ADA Title II rule (WCAG 2.1 AA for state and local government), India RPwD Act 2016 and GIGW for government sites. WCAG 2.2 AA meets or exceeds each; name the one that applies in the report.

Automated tools catch roughly a third of barriers; a perfect score is not proof. Pair every scan with a keyboard pass and a screen-reader pass of the real flows.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `target` | required | — | `http://localhost:3000/checkout` or `src/components/` |
| `level` | optional | `AA` | `A`, `AAA` (selected criteria) |
| `flows` | optional | primary user path | "sign up → verify email → create first project" |
| `scope` | optional | pages in `flows` | component library only |
| `assistive_tech` | optional | keyboard + one screen reader available (VoiceOver, NVDA, TalkBack) | NVDA + Firefox and VoiceOver + Safari |
| `action` | optional | `report+fix` | `report` |
| `viewports` | optional | 1280 px and 320 px (reflow) | add 200% and 400% zoom |

## Output

- Report from [templates/audit-report.md](templates/audit-report.md): scope, method, summary by severity, and findings each with WCAG criterion, location, who is affected, evidence, fix, and status.
- Fixes applied at the source (component or template, not per page), with re-test evidence.
- A list of what was not tested (e.g. no screen reader on Android) so coverage is honest.

## Supporting files

- [REFERENCE.md](REFERENCE.md): WCAG 2.2 AA checklist grouped by area, the 2.2 additions, ARIA patterns for dialog, tabs, disclosure/menu, combobox, live regions, forms and errors, skip link, plus screen-reader quick commands. Read while testing and fixing.
- [templates/audit-report.md](templates/audit-report.md): report skeleton.
- [scripts/a11y-static.py](scripts/a11y-static.py): static scan of HTML/JSX/TSX/Vue/Svelte for common source-level failures (missing alt, unlabeled controls, clickable divs, positive tabindex, heading skips, missing `lang`, `aria-hidden` on focusables). Run first on source: `python3 scripts/a11y-static.py src/`.

## Severity

(When a ui-polish-review already reported an issue as HIGH, it maps to Critical or Serious here.)

- **Critical**: blocks a task for some users (cannot reach checkout by keyboard; form submit has no accessible name; focus trapped).
- **Serious**: major difficulty (contrast below 3:1 on body text; errors announced nowhere).
- **Moderate**: workaround exists (heading levels skip; redundant link text).
- **Minor**: small friction (decorative image announced).

## Steps

1. **Scope**: list pages/components and the flows to walk. With `level=AAA`, agree which AAA criteria are in scope (full AAA conformance is rarely achievable); with `level=A`, still report AA contrast failures as Serious. Note framework and component library (fixing a shared component fixes many pages).
2. **Static scan of source**: `python3 scripts/a11y-static.py <src>`; triage results (some are false positives where a component adds the attribute).
3. **Automated scan of rendered pages**: run an engine such as axe (browser extension, `@axe-core/cli`, or a test integration) or Lighthouse's accessibility audit. Use failing nodes to locate the component, not to search the repo blindly.
4. **Keyboard pass** of each flow: Tab/Shift+Tab order follows visual order; every interactive element reachable and operable (Enter/Space, arrows inside composite widgets, Esc closes overlays); focus always visible and not hidden behind sticky headers; no traps; focus moves into dialogs and returns to the trigger on close; skip link works.
5. **Screen-reader pass**: navigate by headings, landmarks, and form controls; check names, roles, states (expanded, selected, checked, invalid), announcements of async results and errors, and that decorative content is silent.
6. **Visual checks**: contrast of text, icons, borders, focus rings (both themes; sample colors in devtools and check each pair with the `design-system-tokens` skill's `scripts/contrast-check.py --pair FG BG` (or any WCAG contrast checker), or run it on `tokens.json` if the project has one); 320 px reflow without horizontal scroll; 200% text zoom and text-spacing override without clipping; not relying on color alone; motion respects reduced-motion; target size ≥ 24×24 px.
7. **Content checks**: page titles unique; `lang` set; link text meaningful out of context; form labels and instructions; error messages specific; captions/transcripts for media.
8. **Write findings** with criterion (e.g. "2.4.7 Focus Visible"), location, evidence (screenshot, snapshot excerpt, steps), affected users, fix.
9. **Fix at the source** (skip when `action=report`; list the proposed fix instead), preferring native HTML elements over ARIA (a `<button>` beats `div role="button"`). Re-run the automated scan and repeat the manual steps that found each issue.

## Checkpoints

- After step 3: share automated results count and any critical blockers early.
- Before changing shared components: confirm with the user; note pages affected.

## Worked example

Target: checkout, level AA.

| Severity | Criterion | Location | Evidence | Fix |
|---|---|---|---|---|
| Critical | 2.1.1 Keyboard | `PaymentMethod.tsx:30` | card options are `div onClick`; Tab skips them | radio group: `<fieldset><legend>Payment method</legend><input type="radio">…` |
| Critical | 4.1.2 Name, Role, Value | `PlaceOrder.tsx:12` | icon-only submit button announced as "button" | visible text "Place order" (or `aria-label`) and `aria-hidden` on the icon |
| Serious | 3.3.1 Error Identification | `AddressForm.tsx` | invalid postcode only turns border red | text error linked via `aria-describedby`, `aria-invalid="true"`, focus first invalid field on submit |
| Serious | 2.4.11 Focus Not Obscured | sticky footer | focused "Apply coupon" hidden behind footer | `scroll-padding-bottom` equal to footer height |
| Moderate | 1.3.1 Info and Relationships | order summary | headings jump h1 → h4 | use h2/h3 |

After fixes: axe 0 violations on the flow; keyboard and VoiceOver pass recorded.

## Pitfalls

- Treating an automated score of 100 as compliance.
- Adding ARIA to fix what a native element would solve; wrong ARIA is worse than none.
- `aria-label` that differs from visible text (breaks voice control; criterion 2.5.3).
- Removing focus outlines; hiding focus behind sticky elements.
- Placeholder used as the only label.
- Modals that do not trap focus, or do not return focus on close.
- Fixing symptoms page by page instead of in the shared component.
- Live regions added after content changes (they must exist in the DOM before the update).

## Done when

- [ ] Automated scan shows no remaining violations in scope (or each is justified as a false positive).
- [ ] Keyboard pass completes every flow with visible focus and no traps.
- [ ] Screen-reader pass confirms names, roles, states, and announcements on every flow.
- [ ] Contrast, reflow (320 px), zoom (200%), target size, and reduced motion checked.
- [ ] Each finding lists criterion, location, evidence, fix, and re-test status.
- [ ] Untested areas and assistive technologies are stated.
