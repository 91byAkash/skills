#!/usr/bin/env python3
"""Generate a clean PDF report from Markdown with ReportLab: embedded Unicode
font, title/author metadata, header, "Page X of Y" footer, tables, images,
lists, quotes and code.

Usage:
  md_to_pdf.py report.md -o report.pdf [--page a4|letter] [--title T] [--author A]
               [--header "Confidential"] [--font /path/Font.ttf --bold-font /path/Font-Bold.ttf]
               [--accent 1F3864] [--margin 54]

Markdown: # to ### headings, paragraphs, **bold**, *italic*, `code`, [link](url),
- / 1. lists (two-space indent per level), > quote, ``` code, | tables |,
![caption](img.png){width=300} (points), <!-- pagebreak -->.
Superscripts/subscripts: write <super>2</super> / <sub>2</sub>, not Unicode ²/₂
(many fonts lack those glyphs and print black boxes).
"""
import argparse, html, re, sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, ListFlowable, ListItem, PageBreak, Paragraph,
                                Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle)

FONT_CANDIDATES = [
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    ("/Library/Fonts/Arial Unicode.ttf", "/Library/Fonts/Arial Bold.ttf"),
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
]


def register_fonts(regular, bold):
    pairs = [(regular, bold)] if regular else FONT_CANDIDATES
    for reg, bld in pairs:
        if reg and Path(reg).exists():
            pdfmetrics.registerFont(TTFont("Body", reg))
            pdfmetrics.registerFont(TTFont("Body-Bold", bld if bld and Path(bld).exists() else reg))
            from reportlab.pdfbase.pdfmetrics import registerFontFamily
            registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body", boldItalic="Body-Bold")
            return "Body", "Body-Bold"
    print("warn: no TTF found; using Helvetica (Latin-1 only)", file=sys.stderr)
    return "Helvetica", "Helvetica-Bold"


def inline(text):
    keep = {}

    def stash(m):
        keep[f"\x00{len(keep)}\x00"] = m.group(0)
        return f"\x00{len(keep) - 1}\x00"
    text = re.sub(r"</?(super|sub)>", stash, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+)`", r'<font face="Courier">\1</font>', text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<link href="\2" color="#0563C1"><u>\1</u></link>', text)
    for k, v in keep.items():
        text = text.replace(k, v)
    return text


def build(md, a):
    body, bold = register_fonts(a.font, a.bold_font)
    ss = getSampleStyleSheet()
    accent = colors.HexColor("#" + a.accent)
    st = {
        "body": ParagraphStyle("body", parent=ss["BodyText"], fontName=body, fontSize=10.5, leading=14.5, spaceAfter=6),
        "h1": ParagraphStyle("h1", parent=ss["Heading1"], fontName=bold, fontSize=20, leading=24, textColor=accent, spaceAfter=10),
        "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontName=bold, fontSize=14, leading=18, textColor=accent, spaceBefore=10),
        "h3": ParagraphStyle("h3", parent=ss["Heading3"], fontName=bold, fontSize=11.5, leading=15, spaceBefore=8),
        "quote": ParagraphStyle("quote", parent=ss["BodyText"], fontName=body, fontSize=10.5, leading=14.5, leftIndent=18, textColor=colors.HexColor("#444444")),
        "cell": ParagraphStyle("cell", parent=ss["BodyText"], fontName=body, fontSize=9.5, leading=12),
        "cellh": ParagraphStyle("cellh", parent=ss["BodyText"], fontName=bold, fontSize=9.5, leading=12),
        "caption": ParagraphStyle("caption", parent=ss["BodyText"], fontName=body, fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor("#555555")),
        "code": ParagraphStyle("code", parent=ss["Code"], fontSize=8.5, leading=11, backColor=colors.HexColor("#F4F4F4")),
    }
    page = A4 if a.page == "a4" else letter
    frame_w = page[0] - 2 * a.margin
    story, lines, i, para = [], md.splitlines(), 0, []

    def flush():
        if para:
            story.append(Paragraph(inline(" ".join(para)), st["body"]))
            para.clear()

    while i < len(lines):
        raw = lines[i]; s = raw.strip()
        if not s:
            flush(); i += 1; continue
        if s == "<!-- pagebreak -->":
            flush(); story.append(PageBreak()); i += 1; continue
        if s.startswith("```"):
            flush(); i += 1; buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            story.append(Preformatted("\n".join(buf), st["code"])); i += 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)", s)
        if m:
            flush(); lvl = min(len(m.group(1)), 3)
            story.append(Paragraph(inline(m.group(2)), st[f"h{lvl}"])); i += 1; continue
        if s.startswith("|"):
            flush(); rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            ncol = max(len(r) for r in rows)
            data = [[Paragraph(inline(r[j] if j < len(r) else ""), st["cellh" if k == 0 else "cell"]) for j in range(ncol)] for k, r in enumerate(rows)]
            t = Table(data, colWidths=[frame_w / ncol] * ncol, repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EDF5")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9AA5B8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FC")]),
            ]))
            story += [t, Spacer(1, 8)]; continue
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)(\{width=(\d+)\})?", s)
        if m:
            flush()
            path = Path(m.group(2)); path = path if path.is_absolute() else Path(a.base) / path
            from reportlab.lib.utils import ImageReader
            if not path.is_file():
                # keep going so the rest of the document can be checked; flag it loudly
                print(f"warning: image not found: {path} (placeholder inserted)", file=sys.stderr)
                story += [Paragraph(f"[missing image: {m.group(2)}]", st["caption"]), Spacer(1, 6)]
                i += 1; continue
            iw, ih = ImageReader(str(path)).getSize()
            w = min(float(m.group(4) or frame_w), frame_w)
            img = Image(str(path), width=w, height=w * ih / iw)
            parts = [img] + ([Paragraph(inline(m.group(1)), st["caption"])] if m.group(1) else [])
            story.append(KeepTogether(parts)); i += 1; continue
        if re.match(r"^\s*([-*]|\d+[.)])\s+", raw):
            flush()
            ordered = bool(re.match(r"^\s*\d", raw))
            items = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+[.)])\s+", lines[i]):
                depth = (len(lines[i]) - len(lines[i].lstrip())) // 2
                text = re.sub(r"^\s*([-*]|\d+[.)])\s+", "", lines[i])
                items.append(ListItem(Paragraph(inline(text), st["body"]), leftIndent=12 + 14 * depth))
                i += 1
            story.append(ListFlowable(items, bulletType="1" if ordered else "bullet", start="1" if ordered else None,
                                      bulletFontName=body, bulletFontSize=9))
            continue
        if s.startswith(">"):
            flush(); story.append(Paragraph(inline(s.lstrip("> ")), st["quote"])); i += 1; continue
        para.append(s); i += 1
    flush()
    return story, page, body


