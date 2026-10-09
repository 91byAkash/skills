# Accessibility Reference (WCAG 2.2)

## Contents
- AA checklist by area
- New in 2.2
- Native first, ARIA rules
- Patterns: skip link, dialog, disclosure and menu, tabs, combobox, forms and errors, live regions, tables, media
- Visually hidden utility
- Screen-reader quick commands
- Tools

## AA checklist by area

**Structure and semantics**
- [ ] `<html lang>` set; language changes marked (`lang` on the element) — 3.1.1, 3.1.2
- [ ] Unique, descriptive `<title>` per page — 2.4.2
- [ ] Landmarks: one `<main>`, `<header>`, `<nav>` (labelled if several), `<footer>` — 1.3.1
- [ ] Headings in order, one h1, no skipped levels for styling — 1.3.1, 2.4.6
- [ ] Lists, tables, and form groups use real elements — 1.3.1
- [ ] Reading order in DOM matches visual order — 1.3.2

**Text alternatives and media**
- [ ] Informative images have alt that conveys purpose; decorative images `alt=""` — 1.1.1
- [ ] Icon-only controls have accessible names; icons inside labelled controls `aria-hidden="true"` — 1.1.1, 4.1.2
- [ ] Charts have a text summary or data table — 1.1.1
- [ ] Prerecorded video has captions; audio has transcripts; audio description where visuals carry meaning — 1.2.x
- [ ] No autoplaying audio > 3 s without controls — 1.4.2

**Color and visual**
- [ ] Text contrast ≥ 4.5:1 (large ≥ 3:1) — 1.4.3
- [ ] UI component boundaries, icons, focus indicators ≥ 3:1 — 1.4.11
- [ ] Information not by color alone (errors, required, status, links in text) — 1.4.1
- [ ] Reflow at 320 CSS px without 2-D scrolling (except tables, maps) — 1.4.10
- [ ] Text resizes to 200% without loss — 1.4.4
- [ ] Text spacing override (line height 1.5, paragraph 2×, letter 0.12, word 0.16 em) does not clip — 1.4.12
- [ ] Content on hover/focus (tooltips) dismissible (Esc), hoverable, persistent — 1.4.13
- [ ] Orientation not locked — 1.3.4

**Keyboard and focus**
- [ ] Everything operable by keyboard — 2.1.1; no traps — 2.1.2
- [ ] Focus order logical — 2.4.3; focus visible — 2.4.7
- [ ] Skip link or landmarks to bypass repeated blocks — 2.4.1
- [ ] Single-key shortcuts can be turned off or remapped — 2.1.4
- [ ] Focus not entirely hidden by sticky content — 2.4.11 (2.2)

**Pointer and motion**
- [ ] Target size ≥ 24×24 CSS px or enough spacing — 2.5.8 (2.2)
- [ ] Dragging has a single-pointer alternative — 2.5.7 (2.2)
- [ ] Actions fire on up-event or can be aborted — 2.5.2
- [ ] Accessible name contains visible label text — 2.5.3
- [ ] Moving/auto-updating content can be paused — 2.2.2; no flashing > 3/s — 2.3.1
- [ ] Respect `prefers-reduced-motion` for non-essential animation (2.3.3 is AAA but expected)

**Forms**
- [ ] Every control has a programmatic label — 1.3.1, 4.1.2; visible label — 3.3.2
- [ ] Required fields indicated in text, not only color/asterisk without explanation — 3.3.2
- [ ] Errors identified in text and linked to fields — 3.3.1; suggestions given — 3.3.3
- [ ] Legal/financial submissions reversible, checked, or confirmed — 3.3.4
- [ ] `autocomplete` tokens for personal data — 1.3.5
- [ ] No re-entering info already given in the same process — 3.3.7 (2.2)
- [ ] Authentication without cognitive tests (allow paste, password managers, or alternatives) — 3.3.8 (2.2)

**Predictability**
- [ ] No context change on focus or input without warning — 3.2.1, 3.2.2
- [ ] Consistent navigation and identification — 3.2.3, 3.2.4
- [ ] Help mechanisms in consistent place — 3.2.6 (2.2)

**Robust**
- [ ] Custom widgets expose name, role, state — 4.1.2
- [ ] Status messages announced without focus change — 4.1.3

## New in 2.2

2.4.11 Focus Not Obscured (Minimum), 2.5.7 Dragging Movements, 2.5.8 Target Size (Minimum), 3.2.6 Consistent Help, 3.3.7 Redundant Entry, 3.3.8 Accessible Authentication (Minimum). 4.1.1 Parsing was removed.

## Native first, ARIA rules

