# Deck design guide

Read before building or restyling a deck. The aim is slides an audience understands in the five seconds before the speaker talks over them.

## Contents

1. Storyline
2. Layout patterns
3. Palettes
4. Typography
5. Spacing and grid
6. Charts and tables
7. Images and icons
8. Avoid
9. Visual QA checklist

## 1. Storyline

- **Lead with the answer.** Title slide states the conclusion; the second slide gives the 2-3 reasons; the rest is evidence; the last slide is the ask.
- **Action titles.** Every content title is a sentence with a verb and, where possible, a number: "Enterprise onboarding is now the bottleneck" rather than "Onboarding".
- **Title test.** Reading titles alone, top to bottom, should give the argument. `pptx_outline.py deck.pptx --text-only | grep -A1 '^## Slide'` shows them in order.
- **Ratios.** One idea per slide, about one slide per 1-2 minutes of talk, at most ~6 bullets of up to ~12 words, around 40-70 words per slide for presented decks. Reading decks (sent, not presented) can carry more text, but then use full sentences and a clear reading order.
- **Notes carry the talk track.** What you would say goes in speaker notes, not in a text box.
- **Appendix** for backup tables, methodology and detail people may ask about.

Common shapes:

| Deck | Sequence |
|---|---|
| Decision / proposal | answer → why now → options compared → recommendation → risks → ask |
| Status / review | headline → numbers vs. plan → what changed → issues and asks → next period |
| Pitch | problem → who has it → solution → proof → business model → team → ask |
| Training | goal → concepts one per slide → worked example → practice → recap |

## 2. Layout patterns

Vary the layout; the same title-plus-bullets slide ten times reads as a document pasted into slides.

| Content | Pattern | `build_deck.py` type |
|---|---|---|
| Opening / closing statement | full-colour background, large title, one subtitle line | `title`, `closing` |
| A few headline numbers | 2-4 big stat cards, number 54-66 pt, label below | `stats` |
| Trend or comparison of values | native chart left, takeaway card right | `chart` |
| Before/after, pros/cons, option A/B | two tinted columns with headings | `two_column` |
| Steps, timeline, funnel | numbered circles joined by lines, short text under each | `process` |
| Exact figures people will read | table with a dark header row and banded rows, numbers right-aligned | `table` |
| Product, place, people | half-bleed photo on one side, text on the other | `image` |
| Voice of customer | large italic quote on a dark slide | `quote` |
| Chapter break in a long deck | kicker + title on dark background | `section` |
| Argument with a key caveat | bullets plus a callout card | `bullets` with `callout` |

Other patterns to build by hand when needed: 2×2 or 2×3 grid of cards (icon, bold heading, one line); icon rows (icon in a filled circle, heading, description); a map or screenshot with numbered callouts.

## 3. Palettes

Pick colours from the subject (finance: deep green and gold; healthcare: teal and warm grey; climate: forest and sand). One colour dominates (~60-70% of coloured area), one supports, one accent is reserved for the thing you want the eye to land on (the highlighted bar, the key stat).

Starter palettes (hex, no `#`):

| Name | Primary (dominant) | Secondary (tints, cards) | Accent (highlight) | Feel |
|---|---|---|---|---|
| Harbour | `1F2A5C` navy | `D6E2FB` ice | `E04E58` coral | default, confident |
| Ledger | `14452F` deep green | `E3EFE6` mint mist | `C9962B` brass | finance, sober |
| Clinic | `0E6E6E` teal | `E6F2F1` pale aqua | `E07A3F` apricot | health, calm |
| Granite | `2E3440` slate | `ECEFF4` fog | `5E81AC` steel blue | engineering, minimal |
| Ember | `7A1F2B` oxblood | `F6E9E7` blush | `F2A541` amber | bold, editorial |
| Field | `3D5A2A` olive | `EEF1E4` sage mist | `D9822B` rust | sustainability, food |
| Ink | `111111` near-black | `F2F2F2` light grey | `FF5A36` signal orange | dramatic, keynote |

- Dark title and closing slides, light content slides (a "sandwich") is a safe structure; an all-dark deck suits keynotes with few words.
- Backgrounds: white or the brand's colour. Avoid beige/cream defaults unless the brand uses them.
- Contrast: body text ≥ 4.5:1 against its background, large text (≥ 24 pt, or ≥ 18.5 pt bold) ≥ 3:1. `pptx_qa.py` checks solid-colour pairs. Coral-like accents often fail on light grey at small sizes; darken them (e.g. `E04E58` rather than a brighter coral).

## 4. Typography

LibreOffice renders the QA images and substitutes fonts it doesn't have, so the font names in the file must also be ones whose widths the preview gets right.

