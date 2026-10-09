#!/usr/bin/env python3
"""Structural checks for a .docx before you hand it over.

Usage:
  validate_docx.py OUT.docx
  validate_docx.py OUT.docx --original IN.docx            # also: were all edits tracked?
  validate_docx.py OUT.docx --original IN.docx --author "Akash Jha"
  validate_docx.py unpacked/ --json

Checks: every XML part parses; every part has a content type; internal
relationships point at existing parts; revision marks carry id/author/date and
ids are unique; <w:delText> appears only inside deletions and <w:t> never does;
comment references, ranges and comments.xml agree; images referenced by
r:embed exist. With --original, rejects all revisions in both files and
compares the text: any difference is an edit made without track changes.
With --author, new revisions by anyone else are reported.
Exit 0 = clean, 1 = problems found.
"""
import argparse, difflib, json, posixpath, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lxml import etree  # noqa: E402
from wordxml import Package, w, R_NS, CT_NS  # noqa: E402
import track_changes  # noqa: E402


def check_package(pkg, problems):
    names = set(pkg.names())
    roots = {}
    for n in names:
        if n.endswith((".xml", ".rels")):
            try:
                roots[n] = pkg.xml(n)
            except etree.XMLSyntaxError as e:
                problems.append(f"{n}: XML does not parse ({e})")
    ct = roots.get("[Content_Types].xml")
    if ct is None:
        problems.append("missing [Content_Types].xml")
        return roots
    defaults = {d.get("Extension").lower() for d in ct.iter(f"{{{CT_NS}}}Default")}
    overrides = {o.get("PartName") for o in ct.iter(f"{{{CT_NS}}}Override")}
    for n in names:
        if n == "[Content_Types].xml":
            continue
        if "/" + n not in overrides and n.rsplit(".", 1)[-1].lower() not in defaults:
            problems.append(f"{n}: no content type (add a Default or Override)")
    for o in overrides:
        if o.lstrip("/") not in names:
            problems.append(f"[Content_Types].xml: Override for missing part {o}")
    for n, root in roots.items():
        if not n.endswith(".rels"):
            continue
        base = posixpath.dirname(posixpath.dirname(n))
        for rel in root:
            if rel.get("TargetMode") == "External":
                continue
            tgt = rel.get("Target", "")
            path = tgt.lstrip("/") if tgt.startswith("/") else posixpath.normpath(posixpath.join(base, tgt))
            if path not in names:
                problems.append(f"{n}: {rel.get('Id')} -> {tgt} does not exist")
    return roots


def check_story(name, root, problems, rels_ids):
    ids = {}
    for el in root.iter(w("ins"), w("del"), w("moveFrom"), w("moveTo")):
        rid = el.get(w("id"))
        if rid is None or el.get(w("author")) is None:
            problems.append(f"{name}: <{el.tag.split('}')[1]}> without w:id or w:author")
        elif rid in ids:
            problems.append(f"{name}: revision id {rid} used twice")
        ids[rid] = True
    for t in root.iter(w("delText")):
        if not any(a.tag in (w("del"), w("moveFrom")) for a in t.iterancestors()):
            problems.append(f"{name}: <w:delText> outside a deletion: {t.text!r}")
    for d in root.iter(w("del")):
        for t in d.iter(w("t")):
            problems.append(f"{name}: <w:t> inside <w:del> (use <w:delText>): {t.text!r}")
    for el in root.iter():
        emb = el.get(f"{{{R_NS}}}embed") or el.get(f"{{{R_NS}}}id")
        if emb and rels_ids is not None and emb not in rels_ids:
            problems.append(f"{name}: relationship {emb} used but not defined")


def visible_text(pkg):
    root = pkg.xml("word/document.xml")
    track_changes.process(root, "reject", None)
    return ["".join(t.text or "" for t in p.iter(w("t"))) for p in root.iter(w("p"))]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("--original")
    ap.add_argument("--author")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    pkg = Package(a.src)
    problems, warnings = [], []
    roots = check_package(pkg, problems)
    for name in pkg.story_parts():
        if name not in roots:
            continue
        rels_name = posixpath.join(posixpath.dirname(name), "_rels", posixpath.basename(name) + ".rels")
        rels_ids = {r.get("Id") for r in roots[rels_name]} if rels_name in roots else None
        check_story(name, roots[name], problems, rels_ids)
    doc = roots.get("word/document.xml")
    if doc is None:
        problems.append("missing word/document.xml")
    else:
        refs = {e.get(w("id")) for e in doc.iter(w("commentReference"))}
        starts = {e.get(w("id")) for e in doc.iter(w("commentRangeStart"))}
        ends = {e.get(w("id")) for e in doc.iter(w("commentRangeEnd"))}
        cm = roots.get("word/comments.xml")
        defined = {c.get(w("id")) for c in cm.iter(w("comment"))} if cm is not None else set()
        for i in refs - defined:
            problems.append(f"comment reference {i} has no entry in comments.xml")
        for i in starts ^ ends:
            problems.append(f"comment {i}: range start/end not paired")
        for i in defined - refs:
            warnings.append(f"comment {i} is defined but never referenced (invisible)")
    if a.original:
        orig = Package(a.original)
        before, after = visible_text(orig), visible_text(pkg)
        if before != after:
            diff = list(difflib.unified_diff(before, after, "original", "edited(revisions rejected)", lineterm="", n=0))
            problems.append("untracked edits found (text differs after rejecting all revisions):\n  " + "\n  ".join(diff[:40]))
        if a.author:
            def authors(p):
                out = {}
                for n in p.story_parts():
                    for el in p.xml(n).iter(w("ins"), w("del")):
                        out[el.get(w("author"))] = out.get(el.get(w("author")), 0) + 1
                return out
            ob, na = authors(orig), authors(pkg)
            for au, cnt in na.items():
                if au != a.author and cnt > ob.get(au, 0):
                    problems.append(f"{cnt - ob.get(au, 0)} new revision(s) by {au!r}, expected only {a.author!r}")
            if na.get(a.author, 0) == 0:
                warnings.append(f"no revisions by {a.author!r} found")
    if a.json:
        print(json.dumps({"ok": not problems, "problems": problems, "warnings": warnings}, indent=2))
    else:
        for p in problems:
            print("FAIL:", p)
        for wmsg in warnings:
            print("WARN:", wmsg)
        print("OK" if not problems else f"{len(problems)} problem(s)")
    sys.exit(0 if not problems else 1)


if __name__ == "__main__":
    main()
