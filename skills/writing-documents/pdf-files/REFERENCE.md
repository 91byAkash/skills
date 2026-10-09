# PDF reference

## Which library for what

| Need | Use | Why |
|---|---|---|
| merge/split/rotate/encrypt/metadata/forms | `pypdf` | pure Python, keeps page objects intact |
| text with positions, words, tables | `pdfplumber` | char-level boxes; table finder with tunable strategies |
| render pages to images | `pypdfium2` (or `pdftoppm`) | fast, accurate rendering |
| draw new pages | `reportlab` | canvas for exact placement, Platypus for flowing documents |
| HTML/CSS to PDF | headless Chrome, WeasyPrint | full CSS, text shaping for all scripts |
| repair/linearize/lossless split from the shell | `qpdf` | robust with damaged files |
| OCR | `ocrmypdf` (wraps tesseract) | adds an invisible text layer, keeps the images |
| JavaScript in Node or browser | `pdf-lib` (edit, forms), `pdfjs-dist` (render/text) | |

## pypdf recipes

```python
from pypdf import PdfReader, PdfWriter, Transformation
r = PdfReader("in.pdf")
w = PdfWriter(clone_from=r)          # keeps forms, outlines, metadata
w.pages[0].rotate(90)                # clockwise, multiples of 90
w.insert_blank_page(width=612, height=792, index=1)
w.add_outline_item("Chapter 2", 4)   # bookmark to page 5
w.pages[0].merge_transformed_page(r.pages[1], Transformation().scale(0.5).translate(300, 0))  # 2-up
w.pages[0].cropbox.lower_left = (36, 36); w.pages[0].cropbox.upper_right = (576, 756)          # crop
w.add_metadata({"/Title": "Q3 Review", "/Author": "Akash Jha"})
w.encrypt(user_password="open", owner_password="perm", algorithm="AES-256")
with open("out.pdf", "wb") as f: w.write(f)
```
- `PdfWriter()` + `add_page` copies pages only; forms and outlines are lost. Use `clone_from` or `append(reader)` when they matter.
- `page.extract_text(extraction_mode="layout")` is a fallback when pdfplumber isn't installed.
- Remove pages: build a new writer with the pages you keep (`select` subcommand).

## pdfplumber recipes

```python
import pdfplumber
with pdfplumber.open("in.pdf") as pdf:
    p = pdf.pages[0]
    left = p.crop((0, 0, p.width / 2, p.height)).extract_text()      # one column
    words = p.extract_words()                                          # x0, x1, top, bottom
    tables = p.extract_tables({"vertical_strategy": "text", "horizontal_strategy": "text",
                               "snap_tolerance": 3, "intersection_tolerance": 5})
    p.to_image(resolution=100).debug_tablefinder().save("debug.png")  # see what it detected
```
- `lines` strategy (default) needs ruled tables; `text` works on whitespace-aligned tables; mix (`vertical: text`, `horizontal: lines`) for half-ruled ones.
- Multi-page tables: extract per page, drop the repeated header rows, concatenate.
- Numbers come out as strings with thousands separators and `(1,234)` negatives; clean in pandas: `pd.to_numeric(s.str.replace(r"[,$]", "", regex=True).str.replace(r"^\((.*)\)$", r"-\1", regex=True))`.

## ReportLab

- Canvas origin bottom-left, units points. `c.drawString(x, y, s)`, `c.drawRightString`, `c.drawCentredString`, `c.rect`, `c.line`, `c.drawImage(path, x, y, w, h, preserveAspectRatio=True, mask="auto")`.
- Platypus: `SimpleDocTemplate(path, pagesize=A4, leftMargin=54, …)`, flowables `Paragraph` (mini-HTML: `<b> <i> <u> <font> <link> <sub> <super> <br/>`), `Table` + `TableStyle`, `Image`, `Spacer`, `PageBreak`, `KeepTogether`, `ListFlowable`.
- Headers/footers: `doc.build(story, onFirstPage=fn, onLaterPages=fn)`; "Page X of Y" needs a two-pass canvas (see `md_to_pdf.py`).
- Fonts: built-ins (Helvetica, Times, Courier) cover Latin-1 only. Register a TTF (`pdfmetrics.registerFont(TTFont("Body", "DejaVuSans.ttf"))`) for anything else. ReportLab does not shape complex scripts (Indic, Arabic): use the HTML route.
- Escape `&`, `<`, `>` in Paragraph text (`html.escape`), or the parser errors.
- Table column widths must fit the frame (page width − margins), or the table overflows silently.

