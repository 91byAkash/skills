---
name: excel-spreadsheets
description: "Create, clean and edit spreadsheets (.xlsx, .xlsm, .csv) with live formulas, consistent formatting and a recalc + error audit before delivery. Use when a workbook is the main input or deliverable: \"build a model\", \"fix this workbook\", \"add a formula column\", \"turn this CSV into a formatted sheet\", \"why #REF!\". Not for Word reports (use word-documents) or slides (use powerpoint-decks)."
license: MIT
metadata:
  category: "writing-documents"
  version: "3.0.0"
---

# Spreadsheets (.xlsx)

Scope: .xlsx, .xlsm, .xltx, .csv, .tsv; named inputs, validation, charts, financial-model conventions, CSV→workbook conversion. Not for dashboard apps, database pipelines or Google Sheets API work.

Formulas stay live; inputs are visible and labelled; nothing ships with a formula error. **openpyxl** edits cells, formulas and styles; **pandas** moves bulk data; **LibreOffice** recalculates so you can see results.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `task` | yes | - | `build-model`, `edit`, `clean-data`, `convert`, `analyze`, `fix-errors` |
| `source` | for edit/clean/analyze | - | `budget.xlsx`, `export.csv`, `macros.xlsm` |
| `spec` | for build | - | tabs, inputs, outputs, periods, units, scenarios (see `templates/model-brief.md`) |
| `output` | optional | `<stem>-edited.xlsx` / `<slug>.xlsx` | `forecast-2027.xlsx` |
| `conventions` | optional | the existing file's, else the defaults in this skill | "inputs in yellow cells, $k" |
| `font` | optional | Arial (new files) / existing font (edits) | `Calibri` |
| `currency_unit` | optional | from data, stated in headers | `₹ lakh`, `$mm` |

## Output

An `.xlsx` (or `.xlsm` when macros exist) that: recalculates with `recalc.py` → `"status": "success"`; passes `xlsx_audit.py` with 0 errors (warnings explained or fixed); uses formulas for every derived number; marks inputs; documents assumptions and sources next to them. Plus a short reply naming key outputs and any assumptions you made.

## Supporting files

- [REFERENCE.md](REFERENCE.md): openpyxl/pandas recipes (styles, formats, names, validation, conditional formatting, charts, tables, protection, print setup), function compatibility list, model conventions in detail, CSV rules, troubleshooting. Read when building anything beyond a simple table.
- [scripts/recalc.py](scripts/recalc.py): LibreOffice recalculation; JSON error report with cell locations; `--write` stores computed values.
- [scripts/xlsx_audit.py](scripts/xlsx_audit.py): static lint (unsupported functions, missing `_xlfn.`, unquoted sheet names, missing sheets, broken names, cached errors, pattern breaks, short SUM ranges, hard-coded constants, % stored as whole numbers).
- [scripts/xlsx_inspect.py](scripts/xlsx_inspect.py): sheet overview; `--range` shows formula → value (+ `--styles`); `--inputs` lists input-styled cells.
- [scripts/csv_to_xlsx.py](scripts/csv_to_xlsx.py): CSV/TSV → typed, formatted sheets (IDs keep leading zeros, totals as `=SUM`).
- [scripts/model_template.py](scripts/model_template.py): runnable Assumptions → Model → Summary model to copy patterns from.
- [scripts/office_convert.py](scripts/office_convert.py), [scripts/render_pages.py](scripts/render_pages.py): conversions and page images.
- [templates/model-brief.md](templates/model-brief.md): fill in before building a model.
- [examples/extend-existing-model.md](examples/extend-existing-model.md): editing a colour-coded model without breaking it.

## Steps

1. **Inspect the source (if any).** `python scripts/xlsx_inspect.py in.xlsx`, then `--range` on the area you'll touch and `--inputs`. Run `xlsx_audit.py in.xlsx` and save its output: errors that exist **before** you edit are inherited, and you need that proof later.
   - `.xlsm` → keep `.xlsm` and load with `keep_vba=True`.
   - `xl/externalLinks` reported → the file depends on other workbooks; don't recalculate until you've copied any needed linked values in as constants (REFERENCE "External links").
   - Messy CSV/TSV → `csv_to_xlsx.py` first, then work on the workbook.
2. **Decide the conventions.**
   - Editing an existing file → its conventions win: fonts, colours, number formats, where inputs live, formula style. Write only to its input cells unless asked to change structure.
   - New file, no instructions → defaults: Arial; blue font for inputs, black for formulas, green for links to other sheets; yellow fill for key assumptions; units in headers (`Revenue ($k)`); years as text; negatives in parentheses; zeros as `-`; percentages stored as fractions.
3. **Plan the layout** (models): Assumptions (every input in its own labelled cell with a source note) → calculation sheets (one formula pattern per row, periods across columns) → Summary/outputs. Fill `templates/model-brief.md` when the request is bigger than a single sheet.
4. **Write 2-3 formulas first and check them.** Run `recalc.py out.xlsx --write` on a copy, then `xlsx_inspect.py --range` to confirm they pull the cells you meant. Only then fill the grid (copy patterns with `openpyxl.formula.translate.Translator`).
5. **Build or edit** with openpyxl (recipes in REFERENCE):
   - Formulas as strings: `ws["B10"] = "=SUM(B2:B9)"`, never a Python-computed number.
   - Lookups: `INDEX/MATCH`, `SUMIFS`, `IFERROR`; post-2007 functions with `_xlfn.` (`_xlfn.TEXTJOIN`, `_xlfn.IFS`, `_xlfn.MAXIFS`); no `XLOOKUP/FILTER/UNIQUE/SORT/SEQUENCE/LET`; sort/filter/de-duplicate in Python before writing.
   - Absolute refs (`$B$5`) or defined names for assumptions; quote sheet names with spaces (`'Q1 Inputs'!B2`); guard divisions (`IF(B4=0,0,B9/B4)`).
   - Merged cells: write the top-left cell only. Data validation for constrained inputs; freeze header rows; set column widths.
   - New workbook for others to fill in → add a short legend saying which cells to edit and one realistic example row. Never add example rows to a file you were asked to edit.
   - Set `wb.calculation.fullCalcOnLoad = True` so the spreadsheet app recomputes on open.
