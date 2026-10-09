---
name: powerpoint-decks
description: "Create, read and edit PowerPoint decks (.pptx, .potx): build from an outline, fill a template, reorder slides, extract text, and visually QA every slide. Use when a task mentions a deck, slides, a presentation, a pitch, or a .pptx file, e.g. \"update last quarter's slides\". Not for Word documents (use word-documents), PDF handouts (use pdf-files) or standalone diagrams (use system-diagrams)."
license: MIT
metadata:
  category: "writing-documents"
  version: "3.0.0"
---

# Presentations (.pptx)

Scope: designed decks with native charts, tables and speaker notes; template fill or restyle; duplicate, delete and reorder slides without breaking the package; notes extraction; validation. Not for Google Slides edited through their API.

A `.pptx` is a ZIP of XML parts: `ppt/presentation.xml` (slide order in `<p:sldIdLst>`), `ppt/slides/slideN.xml`, layouts and masters, `ppt/notesSlides/`, `ppt/charts/`, `ppt/media/`, relationship files and `[Content_Types].xml`. Most breakage comes from those cross-references, so structural changes go through a script, never by hand.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `task` | yes | - | `create`, `read`, `edit`, `fill-template`, `restructure` |
| `source` | for read/edit | - | `q3-review.pptx`, `brand.potx`, `old.ppt` |
| `content` | for create | - | notes, a doc, data, or an outline |
| `audience_goal` | for create | ask once | "exec staff; approve 2 engineers" |
| `output` | optional | `<source-stem>-edited.pptx` or `<slug>.pptx` | `q4-review.pptx` |
| `template` | optional | built-in theme of `build_deck.py` | `brand.pptx` |
| `theme` | optional | navy/ice/coral, Cambria + Calibri | JSON in the outline |
| `aspect` | optional | 16:9, 13.333 × 7.5 in | template's size |
| `notes` | optional | yes, for any presented deck | `--require-notes` in QA |

## Output

One `.pptx` that opens in PowerPoint without a repair prompt, passes `pptx_validate.py` (with `--original` when built from a template) and `pptx_qa.py` with no ERROR, with every slide rendered and inspected. Charts are native and editable; speaker notes hold what the slide doesn't say. For reads: Markdown text from `pptx_outline.py --text-only`.

## Supporting files

- [REFERENCE.md](REFERENCE.md): package anatomy and units, XML editing rules for templates, python-pptx recipes and limits, pptxgenjs gotchas (when a JS generator is already in play), chart rules, conversions, troubleshooting. Read before any XML edit or when a script doesn't cover the case.
- [DESIGN.md](DESIGN.md): storyline, layout patterns, palettes, type scale, safe fonts, spacing, what to avoid, the visual QA checklist. Read before building or restyling any deck.
- [examples/update-quarterly-deck.md](examples/update-quarterly-deck.md): a real edit session (delete, duplicate, fill, new chart data, validate, QA) with outputs.
- [templates/outline.json](templates/outline.json): a 10-slide outline using every slide type in `build_deck.py`; copy and edit it. Image paths resolve relative to the outline; a missing image becomes a hatched placeholder with a warning, so the layout can be reviewed before the photo arrives.
- [scripts/](scripts/) (Python 3; `python-pptx`, `lxml`, `Pillow`; LibreOffice and poppler for rendering):
  - `build_deck.py outline.json -o deck.pptx [--template brand.pptx]`: designed deck from JSON (title, section, bullets, two_column, stats, chart, table, image, process, quote, closing).
  - `pptx_outline.py deck.pptx [--text-only|--layouts|--slides 2-4]`: text, notes, shapes with positions, tables, chart data; template layouts.
  - `thumbnail_grid.py deck.pptx [--cols 4 --max 12 --prefix name]`: labelled contact sheet(s), named after the deck.
  - `pptx_slides.py list|duplicate|delete|move|reorder|clean`: slide surgery with rels, content types, notes and charts kept consistent.
  - `pptx_replace.py deck.pptx -o out.pptx --pairs map.json [--slides] [--notes]`: fill slots across split runs, keeping formatting; `--list-tokens`.
  - `pptx_validate.py deck.pptx [--original src.pptx]`: package faults PowerPoint rejects.
  - `pptx_qa.py deck.pptx [--min-font 12 --require-notes]`: off-slide, overflow, overlap, contrast, leftover text, density.
  - `ooxml.py unpack|pack`, `office_convert.py`, `render_pages.py`: safe ZIP handling, headless LibreOffice, slide PNGs.

