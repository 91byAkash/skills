#!/usr/bin/env python3
"""Build a styled .docx from Markdown with real Word styles (so the navigation
pane, TOC and numbering work), page setup, header/footer and page numbers.

Usage:
  md_to_docx.py report.md -o report.docx
  md_to_docx.py report.md -o report.docx --page letter --margins 1in --font Calibri --size 11 \
      --toc --header "Q3 Review - Confidential" --page-numbers --title "Q3 Review" --author "Akash Jha"
  md_to_docx.py notes.md -o notes.docx --template brand.dotx_or_docx   # inherit styles

Markdown supported: # to ###### headings, paragraphs, **bold**, *italic*,
`code`, [links](url), - / * bullets and 1. numbers (indent two spaces per
level), > quotes, ``` fenced code, | pipe | tables | (first row = header),
![alt](image.png){width=4in}, and a line containing only <!-- pagebreak -->.
The first "# " heading becomes the Title style when --title-from-h1 is set.
"""
import argparse, re, sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor, Cm

PAGES = {"letter": (Inches(8.5), Inches(11)), "a4": (Cm(21), Cm(29.7)), "legal": (Inches(8.5), Inches(14))}
INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")


def length(s):
    s = s.strip().lower()
    for unit, fn in (("in", Inches), ("cm", Cm), ("pt", Pt)):
        if s.endswith(unit):
            return fn(float(s[: -len(unit)]))
    return Inches(float(s))


def add_field(run, instr, placeholder="1"):
    """Insert a Word field (PAGE, NUMPAGES, TOC ...); Word computes it on open/F9.
    `placeholder` is the cached result shown until then (and in LibreOffice/PDF renders)."""
    for kind, text in (("begin", None), (None, instr), ("separate", None), (None, placeholder), ("end", None)):
        if kind:
            fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), kind)
            if kind == "begin":
                fc.set(qn("w:dirty"), "true")
            run._r.append(fc)
        elif text == instr:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = f" {instr} "
            run._r.append(it)
        else:
            t = OxmlElement("w:t"); t.text = text; run._r.append(t)


def add_hyperlink(paragraph, text, url):
    rid = paragraph.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), rid)
    r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    st = OxmlElement("w:rStyle"); st.set(qn("w:val"), "Hyperlink"); rpr.append(st)
    col = OxmlElement("w:color"); col.set(qn("w:val"), "0563C1"); rpr.append(col)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rpr.append(u)
    r.append(rpr)
    t = OxmlElement("w:t"); t.text = text; t.set(qn("xml:space"), "preserve"); r.append(t)
    h.append(r); paragraph._p.append(h)


def add_inline(paragraph, text, code_font):
    for piece in INLINE.split(text):
        if not piece:
            continue
        if piece.startswith("**") and piece.endswith("**"):
            paragraph.add_run(piece[2:-2]).bold = True
        elif piece.startswith("`") and piece.endswith("`"):
            r = paragraph.add_run(piece[1:-1]); r.font.name = code_font
        elif piece.startswith("[") and "](" in piece:
            label, url = re.match(r"\[([^\]]+)\]\(([^)]+)\)", piece).groups()
            add_hyperlink(paragraph, label, url)
        elif piece.startswith("*") and piece.endswith("*") and len(piece) > 2:
            paragraph.add_run(piece[1:-1]).italic = True
        else:
            paragraph.add_run(piece)


def ensure_style(doc, name, base="Normal", font=None, size=None, kind=WD_STYLE_TYPE.PARAGRAPH):
    try:
        return doc.styles[name]
    except KeyError:
        st = doc.styles.add_style(name, kind)
        st.base_style = doc.styles[base]
        if font:
            st.font.name = font
        if size:
            st.font.size = Pt(size)
        return st


def list_style(doc, ordered, depth):
    base = "List Number" if ordered else "List Bullet"
    name = base if depth == 0 else f"{base} {min(depth + 1, 3)}"
    try:
        return doc.styles[name]
    except KeyError:
        return doc.styles[base]


def set_cell_shading(cell, hex_fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hex_fill)
    tcpr.append(shd)


def mark_header_row(row):
    trpr = row._tr.get_or_add_trPr()
    h = OxmlElement("w:tblHeader"); h.set(qn("w:val"), "true"); trpr.append(h)


def add_table(doc, rows, header_fill, code_font):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    cells = [r for r in cells if not all(re.fullmatch(r":?-{3,}:?", c) for c in r)]
    ncol = max(len(r) for r in cells)
    t = doc.add_table(rows=len(cells), cols=ncol)
    t.style = doc.styles["Table Grid"]
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, r in enumerate(cells):
        for j in range(ncol):
            cell = t.cell(i, j)
            cell.paragraphs[0].text = ""
            add_inline(cell.paragraphs[0], r[j] if j < len(r) else "", code_font)
            if i == 0:
                for run in cell.paragraphs[0].runs:
                    run.bold = True
                set_cell_shading(cell, header_fill)
    mark_header_row(t.rows[0])
    doc.add_paragraph()


