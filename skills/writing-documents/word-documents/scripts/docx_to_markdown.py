#!/usr/bin/env python3
"""Read a .docx as Markdown, including what plain text extraction loses:
heading levels, lists, tables, tracked changes and comments.

Usage:
  docx_to_markdown.py IN.docx                    # tracked changes shown as {+ins+} {-del-}
  docx_to_markdown.py IN.docx --changes accept   # or reject
  docx_to_markdown.py IN.docx --no-comments -o out.md

Use it to understand a document before editing; plan XML edits from the XML,
not from this view (it does not show run boundaries).
"""
import argparse, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wordxml import Package, w  # noqa: E402

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


def style_map(pkg):
    names = {}
    if pkg.has("word/styles.xml"):
        for s in pkg.xml("word/styles.xml").iter(w("style")):
            n = s.find(w("name"))
            names[s.get(w("styleId"))] = n.get(w("val")) if n is not None else s.get(w("styleId"))
    return names


def heading_level(p, styles):
    ppr = p.find(w("pPr"))
    if ppr is None:
        return 0
    ol = ppr.find(w("outlineLvl"))
    st = ppr.find(w("pStyle"))
    name = styles.get(st.get(w("val")), st.get(w("val"))) if st is not None else ""
    low = name.lower()
    if low == "title":
        return 1
    if low.startswith("heading") and low[7:].strip().isdigit():
        return min(int(low[7:].strip()), 6)
    if ol is not None and ol.get(w("val")).isdigit():
        return min(int(ol.get(w("val"))) + 1, 6)
    return 0


def list_info(p, styles):
    ppr = p.find(w("pPr"))
    if ppr is None:
        return None
    num = ppr.find(w("numPr"))
    st = ppr.find(w("pStyle"))
    name = (styles.get(st.get(w("val")), "") if st is not None else "").lower()
    if num is not None or "list" in name:
        lvl = num.find(w("ilvl")) if num is not None else None
        depth = int(lvl.get(w("val"))) if lvl is not None else (1 if name.endswith(" 2") else 0)
        return depth, ("1." if "number" in name else "-")
    return None


def run_text(r, mode):
    out = []
    in_del = any(a.tag in (w("del"), w("moveFrom")) for a in r.iterancestors())
    in_ins = any(a.tag in (w("ins"), w("moveTo")) for a in r.iterancestors())
    if (in_del and mode == "accept") or (in_ins and mode == "reject"):
        return ""
    rpr = r.find(w("rPr"))
    bold = rpr is not None and rpr.find(w("b")) is not None and rpr.find(w("b")).get(w("val"), "1") not in ("0", "false")
    ital = rpr is not None and rpr.find(w("i")) is not None and rpr.find(w("i")).get(w("val"), "1") not in ("0", "false")
    for c in r:
        if c.tag in (w("t"), w("delText")):
            out.append(c.text or "")
        elif c.tag == w("tab"):
            out.append("\t")
        elif c.tag in (w("br"), w("cr")):
            out.append("  \n")
        elif c.tag == w("drawing"):
            out.append("![image]()")
    s = "".join(out)
    if s.strip() and (bold or ital):
        # keep surrounding whitespace outside the markers ("** x**" is not valid Markdown)
        core = s.strip()
        lead, trail = s[:len(s) - len(s.lstrip())], s[len(s.rstrip()):]
        if bold:
            core = f"**{core}**"
        if ital:
            core = f"*{core}*"
        s = lead + core + trail
    if mode == "show" and s:
        if in_del:
            s = "{-" + s + "-}"
        elif in_ins:
            s = "{+" + s + "+}"
    return s


def para_md(p, mode, comments, notes):
    parts = []
    for el in p.iter(w("r"), w("commentReference")):
        if el.tag == w("commentReference"):
            cid = el.get(w("id"))
            if comments is not None and cid in comments:
                notes.append((cid, comments[cid]))
                parts.append(f"[^c{cid}]")
        elif el.find(w("commentReference")) is None:
            parts.append(run_text(el, mode))
    return "".join(parts).strip()


def table_md(tbl, mode, comments, notes):
    rows = []
    for tr in tbl.findall(w("tr")):
        cells = []
        for tc in tr.findall(w("tc")):
            cells.append(" <br> ".join(filter(None, (para_md(p, mode, comments, notes) for p in tc.iter(w("p"))))).replace("|", "\\|"))
        rows.append(cells)
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(lines)


def convert(src, mode="show", with_comments=True):
    pkg = Package(src)
    styles = style_map(pkg)
    comments = None
    if with_comments and pkg.has("word/comments.xml"):
        comments = {}
        for c in pkg.xml("word/comments.xml").iter(w("comment")):
            body = " ".join("".join(t.text or "" for t in p.iter(w("t"))) for p in c.iter(w("p")))
            comments[c.get(w("id"))] = f"{c.get(w('author'))}: {body.strip()}"
    body = pkg.xml("word/document.xml").find(w("body"))
    out, notes = [], []
    for el in body:
        if el.tag == w("p"):
            text = para_md(el, mode, comments, notes)
            if not text:
                continue
            lvl = heading_level(el, styles)
            li = list_info(el, styles)
            if lvl:
                out.append("#" * lvl + " " + text.replace("**", ""))
            elif li:
                out.append("  " * li[0] + li[1] + " " + text)
            else:
                out.append(text)
        elif el.tag == w("tbl"):
            out.append(table_md(el, mode, comments, notes))
    md = ""
    for i, block in enumerate(out):
        is_list = block.lstrip().startswith(("- ", "1. "))
        prev_list = i > 0 and out[i - 1].lstrip().startswith(("- ", "1. "))
        md += ("\n" if is_list and prev_list else "\n\n") + block
    if notes:
        md += "\n\n" + "\n".join(f"[^c{cid}]: {txt}" for cid, txt in notes)
    return md.strip() + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("--changes", choices=["show", "accept", "reject"], default="show")
    ap.add_argument("--no-comments", action="store_true")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    md = convert(a.src, a.changes, not a.no_comments)
    if a.out:
        Path(a.out).write_text(md)
    else:
        sys.stdout.write(md)


if __name__ == "__main__":
    main()