## Steps

1. **Classify the task.**
   - Read or summarise → `python scripts/pptx_outline.py deck.pptx --text-only`. If the design matters too, `thumbnail_grid.py deck.pptx`. Stop.
   - `.ppt` → `python scripts/office_convert.py old.ppt --to pptx` and continue with the result.
   - `.potx` → copy it to a `.pptx` name to work on; save the final as `.potx` only if the user wants a template back (REFERENCE "Templates").
   - New deck → step 2. Existing deck or template → step 4.
2. **Plan the story before any slide.**
   - Pin down audience, goal, time slot and the single decision or belief the deck should produce. If the user gave none, infer from the content and state your assumption in one line.
   - Write the slide titles first as full-sentence takeaways ("Churn fell 18% after the onboarding changes"). Read the titles alone: if they don't tell the story, fix them now.
   - One idea per slide; detail goes to speaker notes or an appendix. Rough budget: one slide per 1-2 minutes.
   - Pick a slide type per idea (DESIGN "Layout patterns"); never run three bullet slides in a row.
3. **Build.**
   - If there is no template: copy `templates/outline.json`, set the theme (DESIGN "Palettes"), fill the slides, then `python scripts/build_deck.py outline.json -o deck.pptx`.
   - If there is a brand template: `build_deck.py outline.json -o deck.pptx --template brand.pptx` keeps its masters, theme and light backgrounds (its sample slides are dropped unless `--keep-template-slides`). If the template has designed content slides you must reuse, go to step 4 instead.
   - If a slide needs something the builder lacks (icons, a custom diagram), add it afterwards with python-pptx (REFERENCE "python-pptx recipes"), or render a diagram via system-diagrams and place it as an image.
   - Numbers → native chart, one message per chart, the key point highlighted, axis starting at zero for bars. Only chart types the app has no native form for (Sankey, network) go in as images.
   - Go to step 6.
4. **Map an existing deck or template.**
   - `pptx_outline.py src.pptx --layouts` (which layouts exist, which are used) and `thumbnail_grid.py src.pptx` (look at it).
   - Map each piece of content to a source slide. Template slots rarely match your items: with 3 people for a 4-person slide, plan to delete the 4th person's whole group, not just its text.
5. **Restructure first, then edit content.**
   - All structural changes before any text edit, because duplication copies the slide as it currently is:
     `pptx_slides.py duplicate src.pptx 3 --after 3 -o s1.pptx`, `delete s1.pptx 7 8 -o s2.pptx`, `move`, `reorder 1,3,2,4-9` (lists every slide; it refuses to drop omitted slides unless `--drop-omitted`). Each run cleans orphaned parts.
   - Fill text: `pptx_replace.py s2.pptx -o s3.pptx --pairs map.json --slides 1-2` (add `--notes` to update speaker notes). Exit code 2 means a key wasn't found: check spelling and the `--slides` range rather than ignoring it.
   - Chart data, images, removing a shape group: python-pptx (REFERENCE "python-pptx recipes"). For anything python-pptx can't reach, `ooxml.py unpack`, edit with lxml following REFERENCE "XML editing rules", `ooxml.py pack`.
   - Never assign `text_frame.text = …` on a styled shape; it drops run formatting. Replace run text instead.
6. **Validate the file.** `python scripts/pptx_validate.py out.pptx` (add `--original src.pptx` when built from an existing deck or template). If it reports ERROR, fix the generator or edit step and rebuild; don't patch the packed zip by hand.
7. **QA content and layout.**
   - `pptx_qa.py out.pptx --require-notes` and fix every ERROR. Treat WARN as a prompt to look at that slide.
   - `pptx_outline.py out.pptx --text-only` and read it: missing content, typos, wrong order, stale numbers or dates.
   - `pptx_replace.py out.pptx --list-tokens` must report 0 tokens for a filled template.
8. **QA visually.** `python scripts/thumbnail_grid.py out.pptx` for the overview, and `python scripts/render_pages.py out.pptx --dpi 110` for full-size slides to inspect. Look at every slide with fresh eyes (a sub-agent if available) against DESIGN "Visual QA". Fix, re-render only the changed slides, re-check. Stop after the defects are fixed; don't polish indefinitely.
9. **Deliver.** Hand over the `.pptx` (not the renders unless asked), name the output, and list anything assumed (audience, numbers you computed, fonts substituted).

## Checkpoints

