#!/usr/bin/env python3
"""Everyday PDF operations with pypdf / pdfplumber / pypdfium2 (pure Python).

Usage (pages are 1-based; ranges like "1-3,7,10-"):
  pdf_tool.py info IN.pdf [--json]                 # pages, sizes, metadata, encryption, form, text per page
  pdf_tool.py text IN.pdf [--pages 1-5] [--layout] [-o out.txt]
  pdf_tool.py tables IN.pdf [--pages 2] [-o tables.xlsx|tables.csv|dir/]
  pdf_tool.py merge A.pdf B.pdf C.pdf -o merged.pdf [--bookmarks]
  pdf_tool.py split IN.pdf --ranges "1-3,4-6,7-" -o outdir/      # or --every 1
  pdf_tool.py select IN.pdf --pages "3,1,2" -o reordered.pdf      # pick/reorder/delete
  pdf_tool.py rotate IN.pdf --pages 2 --angle 90 -o out.pdf
  pdf_tool.py watermark IN.pdf -o out.pdf --text "DRAFT" [--opacity 0.15] [--under]
  pdf_tool.py watermark IN.pdf -o out.pdf --stamp letterhead.pdf [--under]
  pdf_tool.py number IN.pdf -o out.pdf [--format "Page {n} of {total}"] [--skip-first]
  pdf_tool.py encrypt IN.pdf -o out.pdf --user-password U [--owner-password O]
  pdf_tool.py decrypt IN.pdf -o out.pdf --password P
  pdf_tool.py meta IN.pdf -o out.pdf --title T --author A [--subject S]
  pdf_tool.py images IN.pdf -o imgdir/             # embedded images as files
  pdf_tool.py render IN.pdf -o pngdir/ [--dpi 110] [--pages 1-2]
  pdf_tool.py scanned IN.pdf                       # which pages have no text layer (need OCR)
  pdf_tool.py compress IN.pdf -o out.pdf           # lossless: dedupe objects, recompress streams
"""
import argparse, io, json, logging, sys
from pathlib import Path

logging.getLogger("pdfminer").setLevel(logging.ERROR)  # font-descriptor noise on some generators


def parse_ranges(spec, n):
    """'1-3,7,10-' -> [0,1,2,6,9..n-1]; order preserved, 1-based input."""
    out = []
    for part in (spec or f"1-{n}").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            lo = int(a) if a else 1
            hi = int(b) if b else n
            step = 1 if hi >= lo else -1
            out.extend(range(lo - 1, hi - 1 + step, step))
        else:
            out.append(int(part) - 1)
    bad = [i + 1 for i in out if not 0 <= i < n]
    if bad:
        sys.exit(f"error: page(s) {bad} out of range 1-{n}")
    return out


def reader(path, password=None):
    from pypdf import PdfReader
    r = PdfReader(path)
    if r.is_encrypted:
        if r.decrypt(password or "") == 0:
            sys.exit(f"error: {path} is encrypted; pass the password (never try to guess or break it)")
    return r


def write(writer, out):
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as f:
        writer.write(f)
    print(out)


def cmd_info(a):
    import pdfplumber
    r = reader(a.input, a.password)
    info = {
        "file": a.input, "pages": len(r.pages), "encrypted": r.is_encrypted,
        "metadata": {k.lstrip("/"): str(v) for k, v in (r.metadata or {}).items()},
        "form_fields": len(r.get_fields() or {}),
        "outline_entries": len(r.outline) if r.outline else 0,
        "page_sizes_pt": [], "chars_per_page": [],
    }
    with pdfplumber.open(a.input, password=a.password or "") as pdf:
        for p in pdf.pages:
            info["page_sizes_pt"].append([round(float(p.width), 1), round(float(p.height), 1)])
            info["chars_per_page"].append(len(p.chars))
    sizes = {tuple(s) for s in info["page_sizes_pt"]}
    if a.json:
        print(json.dumps(info, indent=2))
        return
    print(f"pages: {info['pages']}  encrypted: {info['encrypted']}  form fields: {info['form_fields']}  bookmarks: {info['outline_entries']}")
    print("sizes (pt):", ", ".join(f"{w}x{h}" for w, h in sorted(sizes)), " (612x792 Letter, 595x842 A4)")
    for k, v in info["metadata"].items():
        print(f"{k}: {v}")
    empty = [i + 1 for i, c in enumerate(info["chars_per_page"]) if c < 20]
    if empty:
        print(f"pages with (almost) no text layer: {empty} -> scanned? see `scanned`")


