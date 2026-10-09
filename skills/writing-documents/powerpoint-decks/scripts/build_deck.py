#!/usr/bin/env python3
"""Build a designed 16:9 deck from a JSON outline with python-pptx: consistent
theme, real (editable) charts and tables, speaker notes, varied layouts.

Usage:
  build_deck.py outline.json -o deck.pptx
  build_deck.py outline.json -o deck.pptx --template brand.pptx   # use the template's layouts/placeholders

outline.json (see templates/outline.json for every slide type):
{
  "theme": {"primary": "1F2A5C", "secondary": "D6E2FB", "accent": "E04E58", "background": "FFFFFF",
            "text": "1D1D1F", "heading_font": "Cambria", "body_font": "Calibri"},
  "slides": [
    {"type": "title", "title": "Churn fell 18% after onboarding changes", "subtitle": "Q3 review · Oct 2026"},
    {"type": "bullets", "title": "...", "bullets": ["...", ["sub-point", 1]], "notes": "..."},
    {"type": "two_column", "title": "...", "left": {"heading": "...", "bullets": []}, "right": {...}},
    {"type": "stats", "title": "...", "stats": [{"value": "18%", "label": "lower churn"}]},
    {"type": "chart", "title": "...", "chart": {"kind": "column|bar|stacked|stacked_bar|line|pie|doughnut", "categories": [],
             "series": [{"name": "", "values": []}], "number_format": "0%", "highlight": 2, "axis_min": null}, "takeaway": "..."},
    {"type": "table", "title": "...", "columns": [], "rows": [[]]},
    {"type": "image", "title": "...", "image": "path.png", "alt": "...", "caption": "...", "side": "left|right|full"},
    {"type": "process", "title": "...", "steps": [{"title": "", "text": ""}]},
    {"type": "quote", "quote": "...", "attribution": "..."},
    {"type": "section", "title": "...", "kicker": "Part 2"},
    {"type": "closing", "title": "...", "bullets": ["Ask 1", "Ask 2"]}
  ]
}
Colours are 6-digit hex without '#'. Sizes follow: title 36-40 pt, body 16-20 pt,
captions 12 pt, margins 0.6 in.
"""
import argparse, json, re, sys
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

W, H = Inches(13.333), Inches(7.5)
M = Inches(0.6)          # outer margin
GAP = Inches(0.35)       # between blocks
DEFAULT_THEME = {"primary": "1F2A5C", "secondary": "D6E2FB", "accent": "E04E58", "background": "FFFFFF",
                 "text": "1D1D1F", "muted": "5F6368", "heading_font": "Cambria", "body_font": "Calibri"}


def E(*vals):
    """EMU must be integers in the XML; layout maths produces floats."""
    return [int(round(v)) for v in vals]


def rgb(h):
    return RGBColor.from_string(h.lstrip("#").upper()[:6])