def build(md, out, a):
    doc = Document(a.template) if a.template else Document()
    if a.template:
        body = doc.element.body
        for el in list(body):
            if el.tag != qn("w:sectPr"):
                body.remove(el)
    sec = doc.sections[0]
    if a.page:
        w_, h_ = PAGES[a.page]
        if a.landscape:
            sec.orientation = WD_ORIENT.LANDSCAPE
            w_, h_ = h_, w_
        sec.page_width, sec.page_height = w_, h_
    m = length(a.margins)
    sec.left_margin = sec.right_margin = sec.top_margin = sec.bottom_margin = m
    normal = doc.styles["Normal"]
    normal.font.name = a.font
    normal.font.size = Pt(a.size)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), a.font)
    for lvl in range(1, 4):
        hs = doc.styles[f"Heading {lvl}"]
        hs.font.name = a.heading_font or a.font
        hs.font.color.rgb = RGBColor.from_string(a.accent)
    code_style = ensure_style(doc, "Code Block", font=a.code_font, size=max(a.size - 1, 8))
    code_style.paragraph_format.space_after = Pt(0)
    if a.title or a.author:
        doc.core_properties.title = a.title or ""
        doc.core_properties.author = a.author or ""
    if a.header:
        hp = sec.header.paragraphs[0]; hp.text = a.header; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if a.page_numbers:
        fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fp.add_run("Page "); add_field(fp.add_run(), "PAGE"); fp.add_run(" of "); add_field(fp.add_run(), "NUMPAGES")
    if a.toc:
        doc.add_paragraph("Contents", style="TOC Heading" if "TOC Heading" in [s.name for s in doc.styles] else "Heading 1")
        toc_run = doc.add_paragraph().add_run()
        add_field(toc_run, 'TOC \\o "1-3" \\h \\z \\u', placeholder="TOC_PLACEHOLDER")
        doc.add_page_break()

    lines = md.splitlines()
    i, first_h1 = 0, True
    para_buf = []

    def flush():
        if para_buf:
            add_inline(doc.add_paragraph(), " ".join(s.strip() for s in para_buf), a.code_font)
            para_buf.clear()

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            flush(); i += 1; continue
        if s == "<!-- pagebreak -->":
            flush(); doc.add_page_break(); i += 1; continue
        if s.startswith("```"):
            flush(); i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                doc.add_paragraph(lines[i], style=code_style); i += 1
            i += 1; continue
        mh = re.match(r"^(#{1,6})\s+(.*)", s)
        if mh:
            flush()
            lvl = len(mh.group(1))
            if lvl == 1 and first_h1 and a.title_from_h1:
                doc.add_paragraph(mh.group(2), style="Title")
            else:
                doc.add_heading(mh.group(2), level=min(lvl, 9))
            first_h1 = first_h1 and lvl != 1
            i += 1; continue
        if s.startswith("|"):
            flush(); rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i]); i += 1
            add_table(doc, rows, a.header_fill, a.code_font); continue
        mi = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)(\{width=([^}]+)\})?", s)
        if mi:
            flush()
            img = Path(mi.group(2))
            if not img.is_absolute():
                img = Path(a.base) / img
            width = length(mi.group(4)) if mi.group(4) else None
            doc.add_picture(str(img), width=width)
            pic = doc.paragraphs[-1]; pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
            docpr = pic._p.find(".//" + qn("wp:docPr"))
            if docpr is not None:
                docpr.set("descr", mi.group(1))  # alt text for screen readers
            if mi.group(1):
                doc.add_paragraph(mi.group(1), style="Caption")
            i += 1; continue
        ml = re.match(r"^(\s*)([-*]|\d+[.)])\s+(.*)", line)
        if ml:
            flush()
            depth = len(ml.group(1).replace("\t", "  ")) // 2
            ordered = ml.group(2)[0].isdigit()
            add_inline(doc.add_paragraph(style=list_style(doc, ordered, depth)), ml.group(3), a.code_font)
            i += 1; continue
        if s.startswith(">"):
            flush()
            add_inline(doc.add_paragraph(style="Quote"), s.lstrip("> "), a.code_font)
            i += 1; continue
        para_buf.append(s); i += 1
    flush()
    if a.toc:
        # Cached TOC result: heading titles (no page numbers) so renders that do not
        # update fields still show a usable contents list; Word rebuilds it on open.
        heads = [(int(p.style.name.split()[-1]), p.text) for p in doc.paragraphs
                 if p.style is not None and p.style.name in ("Heading 1", "Heading 2", "Heading 3") and p.text.strip()]
        for t in toc_run._r.iter(qn("w:t")):
            if t.text == "TOC_PLACEHOLDER":
                r = t.getparent(); idx = list(r).index(t); r.remove(t)
                top = min((lvl for lvl, _ in heads), default=1)
                lines = [("    " * (lvl - top)) + txt for lvl, txt in heads] or ["Update field (F9) to build the contents"]
                for n, line in enumerate(lines):
                    if n:
                        r.insert(idx, OxmlElement("w:br")); idx += 1
                    nt = OxmlElement("w:t"); nt.set(qn("xml:space"), "preserve"); nt.text = line
                    r.insert(idx, nt); idx += 1
                break
    doc.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--template", help=".docx whose styles, headers and page setup to reuse")
    ap.add_argument("--page", choices=sorted(PAGES), default=None, help="default: keep template/library default (Letter)")
    ap.add_argument("--landscape", action="store_true")
    ap.add_argument("--margins", default="1in")
    ap.add_argument("--font", default="Calibri")
    ap.add_argument("--heading-font")
    ap.add_argument("--code-font", default="Courier New")
    ap.add_argument("--size", type=float, default=11)
    ap.add_argument("--accent", default="1F3864", help="heading colour, hex without #")
    ap.add_argument("--header-fill", default="D9E2F3", help="table header shading, hex without #")
    ap.add_argument("--header")
    ap.add_argument("--page-numbers", action="store_true")
    ap.add_argument("--toc", action="store_true")
    ap.add_argument("--title"); ap.add_argument("--author")
    ap.add_argument("--title-from-h1", action="store_true")
    a = ap.parse_args()
    a.base = str(Path(a.src).resolve().parent)
    build(Path(a.src).read_text(encoding="utf-8"), a.out, a)
    print(a.out)


if __name__ == "__main__":
    main()
