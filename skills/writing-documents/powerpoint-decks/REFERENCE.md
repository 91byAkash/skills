# PPTX reference

Read the section you need. Scripts mentioned live in `scripts/`.

## Contents

1. Package anatomy and units
2. Slide order, ids and notes
3. XML editing rules (templates)
4. python-pptx recipes
5. python-pptx limits
6. pptxgenjs gotchas
7. Charts
8. Templates (.potx) and masters
9. Conversions and reading
10. Troubleshooting

## 1. Package anatomy and units

```
[Content_Types].xml                 content type per part (Default by extension, Override per part)
_rels/.rels                         root -> ppt/presentation.xml, docProps
ppt/presentation.xml                sldMasterIdLst, notesMasterIdLst, sldIdLst (order), sldSz, notesSz, defaultTextStyle
ppt/_rels/presentation.xml.rels     rIds for masters, slides, theme, presProps...
ppt/slides/slideN.xml               one slide; N is a file name, not the position
ppt/slides/_rels/slideN.xml.rels    -> slideLayoutK, notesSlideJ, media, charts
ppt/slideLayouts/, ppt/slideMasters/, ppt/theme/theme1.xml
ppt/notesSlides/notesSlideJ.xml     speaker notes; its rels point back to its slide
ppt/charts/chartK.xml (+ rels -> embedded workbook)   ppt/media/   ppt/embeddings/
```

Units: 914,400 EMU per inch, 12,700 EMU per point, 360,000 per cm. EMU values in XML are integers; a float such as `7322313.9` makes python-pptx and PowerPoint fail. Font sizes in `sz` are hundredths of a point (`sz="1800"` = 18 pt). Common slide sizes: 16:9 at 13.333 × 7.5 in (PowerPoint's current default) or 10 × 5.625 in (same ratio, smaller canvas, other tools' default); 4:3 at 10 × 7.5 in. Mixing coordinates from one canvas into another is a frequent cause of shapes off the slide.

Shape tree: `p:sp` (shape/text box/placeholder), `p:pic`, `p:graphicFrame` (table, chart, SmartArt), `p:grpSp` (group, with its own child coordinate space `a:chOff`/`a:chExt`), `p:cxnSp` (connector). Text: `p:txBody` → `a:bodyPr` (insets `lIns`… in EMU, `anchor`, autofit) → `a:p` → `a:pPr` (level `lvl`, bullets, spacing) → `a:r` (`a:rPr` with `sz`, `b`, `i`, colour; `a:t` text). Placeholders (`p:nvPr/p:ph type= idx=`) inherit position and formatting from the layout when their own `a:xfrm`/properties are absent.

## 2. Slide order, ids and notes

- Order is the order of `p:sldId` elements in `p:sldIdLst`. Each has a unique `id` (≥ 256) and an `r:id` into the presentation rels.
- A slide exists as far as PowerPoint is concerned only when listed there. Unlisted slide parts still bloat the file; `pptx_slides.py clean` deletes anything unreachable from the root rels.
- A new slide needs: the part, its rels (layout at minimum), a content-type Override, a presentation rel, a `sldId`. `pptx_slides.py duplicate` does all of it and copies notes and charts so the copy is independent.
- Hidden slide: `show="0"` on `p:sld`. python-pptx: `slide._element.set("show", "0")`.
- Notes slide rels point at their slide and at the notes master; two slides sharing one notes slide is a corruption PowerPoint repairs by dropping notes (`pptx_validate.py` flags it).

## 3. XML editing rules (templates)

- Parse and write with lxml (`etree.fromstring` / `etree.tostring(..., xml_declaration=True, encoding="UTF-8", standalone=True)`). `xml.etree.ElementTree` renames namespace prefixes (`ns0:`) and the deck stops opening.
- Do structural changes (duplicate, delete, reorder) before content edits, and `clean` after deletions.
- One `a:p` per bullet or line. To add an item, deep-copy an existing sibling paragraph (keeps its `a:pPr` spacing and level) and change only its `a:t`.
- Bold labels and headings: `b="1"` on that run's `a:rPr`; keep the label and value in separate runs ("Owner:" bold, value regular).
- Bullets come from the layout/master. Override only when needed: `<a:buChar char="•"/>`, `<a:buAutoNum type="arabicPeriod"/>`, `<a:buNone/>`. Never type the bullet character into the text.
- Text with leading/trailing spaces needs `xml:space="preserve"` on `a:t`.
- When a slot is unused (3 items for a 4-slot layout), remove the whole group or every shape of that slot (picture, text, icon, connector). Then re-check alignment: the remaining items may need re-spacing.
- Never reorder the children of `p:presentation`; the schema order is sldMasterIdLst, notesMasterIdLst, handoutMasterIdLst, sldIdLst, sldSz, notesSz, …, extLst. Some generators place parts in unusual but valid positions; leave them where they are.
- Relationship ids are unique per rels file, not per package. Check before adding `rId7`.
- Autofit: `<a:normAutofit/>` in `a:bodyPr` asks PowerPoint to shrink text, but it only recomputes when the file is opened and edited in the app; LibreOffice and python-pptx won't shrink. Size boxes so text fits without it.
- Colours: `a:srgbClr val="1F2A5C"` (6 hex digits) or theme colours `a:schemeClr val="accent1"`. Transparency is a child: `<a:srgbClr val="000000"><a:alpha val="20000"/></a:srgbClr>` (20%).

