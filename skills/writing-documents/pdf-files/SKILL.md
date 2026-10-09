---
name: pdf-files
description: "Read, create and manipulate PDF files: extract text and tables, merge, split, fill forms, OCR scans, and render Markdown or HTML to PDF. Use when a .pdf is the input or output: \"fill this form\", \"merge these PDFs\", \"pull the tables out\", \"make a PDF report\". Not for editing Word, Excel or PowerPoint sources (use word-documents, excel-spreadsheets, powerpoint-decks)."
license: MIT
metadata:
  category: "writing-documents"
  version: "3.0.0"
---

# PDF

Scope: text and tables (to CSV/XLSX), scanned-page detection and OCR, merge, split, reorder, rotate, watermark/stamp, page numbers, encrypt/decrypt, metadata, image extraction, fillable and flat form filling with flattening, and PDF generation from Markdown or HTML. Not for breaking PDF passwords.

Pick the tool by job: **pypdf** for page-level structure (merge, split, rotate, encrypt, forms), **pdfplumber** for text with positions and tables, **pypdfium2** for rendering, **ReportLab** to draw new PDFs, **headless Chrome** to print HTML. Everything below is wrapped in `scripts/`.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `task` | yes | - | `extract`, `tables`, `merge`, `split`, `fill-form`, `create`, `watermark`, `ocr` |
| `input` | for all but create | - | `statement.pdf`, `a.pdf b.pdf`, `form.pdf` |
| `pages` | optional | all | `1-3,7,10-` (1-based) |
| `output` | optional | `<stem>-<task>.pdf` beside the input | `merged.pdf`, `tables.xlsx`, `parts/` |
| `values` | for forms | - | `values.json` (`{"full_name": "Akash Jha", "agree": true}`) |
| `password` | if encrypted | none | supplied by the file's owner |
| `content` | for create | - | `report.md`, `invoice.html` |
| `flatten` | optional | no | `--flatten` to lock filled values |

## Output

The requested artifact: a PDF (merged/split/filled/stamped/new) that opens cleanly and has been rendered and inspected, or extracted data (`.txt`, `.csv`, `.xlsx`, PNGs). Report page counts and anything that could not be extracted.

## Supporting files

- [scripts/pdf_tool.py](scripts/pdf_tool.py): `info, text, tables, merge, split, select, rotate, watermark, number, encrypt, decrypt, meta, images, render, scanned, compress`. Run with `-h`.
- [scripts/pdf_forms.py](scripts/pdf_forms.py): `fields` (+ fill template), `fill` (validated, optional `--flatten`), `words`, `grid`, `overlay` for flat forms.
- [scripts/md_to_pdf.py](scripts/md_to_pdf.py): Markdown → PDF with embedded Unicode font, header, "Page X of Y", tables, images.
- [scripts/html_to_pdf.sh](scripts/html_to_pdf.sh): HTML/CSS → PDF via headless Chrome (complex scripts, rich layout).
- [FORMS.md](FORMS.md): the full form-filling procedure, field types, flat-form coordinates. Read for any form task.
- [REFERENCE.md](REFERENCE.md): library recipes, CLI equivalents (qpdf, poppler, pdftk), OCR, JavaScript pdf-lib, troubleshooting. Read when a script doesn't cover the case.
- [templates/report.md](templates/report.md), [templates/invoice.html](templates/invoice.html): starting points for `create`.
- [examples/statement-tables.md](examples/statement-tables.md): end-to-end extraction example.

Dependencies: `pypdf`, `pdfplumber`, `pypdfium2`, `reportlab`, `openpyxl` (for xlsx table output); optional poppler-utils, qpdf, Chrome/Chromium (set `CHROME=/path` if it is not on PATH), ocrmypdf/tesseract.

## Steps

1. **Inspect first:** `python scripts/pdf_tool.py info in.pdf`. Note page count, sizes, encryption, form fields and pages with no text.
   - Encrypted → ask for the password; use `--password`. Never attempt to remove protection without it.
   - Pages without text layer → step 3 (OCR) before any extraction.
   - `form fields: N > 0` and the task is filling → [FORMS.md](FORMS.md).
2. **Extract** (if asked):
   - Text: `pdf_tool.py text in.pdf --pages 1-5` (`--layout` keeps columns aligned; check reading order on multi-column pages).
   - Tables: `pdf_tool.py tables in.pdf --pages 3-4 -o tables.xlsx`. No hits → `--strategy text` for tables without ruling lines. Always compare one extracted table against the rendered page.
   - Images: `pdf_tool.py images in.pdf -o imgs/`. Vector charts are not images; use `render`.
   - Large files: work per page range and summarize per section; don't pull 300 pages into context.