## Command-line equivalents

| Task | poppler / qpdf / pdftk |
|---|---|
| text | `pdftotext -layout -f 1 -l 5 in.pdf out.txt` |
| info / fonts | `pdfinfo in.pdf`, `pdffonts in.pdf` (shows embedded or not) |
| render | `pdftoppm -png -r 100 -f 1 -l 3 in.pdf page` |
| images | `pdfimages -png in.pdf img` (`-list` to inspect) |
| merge | `qpdf --empty --pages a.pdf b.pdf -- out.pdf` or `pdfunite a.pdf b.pdf out.pdf` |
| page range | `qpdf in.pdf --pages . 1-5 -- out.pdf` |
| rotate | `qpdf in.pdf out.pdf --rotate=+90:1-3` |
| decrypt (known password) | `qpdf --password=PW --decrypt in.pdf out.pdf` |
| repair | `qpdf in.pdf repaired.pdf` (rewrites xref) |
| linearize (fast web view) | `qpdf --linearize in.pdf out.pdf` |
| burst | `pdftk in.pdf burst output page_%03d.pdf` |
| lossy shrink | `gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -o out.pdf in.pdf` (check readability after) |

## OCR

Preferred: `ocrmypdf --skip-text --rotate-pages --deskew -l eng in.pdf out.pdf` (add `-l eng+hin` etc. for other languages; needs the tesseract language packs). Result keeps the page images and adds a searchable text layer.

Fallback without ocrmypdf:
```python
import pypdfium2 as pdfium, pytesseract
doc = pdfium.PdfDocument("scan.pdf")
for i in range(len(doc)):
    img = doc[i].render(scale=300 / 72).to_pil()
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    conf = [int(c) for c in data["conf"] if str(c) != "-1"]
    print(i + 1, sum(conf) / max(len(conf), 1), pytesseract.image_to_string(img)[:200])
```
- 300 dpi for body text; report mean confidence and flag pages under ~80.
- OCR mistakes cluster in digits (0/O, 1/l, 5/S): double-check amounts, IDs, dates.

## pdf-lib (JavaScript)

```js
import { PDFDocument, StandardFonts, rgb } from "pdf-lib";
const pdf = await PDFDocument.load(bytes);
const form = pdf.getForm();
form.getTextField("full_name").setText("Akash Jha");
form.getCheckBox("agree").check();
form.flatten();
const merged = await PDFDocument.create();
for (const src of [a, b]) { const d = await PDFDocument.load(src); (await merged.copyPages(d, d.getPageIndices())).forEach(p => merged.addPage(p)); }
```

## Accessibility and archiving

- Tagged PDF (screen readers) comes from the authoring tool (Word/LibreOffice export with "tagged PDF", Chrome print keeps HTML semantics better than ReportLab). Set document title and language.
- PDF/A for archiving: LibreOffice export filter `pdf:writer_pdf_Export:{"SelectPdfVersion":{"type":"long","value":"2"}}` or `ocrmypdf --output-type pdfa`.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `extract_text` returns gibberish | font without a ToUnicode map | OCR the page |
| Words run together or split | spacing heuristics | adjust `x_tolerance` in pdfplumber, or use `--layout` |
| Merge output missing form data | writer created without cloning | `PdfWriter(clone_from=…)` / `append` |
| `PdfReadError: EOF marker not found` | truncated/damaged file | `qpdf in.pdf fixed.pdf`, then retry |
| Black boxes instead of characters | glyph missing in font | embed a TTF that has them; HTML route for complex scripts |
| Huge output after merge | duplicated fonts/images | `pdf_tool.py compress` |
| Text upside down/sideways in overlay | page has `/Rotate` | rotate the overlay or normalize the page first |