## 4. python-pptx recipes

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.chart.data import CategoryChartData

prs = Presentation("in.pptx")                      # Presentation() for a blank 4:3 deck: set the size
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)

layout = next(l for l in prs.slide_layouts if l.name == "Title and Content")
s = prs.slides.add_slide(layout)
s.shapes.title.text = "Churn fell 18%"            # fine on a fresh placeholder
body = s.placeholders[1]                          # by idx; list with [(p.placeholder_format.idx, p.name) for p in s.placeholders]

# edit text without losing formatting: change runs, not text_frame.text
p = body.text_frame.paragraphs[0]
p.runs[0].text = "New wording"
for r in p.runs[1:]:
    r._r.getparent().remove(r._r)

# new paragraph cloned from an existing one (keeps spacing/bullets)
import copy
new_p = copy.deepcopy(p._p); p._p.addnext(new_p)

# delete a shape or a whole group
sh = next(x for x in s.shapes if x.name == "Card 4"); sh._element.getparent().remove(sh._element)

# replace a picture's image but keep its frame and crop
pic = next(x for x in s.shapes if x.shape_type == 13)
img_part, rid = pic.part.get_or_add_image_part("new.png")
pic._element.blipFill.blip.rEmbed = rid

# chart data (keeps the chart's formatting); bars back to a zero baseline afterwards
chart = next(x.chart for x in s.shapes if x.has_chart)
cd = CategoryChartData(number_format="0.0%"); cd.categories = ["Jul", "Aug"]; cd.add_series("Churn", [0.046, 0.043])
chart.replace_data(cd); chart.value_axis.minimum_scale = 0

# one bar in the accent colour
pt = chart.plots[0].series[0].points[1]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = RGBColor.from_string("E04E58")

# table cell
cell = tbl.cell(0, 0); cell.text = "Plan"; cell.fill.solid(); cell.fill.fore_color.rgb = RGBColor(0x1F, 0x2A, 0x5C)
cell.text_frame.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

# notes, alt text, hide
s.notes_slide.notes_text_frame.text = "Talk track…"
pic._element.nvPicPr.cNvPr.set("descr", "Bar chart of monthly churn")
s._element.set("show", "0")

# move a slide (python-pptx has no API; reorder the id list)
lst = prs.slides._sldIdLst; el = lst[5]; lst.remove(el); lst.insert(1, el)
prs.save("out.pptx")
```

Text measurement: python-pptx cannot measure rendered text. `pptx_qa.py` estimates fit (≈ 0.5 em average glyph width, 1.2 line height); confirm on the render.

## 5. python-pptx limits

| Need | Status | Do instead |
|---|---|---|
| Duplicate a slide | no API | `pptx_slides.py duplicate` |
| Delete a slide | no API | `pptx_slides.py delete` (or drop the `sldId` + rel and save; python-pptx omits unreachable parts) |
| SVG / EMF / WMF pictures | `add_picture` raises on them | rasterise to PNG (≥ 2× display size); to reuse template art, duplicate the slide or layout that contains it |
| Animations, transitions | not modelled | edit `p:timing` / `p:transition` XML, or leave to the user |
| SmartArt | read-only XML | replace with shapes or an image |
| Embedded fonts | not supported | ship a PDF alongside |
| `.potx` | refused (content type) | `potx.py to-pptx` first |
| Gradient fills | supported (`fill.gradient()`) but often looks dated | flat colour or a background image |

## 6. pptxgenjs gotchas

Only relevant when a JavaScript generator is already in use; otherwise `build_deck.py` covers the same ground in Python.

- Choose the canvas first: `pres.layout = "LAYOUT_WIDE"` (13.33 × 7.5 in). The default `LAYOUT_16x9` is 10 × 5.625 in, and coordinates past the edge are written as-is, so shapes silently fall off the slide.
- Colours are 6 hex digits without `#`. A `#` or an 8-digit value with alpha produces a file PowerPoint calls corrupt. Use `transparency` (0-100) on fills/images and `opacity` (0-1) on shadows; each is ignored on the other.
- Option objects are mutated in place (values converted to EMU on first use). Build a fresh object for each call; a shared `shadow` object yields wrong sizes on the second shape.
- Shadow `offset` must be ≥ 0; aim it with `angle` (270 = upward). Negative offsets corrupt the file.
- Letter spacing is `charSpacing`; `letterSpacing` is ignored without warning.
- Lists: `bullet: true` per item, `breakLine: true` on all but the last, spacing with `paraSpaceAfter`. A typed "•" doubles up; `lineSpacing` for spacing produces huge gaps.
- One `new pptxgen()` per output file.
- `rectRadius` needs the rounded-rectangle shape type.
- Text boxes have an internal margin; set `margin: 0` to align text with shapes at the same x.
- Notes via `slide.addNotes(text)`, once per slide.
- Charts render bare by default: set the palette (`chartColors`), data labels (`showValue`, `dataLabelPosition`), quiet axes and gridlines, hide the legend for one series.
- Stacked bar/column: data label position must be centre, inside end or inside base; outside end corrupts the file.
- Combo charts with a secondary axis need both value-axis and category-axis arrays (two entries each); otherwise axis ids are referenced but never declared and the chart is dropped as corrupt. `pptx_validate.py` reports both chart faults.
- Images from memory need a data URI prefix (`image/png;base64,...`). Icons from an icon library: render to SVG markup, rasterise to PNG ≥ 256 px, insert as image data.
- Validate every generated file; fix faults in the generator, not in the packed XML.

