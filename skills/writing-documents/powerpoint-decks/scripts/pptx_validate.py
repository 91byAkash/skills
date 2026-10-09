#!/usr/bin/env python3
"""Package-level validation for a .pptx (or unpacked folder) — the faults that
make PowerPoint refuse or "repair" a file even though python-pptx and LibreOffice
open it happily.

Usage:
  pptx_validate.py deck.pptx
  pptx_validate.py out.pptx --original template.pptx   # ignore problems the template already had
  pptx_validate.py deck.pptx --json

Checks
  package   every internal relationship target exists; every part has a content
            type (Override or Default by extension); no duplicate rel ids
  slides    sldIdLst ids unique and >= 256; each r:id resolves to a slide part;
            notes slides point back at the slide that owns them
  order     children of <p:presentation> in schema order (sldMasterIdLst,
            notesMasterIdLst, handoutMasterIdLst, sldIdLst, sldSz, notesSz, ...)
  xml       every XML part parses; colour values are 6 hex digits; shadow
            distances are not negative; <a:t> with edge spaces has xml:space="preserve"
  charts    stacked bar/column data labels not at outEnd; every c:axId used by a
            plot is declared as an axis in the same chart
Exit 1 on any ERROR that is not also in --original.
"""
import argparse, json, posixpath, re, sys, zipfile
from pathlib import Path
from lxml import etree

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
C = "http://schemas.openxmlformats.org/drawingml/2006/chart"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
XMLNS = "http://www.w3.org/XML/1998/namespace"
PRES_ORDER = ["sldMasterIdLst", "notesMasterIdLst", "handoutMasterIdLst", "sldIdLst", "sldSz", "notesSz",
              "smartTags", "embeddedFontLst", "custShowLst", "photoAlbum", "custDataLst", "kinsoku",
              "defaultTextStyle", "modifyVerifier", "extLst"]


def load(src):
    src = Path(src)
    if src.is_dir():
        return {f.relative_to(src).as_posix(): f.read_bytes() for f in src.rglob("*") if f.is_file()}
    with zipfile.ZipFile(src) as z:
        return {n: z.read(n) for n in z.namelist() if not n.endswith("/")}


def rels_owner(rels_name):
    d, f = posixpath.split(rels_name)
    return posixpath.join(posixpath.dirname(d), f[:-5]) if f != ".rels" else ""