3. **OCR scanned pages:** `pdf_tool.py scanned in.pdf` lists them. If `ocrmypdf` exists → `ocrmypdf --skip-text in.pdf ocr.pdf` and continue with `ocr.pdf`. Else render + tesseract (REFERENCE "OCR"). If neither is installed, say so and offer installation; don't invent text. Spot-check OCR on numbers and names.
4. **Manipulate** (one command each; outputs never overwrite inputs):
   - Merge: `merge a.pdf b.pdf -o all.pdf --bookmarks` · Split: `split in.pdf --ranges "1-3,4-" -o parts/` or `--every 1`
   - Reorder/delete: `select in.pdf --pages "3,1,2,5-" -o out.pdf` · Rotate: `rotate in.pdf --pages 2 --angle 90 -o out.pdf`
   - Watermark: `watermark in.pdf --text "DRAFT" -o out.pdf` or `--stamp letterhead.pdf --under`
   - Page numbers: `number in.pdf -o out.pdf --skip-first` · Metadata: `meta in.pdf --title … --author … -o out.pdf`
   - Protect: `encrypt in.pdf --user-password … -o out.pdf` (AES-256) · Shrink: `compress in.pdf -o out.pdf`
5. **Create:**
   - Document-like (reports, letters) → write Markdown (`templates/report.md`) → `md_to_pdf.py report.md -o report.pdf --page a4 --author "…" --header "…"`.
   - Designed layout, brand CSS, or non-Latin scripts needing shaping (Devanagari, Arabic) → HTML (`templates/invoice.html`) → `html_to_pdf.sh invoice.html invoice.pdf`.
   - Pixel-precise drawing (labels, certificates, overlays) → ReportLab canvas (REFERENCE "ReportLab").
   - Source is a .docx/.pptx/.xlsx → convert with LibreOffice (see `word-documents` skill's `office_convert.py`), not by re-typing.
6. **Verify:** `pdf_tool.py render out.pdf -o qa/ --dpi 80` and look at every page (or a sample of ≥5 spread across a long file): order, rotation, clipped text, missing glyphs (boxes), table borders, filled values. Re-run `info` to confirm page count and metadata.

## Checkpoints

- After step 1: you know if the file is encrypted, scanned, or a form; the plan matches.
- After extraction: counts reported (pages, tables, rows) and one sample compared with the render.
- After manipulation: page count of output equals what the ranges imply (e.g. merge = sum of inputs).
- After fill: `pdf_forms.py fields out.pdf` reads back every value (unless flattened), and the render shows them.

## Worked example

Request: "Fill the onboarding form with my details and lock it."

```bash
python scripts/pdf_tool.py info form.pdf                 # pages: 1 ... form fields: 4
python scripts/pdf_forms.py fields form.pdf --template values.json
# p1  text      'full_name'  value=''      rect=[150.0, 690.0, 400.0, 710.0]
# p1  checkbox  'agree'      value='/Off'  ['/Yes']
# p1  choice    'country'    value='USA'   ['India', 'USA', 'UK']
# p1  radio     'plan'       value='/basic' ['/basic', '/pro']
cat > values.json <<'J'
{"full_name": "Akash Jha", "agree": true, "country": "India", "plan": "pro"}
J
python scripts/pdf_forms.py fill form.pdf values.json -o form-filled.pdf
python scripts/pdf_forms.py fields form-filled.pdf       # values read back
python scripts/pdf_forms.py fill form.pdf values.json -o form-final.pdf --flatten
python scripts/pdf_tool.py render form-final.pdf -o qa/ --dpi 80   # look at qa/page-1.png
```
A typo such as `"ful_name"` stops with `error: unknown field 'ful_name' (did you mean ['full_name']?)`, exit 2. Deliver `form-final.pdf` (locked) and keep `form-filled.pdf` (editable) in case corrections are needed.

## Pitfalls

- **Reading order ≠ extraction order** in multi-column layouts, headers/footers and sidebars. Crop (`page.crop(bbox)` in pdfplumber) or use `--layout` and check.
- **Scanned pages extract as empty strings**, silently. Run `scanned` first.
- **Form values invisible** in some viewers when appearance streams are missing: the fill script sets NeedAppearances; flatten when the recipient's viewer is unknown.
- **Checkbox "on" value isn't always `/Yes`** (`/On`, `/1`, a custom export name); `fields` shows the real one and `fill` maps `true` to it.
- **Unicode sub/superscripts and non-Latin text in ReportLab** render as black boxes with built-in fonts. Use `<sub>`/`<super>` markup and an embedded TTF; for scripts that need shaping use the HTML route.
- **Saving with a tool that drops the AcroForm** turns a fillable form into a flat one. Check `info` (form fields count) after any manipulation of a form.
- **Coordinates:** PDF origin is bottom-left in points (72/inch); pdfplumber's `top` is from the top. `pdf_forms.py words` already converts.
- **Rotated pages** (`/Rotate`) swap what "x" and "y" mean for overlays; render to check placement.
- **Lossy "compression"** (image downsampling via Ghostscript) can make scans unreadable; the built-in `compress` is lossless.

## Done when

- [ ] Output exists at the agreed path; inputs untouched.
- [ ] `info` on the output shows the expected page count, metadata and (for forms) field state.
- [ ] Every page (or a spread sample for long files) was rendered and inspected.
- [ ] Extracted data was spot-checked against the page; OCR'd text flagged as OCR.
- [ ] For forms: all requested fields filled with valid options, none left blank by a name typo; flattened if the user wanted it locked.
- [ ] Reply states what was done, counts, and any limits (scanned pages not OCR'd, fonts substituted, password needed).

Related skills: `word-documents`, `powerpoint-decks`, `excel-spreadsheets` (author in the source format, export last), `system-diagrams` (figures), `internal-communications` (content for reports).
