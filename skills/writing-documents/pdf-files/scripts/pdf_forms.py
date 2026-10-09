#!/usr/bin/env python3
"""Fill PDF forms: fillable (AcroForm) fields by name, or flat forms by
drawing text at coordinates found from the page's own labels.

Usage:
  pdf_forms.py fields FORM.pdf [--template values.json]   # list fields; write a fill template
  pdf_forms.py fill FORM.pdf values.json -o filled.pdf [--flatten]
  pdf_forms.py words FORM.pdf --page 1 [--grep "Name|Date"]   # label positions, PDF points
  pdf_forms.py grid FORM.pdf --page 1 -o grid.png [--step 50]  # page image with coordinate grid
  pdf_forms.py overlay FORM.pdf entries.json -o filled.pdf     # flat (non-fillable) forms

values.json (fill):  {"full_name": "Akash Jha", "agree": true, "country": "India"}
  - checkbox: true/false (mapped to the box's own on-state, e.g. /Yes or /On)
  - radio group: one of the export values listed by `fields`
  - choice/list: one of the listed options
entries.json (overlay): [
  {"page": 1, "label": "Name:", "text": "Akash Jha"},             # placed right of the label
  {"page": 1, "label": "Date", "below": true, "text": "2026-10-08"},
  {"page": 1, "x": 400, "y": 640, "text": "X", "size": 12}       # absolute, origin bottom-left
]
Unknown field names, invalid options and missing labels are errors (exit 2),
so nothing is silently left blank.
"""
import argparse, difflib, io, json, logging, re, sys
from pathlib import Path

logging.getLogger("pdfminer").setLevel(logging.ERROR)


def field_kind(f):
    ft = f.get("/FT")
    flags = int(f.get("/Ff", 0))
    if ft == "/Btn":
        return "radio" if flags & (1 << 15) else ("button" if flags & (1 << 16) else "checkbox")
    return {"/Tx": "text", "/Ch": "choice", "/Sig": "signature"}.get(ft, str(ft))


def on_states(annot_or_field):
    states = set()
    objs = [annot_or_field] + [k.get_object() for k in annot_or_field.get("/Kids", [])]
    for o in objs:
        ap = o.get("/AP")
        if ap and "/N" in ap:
            states |= {k for k in ap["/N"].keys() if k != "/Off"}
    return sorted(states)


def collect(path):
    from pypdf import PdfReader
    r = PdfReader(path)
    if r.is_encrypted:
        r.decrypt("")
    fields = r.get_fields() or {}
    pages = {}
    for pi, page in enumerate(r.pages):
        for a in page.get("/Annots", []) or []:
            a = a.get_object()
            if a.get("/Subtype") != "/Widget":
                continue
            name, node = a.get("/T"), a
            parts = []
            while node is not None:
                if node.get("/T") is not None:
                    parts.append(str(node["/T"]))
                node = node.get("/Parent").get_object() if node.get("/Parent") else None
            full = ".".join(reversed(parts))
            pages.setdefault(full, {"page": pi + 1, "rect": [round(float(x), 1) for x in a.get("/Rect", [])]})
    out = []
    for name, f in fields.items():
        kind = field_kind(f)
        info = {"name": name, "type": kind, "value": str(f.get("/V")) if f.get("/V") is not None else None}
        info.update(pages.get(name, {}))
        if kind in ("checkbox", "radio"):
            info["states"] = on_states(f) or ["/Yes"]
        if kind == "choice":
            info["options"] = [o[1] if isinstance(o, list) else str(o) for o in f.get("/Opt", [])]
        if f.get("/MaxLen"):
            info["max_len"] = int(f["/MaxLen"])
        flags = int(f.get("/Ff", 0))
        info["required"] = bool(flags & 2)
        info["readonly"] = bool(flags & 1)
        out.append(info)
    return r, out


def cmd_fields(a):
    _, fields = collect(a.input)
    if not fields:
        print("no fillable fields: use `words`/`grid` + `overlay` for a flat form")
        sys.exit(1)
    for f in fields:
        extra = f.get("states") or f.get("options") or ""
        print(f"p{f.get('page', '?')}  {f['type']:<9} {f['name']!r:<32} value={f['value']!r} {extra} rect={f.get('rect')}")
    if a.template:
        def start(f):
            # keep what the form already holds, so an untouched template entry changes nothing
            v = f.get("value")
            v = "" if v in (None, "/Off", "Off") else str(v).lstrip("/")
            if f["type"] == "checkbox":
                return v != ""
            return v
        tmpl = {f["name"]: start(f) for f in fields if f["type"] not in ("button", "signature")}
        Path(a.template).write_text(json.dumps(tmpl, indent=2))
        print(f"template -> {a.template}")