## 7. Charts

- Keep charts native (editable, data travels with the deck). Images only for types without a native form (Sankey, network, chord), with the data in notes or an appendix.
- Native extras python-pptx doesn't expose (trendline, error bars, combo line-on-bar) can be added in chart XML (`c:trendline` inside `c:ser`; a second `c:lineChart` in `c:plotArea` sharing the category axis id), or compute the extra series yourself and plot it as a normal series.
- Every `c:axId` referenced inside a `c:*Chart` must match a declared `c:catAx`/`c:valAx`/`c:dateAx` in the same plot area.
- Stacked groupings: no `outEnd` label position.
- `replace_data` resets axis scaling to auto; re-apply `minimum_scale = 0` for bars and re-apply point highlights if categories changed.
- Number formats: on data labels (`plot.data_labels.number_format`, `number_format_is_linked = False`) and tick labels separately.
- The embedded workbook (`ppt/embeddings/*.xlsx`) is what "Edit data" opens; python-pptx rewrites it on `replace_data`. Editing chart XML by hand without updating it leaves the two out of sync.

## 8. Templates (.potx) and masters

- `.potx` differs from `.pptx` only in the main content type (`…presentationml.template.main+xml`). `potx.py to-pptx brand.potx work.pptx`, work, then `potx.py to-potx` if the user wants a template back.
- Analyse first: `pptx_outline.py brand.pptx --layouts` (layout names, placeholders, usage) and `thumbnail_grid.py brand.pptx --prefix brand-thumbs`. Name grids after the deck, so two decks in one folder never overwrite each other.
- Prefer the template's layouts and placeholders over free text boxes so the master controls fonts, colours and positions.
- `build_deck.py --template` uses the template's masters and theme with its own slide designs on the Blank layout; light slides keep the master background.
- Theme fonts and colours live in `ppt/theme/theme1.xml` (`a:fontScheme`, `a:clrScheme`). Changing them there restyles every slide that uses theme references.
- `pptx_validate.py out.pptx --original template.pptx` marks faults the template already had as INHERITED so they don't hide new ones.

## 9. Conversions and reading

| From → To | Command |
|---|---|
| .ppt → .pptx | `office_convert.py old.ppt --to pptx` |
| .pptx → .pdf | `office_convert.py deck.pptx --to pdf` (hidden slides are included; delete them first if unwanted) |
| .pptx → slide PNGs | `render_pages.py deck.pptx --dpi 110` |
| .pptx → contact sheet | `thumbnail_grid.py deck.pptx` |
| .pptx → text/notes | `pptx_outline.py deck.pptx --text-only` |
| .odp ↔ .pptx | `office_convert.py file.odp --to pptx` |
| Extract media | `ooxml.py unpack deck.pptx d/` then `d/ppt/media/` |
| Google Slides / Keynote | export to .pptx in that app, then treat as a normal deck; expect font substitution |

LibreOffice rendering differs from PowerPoint in font metrics (see DESIGN "Typography"), some chart styling, and SmartArt. Treat the render as a close preview, not a pixel-exact one.

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| PowerPoint "needs repair" | missing rel target, missing content type, duplicate ids, chart axis/label fault | `pptx_validate.py`; fix the generator |
| `ValueError: invalid literal for int()` on open | float EMU written into XML | cast coordinates to int before setting |
| Shapes missing on the slide | coordinates for another canvas size | check `slide_width`/`height`; use one canvas |
| Text cut off in the render | box too small or font substituted | shorten/split/enlarge; safe fonts |
| Double bullets | typed "•" on a bulleted layout | remove the character; use paragraph bullets |
| Editing one chart changes another | duplicated slide shares the chart part | `pptx_slides.py duplicate` (copies charts) |
| Notes missing after duplicate | notes slide not copied or shared | `pptx_slides.py duplicate`; `pptx_validate.py` |
| File size grew after deleting slides | orphaned parts | `pptx_slides.py clean` |
| `UnidentifiedImageError` | SVG/EMF passed to `add_picture` | rasterise to PNG |
| Replace didn't match | text split across runs or in a table/notes | `pptx_replace.py` (spans runs, tables; `--notes`) |
| Bars look dramatic after new data | axis auto-scaled above zero | `value_axis.minimum_scale = 0` |
| LibreOffice conversion hangs | stale profile lock or a second instance | `office_convert.py` uses a throwaway profile and a timeout |
