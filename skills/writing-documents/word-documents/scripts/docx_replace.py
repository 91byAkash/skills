#!/usr/bin/env python3
"""Find and replace text in a .docx without losing formatting, optionally as a
tracked change (redline) under a named author.

Usage:
  docx_replace.py IN.docx -o OUT.docx --find "30 days" --replace "45 days"
  docx_replace.py IN.docx -o OUT.docx --find "Acme Ltd" --replace "Acme Inc" --track --author "Akash Jha"
  docx_replace.py unpacked/ --find "draft" --replace "final" --all
  docx_replace.py IN.docx -o OUT.docx --pairs edits.json --track --author "Legal"

Options:
  --all            replace every occurrence (default: first occurrence only)
  --track          wrap old text in <w:del> and new text in <w:ins>
  --author/--date  revision metadata (date defaults to now, UTC)
  --pairs FILE     JSON list of {"find": ..., "replace": ...}
  --match-case     default is case-sensitive; pass --ignore-case to relax
The replacement inherits the formatting of the first character it replaces.
Matches may span runs but must sit inside one paragraph. Prints a count per
pattern and exits 2 if any pattern was not found.
"""
import argparse, copy, datetime as dt, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lxml import etree  # noqa: E402
from wordxml import Package, w, XML_SPACE, isolate, paragraph_text, next_revision_id  # noqa: E402


def make_run_like(template, text, deleted=False):
    r = etree.Element(w("r"), nsmap=template.nsmap)
    rpr = template.find(w("rPr"))
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    t = etree.SubElement(r, w("delText" if deleted else "t"))
    t.text = text
    t.set(XML_SPACE, "preserve")
    return r


def replace_in_paragraph(p, pattern, repl, track, meta, state, replace_all):
    count = 0
    search_from = 0
    while True:
        text = paragraph_text(p)
        m = pattern.search(text, search_from)
        if not m or m.end() == m.start():
            return count
        runs = isolate(p, m.start(), m.end())
        if not runs:
            return count
        parent = runs[0].getparent()
        if any(r.getparent() is not parent for r in runs):
            print(f"  skipped a match spanning containers: {m.group(0)!r}", file=sys.stderr)
            return count
        first = runs[0]
        if track:
            d = etree.Element(w("del"), nsmap=first.nsmap)
            d.set(w("id"), str(state["id"])); state["id"] += 1
            d.set(w("author"), meta["author"]); d.set(w("date"), meta["date"])
            first.addprevious(d)
            for r in runs:
                t = r.find(w("t"))
                t.tag = w("delText")
                d.append(r)
            if repl:
                ins = etree.Element(w("ins"), nsmap=first.nsmap)
                ins.set(w("id"), str(state["id"])); state["id"] += 1
                ins.set(w("author"), meta["author"]); ins.set(w("date"), meta["date"])
                ins.append(make_run_like(first, repl))
                d.addnext(ins)
        else:
            t = first.find(w("t"))
            t.text = repl
            t.set(XML_SPACE, "preserve")
            for r in runs[1:]:
                parent.remove(r)
            if not repl:
                parent.remove(first)
        count += 1
        # deleted text is no longer visible, so in both modes resume after the new text
        search_from = m.start() + len(repl)
        if not replace_all:
            return count


def delete_paragraph(p, track, meta, state):
    """Remove a whole paragraph; tracked = delete every run plus the paragraph mark."""
    if not track:
        p.getparent().remove(p)
        return
    for run in [r for r in p.iter(w("r")) if not any(a.tag == w("del") for a in r.iterancestors())]:
        d = etree.Element(w("del"), nsmap=run.nsmap)
        d.set(w("id"), str(state["id"])); state["id"] += 1
        d.set(w("author"), meta["author"]); d.set(w("date"), meta["date"])
        run.addprevious(d)
        d.append(run)
        for t in run.iter(w("t")):
            t.tag = w("delText")
    ppr = p.find(w("pPr"))
    if ppr is None:
        ppr = etree.Element(w("pPr")); p.insert(0, ppr)
    rpr = ppr.find(w("rPr"))
    if rpr is None:
        rpr = etree.SubElement(ppr, w("rPr"))  # rPr must stay the last pPr child except sectPr/pPrChange
        sect = ppr.find(w("sectPr"))
        if sect is not None:
            sect.addprevious(rpr)
    mark = etree.Element(w("del"))
    mark.set(w("id"), str(state["id"])); state["id"] += 1
    mark.set(w("author"), meta["author"]); mark.set(w("date"), meta["date"])
    rpr.insert(0, mark)  # schema order: the revision mark precedes other rPr children


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("-o", "--out")
    ap.add_argument("--find")
    ap.add_argument("--replace", default="")
    ap.add_argument("--pairs")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--delete-paragraph", metavar="TEXT", help="delete each paragraph containing TEXT (whole paragraph)")
    ap.add_argument("--regex", action="store_true", help="treat --find as a regular expression")
    ap.add_argument("--ignore-case", action="store_true")
    ap.add_argument("--track", action="store_true")
    ap.add_argument("--author", default="Reviewer")
    ap.add_argument("--date", default=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    a = ap.parse_args()
    pairs = json.loads(Path(a.pairs).read_text()) if a.pairs else ([{"find": a.find, "replace": a.replace}] if a.find else [])
    if not pairs and not a.delete_paragraph:
        sys.exit("error: give --find, --pairs or --delete-paragraph")
    if any(not p.get("find") for p in pairs):
        sys.exit("error: every pair needs a non-empty find")
    pkg = Package(a.src)
    if not pkg.is_dir and not a.out:
        sys.exit("error: pass -o OUT.docx when the input is a file")
    roots = {n: pkg.xml(n) for n in pkg.story_parts()}
    state = {"id": next_revision_id(roots.values())}
    meta = {"author": a.author, "date": a.date}
    missing = 0
    for pair in pairs:
        flags = re.IGNORECASE if a.ignore_case else 0
        pat = re.compile(pair["find"] if a.regex else re.escape(pair["find"]), flags)
        n = 0
        for root in roots.values():
            for p in root.iter(w("p")):
                if n and not a.all:
                    break
                n += replace_in_paragraph(p, pat, pair.get("replace", ""), a.track, meta, state, a.all)
        print(f"{n:>4}  {pair['find']!r} -> {pair.get('replace', '')!r}")
        missing += n == 0
    if a.delete_paragraph:
        n = 0
        for root in roots.values():
            for p in [p for p in root.iter(w("p")) if a.delete_paragraph in paragraph_text(p)]:
                delete_paragraph(p, a.track, meta, state)
                n += 1
        print(f"{n:>4}  paragraph(s) containing {a.delete_paragraph!r} deleted")
        missing += n == 0
    for name, root in roots.items():
        pkg.write(name, root)
    pkg.save(a.out)
    sys.exit(2 if missing else 0)


if __name__ == "__main__":
    main()