def flatten(wr):
    """Paint every widget's current appearance into the page, then remove the
    widgets and the form so values can no longer be edited."""
    from pypdf.generic import ArrayObject, DictionaryObject, NameObject, DecodedStreamObject
    for page in wr.pages:
        annots = page.get("/Annots")
        if not annots:
            continue
        ops, keep = [], []
        res = page.setdefault(NameObject("/Resources"), DictionaryObject())
        xobjs = res.setdefault(NameObject("/XObject"), DictionaryObject())
        for i, ref in enumerate(annots):
            o = ref.get_object()
            if o.get("/Subtype") != "/Widget":
                keep.append(ref)
                continue
            ap = o.get("/AP", {}).get("/N")
            if ap is None:
                continue
            ap_obj = ap.get_object()
            if "/BBox" not in ap_obj:  # state dictionary (checkbox/radio)
                state = o.get("/AS") or "/Off"
                if state not in ap_obj:
                    continue  # nothing to paint for this state
                ap = ap_obj[state]
                ap_obj = ap.get_object()
            x0, y0, x1, y1 = [float(v) for v in o["/Rect"]]
            bx0, by0, bx1, by1 = [float(v) for v in ap_obj.get("/BBox", [0, 0, x1 - x0, y1 - y0])]
            sx = (x1 - x0) / ((bx1 - bx0) or 1)
            sy = (y1 - y0) / ((by1 - by0) or 1)
            name = NameObject(f"/FlatW{i}")
            xobjs[name] = ap if hasattr(ap, "idnum") else wr._add_object(ap_obj)
            ops.append(f"q {sx:.4f} 0 0 {sy:.4f} {x0 - bx0 * sx:.2f} {y0 - by0 * sy:.2f} cm {name} Do Q")
        if ops:
            stream = DecodedStreamObject()
            stream.set_data(("\n".join(ops) + "\n").encode())
            contents = page.get("/Contents")
            arr = ArrayObject()
            if contents is not None:
                c = contents.get_object()
                if isinstance(c, ArrayObject):
                    arr.extend(c)
                else:
                    arr.append(contents)
            arr.append(wr._add_object(stream))
            page[NameObject("/Contents")] = arr
        if keep:
            page[NameObject("/Annots")] = ArrayObject(keep)
        else:
            del page["/Annots"]
    if "/AcroForm" in wr._root_object:
        del wr._root_object["/AcroForm"]


def cmd_fill(a):
    from pypdf import PdfWriter
    reader, fields = collect(a.input)
    values = json.loads(Path(a.values).read_text())
    by_name = {f["name"]: f for f in fields}
    errors = []
    resolved = {}
    for name, val in values.items():
        f = by_name.get(name)
        if not f:
            close = difflib.get_close_matches(name, list(by_name), n=3, cutoff=0.6)
            errors.append(f"unknown field {name!r}" + (f" (did you mean {close[:3]}?)" if close else ""))
            continue
        if f["type"] == "checkbox":
            resolved[name] = f["states"][0] if val in (True, "true", "yes", "on", 1) else "/Off"
        elif f["type"] == "radio":
            v = val if str(val).startswith("/") else "/" + str(val)
            if v not in f["states"]:
                errors.append(f"{name!r}: {val!r} not in {f['states']}")
            resolved[name] = v
        elif f["type"] == "choice":
            if f.get("options") and val not in f["options"]:
                errors.append(f"{name!r}: {val!r} not in options {f['options']}")
            resolved[name] = str(val)
        else:
            s = str(val)
            if f.get("max_len") and len(s) > f["max_len"]:
                errors.append(f"{name!r}: {len(s)} chars exceeds max {f['max_len']}")
            resolved[name] = s
    if errors:
        print("\n".join("error: " + e for e in errors), file=sys.stderr)
        sys.exit(2)
    wr = PdfWriter(clone_from=reader)
    wr.set_need_appearances_writer(True)
    for page in wr.pages:
        names_here = set()
        for annot in page.get("/Annots", []) or []:
            o = annot.get_object()
            t = o.get("/T") or (o.get("/Parent").get_object().get("/T") if o.get("/Parent") else None)
            if t is not None:
                names_here.add(str(t))
        subset = {k: v for k, v in resolved.items() if k.split(".")[-1] in names_here or k in names_here}
        if subset:
            wr.update_page_form_field_values(page, subset, auto_regenerate=False)
    if a.flatten:
        flatten(wr)
    with open(a.out, "wb") as fh:
        wr.write(fh)
    _, after = collect(a.out) if not a.flatten else (None, [])
    for f in after:
        if f["name"] in resolved and (f["value"] or "/Off") != resolved[f["name"]] and f["type"] != "checkbox":
            print(f"warn: {f['name']} reads back {f['value']!r}", file=sys.stderr)
    print(f"filled {len(resolved)} field(s) -> {a.out}" + (" (flattened)" if a.flatten else ""))


