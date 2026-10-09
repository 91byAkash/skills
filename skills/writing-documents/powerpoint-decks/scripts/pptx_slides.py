#!/usr/bin/env python3
"""Slide-level surgery on a .pptx at the package (XML) level, keeping every
relationship, content type and notes slide consistent. Works on a .pptx file
(write the result with -o) or on a folder unpacked with ooxml.py (edited in place).

Usage:
  pptx_slides.py list deck.pptx
  pptx_slides.py duplicate deck.pptx 3 [--after 5] -o out.pptx   # copy slide 3 (+ its notes and charts)
  pptx_slides.py delete deck.pptx 4 7 -o out.pptx                 # remove slides 4 and 7, then clean
  pptx_slides.py move deck.pptx 6 --to 2 -o out.pptx              # slide 6 becomes slide 2
  pptx_slides.py reorder deck.pptx 1,3,2,4-9 -o out.pptx          # new order; must list every slide (--drop-omitted deletes the rest)
  pptx_slides.py clean unpacked_dir/                              # drop parts nothing references

Slide numbers are 1-based in presentation order. delete/reorder run clean
afterwards, so orphaned slides, notes, charts and media do not bloat the file.
Duplicated slides get their own copy of chart parts so editing one chart does
not change the other; images are shared (that is safe, they are read-only).
"""
import argparse, posixpath, re, sys, zipfile
from pathlib import Path
from lxml import etree

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
}
RT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"
CT_SLIDE = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
CT_NOTES = "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"
CT_CHART = "application/vnd.openxmlformats-officedocument.drawingml.chart+xml"


class Pkg:
    def __init__(self, src):
        self.src = Path(src)
        self.parts = {}
        if self.src.is_dir():
            for f in self.src.rglob("*"):
                if f.is_file() and not f.is_symlink():
                    self.parts[f.relative_to(self.src).as_posix()] = f.read_bytes()
        else:
            with zipfile.ZipFile(self.src) as z:
                for n in z.namelist():
                    if not n.endswith("/"):
                        self.parts[n] = z.read(n)
        if "ppt/presentation.xml" not in self.parts:
            sys.exit("not a presentation package (ppt/presentation.xml missing)")

    # -- xml helpers
    def xml(self, name):
        return etree.fromstring(self.parts[name])

    def put(self, name, tree):
        self.parts[name] = etree.tostring(tree, xml_declaration=True, encoding="UTF-8", standalone=True)

    @staticmethod
    def rels_name(part):
        d, f = posixpath.split(part)
        return posixpath.join(d, "_rels", f + ".rels")

    def rels(self, part):
        rn = self.rels_name(part)
        if rn in self.parts:
            return etree.fromstring(self.parts[rn])
        return etree.Element(f"{{{NS['rel']}}}Relationships", nsmap={None: NS["rel"]})

    @staticmethod
    def resolve(part, target):
        return posixpath.normpath(posixpath.join(posixpath.dirname(part), target))

    def next_name(self, pattern):  # pattern like 'ppt/slides/slide{}.xml'
        n = 1
        while pattern.format(n) in self.parts:
            n += 1
        return pattern.format(n)

    def add_override(self, part, ctype):
        ct = self.xml("[Content_Types].xml")
        if not ct.xpath(f"ct:Override[@PartName='/{part}']", namespaces=NS):
            e = etree.SubElement(ct, f"{{{NS['ct']}}}Override")
            e.set("PartName", "/" + part)
            e.set("ContentType", ctype)
        self.put("[Content_Types].xml", ct)

    # -- slide list
    def slide_list(self):
        pres = self.xml("ppt/presentation.xml")
        prels = self.rels("ppt/presentation.xml")
        rmap = {r.get("Id"): self.resolve("ppt/presentation.xml", r.get("Target")) for r in prels}
        lst = pres.find("p:sldIdLst", NS)
        out = []
        for s in (lst if lst is not None else []):
            out.append((s, rmap.get(s.get(f"{{{NS['r']}}}id"))))
        return pres, lst, out

    def save(self, out):
        if self.src.is_dir() and not out:
            for name, data in self.parts.items():
                f = self.src / name
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes(data)
            existing = {f.relative_to(self.src).as_posix() for f in self.src.rglob("*") if f.is_file()}
            for gone in existing - set(self.parts):
                (self.src / gone).unlink()
            return str(self.src)
        if not out:
            sys.exit("give -o OUT.pptx (the input file is never overwritten in place)")
        if Path(out).resolve() == self.src.resolve():
            sys.exit("-o must differ from the input")
        order = ["[Content_Types].xml"] + sorted(n for n in self.parts if n != "[Content_Types].xml")
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for n in order:
                z.writestr(n, self.parts[n])
        return out


