#!/usr/bin/env python3
"""Coalesce adjacent runs that have identical formatting so visible phrases
become findable strings in the XML. Content and rendering do not change.

Usage:
  merge_runs.py unpacked_dir/                 # edits word/*.xml in place
  merge_runs.py in.docx -o merged.docx        # works on a file directly

Also drops spell/grammar markers (<w:proofErr>) and run-level rsid attributes,
which are what fragment text in the first place.
"""
import argparse, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lxml import etree  # noqa: E402
from wordxml import Package, w, XML_SPACE  # noqa: E402

RSID_ATTRS = [w(a) for a in ("rsidR", "rsidRPr", "rsidDel", "rsidRDefault")]


def rpr_key(run):
    rpr = run.find(w("rPr"))
    return b"" if rpr is None else etree.tostring(rpr, method="c14n")


def plain_text_run(run):
    kids = [c for c in run if c.tag != w("rPr")]
    return len(kids) == 1 and kids[0].tag == w("t")


def merge_in(root):
    merged = 0
    for pe in list(root.iter(w("proofErr"))):
        pe.getparent().remove(pe)
    for run in root.iter(w("r")):
        for a in RSID_ATTRS:
            run.attrib.pop(a, None)
    for parent in list(root.iter()):
        prev = None
        for child in list(parent):
            if child.tag == w("r") and plain_text_run(child):
                if prev is not None and rpr_key(prev) == rpr_key(child):
                    pt, ct = prev.find(w("t")), child.find(w("t"))
                    pt.text = (pt.text or "") + (ct.text or "")
                    pt.set(XML_SPACE, "preserve")
                    parent.remove(child)
                    merged += 1
                    continue
                prev = child
            else:
                prev = None
    return merged


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    pkg = Package(a.src)
    if not pkg.is_dir and not a.out:
        sys.exit("error: pass -o OUT.docx when the input is a file")
    total = 0
    for name in pkg.story_parts():
        root = pkg.xml(name)
        n = merge_in(root)
        total += n
        pkg.write(name, root)
    pkg.save(a.out)
    print(f"merged {total} runs")


if __name__ == "__main__":
    main()
