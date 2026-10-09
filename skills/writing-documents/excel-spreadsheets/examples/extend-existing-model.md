# Example: extend an existing colour-coded model

Request: "Raise base growth to 20% and add 2031 to the projection."

## 1. Baseline
```bash
python scripts/xlsx_inspect.py existing.xlsx --inputs
```
```
Assumptions!B5: 1200 (font 0000FF, fill -)
Assumptions!B6: 0.18 (font 0000FF, fill FFFF00)     <- base growth
...
Assumptions!B13: 'Base' (font 0000FF, fill FFFF00)  <- scenario selector
```
```bash
python scripts/xlsx_audit.py existing.xlsx > before.txt   # inherited issues, if any
```

## 2. Edit inputs only where inputs live; extend patterns, don't retype them
```python
import copy, openpyxl
from openpyxl.formula.translate import Translator
wb = openpyxl.load_workbook("existing.xlsx")
wb["Assumptions"]["B6"] = 0.20                       # an input cell, keeps its blue/yellow style
m = wb["Model"]
m["G3"] = str(int(m["F3"].value) + 1)                # year label stays text: "2031"
m["G3"]._style = copy.copy(m["F3"]._style)
for r in range(4, 11):                               # every line item
    src = m[f"F{r}"]
    m[f"G{r}"] = Translator(src.value, origin=src.coordinate).translate_formula(f"G{r}")
    m[f"G{r}"]._style = copy.copy(src._style)
s = wb["Summary"]                                    # outputs must now point at G
s["B4"] = "=Model!G4"
s["B5"] = "=IFERROR((Model!G4/Model!B4)^(1/(COLUMNS(Model!B4:G4)-1))-1,0)"
s["B6"] = "=SUM(Model!B9:G9)"
s["B7"] = "=AVERAGE(Model!B10:G10)"
s["A4"] = "Revenue 2031"; s["A5"] = "Revenue CAGR 2026-2031"
wb.save("existing-edited.xlsx")
```
(The chart's data references also end at column F; extend them or note it.)

## 3. Verify
```bash
python scripts/recalc.py existing-edited.xlsx            # "status": "success", "total_formulas": 48
python scripts/xlsx_audit.py existing-edited.xlsx        # 0 error(s); only the known first-year seed warning
python scripts/recalc.py existing-edited.xlsx --write
python scripts/xlsx_inspect.py existing-edited.xlsx --range "Model!F3:G4"
```
```
     F3  '2030'
     G3  '2031'
     F4  '=E4*(1+growth)'  ->  2985.984
     G4  '=F4*(1+growth)'  ->  3583.1808
```
Hand-check: 1200 × 1.20^6 = 3583.2 ✓.

A first attempt wrote the CAGR exponent as `^(1/5)`; the audit flagged
`hard-coded constant(s) ['5']`. Counting the periods with `COLUMNS()` keeps the
formula right when another year is added.

## 4. Reply
"Base growth now 20% (Assumptions!B6). Added 2031 to every Model line and
pointed the Summary at it: 2031 revenue $3,583k, CAGR 20.0%. Recalculated with 0
errors. The Summary chart still ends at 2030; say if you want it extended."
