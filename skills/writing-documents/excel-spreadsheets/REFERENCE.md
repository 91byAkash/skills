# xlsx reference

## 1. Tool choice

| Job | Tool | Notes |
|---|---|---|
| cells, formulas, styles, names, validation, charts | `openpyxl` | writes formulas as text; no calculation engine |
| bulk read/write, cleaning, joins, pivots | `pandas` (`read_excel`, `to_excel`, `ExcelWriter(engine="openpyxl")`) | writes values only; formats lost unless styled after |
| quick text preview | `markitdown file.xlsx` if installed | no coordinates: don't plan edits from it |
| recalculation, conversion to/from .xls/.ods/.csv | LibreOffice via `scripts/recalc.py` / `office_convert.py` | |
| very large write-only exports | `openpyxl` `Workbook(write_only=True)` or `xlsxwriter` | xlsxwriter cannot read/edit existing files |
| read formulas *and* values | two `load_workbook` calls (`data_only=False` and `True`) | `xlsx_inspect.py --range` does it |

## 2. openpyxl recipes

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, NamedStyle
from openpyxl.utils import get_column_letter
wb = openpyxl.load_workbook("in.xlsx")            # keep_vba=True for .xlsm
ws = wb["Model"]

ws["B10"] = "=SUM(B2:B9)"
ws["B10"].number_format = '#,##0;(#,##0);"-"'
ws["B10"].font = Font(name="Arial", bold=True)
ws["A1"].fill = PatternFill("solid", fgColor="1F3864")      # fill_type "solid" or it won't show
ws.column_dimensions["A"].width = 30
ws.row_dimensions[1].height = 22
ws.freeze_panes = "B2"                                       # freezes row 1 and column A
ws.merge_cells("A1:F1")                                      # write ws["A1"] only
ws.auto_filter.ref = "A1:F200"
wb.calculation.fullCalcOnLoad = True
wb.save("out.xlsx")
```

Copy a formula pattern to new cells:
```python
from openpyxl.formula.translate import Translator
ws["G4"] = Translator(ws["F4"].value, origin="F4").translate_formula("G4")   # =E4*(1+growth) -> =F4*(1+growth)
```

Copy styles: `dst._style = copy.copy(src._style)`.

Insert rows/columns: `ws.insert_rows(5)` shifts cells but does **not** rewrite formulas that point at shifted cells, merged ranges, charts or defined names. Prefer appending, or rewrite affected formulas yourself and re-run the audit.

Defined names (openpyxl ≥ 3.1):
```python
from openpyxl.workbook.defined_name import DefinedName
wb.defined_names["tax"] = DefinedName("tax", attr_text="Assumptions!$B$11")
ws["C8"] = "=-MAX(C7,0)*tax"
```

Data validation:
```python
from openpyxl.worksheet.datavalidation import DataValidation
dv = DataValidation(type="list", formula1='"Base,Downside,Upside"', showErrorMessage=True)
ws.add_data_validation(dv); dv.add("B13")
DataValidation(type="decimal", operator="between", formula1="0", formula2="1")    # 0-100% input
DataValidation(type="list", formula1="=Lists!$A$2:$A$20")                         # list from a range
```

Conditional formatting:
```python
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule, FormulaRule
ws.conditional_formatting.add("B9:F9", CellIsRule(operator="lessThan", formula=["0"], font=Font(color="C00000")))
ws.conditional_formatting.add("B2:B50", ColorScaleRule(start_type="min", start_color="F8696B", end_type="max", end_color="63BE7B"))
ws.conditional_formatting.add("A2:F50", FormulaRule(formula=["$F2>1000"], fill=PatternFill("solid", fgColor="FFF2CC")))
```

Excel table (structured, filterable):
```python
from openpyxl.worksheet.table import Table, TableStyleInfo
t = Table(displayName="Sales", ref="A1:F200")      # name: letters/digits/_, unique, no spaces
t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
ws.add_table(t)
```
Structured references (`=SUM(Sales[Amount])`) are fine in Excel; keep plain ranges if LibreOffice verification matters.

Charts (native, update with the data):
```python
from openpyxl.chart import BarChart, LineChart, PieChart, ScatterChart, Reference
ch = LineChart(); ch.title = "Revenue"; ch.y_axis.title = "$k"; ch.x_axis.title = "Year"
data = Reference(ws, min_col=2, max_col=6, min_row=4, max_row=4)        # one series in a row
ch.add_data(data, from_rows=True, titles_from_data=False)
ch.set_categories(Reference(ws, min_col=2, max_col=6, min_row=3, max_row=3))
ch.height, ch.width = 7.5, 16                                           # cm
ws.add_chart(ch, "H3")
```
Combine bar + line: build both, `bar + line` with `line.y_axis.axId = 200; line.y_axis.crosses = "max"` for a secondary axis.

Comments (source notes): `ws["B5"].comment = Comment("Source: FY2025 10-K p.45", "analyst")`.

Protection: `ws.protection.sheet = True` plus `cell.protection = Protection(locked=False)` on input cells. It is a guard against accidents, not security.

Print setup: `ws.print_options.gridLines = False; ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1; ws.sheet_properties.pageSetUpPr.fitToPage = True; ws.print_title_rows = "1:3"`.

## 3. Function compatibility

| Category | Functions | Write as |
|---|---|---|
| Safe everywhere | SUM, SUMIFS, COUNTIFS, AVERAGEIFS, INDEX, MATCH, VLOOKUP, HLOOKUP, IF, IFERROR, AND, OR, ROUND, MIN, MAX, SUMPRODUCT, EOMONTH, EDATE, DATE, YEAR, TEXT, NPV, IRR, XNPV, XIRR, PMT, OFFSET (volatile) | bare |
| Post-2007, need prefix | TEXTJOIN, CONCAT, IFS, SWITCH, MAXIFS, MINIFS, IFNA, XOR, DAYS, STDEV.S, VAR.S, PERCENTILE.INC, RANK.EQ, CEILING.MATH, FLOOR.MATH, AGGREGATE | `_xlfn.TEXTJOIN(...)` |
| Avoid in generated files | XLOOKUP, XMATCH, FILTER, UNIQUE, SORT, SORTBY, SEQUENCE, RANDARRAY, LET, LAMBDA, TEXTSPLIT, VSTACK/HSTACK, TAKE/DROP | INDEX/MATCH; do the array work in Python. openpyxl can't write their spill metadata, and recalc needs LibreOffice 24.8+ (25.8+ for TEXTSPLIT, VSTACK/HSTACK, TAKE/DROP) |

Lookup patterns:
- Exact lookup: `=INDEX(Prices!$C:$C, MATCH($A2, Prices!$A:$A, 0))`
- Two-key lookup: `=SUMIFS(Data!$D:$D, Data!$A:$A, $A2, Data!$B:$B, B$1)` (numeric results)
- Not found → blank: `=IFERROR(INDEX(...), "")` (but don't wrap everything in IFERROR; it hides real errors)

## 4. Financial-model conventions (defaults for new models)

| Element | Convention |
|---|---|
| Hard-coded inputs, scenario levers | blue font `0000FF` |
| Formulas | black font |
| Links to another sheet | green font `008000` |
| Links to another file | red font `FF0000` (and avoid where possible) |
| Key assumptions / cells to fill | yellow fill `FFFF00` |
| Currency | `$#,##0;($#,##0);"-"`, unit in header: `Revenue ($mm)` |
| Percent | `0.0%`, stored as fraction |
| Multiples | `0.0x` |
| Years | text: `"2026"`; or `FY2026` labels |
| Negatives | parentheses |
| Sign convention | state it (costs negative, or positive and subtracted) and keep it everywhere |