6. **Recalculate and audit.**
   ```bash
   python scripts/recalc.py out.xlsx          # must say "status": "success" (exit 0; exit 2 = errors found)
   python scripts/xlsx_audit.py out.xlsx      # 0 error(s); read every WARN
   ```
   - `errors_found` → fix each listed cell, rerun. A cell erroring in the *original* too: show the original's cached value as proof, then fix it or report it.
   - `suspect_functions` → that function isn't supported; rewrite it.
   - WARN "breaks the row pattern" → intended (first period, subtotal)? say so; otherwise fix.
7. **Spot-check numbers.** Recompute 2-3 key outputs by hand or with pandas from the inputs; reconcile totals to the source data (row counts, sums).
8. **Finish.** If previewers/pandas must read values, run `recalc.py out.xlsx --write` last (it stores computed values). Optionally render (`render_pages.py out.xlsx`) to check print layout. Report outputs, assumptions and anything inherited.

## Checkpoints

- Before editing: baseline audit saved; input cells identified.
- After step 4: sample formulas return the values you expect, not merely "no error".
- After step 6: `"status": "success"`, `total_errors: 0`, audit `0 error(s)`.
- Before delivery: no hard-coded results where a formula belongs; every hard-coded number has a label and source.

## Worked example

Request: "Build a 5-year revenue and profit projection with base/downside/upside scenarios."

```bash
python scripts/model_template.py -o forecast.xlsx --years 5 --start-year 2026 --currency "$" --unit "k"
python scripts/recalc.py forecast.xlsx
# {"status": "success", "total_formulas": 41, "total_errors": 0, ...}
python scripts/xlsx_audit.py forecast.xlsx
# WARN: Model!B4: =rev0*(1+growth) breaks the row pattern of its neighbours   <- first year seeds from the input; intended
# 0 error(s), 1 warning(s)
python scripts/recalc.py forecast.xlsx --write
python scripts/xlsx_inspect.py forecast.xlsx --range "Summary!A3:B7"
#  B4  '=Model!F4'  ->  2745.30930816
#  B5  '=IFERROR((Model!F4/Model!B4)^(1/(COLUMNS(Model!B4:F4)-1))-1,0)'  ->  0.18
```
Hand-check: 1200 × 1.18^5 = 2745.3 ✓. Switching `Assumptions!B13` to "Upside" changes every year because all formulas reference the `growth` name. Reply: outputs (2030 revenue $2,745k, cumulative net income $1,596k), where to change scenarios, and which inputs came from the user.

## Pitfalls

- **Hard-coded results.** A pasted total silently goes stale. Use formulas; compute in Python only for static exports, and say so.
- **`data_only=True` then save** replaces every formula with its last value, permanently. Use it only for reading.
- **No cached values after openpyxl writes**: pandas and `data_only` read `None` until you recalc (`--write`).
- **Unsupported/unprefixed functions** become `#NAME?`; LibreOffice also lowercases what it can't parse.
- **Spilling functions** (FILTER, UNIQUE, SORT, SEQUENCE) written by openpyxl lack spill metadata; only one cell fills even where they evaluate.
- **A green recalc isn't correctness**: off-by-one ranges and wrong rows evaluate fine. The audit flags short SUM ranges and pattern breaks; you still spot-check.
- **Percent as whole numbers**: 15 formatted `0%` shows 1500%. Store 0.15.
- **Years as numbers** display `2,026` with a thousands format and get summed by accident. Store as text labels.
- **Sheet names with spaces** unquoted → `#VALUE!`/`#REF!`. Quote them.
- **Re-saving with openpyxl** drops what it doesn't model: VBA (unless `keep_vba=True`), pivot caches, slicers, form controls, some chart formatting, images in older versions. Check with `xlsx_inspect.py` before/after; if critical, edit the XML directly (see `word-documents` skill's `ooxml.py`).
- **External links** lose their cached values on openpyxl save + recalc and turn into errors.
- **CSV**: IDs lose leading zeros, long numbers lose digits, dates flip day/month. Treat IDs as text, use ISO dates, state the encoding (UTF-8; add a BOM only if the user's spreadsheet app needs it).

## Done when

- [ ] Output saved with the right extension (`.xlsm` kept for macro files); source untouched.
- [ ] `recalc.py` → `"status": "success"`, 0 errors; `xlsx_audit.py` → 0 errors, warnings explained.
- [ ] Every derived number is a formula; inputs are marked and carry a source/assumption note.
- [ ] The user's literal spec is met: exact tab names, headers, and any formula they specified.
- [ ] Existing conventions preserved on edits; only intended cells changed.
- [ ] 2-3 key outputs hand-checked; totals reconcile to source data.
- [ ] Reply lists the key outputs, assumptions, and anything inherited or not fixed.

Related skills: `pdf-files` (tables out of PDFs), `word-documents` / `powerpoint-decks` (report or deck built on the numbers), `internal-communications` (sharing results), `system-diagrams` (data-flow figures).