- **Safe (true widths in QA and present in Office installs):** Arial, Calibri, Cambria, Times New Roman, Courier New, Bookman Old Style, Century Schoolbook.
- **Character without risk:** a safe serif heading (Cambria, Bookman Old Style, Century Schoolbook) over a safe sans body (Calibri, Arial). This is the builder's default.
- **QA-unreliable (preview width differs):** Georgia, Trebuchet MS, Garamond, Palatino Linotype, Impact, Arial Black, Consolas, Calibri Light, Aptos. If the brand requires one, use it, leave ~10% slack in every box, and say in the hand-off that text fit was checked approximately.
- Never pick Aptos when you get to choose: there is no width-compatible substitute and older Office versions lack it.
- Embedding fonts is a desktop-app option, not something python-pptx can do; when exact fonts matter, also deliver a PDF.

| Element | Size |
|---|---|
| Slide title | 32-40 pt, bold or a serif heading face |
| Big number | 54-72 pt |
| Section/card heading | 20-24 pt bold |
| Body / bullets | 16-20 pt (never below 14 pt in a presented deck) |
| Captions, sources | 12 pt, muted colour |

Left-align body text and lists; centre only titles on title/section slides and short stat labels.

## 5. Spacing and grid

- Margins ≥ 0.5 in on every edge (the builder uses 0.6 in on a 13.333 × 7.5 in slide).
- Gaps between blocks: choose 0.3 or 0.5 in and use it everywhere.
- Align to a few vertical lines: the left margin, a column split (≈ 60/40 for chart + takeaway), and the right margin.
- Title zone the same height and position on every content slide; content starts at the same y.
- Set text-box insets to 0 when text must line up with a shape edge or line at the same x; otherwise the default inset (~0.1 in) makes it look off.
- Leave space. A slide with nothing to remove is usually too full.

## 6. Charts and tables

- One message per chart, stated in the title or a takeaway card; highlight the bar/point that proves it in the accent colour, grey or tint the rest.
- Bars start at zero. Lines may zoom, but label the axis so the zoom is visible.
- Direct data labels instead of gridline-reading; legend only when there are several series (or a pie/doughnut); no chart title when the slide title says it; no 3-D, no shadows on bars.
- Pies only for parts of a whole with ≤ 5 slices; otherwise a sorted bar.
- Format numbers in the chart (`0%`, `#,##0`, `$#,##0,"k"`) rather than in the source data.
- Tables: ≤ 7 rows and ≤ 6 columns on a slide; header row in the primary colour; numbers right-aligned with the same decimals; highlight the row that matters; put the full table in the appendix.
- Always add a source line (12 pt, muted) for external or computed figures.

## 7. Images and icons

- Images must carry meaning (the product, the place, the people, the screenshot being discussed). Decorative stock photos dilute.
- Crop to fill (half-bleed or full-bleed) rather than floating a small picture; keep faces and subjects away from the crop edge.
- Use ≥ 1600 px wide for full-bleed images; compress very large photos before inserting.
- Icons: one style family, one colour, sitting in a filled circle or rounded square in a tint of the primary colour. Rasterise SVG icons to PNG at ≥ 256 px if the tool can't insert SVG (python-pptx can't).
- Every meaningful image gets alt text (`pic._element.nvPicPr.cNvPr.set("descr", "...")`).

## 8. Avoid

- The same layout on every slide; styling one slide and leaving the rest plain.
- Text-only slides when a number, chart, diagram or image could carry the point.
- Centred paragraphs; tiny size contrast between title and body.
- Underline accents beneath titles, full-width header/footer bars, and coloured edge stripes on cards. These read as generated filler; use whitespace, a tint, or a soft shadow to set things apart.
- Low-contrast text or icons (light on light, dark on dark).
- Walls of text pasted from a document; full paragraphs in bullets.
- Clip-art, gradients for their own sake, more than two typefaces, more than one accent.
- Text that doesn't fit: shorten, split the slide, or enlarge the box. Never ship cut-off text.

## 9. Visual QA checklist

Run `thumbnail_grid.py` for the overview and `render_pages.py` for full-size slides. Look at every slide; the first render almost always has a few real problems.

1. Text overflowing or clipped at a box or slide edge (check first; most common).
2. Overlaps: text over shapes, lines through words, a source line colliding with content above.
3. Anything closer than ~0.3 in to another block or ~0.5 in to the slide edge; uneven gaps.
4. Columns, cards and titles not aligned to the same lines across slides.
5. Low-contrast text or icons.
6. Template decoration in the wrong place after text changed (an underline sized for a one-line title under a two-line title).
7. Leftover placeholder text, empty placeholders, orphaned icons or images from deleted slots.
8. Charts: axis from zero for bars, labels readable, highlight on the right point, no duplicated title.
9. Wrapping in boxes that are too narrow (one or two words per line).
10. Consistency: same title position, fonts, colours and gaps on every slide.

Fix, re-render only what changed, re-check those slides, then stop.