class Deck:
    def __init__(self, theme, template=None, keep_template_slides=False):
        self.t = {**DEFAULT_THEME, **(theme or {})}
        self.prs = Presentation(template) if template else Presentation()
        if template and not keep_template_slides:
            # start from the template's masters only; python-pptx skips unreferenced parts on save
            lst = self.prs.slides._sldIdLst
            for sid in list(lst):
                self.prs.part.drop_rel(sid.rId)
                lst.remove(sid)
        if not template:
            self.prs.slide_width, self.prs.slide_height = W, H
        self.W, self.H = self.prs.slide_width, self.prs.slide_height
        self.template = template

    # ---- primitives ---------------------------------------------------
    def blank(self, dark=False):
        layout = self._layout("Blank") or self.prs.slide_layouts[6 if len(self.prs.slide_layouts) > 6 else -1]
        s = self.prs.slides.add_slide(layout)
        for ph in list(s.placeholders):
            ph._element.getparent().remove(ph._element)
        if dark or not self.template:  # light slides on a template keep the master's own background
            bg = s.background.fill
            bg.solid()
            bg.fore_color.rgb = rgb(self.t["primary"] if dark else self.t["background"])
        return s

    def _layout(self, name):
        for l in self.prs.slide_layouts:
            if l.name.lower() == name.lower():
                return l
        return None

    def text(self, slide, x, y, w, h, text, size=18, bold=False, color=None, font=None, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, italic=False):
        tb = slide.shapes.add_textbox(*E(x, y, w, h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0  # aligns with shapes at the same x
        tf.vertical_anchor = anchor
        lines = text if isinstance(text, list) else [text]
        for i, line in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            r = p.add_run()
            r.text = str(line)
            f = r.font
            f.size, f.bold, f.italic = Pt(size), bold, italic
            f.name = font or self.t["body_font"]
            f.color.rgb = rgb(color or self.t["text"])
        return tb

    def bullets(self, slide, x, y, w, h, items, size=18, color=None):
        tb = slide.shapes.add_textbox(*E(x, y, w, h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        for i, item in enumerate(items):
            text, level = (item[0], int(item[1])) if isinstance(item, list) else (item, 0)
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.level = level
            self._bullet(p, level)
            p.space_after = Pt(10 if level == 0 else 4)
            r = p.add_run()
            r.text = text
            r.font.size = Pt(size - 2 * level)
            r.font.name = self.t["body_font"]
            r.font.color.rgb = rgb(color or self.t["text"])
        return tb

    def _bullet(self, p, level):
        """Real bullets via paragraph properties (never a typed '•')."""
        from pptx.oxml.ns import qn
        pPr = p._p.get_or_add_pPr()
        indent = Emu(Inches(0.28 + 0.3 * level))
        pPr.set("marL", str(int(indent)))
        pPr.set("indent", str(-int(Inches(0.25))))
        for tag in ("a:buNone", "a:buChar", "a:buAutoNum", "a:buClr", "a:buFont"):
            for el in pPr.findall(qn(tag)):
                pPr.remove(el)
        clr = pPr.makeelement(qn("a:buClr"), {})
        srgb = clr.makeelement(qn("a:srgbClr"), {"val": self.t["accent"]})
        clr.append(srgb)
        pPr.append(clr)
        bu = pPr.makeelement(qn("a:buChar"), {"char": "•" if level == 0 else "–"})
        pPr.append(bu)

    def rect(self, slide, x, y, w, h, fill, radius=False, line=None):
        shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, *E(x, y, w, h))
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgb(fill)
        if line:
            shp.line.color.rgb = rgb(line)
        else:
            shp.line.fill.background()
        shp.shadow.inherit = False
        if radius:
            shp.adjustments[0] = 0.08
        return shp

    def title(self, slide, text, dark=False, y=None):
        return self.text(slide, M, y or Inches(0.45), self.W - 2 * M, Inches(1.0), text, size=34, bold=True,
                         font=self.t["heading_font"], color="FFFFFF" if dark else self.t["primary"], anchor=MSO_ANCHOR.TOP)

    def notes(self, slide, text):
        if text:
            slide.notes_slide.notes_text_frame.text = text

    # ---- slide types --------------------------------------------------
    def s_title(self, d):
        s = self.blank(dark=True)
        self.text(s, M, Inches(2.3), self.W - 2 * M, Inches(1.8), d["title"], size=44, bold=True,
                  font=self.t["heading_font"], color="FFFFFF", anchor=MSO_ANCHOR.BOTTOM)
        if d.get("subtitle"):
            self.text(s, M, Inches(4.35), self.W - 2 * M, Inches(0.8), d["subtitle"], size=20, color=self.t["secondary"])
        return s

    def s_section(self, d):
        s = self.blank(dark=True)
        if d.get("kicker"):
            self.text(s, M, Inches(2.5), Inches(8), Inches(0.5), d["kicker"].upper(), size=14, bold=True, color=self.t["accent"])
        self.text(s, M, Inches(3.0), self.W - 2 * M, Inches(1.6), d["title"], size=40, bold=True,
                  font=self.t["heading_font"], color="FFFFFF")
        return s

    def s_bullets(self, d):
        s = self.blank()
        self.title(s, d["title"])
        has_side = bool(d.get("callout"))
        bw = (self.W - 2 * M) * (0.62 if has_side else 1)
        self.bullets(s, M, Inches(1.75), bw, self.H - Inches(2.5), d.get("bullets", []), size=d.get("size", 20))
        if has_side:
            x = M + bw + GAP
            box = self.rect(s, x, Inches(1.75), self.W - M - x, Inches(3.2), self.t["secondary"], radius=True)
            self.text(s, x + Inches(0.3), Inches(2.0), self.W - M - x - Inches(0.6), Inches(2.7), d["callout"],
                      size=22, bold=True, color=self.t["primary"], font=self.t["heading_font"])
        return s

    def s_two_column(self, d):
        s = self.blank()
        self.title(s, d["title"])
        colw = (self.W - 2 * M - GAP) / 2
        for i, side in enumerate(("left", "right")):
            col = d.get(side, {})
            x = M + i * (colw + GAP)
            self.rect(s, x, Inches(1.75), colw, self.H - Inches(2.45), "F4F6FA" if i == 0 else self.t["secondary"], radius=True)
            self.text(s, x + Inches(0.3), Inches(1.95), colw - Inches(0.6), Inches(0.6), col.get("heading", ""),
                      size=22, bold=True, color=self.t["primary"])
            self.bullets(s, x + Inches(0.3), Inches(2.7), colw - Inches(0.6), self.H - Inches(3.6), col.get("bullets", []), size=17)
        return s

    def s_stats(self, d):
        s = self.blank()
        self.title(s, d["title"])
        stats = d.get("stats", [])[:4]
        n = max(len(stats), 1)
        cw = (self.W - 2 * M - GAP * (n - 1)) / n
        for i, st in enumerate(stats):
            x = M + i * (cw + GAP)
            self.rect(s, x, Inches(2.0), cw, Inches(3.4), "F4F6FA", radius=True)
            self.text(s, x, Inches(2.35), cw, Inches(1.5), st["value"], size=60, bold=True,
                      color=self.t["accent"] if i == d.get("highlight", 0) else self.t["primary"],
                      font=self.t["heading_font"], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            self.text(s, x + Inches(0.25), Inches(3.95), cw - Inches(0.5), Inches(1.2), st["label"], size=16,
                      color=self.t["muted"], align=PP_ALIGN.CENTER)
        if d.get("source"):
            self.text(s, M, self.H - Inches(0.7), self.W - 2 * M, Inches(0.35), d["source"], size=12, color=self.t["muted"])
        return s

    def s_chart(self, d):
        s = self.blank()
        self.title(s, d["title"])
        c = d["chart"]
        kinds = {"bar": XL_CHART_TYPE.BAR_CLUSTERED, "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
                 "stacked": XL_CHART_TYPE.COLUMN_STACKED, "stacked_bar": XL_CHART_TYPE.BAR_STACKED, "line": XL_CHART_TYPE.LINE_MARKERS,
                 "pie": XL_CHART_TYPE.PIE, "doughnut": XL_CHART_TYPE.DOUGHNUT}
        cd = CategoryChartData()
        cd.categories = c["categories"]
        for ser in c["series"]:
            cd.add_series(ser["name"], ser["values"])
        has_take = bool(d.get("takeaway"))
        cw = (self.W - 2 * M) * (0.66 if has_take else 1)
        gf = s.shapes.add_chart(kinds[c.get("kind", "column")], *E(M, Inches(1.7), cw, self.H - Inches(2.4)), cd)
        ch = gf.chart
        ch.has_title = False  # the slide title is the headline; a chart title repeats it
        ch.font.size = Pt(13)
        ch.font.name = self.t["body_font"]
        multi = len(c["series"]) > 1
        ch.has_legend = multi or c.get("kind") in ("pie", "doughnut")
        if ch.has_legend:
            ch.legend.position = XL_LEGEND_POSITION.BOTTOM
            ch.legend.include_in_layout = False
        palette = [self.t["primary"], self.t["accent"], self.t["secondary"], self.t["muted"]]
        plot = ch.plots[0]
        plot.has_data_labels = True
        dl = plot.data_labels
        dl.font.size = Pt(12)
        dl.number_format = c.get("number_format", "General")
        dl.number_format_is_linked = False
        if c.get("kind") not in ("pie", "doughnut", "line"):
            # stacked charts only accept centre/inside label positions
            dl.position = XL_LABEL_POSITION.CENTER if c.get("kind") in ("stacked", "stacked_bar") else XL_LABEL_POSITION.OUTSIDE_END
            plot.gap_width = 60
        if c.get("kind") in ("pie", "doughnut"):
            pts = plot.series[0].points
            for i in range(len(c["categories"])):
                pts[i].format.fill.solid()
                pts[i].format.fill.fore_color.rgb = rgb(palette[i % len(palette)])
        else:
            for i, ser in enumerate(plot.series):
                fill = ser.format.fill if c.get("kind") != "line" else None
                color = palette[i % len(palette)] if multi else self.t["secondary"]
                if c.get("kind") == "line":
                    ser.format.line.color.rgb = rgb(palette[i % len(palette)])
                    ser.format.line.width = Pt(2.5)
                    ser.smooth = False
                else:
                    fill.solid()
                    fill.fore_color.rgb = rgb(color)
                    hl = c.get("highlight")
                    if hl is not None and not multi:
                        pt = ser.points[hl]
                        pt.format.fill.solid()
                        pt.format.fill.fore_color.rgb = rgb(self.t["accent"])
            va = ch.value_axis
            va.has_major_gridlines = True
            va.major_gridlines.format.line.color.rgb = rgb("E3E6EC")
            va.format.line.fill.background()
            va.tick_labels.font.size = Pt(12)
            va.tick_labels.font.color.rgb = rgb(self.t["muted"])
            # bars encode value as length, so their axis must start at zero; lines may zoom via axis_min
            if c.get("axis_min") is not None:
                va.minimum_scale = c["axis_min"]
            elif c.get("kind", "column") in ("column", "bar", "stacked", "stacked_bar"):
                va.minimum_scale = 0
            if c.get("number_format"):
                va.tick_labels.number_format = c["number_format"]
                va.tick_labels.number_format_is_linked = False
            ca = ch.category_axis
            ca.tick_labels.font.size = Pt(12)
            ca.tick_labels.font.color.rgb = rgb(self.t["muted"])
            ca.format.line.color.rgb = rgb("C9CED6")
        if has_take:
            x = M + cw + GAP
            self.rect(s, x, Inches(2.0), self.W - M - x, Inches(3.0), self.t["primary"], radius=True)
            self.text(s, x + Inches(0.3), Inches(2.25), self.W - M - x - Inches(0.6), Inches(2.5), d["takeaway"],
                      size=22, bold=True, color="FFFFFF", font=self.t["heading_font"], anchor=MSO_ANCHOR.MIDDLE)
        if d.get("source"):
            self.text(s, M, self.H - Inches(0.6), self.W - 2 * M, Inches(0.3), d["source"], size=12, color=self.t["muted"])
        return s

    def s_table(self, d):
        s = self.blank()
        self.title(s, d["title"])
        cols, rows = d["columns"], d["rows"]
        few = len(rows) <= 6  # short tables get room to breathe and stage-readable type
        body_pt, head_pt, row_h = (18, 18, Inches(0.7)) if few else (14, 15, Inches(0.5))
        h = min(row_h * (len(rows) + 1), self.H - Inches(2.4))
        gt = s.shapes.add_table(len(rows) + 1, len(cols), *E(M, Inches(1.8), self.W - 2 * M, h)).table
        num_re = re.compile(r"^[-+\u2212]?[$\u20ac\u00a3\u20b9]?\s?[\d,]*\.?\d+\s?(%|pt|pp|x|\u00d7|k|m|mm|bn|cr|L)?$", re.I)
        def is_num(v):
            return isinstance(v, (int, float)) or bool(num_re.match(str(v).strip()))
        numeric = [bool(rows) and all(is_num(r[j]) for r in rows if j < len(r) and str(r[j]).strip())
                   for j in range(len(cols))]
        for j, name in enumerate(cols):
            cell = gt.cell(0, j)
            cell.text = str(name)
            cell.fill.solid(); cell.fill.fore_color.rgb = rgb(self.t["primary"])
            para = cell.text_frame.paragraphs[0]
            para.runs[0].font.bold = True; para.runs[0].font.size = Pt(head_pt)
            para.runs[0].font.color.rgb = rgb("FFFFFF"); para.runs[0].font.name = self.t["body_font"]
            if numeric[j]:
                para.alignment = PP_ALIGN.RIGHT  # header sits over its numbers
        for i, row in enumerate(rows, start=1):
            for j, val in enumerate(row):
                cell = gt.cell(i, j)
                cell.text = str(val)
                cell.fill.solid(); cell.fill.fore_color.rgb = rgb("FFFFFF" if i % 2 else "F4F6FA")
                run = cell.text_frame.paragraphs[0].runs[0]
                run.font.size = Pt(body_pt); run.font.name = self.t["body_font"]; run.font.color.rgb = rgb(self.t["text"])
                if numeric[j]:
                    cell.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
        return s

    def _placeholder_image(self, name):
        """Missing image: insert a tinted stand-in so the layout can be reviewed, and say so loudly."""
        import tempfile
        from PIL import Image, ImageDraw
        print(f"WARNING: image {name!r} not found; inserted a placeholder - replace it before delivery", file=sys.stderr)
        im = Image.new("RGB", (1200, 1350), "#" + self.t["secondary"])
        dr = ImageDraw.Draw(im)
        for x in range(-1350, 1200, 90):  # diagonal hatching marks it clearly as a stand-in
            dr.line([(x, 1350), (x + 1350, 0)], fill="#" + self.t["primary"], width=18)
        out = Path(tempfile.mkdtemp()) / "placeholder.png"
        im.save(out)
        return out

    def s_image(self, d):
        s = self.blank()
        img = Path(d["image"])
        if not img.is_absolute():
            img = Path(self.base) / img
        if not img.exists():
            img = self._placeholder_image(img.name)
        side = d.get("side", "right")
        if side == "full":
            self.title(s, d["title"])
            pic = s.shapes.add_picture(str(img), *E(M, Inches(1.7)), height=int(self.H - Inches(2.5)))
            if pic.width > self.W - 2 * M:  # keep inside margins, aspect preserved
                ratio = (self.W - 2 * M) / pic.width
                pic.width, pic.height = int(pic.width * ratio), int(pic.height * ratio)
            pic.left = int((self.W - pic.width) / 2)
        else:
            half = self.W / 2
            px = 0 if side == "left" else half
            pic = s.shapes.add_picture(str(img), int(px), 0, width=int(half))
            if pic.height < self.H:  # cover the half: scale up and crop the overflow
                ratio = self.H / pic.height
                pic.width, pic.height = int(pic.width * ratio), int(self.H)
                over = (pic.width - half) / pic.width
                pic.crop_left = pic.crop_right = over / 2
                pic.width, pic.left = int(half), int(px)
            tx = M if side == "right" else half + M
            self.text(s, tx, Inches(0.6), half - 2 * M, Inches(1.8), d["title"], size=32, bold=True,
                      font=self.t["heading_font"], color=self.t["primary"])
            if d.get("bullets"):
                self.bullets(s, tx, Inches(2.6), half - 2 * M, Inches(4), d["bullets"], size=18)
        pic._element.nvPicPr.cNvPr.set("descr", d.get("alt") or d.get("caption") or d["title"])  # alt text
        if d.get("caption"):
            cx, cw = (M, self.W - 2 * M) if side == "full" else (tx, self.W / 2 - 2 * M)  # keep off the photo
            self.text(s, cx, self.H - Inches(0.6), cw, Inches(0.3), d["caption"], size=12, color=self.t["muted"])
        return s

    def s_process(self, d):
        s = self.blank()
        self.title(s, d["title"])
        steps = d.get("steps", [])[:5]
        n = max(len(steps), 1)
        cw = (self.W - 2 * M - GAP * (n - 1)) / n
        for i, st in enumerate(steps):
            x = M + i * (cw + GAP)
            circ = s.shapes.add_shape(MSO_SHAPE.OVAL, *E(x, Inches(2.0), Inches(0.8), Inches(0.8)))
            circ.fill.solid(); circ.fill.fore_color.rgb = rgb(self.t["accent"] if i == 0 else self.t["primary"])
            circ.line.fill.background()
            tf = circ.text_frame; tf.text = str(i + 1)
            r = tf.paragraphs[0].runs[0]; r.font.size = Pt(20); r.font.bold = True; r.font.color.rgb = rgb("FFFFFF")
            tf.paragraphs[0].alignment = PP_ALIGN.CENTER
            if i < n - 1:
                ln = s.shapes.add_connector(1, *E(x + Inches(0.9), Inches(2.4), x + cw + GAP - Inches(0.1), Inches(2.4)))
                ln.line.color.rgb = rgb("C9CED6"); ln.line.width = Pt(2)
            self.text(s, x, Inches(3.05), cw, Inches(0.8), st["title"], size=20, bold=True, color=self.t["primary"])
            self.text(s, x, Inches(3.85), cw, Inches(2.6), st.get("text", ""), size=15, color=self.t["muted"])
        return s

    def s_quote(self, d):
        s = self.blank(dark=True)
        self.text(s, Inches(1.2), Inches(1.6), self.W - Inches(2.4), Inches(3.4), f"“{d['quote']}”", size=34,
                  italic=True, font=self.t["heading_font"], color="FFFFFF", anchor=MSO_ANCHOR.MIDDLE)
        if d.get("attribution"):
            self.text(s, Inches(1.2), Inches(5.3), self.W - Inches(2.4), Inches(0.6), "— " + d["attribution"], size=18,
                      color=self.t["secondary"])
        return s

    def s_closing(self, d):
        s = self.blank(dark=True)
        self.text(s, M, Inches(1.2), self.W - 2 * M, Inches(1.4), d["title"], size=40, bold=True,
                  font=self.t["heading_font"], color="FFFFFF")
        if d.get("bullets"):
            self.bullets(s, M, Inches(2.9), self.W - 2 * M, Inches(3.5), d["bullets"], size=22, color="FFFFFF")
        return s

    def add(self, d):
        fn = getattr(self, "s_" + d.get("type", "bullets"), None)
        if not fn:
            sys.exit(f"error: unknown slide type {d.get('type')!r}")
        s = fn(d)
        self.notes(s, d.get("notes"))
        return s


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("outline")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--template", help=".pptx whose masters/theme to build on (slides use its Blank layout)")
    ap.add_argument("--keep-template-slides", action="store_true", help="keep the template's existing slides before the new ones")
    a = ap.parse_args()
    spec = json.loads(Path(a.outline).read_text(encoding="utf-8"))
    deck = Deck(spec.get("theme"), a.template, a.keep_template_slides)
    deck.base = str(Path(a.outline).resolve().parent)
    for d in spec["slides"]:
        deck.add(d)
    if spec.get("title"):
        deck.prs.core_properties.title = spec["title"]
    if spec.get("author"):
        deck.prs.core_properties.author = spec["author"]
    deck.prs.save(a.out)
    print(f"{a.out}: {len(spec['slides'])} slides")


if __name__ == "__main__":
    main()