def page_words(path, page_no):
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        p = pdf.pages[page_no - 1]
        h = float(p.height)
        words = p.extract_words(keep_blank_chars=True, x_tolerance=1.5)
        # convert to PDF user space: origin bottom-left
        return h, [{"text": w_["text"], "x0": round(w_["x0"], 1), "x1": round(w_["x1"], 1),
                    "y_bottom": round(h - w_["bottom"], 1), "y_top": round(h - w_["top"], 1)} for w_ in words]


def cmd_words(a):
    _, words = page_words(a.input, a.page)
    pat = re.compile(a.grep, re.I) if a.grep else None
    for w_ in words:
        if pat and not pat.search(w_["text"]):
            continue
        print(f"x0={w_['x0']:>6} x1={w_['x1']:>6} y_bottom={w_['y_bottom']:>6} y_top={w_['y_top']:>6}  {w_['text']!r}")


def cmd_grid(a):
    import pypdfium2 as pdfium
    from PIL import ImageDraw
    doc = pdfium.PdfDocument(a.input)
    doc.init_forms()
    page = doc[a.page - 1]
    scale = 2.0
    img = page.render(scale=scale, may_draw_forms=True).to_pil().convert("RGB")
    d = ImageDraw.Draw(img)
    w_pt, h_pt = page.get_size()
    for x in range(0, int(w_pt) + 1, a.step):
        d.line([(x * scale, 0), (x * scale, img.height)], fill=(255, 0, 0), width=1)
        d.text((x * scale + 2, 2), str(x), fill=(255, 0, 0))
    for y in range(0, int(h_pt) + 1, a.step):
        yy = img.height - y * scale
        d.line([(0, yy), (img.width, yy)], fill=(0, 0, 255), width=1)
        d.text((2, yy - 12), str(y), fill=(0, 0, 255))
    img.save(a.out)
    print(a.out, "(red = x, blue = y; PDF points, origin bottom-left)")


def cmd_overlay(a):
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    entries = json.loads(Path(a.entries).read_text())
    src = PdfReader(a.input)
    wr = PdfWriter(clone_from=src)
    errors, per_page = [], {}
    cache = {}
    for e in entries:
        pg = int(e.get("page", 1))
        if "label" in e:
            if pg not in cache:
                cache[pg] = page_words(a.input, pg)[1]
            hits = [w_ for w_ in cache[pg] if e["label"].lower() in w_["text"].lower()]
            idx = int(e.get("occurrence", 1)) - 1
            if len(hits) <= idx:
                errors.append(f"page {pg}: label {e['label']!r} not found")
                continue
            h = hits[idx]
            if e.get("below"):
                x, y = h["x0"] + e.get("dx", 0), h["y_bottom"] - e.get("dy", 14)
            else:
                x, y = h["x1"] + e.get("dx", 6), h["y_bottom"] + e.get("dy", 0)
        else:
            x, y = float(e["x"]), float(e["y"])
        per_page.setdefault(pg, []).append((x, y, str(e["text"]), float(e.get("size", a.size)), e.get("font", a.font)))
    if errors:
        print("\n".join("error: " + m for m in errors), file=sys.stderr)
        sys.exit(2)
    for pg, items in per_page.items():
        page = wr.pages[pg - 1]
        w_, h_ = float(page.mediabox.width), float(page.mediabox.height)
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=(w_, h_))
        for x, y, text, size, font in items:
            c.setFont(font, size)
            c.drawString(x, y, text)
        c.save()
        page.merge_page(PdfReader(io.BytesIO(buf.getvalue())).pages[0])
    with open(a.out, "wb") as fh:
        wr.write(fh)
    print(f"placed {sum(len(v) for v in per_page.values())} value(s) -> {a.out}; render and check alignment")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("fields"); p.add_argument("input"); p.add_argument("--template"); p.set_defaults(fn=cmd_fields)
    p = sub.add_parser("fill"); p.add_argument("input"); p.add_argument("values"); p.add_argument("-o", "--out", required=True)
    p.add_argument("--flatten", action="store_true"); p.set_defaults(fn=cmd_fill)
    p = sub.add_parser("words"); p.add_argument("input"); p.add_argument("--page", type=int, default=1); p.add_argument("--grep"); p.set_defaults(fn=cmd_words)
    p = sub.add_parser("grid"); p.add_argument("input"); p.add_argument("--page", type=int, default=1); p.add_argument("-o", "--out", required=True)
    p.add_argument("--step", type=int, default=50); p.set_defaults(fn=cmd_grid)
    p = sub.add_parser("overlay"); p.add_argument("input"); p.add_argument("entries"); p.add_argument("-o", "--out", required=True)
    p.add_argument("--size", type=float, default=10); p.add_argument("--font", default="Helvetica"); p.set_defaults(fn=cmd_overlay)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