- After step 2: the titles alone tell the story, and each slide has a type. Show the title list to the user when the deck is long or the goal is unclear.
- After step 5: `pptx_slides.py list` shows the intended order and titles; nothing references a deleted slide.
- After step 6: 0 errors from `pptx_validate.py`.
- After step 8: every slide looked at as an image; no overflow, overlap, off-slide content, or leftover placeholder.

## Worked example

Brief: "Turn last quarter's retention deck into the Q4 version: drop the customer-quote slides, add a Q4 churn chart next to the Q3 one, update the title and stats headline."

```bash
python scripts/pptx_slides.py delete q3-review.pptx 7 8 -o step1.pptx
# clean: removed 5 unreferenced part(s): ppt/media/image1.jpg, ... slide7.xml, slide8.xml
python scripts/pptx_slides.py duplicate step1.pptx 3 --after 3 -o step2.pptx
# duplicated slide 3 -> new slide 4 (ppt/slides/slide7.xml)    <- its chart is a separate copy
python scripts/pptx_replace.py step2.pptx -o step3.pptx --pairs pairs.json --slides 1-2
python scripts/pptx_replace.py step3.pptx -o step4.pptx --pairs s4.json --slides 4 --notes
# python-pptx: chart.replace_data(...) on slide 4, value_axis.minimum_scale = 0, highlight December
python scripts/pptx_validate.py q4-review.pptx --original q3-review.pptx   # 0 error(s)
python scripts/pptx_qa.py q4-review.pptx                                    # 9 slides, 0 error(s), 0 warning(s)
python scripts/thumbnail_grid.py q4-review.pptx --cols 3
```

The grid showed that after `replace_data` the value axis had rescaled to start at 3.7%, exaggerating a flat line, which is why `minimum_scale = 0` is in the recipe. The full session with the JSON maps and outputs is in [examples/update-quarterly-deck.md](examples/update-quarterly-deck.md).

## Pitfalls

- **Editing XML through a non-preserving parser.** Python's `xml.etree` rewrites namespace prefixes and PowerPoint then refuses the file. Use lxml (the scripts do).
- **Copying slide files by hand.** A slide needs a rel from the presentation, a `sldId`, a content-type override and its own notes slide. Use `pptx_slides.py duplicate`.
- **Shared notes or charts after duplication.** Two slides pointing at one notes slide or one chart part means editing one changes both. `pptx_slides.py` copies both; other tools often don't.
- **Formatting loss.** `text_frame.text = …` collapses a paragraph to one unstyled run; labels lose bold, bullets lose their level.
- **Literal bullets.** Typing "•" gives double bullets on bulleted layouts. Use paragraph bullets (`a:buChar`) or let the layout supply them.
- **One paragraph for many items.** Each list item is its own `<a:p>`. Copy the sibling `<a:pPr>` so spacing matches.
- **Leading/trailing spaces vanish** unless the `<a:t>` has `xml:space="preserve"`.
- **Half-emptied template slots.** Clearing the text of a 4th card leaves an empty box with its icon. Delete the whole group.
- **Fonts that render at a different width in QA.** LibreOffice substitutes fonts it lacks, so overflow checks on Georgia, Garamond, Trebuchet or Aptos aren't trustworthy. Use the safe fonts in DESIGN or leave 10% slack.
- **Bars on a truncated axis**, a chart title repeating the slide title, a legend on a single series: all make the chart worse.
- **Stale renders.** Re-convert to PDF after every change; `render_pages.py` and `thumbnail_grid.py` delete old images first so you never inspect a stale image.
- **pptxgenjs specifics** (canvas size, `#` in colours, mutated option objects, stacked-label corruption): REFERENCE "pptxgenjs gotchas".

## Done when

- [ ] The output `.pptx` exists at the agreed path and the source file is unchanged.
- [ ] Slide titles read as a story; each slide makes one point.
- [ ] `pptx_validate.py` reports 0 errors (with `--original` for decks built from a source).
- [ ] `pptx_qa.py` reports 0 errors; remaining warnings were looked at and are intentional (e.g. a quote slide without a title).
- [ ] `--list-tokens` and the placeholder grep find nothing; no empty placeholders.
- [ ] Every slide was rendered and inspected after the last change.
- [ ] Charts are native, labelled, bars start at zero, the takeaway is visible.
- [ ] Speaker notes exist for presented decks; nothing assumed is left unstated in the hand-off.

Related skills: word-documents (Word handouts of the same content), pdf-files (PDF export and handouts), excel-spreadsheets (data behind charts), system-diagrams (diagram slides), cowrite-document (writing the narrative first), internal-communications (status-update decks).