Structure: Inputs → Calculations → Outputs; one formula per row copied across periods; no constants inside formulas (`=B5*(1+$B$6)`, not `=B5*1.05`); subtotal rows visually separated (top border); checks row (`=IF(ABS(BS_total-0)<0.01,"OK","CHECK")`) for balance sheets; circular references only with iterative calculation explicitly enabled and documented (better: avoid).

Document hard-coded numbers where the reader sees them: a Notes column or cell comment, e.g. `Source: FY2025 annual report, p.45, revenue note` or `Provided by user on 2026-10-08`.

## 5. pandas

```python
df = pd.read_excel("in.xlsx", sheet_name="Data", dtype={"Account ID": str}, header=0)   # IDs as text
all_sheets = pd.read_excel("in.xlsx", sheet_name=None)                                  # dict of frames
df = pd.read_csv("in.csv", dtype=str, encoding="utf-8-sig", sep=None, engine="python")   # sniff delimiter
with pd.ExcelWriter("out.xlsx", engine="openpyxl") as xw:
    df.to_excel(xw, sheet_name="Data", index=False)
```
After `to_excel`, reopen with openpyxl to add formats, widths, freeze panes and formulas. `read_excel` returns cached values only: for a file openpyxl just wrote, recalc with `--write` first.

Cleaning checklist: trim whitespace; unify case for keys; parse dates with explicit `format=`; numbers with separators/parentheses (`(1,234)` → -1234); drop exact duplicates and report how many; detect header rows that aren't on row 1 (`header=None`, then locate); unpivot wide month columns with `melt`; report every transformation.

## 6. CSV/TSV

- Write UTF-8; add a BOM (`encoding="utf-8-sig"`) when the file will be double-clicked open in a spreadsheet app that otherwise mis-detects encoding.
- Quote fields containing delimiter, quotes or newlines (`csv.QUOTE_MINIMAL` does it).
- ISO dates `YYYY-MM-DD`; IDs and phone numbers as text; numbers without thousands separators.
- Leading `=`, `+`, `-`, `@` in user-supplied text can execute as formulas when opened (CSV injection): prefix with `'` when exporting untrusted data.

## 7. External links

A formula like `='[1]Returns'!$B$2` refers to another workbook (index 1 in `xl/externalLinks/`). Only the cached value is in this file. openpyxl drops cached values on save, and LibreOffice can't open the linked file during recalc, so the values become errors and the links can vanish. Before saving: read those cells with `data_only=True` from the original, and either paste the values as constants (with a note "value from <file> as of <date>") or leave the workbook unsaved by openpyxl. `recalc.py` refuses to run on linked files unless `--force`.

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `#NAME?` | unsupported or unprefixed function, typo, undefined name | audit lists it; prefix with `_xlfn.` or rewrite |
| `#REF!` | deleted/shifted cell, missing sheet | audit "missing sheet"; rewrite reference |
| `#VALUE!` | text in arithmetic, unquoted sheet name with space | clean inputs; quote names |
| `#DIV/0!` | empty denominator | `IF(den=0,0,num/den)` |
| `#SPILL!` | dynamic array blocked | don't use spilling functions in generated files |
| All formulas read `None` | never recalculated | `recalc.py --write` |
| Numbers stored as text (green triangles) | written as strings | convert to float/int before writing |
| Dates show as 46000 | number format missing | `number_format = "yyyy-mm-dd"` |
| Macros gone | saved without `keep_vba=True` or as .xlsx | reload original with `keep_vba=True`, save as .xlsm |
| LibreOffice timed out | huge file or hung instance | `--timeout 180`; the script uses a fresh profile each run |