1. Use the native element when one exists: `<button>`, `<a href>`, `<input type="checkbox">`, `<select>`, `<dialog>`, `<details>`.
2. Do not change native semantics unnecessarily (`<h2 role="button">` → wrap a button in the heading instead).
3. Every interactive ARIA role must be keyboard operable.
4. Do not put `aria-hidden="true"` or `role="presentation"` on focusable elements.
5. Every interactive element needs an accessible name.

## Patterns

**Skip link**
```html
<a class="skip-link" href="#main">Skip to content</a> … <main id="main" tabindex="-1">
```
```css
.skip-link { position: absolute; left: -9999px; } .skip-link:focus { left: 1rem; top: 1rem; }
```

**Dialog**: prefer `<dialog>` with `showModal()` (built-in focus containment, Esc, inert background).
- Label with `aria-labelledby` pointing to its heading; describe with `aria-describedby` if needed.
- On open, focus the first meaningful control (or the heading with `tabindex="-1"`); on close, return focus to the trigger.
- Custom dialogs: `role="dialog" aria-modal="true"`, make the rest of the page `inert`, trap Tab, close on Esc.

**Disclosure and menus**
- Show/hide section: `<button aria-expanded="false" aria-controls="panel">` toggles `hidden` on the panel.
- Site navigation dropdowns are disclosures, not `role="menu"`. Reserve `menu`/`menuitem` for application menus with arrow-key navigation, Home/End, Esc returning focus to the button.

**Tabs**
```html
<div role="tablist" aria-label="Billing">
  <button role="tab" id="t1" aria-selected="true" aria-controls="p1">Invoices</button>
  <button role="tab" id="t2" aria-selected="false" aria-controls="p2" tabindex="-1">Payments</button>
</div>
<div role="tabpanel" id="p1" aria-labelledby="t1">…</div>
<div role="tabpanel" id="p2" aria-labelledby="t2" hidden>…</div>
```
Arrow keys move between tabs (roving tabindex); Tab moves into the panel.

**Combobox (autocomplete)**
- Input `role="combobox" aria-expanded aria-controls="listbox-id" aria-autocomplete="list"`, options `role="option"` inside `role="listbox"`, active option via `aria-activedescendant`.
- Down/Up move, Enter selects, Esc closes and keeps typed text; announce result counts with a polite live region.
- Prefer a well-tested library component over hand-rolling.

**Forms and errors**
```html
<label for="email">Email</label>
<input id="email" type="email" autocomplete="email" aria-describedby="email-hint email-err" aria-invalid="true" required>
<p id="email-hint">We send receipts here.</p>
<p id="email-err">Enter an email like name@example.com</p>
```
- On submit with errors: summary at top (links to fields) with focus moved to it, or focus the first invalid field.
- Group radios/checkboxes with `<fieldset><legend>`.

**Live regions**
- Put the region in the DOM on page load, then change its text: `<div aria-live="polite" class="visually-hidden" id="status"></div>`.
- `polite` for results/toasts; `assertive` (or `role="alert"`) only for urgent errors.
- Do not announce every keystroke; debounce search-result counts.

**Tables**: `<th scope="col|row">`, `<caption>` for the title, avoid layout tables; sortable headers use a button inside `<th>` and `aria-sort` on the `<th>`.

**Media**: `<track kind="captions" srclang="en" label="English" default>`; provide transcripts; never autoplay with sound.

## Visually hidden utility

```css
.visually-hidden {
  position: absolute !important; width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0 0 0 0); clip-path: inset(50%); white-space: nowrap; border: 0;
}
```

## Screen-reader quick commands

| Action | VoiceOver (macOS) | NVDA (Windows) | TalkBack (Android) |
|---|---|---|---|
| start/stop | Cmd+F5 | Ctrl+Alt+N / Insert+Q | volume up+down 3 s |
| next item | VO (Ctrl+Opt) + → | ↓ | swipe right |
| headings list | VO+U then ←/→ to Headings | Insert+F7 | reading controls → Headings |
| next heading | VO+Cmd+H | H | swipe up/down to Headings, then swipe right |
| landmarks | VO+U → Landmarks | D | reading controls → Landmarks |
| form controls | VO+U → Form controls | F | reading controls → Controls |
| activate | VO+Space | Enter / Space | double tap |

## Tools

- Automated: axe (extension, CLI, test integrations), Lighthouse accessibility audit, WAVE, Pa11y for CI.
- Contrast: browser devtools color picker, contrast checkers; check focus rings and borders too.
- Manual: keyboard only; screen readers above; browser zoom 200%/400%; OS reduced-motion and high-contrast/forced-colors modes (`@media (forced-colors: active)`).
- Linters: eslint-plugin-jsx-a11y, vue-a11y, svelte a11y warnings; enable in CI.