class NumberedDoc(SimpleDocTemplate):
    pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src"); ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--page", choices=["a4", "letter"], default="a4")
    ap.add_argument("--title"); ap.add_argument("--author", default="")
    ap.add_argument("--header", default="")
    ap.add_argument("--font"); ap.add_argument("--bold-font")
    ap.add_argument("--accent", default="1F3864")
    ap.add_argument("--margin", type=float, default=54, help="points (72 = 1 inch)")
    a = ap.parse_args()
    a.base = str(Path(a.src).resolve().parent)
    md = Path(a.src).read_text(encoding="utf-8")
    title = a.title or next((l.lstrip("# ").strip() for l in md.splitlines() if l.startswith("# ")), Path(a.src).stem)
    story, page, body = build(md, a)

    from reportlab.pdfgen import canvas as rl_canvas

    class PageCountCanvas(rl_canvas.Canvas):
        """Two-pass canvas so the footer can say 'Page X of Y'."""
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw); self._saved = []

        def showPage(self):
            self._saved.append(dict(self.__dict__)); self._startPage()

        def save(self):
            total = len(self._saved)
            for state in self._saved:
                self.__dict__.update(state)
                self.setFont(body, 8.5); self.setFillColor(colors.HexColor("#666666"))
                self.drawCentredString(page[0] / 2, a.margin / 2, f"Page {self._pageNumber} of {total}")
                if a.header:
                    self.drawRightString(page[0] - a.margin, page[1] - a.margin / 2, a.header)
                super().showPage()
            super().save()

    doc = NumberedDoc(a.out, pagesize=page, leftMargin=a.margin, rightMargin=a.margin, topMargin=a.margin,
                      bottomMargin=a.margin, title=title, author=a.author, subject=title, creator="md_to_pdf")
    doc.build(story, canvasmaker=PageCountCanvas)
    print(a.out)


if __name__ == "__main__":
    main()