def check(parts):
    issues = []
    add = lambda sev, where, msg: issues.append({"severity": sev, "part": where, "msg": msg})
    trees = {}
    for n, data in parts.items():
        if n.endswith(".xml") or n.endswith(".rels"):
            try:
                trees[n] = etree.fromstring(data)
            except etree.XMLSyntaxError as e:
                add("ERROR", n, f"XML does not parse: {e}")
    ct = trees.get("[Content_Types].xml")
    if ct is None:
        add("ERROR", "[Content_Types].xml", "missing")
        return issues
    overrides = {o.get("PartName").lstrip("/") for o in ct.findall(f"{{{CT}}}Override")}
    defaults = {d.get("Extension").lower() for d in ct.findall(f"{{{CT}}}Default")}
    for n in parts:
        if n == "[Content_Types].xml":
            continue
        if n not in overrides and n.rsplit(".", 1)[-1].lower() not in defaults:
            add("ERROR", n, "no content type (add an Override or a Default for its extension)")
    for o in overrides:
        if o not in parts:
            add("ERROR", "[Content_Types].xml", f"Override for missing part /{o}")
    # relationships
    for n, t in trees.items():
        if not n.endswith(".rels"):
            continue
        owner = rels_owner(n)
        seen = set()
        for r in t.findall(f"{{{REL}}}Relationship"):
            rid = r.get("Id")
            if rid in seen:
                add("ERROR", n, f"duplicate relationship id {rid}")
            seen.add(rid)
            if r.get("TargetMode") == "External":
                continue
            tgt = r.get("Target")
            path = tgt.lstrip("/") if tgt.startswith("/") else posixpath.normpath(posixpath.join(posixpath.dirname(owner), tgt))
            if path not in parts:
                add("ERROR", n, f"{rid} points at missing part {path}")
    # presentation
    pres = trees.get("ppt/presentation.xml")
    if pres is not None:
        names = [etree.QName(c).localname for c in pres]
        idx = [PRES_ORDER.index(x) for x in names if x in PRES_ORDER]
        if idx != sorted(idx):
            add("ERROR", "ppt/presentation.xml", f"children out of schema order: {names}")
        prel = trees.get("ppt/_rels/presentation.xml.rels")
        rmap = {r.get("Id"): r.get("Target") for r in (prel if prel is not None else [])}
        ids = []
        for s in pres.iter(f"{{{P}}}sldId"):
            ids.append(int(s.get("id")))
            rid = s.get(f"{{{R}}}id")
            if rid not in rmap:
                add("ERROR", "ppt/presentation.xml", f"sldId {s.get('id')} uses unknown {rid}")
        if len(ids) != len(set(ids)):
            add("ERROR", "ppt/presentation.xml", "duplicate slide ids in sldIdLst")
        if any(i < 256 for i in ids):
            add("ERROR", "ppt/presentation.xml", "slide ids must be >= 256")
    # notes back-references
    for n in parts:
        m = re.match(r"ppt/slides/_rels/(slide\d+\.xml)\.rels$", n)
        if not m or n not in trees:
            continue
        for r in trees[n]:
            if r.get("Type", "").endswith("/notesSlide"):
                notes = posixpath.normpath(posixpath.join("ppt/slides", r.get("Target")))
                nr = trees.get(posixpath.join(posixpath.dirname(notes), "_rels", posixpath.basename(notes) + ".rels"))
                back = [x.get("Target") for x in (nr if nr is not None else []) if x.get("Type", "").endswith("/slide")]
                if back and posixpath.basename(back[0]) != m.group(1):
                    add("ERROR", notes, f"notes slide belongs to {back[0]}, but {m.group(1)} links to it (shared notes)")
    # xml-level content checks
    for n, t in trees.items():
        if not n.startswith("ppt/") or n.endswith(".rels"):
            continue
        for e in t.iter(f"{{{A}}}srgbClr"):
            if not re.fullmatch(r"[0-9A-Fa-f]{6}", e.get("val", "")):
                add("ERROR", n, f"colour value {e.get('val')!r} is not 6 hex digits")
        for e in t.iter(f"{{{A}}}outerShdw", f"{{{A}}}innerShdw"):
            if int(e.get("dist", "0")) < 0:
                add("ERROR", n, "negative shadow distance; use a positive dist and change dir instead")
        for e in t.iter(f"{{{A}}}t"):
            if e.text and e.text != e.text.strip() and e.get(f"{{{XMLNS}}}space") != "preserve":
                add("WARN", n, f"text {e.text[:30]!r} has edge spaces without xml:space=\"preserve\"")
        if n.startswith("ppt/charts/chart"):
            for bar in t.iter(f"{{{C}}}barChart"):
                grp = bar.find(f"{{{C}}}grouping")
                if grp is not None and grp.get("val") in ("stacked", "percentStacked"):
                    for pos in bar.iter(f"{{{C}}}dLblPos"):
                        if pos.get("val") == "outEnd":
                            add("ERROR", n, "stacked bar/column labels at outEnd; use ctr, inEnd or inBase")
                            break
            declared = set()
            for ax in ("catAx", "valAx", "dateAx", "serAx"):
                for e in t.iter(f"{{{C}}}{ax}"):
                    i = e.find(f"{{{C}}}axId")
                    if i is not None:
                        declared.add(i.get("val"))
            pa = t.find(f".//{{{C}}}plotArea")
            if pa is not None:
                for plot in pa:
                    if etree.QName(plot).localname.endswith("Chart"):
                        for i in plot.findall(f"{{{C}}}axId"):
                            if i.get("val") not in declared:
                                add("ERROR", n, f"plot uses axis id {i.get('val')} that no axis declares")
    return issues


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--original")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    issues = check(load(a.deck))
    if a.original:
        base = {(i["part"], i["msg"]) for i in check(load(a.original))}
        for i in issues:
            if (i["part"], i["msg"]) in base:
                i["severity"] = "INHERITED"
    if a.json:
        print(json.dumps(issues, indent=2))
    else:
        for i in issues:
            print(f"{i['severity']:<9} {i['part']}: {i['msg']}")
        errs = sum(i["severity"] == "ERROR" for i in issues)
        print(f"{errs} error(s), {sum(i['severity'] == 'WARN' for i in issues)} warning(s), "
              f"{sum(i['severity'] == 'INHERITED' for i in issues)} inherited")
    sys.exit(1 if any(i["severity"] == "ERROR" for i in issues) else 0)


if __name__ == "__main__":
    main()