def cmd_text(a):
    import pdfplumber
    chunks = []
    with pdfplumber.open(a.input, password=a.password or "") as pdf:
        for i in parse_ranges(a.pages, len(pdf.pages)):
            page = pdf.pages[i]
            txt = page.extract_text(layout=a.layout) or ""
            chunks.append(f"--- page {i + 1} ---\n{txt}")
    out = "\n\n".join(chunks) + "\n"
    if a.out:
        Path(a.out).write_text(out)
        print(a.out)
    else:
        sys.stdout.write(out)


def cmd_tables(a):
    # standard library csv + openpyxl only (pandas is not a pack requirement)
    import csv
    import pdfplumber
    frames = []
    settings = {"vertical_strategy": a.strategy, "horizontal_strategy": a.strategy} if a.strategy != "lines" else {}
    with pdfplumber.open(a.input, password=a.password or "") as pdf:
        for i in parse_ranges(a.pages, len(pdf.pages)):
            for j, t in enumerate(pdf.pages[i].extract_tables(settings)):
                if not t or len(t) < 2:
                    continue
                header = [h if h else f"col{k + 1}" for k, h in enumerate(t[0])]
                rows = [["" if c is None else c for c in r] for r in t[1:]]
                frames.append((f"p{i + 1}_t{j + 1}", header, rows))
    if not frames:
        print("no tables found; try --strategy text for tables without ruling lines", file=sys.stderr)
        sys.exit(2)
    out = a.out or "-"
    if out.endswith(".xlsx"):
        from openpyxl import Workbook
        wb = Workbook()
        wb.remove(wb.active)
        for name, header, rows in frames:
            ws = wb.create_sheet(name[:31])
            ws.append(header)
            for r in rows:
                ws.append(r)
        wb.save(out)
        print(out)
    elif out.endswith("/") or Path(out).is_dir():
        Path(out).mkdir(parents=True, exist_ok=True)
        for name, header, rows in frames:
            with open(Path(out) / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows([header] + rows)
        print(out)
    elif out.endswith(".csv"):
        # one file: rows of every table; a header row is repeated only when the columns change
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            last = None
            for name, header, rows in frames:
                if header != last:
                    w.writerow(header)
                    last = header
                w.writerows(rows)
        print(out)
    else:
        for name, header, rows in frames:
            print(f"## {name} ({len(rows)} rows)")
            print(" | ".join(map(str, header)))
            for r in rows:
                print(" | ".join(map(str, r)))
            print()


def cmd_merge(a):
    from pypdf import PdfWriter
    wr = PdfWriter()
    for path in a.inputs:
        start = len(wr.pages)
        wr.append(reader(path, a.password))
        if a.bookmarks:
            wr.add_outline_item(Path(path).stem, start)
    write(wr, a.out)


def cmd_split(a):
    from pypdf import PdfWriter
    r = reader(a.input, a.password)
    n = len(r.pages)
    outdir = Path(a.out)
    outdir.mkdir(parents=True, exist_ok=True)
    groups = [[i] for i in range(n)] if a.every == 1 else (
        [list(range(s, min(s + a.every, n))) for s in range(0, n, a.every)] if a.every else
        [parse_ranges(g, n) for g in a.ranges.split(",")])
    stem = Path(a.input).stem
    for g in groups:
        wr = PdfWriter()
        for i in g:
            wr.add_page(r.pages[i])
        name = f"{stem}_p{g[0] + 1}" + (f"-{g[-1] + 1}" if len(g) > 1 else "") + ".pdf"
        write(wr, outdir / name)


def cmd_select(a):
    from pypdf import PdfWriter
    r = reader(a.input, a.password)
    wr = PdfWriter()
    for i in parse_ranges(a.pages, len(r.pages)):
        wr.add_page(r.pages[i])
    write(wr, a.out)


def cmd_rotate(a):
    from pypdf import PdfWriter
    r = reader(a.input, a.password)
    wr = PdfWriter(clone_from=r)
    for i in parse_ranges(a.pages, len(r.pages)):
        wr.pages[i].rotate(a.angle)
    write(wr, a.out)


def text_overlay(w, h, text, opacity, size, color, angle=45):
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(w, h))
    c.setFillColor(HexColor("#" + color.lstrip("#")), alpha=opacity)
    c.setFont("Helvetica-Bold", size)
    c.translate(w / 2, h / 2)
    c.rotate(angle)
    c.drawCentredString(0, -size / 3, text)
    c.save()
    from pypdf import PdfReader
    return PdfReader(io.BytesIO(buf.getvalue())).pages[0]


