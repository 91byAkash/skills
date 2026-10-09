# Example: bank statement tables → clean CSV with totals

Request: "Pull the transactions out of statement.pdf into a spreadsheet and tell me the net change."

## 1. Inspect
```bash
python scripts/pdf_tool.py info statement.pdf
```
```
pages: 2  encrypted: False  form fields: 0  bookmarks: 0
sizes (pt): 595.3x841.9  (612x792 Letter, 595x842 A4)
```
No "pages with no text layer" line, so no OCR needed.

## 2. Preview the tables
```bash
python scripts/pdf_tool.py tables statement.pdf
```
```
## p1_t1 (3 rows)
      Date     Description   Amount
2026-09-01 Opening balance 1,200.00
2026-09-04   Cloud hosting (310.50)
2026-09-15  Client payment 2,450.00

## p2_t1 (2 rows)
      Date       Description   Amount
2026-09-21 Software licences (129.99)
2026-09-30          Interest     3.10
```
Same header on both pages: safe to concatenate. Render page 1
(`pdf_tool.py render statement.pdf -o qa/ --pages 1`) and confirm the five
rows match what's printed.

## 3. Export and clean
```bash
python scripts/pdf_tool.py tables statement.pdf -o statement.csv
```
```python
import pandas as pd
df = pd.read_csv("statement.csv")
df["Amount"] = pd.to_numeric(df["Amount"].str.replace(",", "", regex=False)
                             .str.replace(r"^\((.*)\)$", r"-\1", regex=True))
print(round(df.Amount[1:].sum(), 2))   # 2012.61 (excluding the opening balance)
```
Amounts in parentheses are negatives; thousands separators removed before conversion.

## 4. Deliver
"5 rows from 2 pages → statement.csv. Net change for September excluding the
opening balance: +2,012.61. Checked page 1 against the render." For a
spreadsheet with live totals, hand the CSV to the `excel-spreadsheets` skill and use
`=SUM()` formulas instead of the Python total.
