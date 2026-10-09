#!/usr/bin/env python3
"""Turn CSV/TSV files into a tidy workbook: typed columns, leading zeros kept,
ISO dates as real dates, header style, frozen header, autofilter, sensible
widths, optional Excel table and totals row with live SUM formulas.

Usage:
  csv_to_xlsx.py data.csv -o data.xlsx
  csv_to_xlsx.py a.csv b.tsv -o book.xlsx --table --totals Amount,Qty
  csv_to_xlsx.py data.csv -o data.xlsx --text-cols "Zip,Account ID" --date-cols Date --money-cols Amount --currency "₹"

Each input becomes one sheet named after the file (max 31 chars).
Columns whose values look like IDs stay text automatically: leading zeros, 16+ digits,
or an all-digit column whose header names an identifier (id, code, zip, pin, phone, account, sku...).
Override either way with --text-cols.
"""
import argparse, csv, datetime as dt, re, sys
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

NUM_RE = re.compile(r"^-?\(?[\d,]*\.?\d+\)?%?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}(:\d{2})?)?$")


def sniff(path):
    sample = Path(path).read_text(encoding="utf-8-sig", errors="replace")[:4096]
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return "\t" if path.lower().endswith(".tsv") else ","


def convert(value, kind):
    v = value.strip()
    if v == "":
        return None
    if kind == "text":
        return v
    if kind == "date" or (kind == "auto" and DATE_RE.match(v)):
        try:
            return dt.datetime.fromisoformat(v.replace(" ", "T")) if ("T" in v or " " in v) else dt.date.fromisoformat(v)
        except ValueError:
            return v
    if NUM_RE.match(v):
        neg = v.startswith("(") and v.endswith(")")
        pct = v.endswith("%")
        n = v.strip("()%").replace(",", "")
        try:
            num = float(n) if "." in n else int(n)
        except ValueError:
            return v
        num = -num if neg else num
        return num / 100 if pct else num
    return v


# Header words that mark identifier columns: digits, but never quantities to sum or format with commas.
ID_HEADER = re.compile(r"(^|[^a-z])(id|code|zip|pin|pincode|postal|postcode|phone|mobile|account|acct|sku|ifsc|gstin|pan|ean|upc|isbn)([^a-z]|$)", re.I)


def column_kind(values, forced, header=""):
    if forced:
        return forced
    vals = [v.strip() for v in values if v.strip()]
    if vals and all(v.isdigit() for v in vals) and ID_HEADER.search(header.replace("_", " ")):
        return "text"  # pincode 560001 is a label, not 560,001
    if any(len(v) > 1 and v[0] == "0" and v.isdigit() for v in vals):
        return "text"  # 00123 is an ID, not 123
    if vals and all(len(v) >= 16 and v.isdigit() for v in vals):
        return "text"  # >15 digits lose precision as numbers (card/account numbers)
    return "auto"


def add_sheet(wb, path, a):
    delim = sniff(path)
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.reader(fh, delimiter=delim))
    if not rows:
        return
    header, body = rows[0], rows[1:]
    ws = wb.create_sheet(Path(path).stem[:31])
    forced = {}
    for name in a.text_cols:
        forced[name] = "text"
    for name in a.date_cols:
        forced[name] = "date"
    kinds = [column_kind([r[i] if i < len(r) else "" for r in body], forced.get(h), h) for i, h in enumerate(header)]
    ws.append(header)
    for r in body:
        ws.append([convert(r[i] if i < len(r) else "", kinds[i]) for i in range(len(header))])
    hdr_fill = PatternFill("solid", fgColor=a.header_fill)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF" if a.header_fill.upper() in ("1F3864", "305496", "000000") else "000000")
        c.fill = hdr_fill
        c.alignment = Alignment(vertical="center", wrap_text=True)
    n = ws.max_row
    for j, h in enumerate(header, start=1):
        col = get_column_letter(j)
        sample = [ws.cell(i, j).value for i in range(2, min(n, 200) + 1)]
        if h in a.money_cols:
            fmt = f'"{a.currency}"#,##0.00;("{a.currency}"#,##0.00);"-"'
        elif any(isinstance(v, float) and abs(v) <= 1 for v in sample) and h.lower().endswith(("%", "pct", "rate")):
            fmt = "0.0%"
        elif all(isinstance(v, (int, float)) or v is None for v in sample) and any(isinstance(v, float) for v in sample):
            fmt = "#,##0.00"
        elif all(isinstance(v, int) or v is None for v in sample) and kinds[j - 1] != "text":
            fmt = "#,##0" if not h.lower() in ("year", "fy") else "0"
        elif any(isinstance(v, (dt.date, dt.datetime)) for v in sample):
            fmt = "yyyy-mm-dd"
        else:
            fmt = "@" if kinds[j - 1] == "text" else "General"
        for i in range(2, n + 1):
            ws.cell(i, j).number_format = fmt
        width = max([len(str(h))] + [len(str(v)) for v in sample if v is not None]) + 2
        ws.column_dimensions[col].width = min(max(width, 8), 60)
    ws.freeze_panes = "A2"
    last_col = get_column_letter(len(header))
    if a.table:
        t = Table(displayName=re.sub(r"\W", "_", ws.title) or "Table1", ref=f"A1:{last_col}{n}")
        t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        ws.add_table(t)
    else:
        ws.auto_filter.ref = f"A1:{last_col}{n}"
    if a.totals:
        tr = n + 2
        ws.cell(tr, 1, "Total").font = Font(bold=True)
        for name in a.totals:
            if name in header:
                j = header.index(name) + 1
                col = get_column_letter(j)
                c = ws.cell(tr, j, f"=SUM({col}2:{col}{n})")
                c.font = Font(bold=True)
                c.number_format = ws.cell(2, j).number_format
    print(f"{path} -> sheet {ws.title!r}: {len(body)} rows x {len(header)} cols (delimiter {delim!r})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--table", action="store_true")
    ap.add_argument("--totals", default="", help="comma-separated columns to total with =SUM()")
    ap.add_argument("--text-cols", default=""); ap.add_argument("--date-cols", default=""); ap.add_argument("--money-cols", default="")
    ap.add_argument("--currency", default="$")
    ap.add_argument("--header-fill", default="1F3864")
    a = ap.parse_args()
    for k in ("totals", "text_cols", "date_cols", "money_cols"):
        setattr(a, k, [x.strip() for x in getattr(a, k).split(",") if x.strip()])
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for p in a.inputs:
        add_sheet(wb, p, a)
    wb.calculation.fullCalcOnLoad = True
    wb.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