def cmd_watermark(a):
    from pypdf import PdfWriter, PdfReader, Transformation
    r = reader(a.input, a.password)
    wr = PdfWriter(clone_from=r)
    stamp = PdfReader(a.stamp).pages[0] if a.stamp else None
    pages = parse_ranges(a.pages, len(r.pages))
    for i in pages:
        page = wr.pages[i]
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        mark = stamp or text_overlay(w, h, a.text, a.opacity, a.size or min(w, h) / 6, a.color)
        if stamp:  # scale a stamp page onto pages of a different size
            sw, sh = float(stamp.mediabox.width), float(stamp.mediabox.height)
            if (round(sw), round(sh)) != (round(w), round(h)):
                s = min(w / sw, h / sh)
                page.merge_transformed_page(mark, Transformation().scale(s, s), over=not a.under)
                continue
        page.merge_page(mark, over=not a.under)
    write(wr, a.out)


def cmd_number(a):
    from pypdf import PdfWriter, PdfReader
    from reportlab.pdfgen import canvas
    r = reader(a.input, a.password)
    wr = PdfWriter(clone_from=r)
    total = len(wr.pages)
    for i, page in enumerate(wr.pages):
        if a.skip_first and i == 0:
            continue
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=(w, h))
        c.setFont("Helvetica", a.size)
        n = i + 1 - (1 if a.skip_first else 0) + (a.start - 1)
        label = a.format.format(n=n, total=total - (1 if a.skip_first else 0) + (a.start - 1))
        x = {"center": w / 2, "right": w - a.margin, "left": a.margin}[a.align]
        draw = {"center": c.drawCentredString, "right": c.drawRightString, "left": c.drawString}[a.align]
        draw(x, a.margin * 0.6, label)
        c.save()
        page.merge_page(PdfReader(io.BytesIO(buf.getvalue())).pages[0])
    write(wr, a.out)


def cmd_encrypt(a):
    from pypdf import PdfWriter
    r = reader(a.input)
    wr = PdfWriter(clone_from=r)
    wr.encrypt(user_password=a.user_password, owner_password=a.owner_password or a.user_password, algorithm="AES-256")
    write(wr, a.out)


def cmd_decrypt(a):
    from pypdf import PdfWriter
    r = reader(a.input, a.password)
    write(PdfWriter(clone_from=r), a.out)


def cmd_meta(a):
    from pypdf import PdfWriter
    r = reader(a.input, a.password)
    wr = PdfWriter(clone_from=r)
    md = {f"/{k.capitalize()}": v for k, v in (("title", a.title), ("author", a.author), ("subject", a.subject), ("keywords", a.keywords)) if v}
    wr.add_metadata(md)
    write(wr, a.out)


def cmd_images(a):
    r = reader(a.input, a.password)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for pi, page in enumerate(r.pages):
        for img in page.images:
            name = out / f"p{pi + 1}_{img.name}"
            name.write_bytes(img.data)
            n += 1
            print(name)
    if not n:
        print("no embedded images (vector art is not an image; use `render`)", file=sys.stderr)


def cmd_render(a):
    import pypdfium2 as pdfium
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    doc = pdfium.PdfDocument(a.input, password=a.password)
    doc.init_forms()  # draw form-field values too, not just page content
    width = len(str(len(doc)))
    for i in parse_ranges(a.pages, len(doc)):
        path = out / f"page-{str(i + 1).zfill(width)}.png"
        doc[i].render(scale=a.dpi / 72, may_draw_forms=True).to_pil().save(path)
        print(path.resolve())