def title_of(pkg, slide_part):
    t = pkg.xml(slide_part)
    for sp in t.iter(f"{{{NS['p']}}}sp"):
        ph = sp.find(".//p:nvPr/p:ph", NS)
        if ph is not None and ph.get("type") in ("title", "ctrTitle"):
            return "".join(sp.itertext()).strip()
    texts = ["".join(x.itertext()) for x in t.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}t")]
    return (texts[0] if texts else "").strip()


def cmd_list(pkg, a):
    _, _, slides = pkg.slide_list()
    for i, (el, part) in enumerate(slides, 1):
        r = pkg.rels(part)
        notes = any(x.get("Type") == RT + "notesSlide" for x in r)
        lay = [posixpath.basename(x.get("Target")) for x in r if x.get("Type") == RT + "slideLayout"]
        hidden = " hidden" if pkg.xml(part).get("show") == "0" else ""
        print(f"{i:>3}  {part:<26} {lay[0] if lay else '-':<18} notes={'y' if notes else 'n'}{hidden}  {title_of(pkg, part)[:60]}")


def copy_chart(pkg, chart_part):
    new = pkg.next_name("ppt/charts/chart{}.xml")
    pkg.parts[new] = pkg.parts[chart_part]
    rn = pkg.rels_name(chart_part)
    if rn in pkg.parts:  # embedded workbook / style parts stay shared but are re-targeted relative to the new part
        pkg.parts[pkg.rels_name(new)] = pkg.parts[rn]
    pkg.add_override(new, CT_CHART)
    return new


def cmd_duplicate(pkg, a):
    pres, lst, slides = pkg.slide_list()
    if not 1 <= a.slide <= len(slides):
        sys.exit(f"slide {a.slide} out of range 1-{len(slides)}")
    src_el, src = slides[a.slide - 1]
    new = pkg.next_name("ppt/slides/slide{}.xml")
    pkg.parts[new] = pkg.parts[src]
    rels = pkg.rels(src)
    for r in list(rels):
        t = r.get("Type")
        if r.get("TargetMode") == "External":
            continue
        target = pkg.resolve(src, r.get("Target"))
        if t == RT + "notesSlide":
            nn = pkg.next_name("ppt/notesSlides/notesSlide{}.xml")
            pkg.parts[nn] = pkg.parts[target]
            nrels = pkg.rels(target)
            for x in nrels:
                if x.get("Type") == RT + "slide":
                    x.set("Target", posixpath.relpath(new, posixpath.dirname(nn)))
            pkg.put(pkg.rels_name(nn), nrels)
            pkg.add_override(nn, CT_NOTES)
            r.set("Target", posixpath.relpath(nn, posixpath.dirname(new)))
        elif t == RT + "chart":
            nc = copy_chart(pkg, target)
            r.set("Target", posixpath.relpath(nc, posixpath.dirname(new)))
    pkg.put(pkg.rels_name(new), rels)
    pkg.add_override(new, CT_SLIDE)
    prels = pkg.rels("ppt/presentation.xml")
    ids = {r.get("Id") for r in prels}
    k = 1
    while f"rId{k}" in ids:
        k += 1
    rel = etree.SubElement(prels, f"{{{NS['rel']}}}Relationship")
    rel.set("Id", f"rId{k}")
    rel.set("Type", RT + "slide")
    rel.set("Target", posixpath.relpath(new, "ppt"))
    pkg.put(pkg.rels_name("ppt/presentation.xml"), prels)
    el = etree.SubElement(lst, f"{{{NS['p']}}}sldId")
    el.set("id", str(max(int(s.get("id")) for s, _ in slides) + 1))
    el.set(f"{{{NS['r']}}}id", f"rId{k}")
    after = a.after if a.after else a.slide
    lst.remove(el)
    lst.insert(after, el)
    pkg.put("ppt/presentation.xml", pres)
    print(f"duplicated slide {a.slide} -> new slide {after + 1} ({new})")


def drop_slides(pkg, keep_parts):
    """Remove slides not in keep_parts from the slide list and from the presentation rels."""
    pres, lst, slides = pkg.slide_list()
    for el, part in slides:
        if part not in keep_parts:
            lst.remove(el)
    prels = pkg.rels("ppt/presentation.xml")
    for r in list(prels):
        if r.get("Type") == RT + "slide" and pkg.resolve("ppt/presentation.xml", r.get("Target")) not in keep_parts:
            prels.remove(r)
    pkg.put("ppt/presentation.xml", pres)
    pkg.put(pkg.rels_name("ppt/presentation.xml"), prels)


