#!/usr/bin/env python3
"""Accept or reject every tracked change in a .docx (or list them).

Usage:
  track_changes.py list   IN.docx                 # author, type, text of each revision
  track_changes.py accept IN.docx -o clean.docx   # final text, no revision marks
  track_changes.py reject IN.docx -o orig.docx    # text as it was before the redline
  track_changes.py accept unpacked/ [--author NAME]   # only that author's changes

Handles inserted/deleted runs, moves, formatting changes, inserted and deleted
paragraph marks (a deleted mark joins the paragraph to the next one, so a fully
deleted paragraph disappears instead of leaving an empty bullet), and
inserted/deleted table rows.
"""
import argparse, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wordxml import Package, w  # noqa: E402

PROP_CHANGES = ["rPrChange", "pPrChange", "sectPrChange", "tblPrChange", "trPrChange",
                "tcPrChange", "tblGridChange", "numberingChange"]


def mine(el, author):
    return author is None or el.get(w("author")) == author


def unwrap(el):
    parent = el.getparent()
    idx = parent.index(el)
    for i, child in enumerate(list(el)):
        parent.insert(idx + i, child)
    parent.remove(el)


def drop(el):
    el.getparent().remove(el)


def to_t(container):
    for dt_ in container.iter(w("delText")):
        dt_.tag = w("t")
    for dit in container.iter(w("delInstrText")):
        dit.tag = w("instrText")


def is_mark(el):
    """<w:ins>/<w:del> inside rPr = paragraph-mark or row revision, not content."""
    parent = el.getparent()
    return parent is not None and parent.tag in (w("rPr"), w("trPr"))


def join_with_next(p):
    nxt = p.getnext()
    content = [c for c in p if c.tag != w("pPr")]
    if nxt is not None and nxt.tag == w("p"):
        nppr = nxt.find(w("pPr"))
        anchor = 0 if nppr is None else nxt.index(nppr) + 1
        for i, c in enumerate(content):
            nxt.insert(anchor + i, c)
        drop(p)
    elif not any(c.iter(w("t")) for c in content):
        drop(p)


def process(root, mode, author):
    keep_tag, kill_tag = ("ins", "del") if mode == "accept" else ("del", "ins")
    # table rows
    for mark in list(root.iter(w(kill_tag))):
        if mark.getparent() is not None and mark.getparent().tag == w("trPr") and mine(mark, author):
            row = mark.getparent().getparent()
            drop(row)
    for mark in list(root.iter(w(keep_tag))):
        if mark.getparent() is not None and mark.getparent().tag == w("trPr") and mine(mark, author):
            drop(mark)
    # paragraph marks
    for mark in list(root.iter(w(kill_tag))):
        if is_mark(mark) and mark.getparent().getparent().tag == w("pPr") and mine(mark, author):
            p = mark.getparent().getparent().getparent()
            drop(mark)
            join_later = p
            join_later.set("_join", "1")
    for mark in list(root.iter(w(keep_tag))):
        if is_mark(mark) and mine(mark, author):
            drop(mark)
    # content
    move_kill, move_keep = ("moveFrom", "moveTo") if mode == "accept" else ("moveTo", "moveFrom")
    for el in list(root.iter(w(kill_tag), w(move_kill))):
        if el.getparent() is not None and not is_mark(el) and mine(el, author):
            drop(el)
    for el in list(root.iter(w(keep_tag), w(move_keep))):
        if el.getparent() is not None and not is_mark(el) and mine(el, author):
            if mode == "reject":
                to_t(el)
            unwrap(el)
    for tag in ("moveFromRangeStart", "moveFromRangeEnd", "moveToRangeStart", "moveToRangeEnd"):
        for el in list(root.iter(w(tag))):
            drop(el)
    # formatting changes: accept keeps current props; reject restores the old ones
    for name in PROP_CHANGES:
        for ch in list(root.iter(w(name))):
            if not mine(ch, author):
                continue
            if mode == "reject":
                current = ch.getparent()
                old = ch.find("*")
                drop(ch)
                if old is not None:
                    for c in list(current):
                        current.remove(c)
                    for c in list(old):
                        current.append(c)
            else:
                drop(ch)
    for p in list(root.iter(w("p"))):
        if p.attrib.pop("_join", None):
            join_with_next(p)


def list_changes(pkg):
    for name in pkg.story_parts():
        root = pkg.xml(name)
        for el in root.iter(w("ins"), w("del"), w("moveFrom"), w("moveTo")):
            kind = el.tag.split("}")[1]
            if is_mark(el):
                kind += "(paragraph mark)" if el.getparent().getparent().tag == w("pPr") else "(row)"
            text = "".join(t.text or "" for t in el.iter(w("t"), w("delText")))
            print(f"{name}\t{kind}\t{el.get(w('author'))}\t{el.get(w('date'))}\t{text!r}")
        for name_ in PROP_CHANGES:
            for el in root.iter(w(name_)):
                print(f"{name}\t{name_}\t{el.get(w('author'))}\t{el.get(w('date'))}\t''")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["accept", "reject", "list"])
    ap.add_argument("src")
    ap.add_argument("-o", "--out")
    ap.add_argument("--author", help="only touch revisions by this author")
    a = ap.parse_args()
    pkg = Package(a.src)
    if a.mode == "list":
        list_changes(pkg)
        return
    if not pkg.is_dir and not a.out:
        sys.exit("error: pass -o OUT.docx when the input is a file")
    for name in pkg.story_parts():
        root = pkg.xml(name)
        process(root, a.mode, a.author)
        pkg.write(name, root)
    print(f"{a.mode}ed changes -> {pkg.save(a.out)}")


if __name__ == "__main__":
    main()