def cmd_scanned(a):
    import pdfplumber
    with pdfplumber.open(a.input, password=a.password or "") as pdf:
        need = []
        for i, p in enumerate(pdf.pages):
            chars, imgs = len(p.chars), len(p.images)
            # A scan is an image with no (or almost no) text. A sparse page with real
            # text and no images (divider, signature page) is not a scan.
            flag = chars == 0 or (chars < a.min_chars and imgs > 0)
            if flag:
                need.append(i + 1)
            note = "  <- no text layer" if flag else ("  (little text, no images: not a scan)" if chars < a.min_chars else "")
            print(f"page {i + 1}: {chars} chars, {imgs} images{note}")
    if need:
        print(f"OCR needed for pages {need}: `ocrmypdf --skip-text in.pdf out.pdf` (keeps existing text), "
              "or render + tesseract (see REFERENCE.md#ocr)")
    sys.exit(1 if need else 0)


def cmd_compress(a):
    from pypdf import PdfWriter
    r = reader(a.input, a.password)
    wr = PdfWriter(clone_from=r)
    for page in wr.pages:
        page.compress_content_streams()
    try:  # keyword names changed across pypdf versions
        wr.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    except TypeError:
        wr.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    write(wr, a.out)
    before, after = Path(a.input).stat().st_size, Path(a.out).stat().st_size
    print(f"{before:,} -> {after:,} bytes ({100 * after / max(before, 1):.0f}%)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def sp(name, fn, multi=False):
        p = sub.add_parser(name)
        if multi:
            p.add_argument("inputs", nargs="+")
        else:
            p.add_argument("input")
        p.set_defaults(fn=fn)
        p.add_argument("--password", help="password for an encrypted input (supplied by its owner)")
        return p

    p = sp("info", cmd_info); p.add_argument("--json", action="store_true")
    p = sp("text", cmd_text); p.add_argument("--pages"); p.add_argument("--layout", action="store_true"); p.add_argument("-o", "--out")
    p = sp("tables", cmd_tables); p.add_argument("--pages"); p.add_argument("-o", "--out"); p.add_argument("--strategy", choices=["lines", "text"], default="lines")
    p = sp("merge", cmd_merge, multi=True); p.add_argument("-o", "--out", required=True); p.add_argument("--bookmarks", action="store_true")
    p = sp("split", cmd_split); p.add_argument("-o", "--out", required=True); g = p.add_mutually_exclusive_group(required=True); g.add_argument("--ranges"); g.add_argument("--every", type=int)
    p = sp("select", cmd_select); p.add_argument("--pages", required=True); p.add_argument("-o", "--out", required=True)
    p = sp("rotate", cmd_rotate); p.add_argument("--pages"); p.add_argument("--angle", type=int, choices=[90, 180, 270, -90], default=90); p.add_argument("-o", "--out", required=True)
    p = sp("watermark", cmd_watermark); p.add_argument("-o", "--out", required=True); g = p.add_mutually_exclusive_group(required=True); g.add_argument("--text"); g.add_argument("--stamp")
    p.add_argument("--opacity", type=float, default=0.15); p.add_argument("--size", type=float); p.add_argument("--color", default="808080"); p.add_argument("--under", action="store_true"); p.add_argument("--pages")
    p = sp("number", cmd_number); p.add_argument("-o", "--out", required=True); p.add_argument("--format", default="Page {n} of {total}"); p.add_argument("--skip-first", action="store_true")
    p.add_argument("--start", type=int, default=1); p.add_argument("--size", type=float, default=9); p.add_argument("--align", choices=["center", "right", "left"], default="center"); p.add_argument("--margin", type=float, default=36)
    p = sp("encrypt", cmd_encrypt); p.add_argument("-o", "--out", required=True); p.add_argument("--user-password", required=True); p.add_argument("--owner-password")
    p = sp("decrypt", cmd_decrypt); p.add_argument("-o", "--out", required=True)
    p = sp("meta", cmd_meta); p.add_argument("-o", "--out", required=True)
    for f in ("title", "author", "subject", "keywords"):
        p.add_argument(f"--{f}")
    p = sp("images", cmd_images); p.add_argument("-o", "--out", required=True)
    p = sp("render", cmd_render); p.add_argument("-o", "--out", required=True); p.add_argument("--dpi", type=int, default=110); p.add_argument("--pages")
    p = sp("scanned", cmd_scanned); p.add_argument("--min-chars", type=int, default=20)
    p = sp("compress", cmd_compress); p.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    try:
        a.fn(a)
    except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()