def parse_nums(spec_list, n):
    out = []
    for spec in spec_list:
        for part in str(spec).split(","):
            lo, _, hi = part.partition("-")
            out += range(int(lo), int(hi or lo) + 1)
    bad = [x for x in out if not 1 <= x <= n]
    if bad:
        sys.exit(f"slide number(s) out of range 1-{n}: {bad}")
    return out


def cmd_delete(pkg, a):
    _, _, slides = pkg.slide_list()
    gone = set(parse_nums(a.slides, len(slides)))
    if len(gone) == len(slides):
        sys.exit("refusing to delete every slide")
    drop_slides(pkg, {p for i, (_, p) in enumerate(slides, 1) if i not in gone})
    print(f"deleted slides {sorted(gone)}")
    clean(pkg)


def cmd_move(pkg, a):
    pres, lst, slides = pkg.slide_list()
    n = len(slides)
    if not (1 <= a.slide <= n and 1 <= a.to <= n):
        sys.exit(f"slide numbers must be within 1-{n}")
    el = slides[a.slide - 1][0]
    lst.remove(el)
    lst.insert(a.to - 1, el)
    pkg.put("ppt/presentation.xml", pres)
    print(f"moved slide {a.slide} -> {a.to}")


def cmd_reorder(pkg, a):
    pres, lst, slides = pkg.slide_list()
    order = parse_nums([a.order], len(slides))
    if len(set(order)) != len(order):
        sys.exit("a slide appears twice; use duplicate first")
    missing = [i for i in range(1, len(slides) + 1) if i not in order]
    if missing and not a.drop_omitted:
        sys.exit(f"error: order omits slides {missing} of {len(slides)}; list every slide "
                 f"(e.g. 1,3,2,4-{len(slides)}) or pass --drop-omitted to delete them")
    for el, _ in slides:
        lst.remove(el)
    for i in order:
        lst.append(slides[i - 1][0])
    pkg.put("ppt/presentation.xml", pres)
    dropped = [i for i in range(1, len(slides) + 1) if i not in order]
    if dropped:
        drop_slides(pkg, {slides[i - 1][1] for i in order})
        print(f"dropped slides {dropped}")
    print(f"new order: {order}")
    clean(pkg)


def clean(pkg, verbose=True):
    """Remove parts unreachable from the root relationships (plus their rels and overrides)."""
    reach, todo = set(), ["", ]
    # the package root rels are '_rels/.rels' and belong to part ''
    while todo:
        part = todo.pop()
        rn = "_rels/.rels" if part == "" else pkg.rels_name(part)
        if rn not in pkg.parts:
            continue
        for r in etree.fromstring(pkg.parts[rn]):
            if r.get("TargetMode") == "External":
                continue
            tgt = r.get("Target")
            t = tgt.lstrip("/") if tgt.startswith("/") else pkg.resolve(part or "x", tgt) if part else tgt
            if t not in reach and t in pkg.parts:
                reach.add(t)
                todo.append(t)
    keep = {"[Content_Types].xml", "_rels/.rels"} | reach | {pkg.rels_name(p) for p in reach}
    gone = sorted(n for n in pkg.parts if n not in keep)
    for n in gone:
        del pkg.parts[n]
    ct = pkg.xml("[Content_Types].xml")
    for o in ct.xpath("ct:Override", namespaces=NS):
        if o.get("PartName").lstrip("/") not in pkg.parts:
            ct.remove(o)
    pkg.put("[Content_Types].xml", ct)
    if verbose:
        print(f"clean: removed {len(gone)} unreferenced part(s)" + (": " + ", ".join(gone[:8]) + (" ..." if len(gone) > 8 else "") if gone else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    def add(name, **kw):
        s = sub.add_parser(name)
        s.add_argument("src")
        if name != "list":
            s.add_argument("-o", "--out")
        return s
    add("list")
    s = add("duplicate"); s.add_argument("slide", type=int); s.add_argument("--after", type=int)
    s = add("delete"); s.add_argument("slides", nargs="+")
    s = add("move"); s.add_argument("slide", type=int); s.add_argument("--to", type=int, required=True)
    s = add("reorder"); s.add_argument("order")
    s.add_argument("--drop-omitted", action="store_true", help="delete slides left out of ORDER")
    add("clean")
    a = ap.parse_args()
    pkg = Pkg(a.src)
    if a.cmd == "list":
        return cmd_list(pkg, a)
    {"duplicate": cmd_duplicate, "delete": cmd_delete, "move": cmd_move, "reorder": cmd_reorder,
     "clean": lambda p, _: clean(p)}[a.cmd](pkg, a)
    print("wrote", pkg.save(getattr(a, "out", None)))


if __name__ == "__main__":
    main()
