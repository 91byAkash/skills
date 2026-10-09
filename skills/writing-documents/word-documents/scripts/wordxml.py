"""Shared helpers for the docx scripts: open a .docx or an unpacked folder,
parse parts with lxml (which keeps namespace prefixes intact), and split runs
so edits can target exact character ranges. Not a CLI."""
import copy, io, zipfile
from pathlib import Path
from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
NS = {"w": W_NS, "r": R_NS}
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def w(tag):
    return f"{{{W_NS}}}{tag}"


class Package:
    """Uniform access to parts whether the source is a .docx or a folder."""

    def __init__(self, src):
        self.src = Path(src)
        self.is_dir = self.src.is_dir()
        self.parts = {}
        if not self.is_dir:
            with zipfile.ZipFile(self.src) as z:
                for i in z.infolist():
                    if not i.filename.endswith("/"):
                        self.parts[i.filename] = z.read(i)

    def names(self):
        if self.is_dir:
            return sorted(p.relative_to(self.src).as_posix() for p in self.src.rglob("*") if p.is_file())
        return sorted(self.parts)

    def has(self, name):
        return (self.src / name).exists() if self.is_dir else name in self.parts

    def read(self, name):
        return (self.src / name).read_bytes() if self.is_dir else self.parts[name]

    def xml(self, name):
        parser = etree.XMLParser(remove_blank_text=False, resolve_entities=False, no_network=True)
        return etree.fromstring(self.read(name), parser)

    def write(self, name, data):
        if isinstance(data, etree._Element):
            data = etree.tostring(data, xml_declaration=True, encoding="UTF-8", standalone=True)
        if self.is_dir:
            p = self.src / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        else:
            self.parts[name] = data

    def save(self, out=None):
        """Folder: already written. File: write to out (or back to src)."""
        if self.is_dir:
            return self.src
        out = Path(out or self.src)
        order = sorted(self.parts, key=lambda n: (n != "[Content_Types].xml", n))
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for n in order:
                z.writestr(n, self.parts[n])
        out.write_bytes(buf.getvalue())
        return out

    def story_parts(self):
        """document.xml plus headers, footers, footnotes, endnotes."""
        out = []
        for n in self.names():
            if n == "word/document.xml" or (n.startswith("word/") and n.split("/")[-1].startswith(("header", "footer", "footnotes", "endnotes")) and n.endswith(".xml")):
                out.append(n)
        return out


def run_text_children(run):
    return [c for c in run if c.tag in (w("t"), w("delText"), w("tab"), w("br"), w("cr"), w("noBreakHyphen"))]


def normalize_runs(paragraph):
    """Split runs that carry several text/tab/br children into one run per child,
    each with a copy of the run properties. Makes offset maths simple."""
    for run in list(paragraph.iter(w("r"))):
        kids = run_text_children(run)
        if len(kids) <= 1:
            continue
        rpr = run.find(w("rPr"))
        parent = run.getparent()
        idx = parent.index(run)
        new_runs = []
        for k in kids:
            nr = etree.Element(w("r"), nsmap=run.nsmap)
            for attr, val in run.attrib.items():
                nr.set(attr, val)
            if rpr is not None:
                nr.append(copy.deepcopy(rpr))
            nr.append(copy.deepcopy(k))
            new_runs.append(nr)
        others = [c for c in run if c is not rpr and c not in kids]
        if others:  # unusual content (fldChar, drawing...): keep the run untouched
            continue
        parent.remove(run)
        for off, nr in enumerate(new_runs):
            parent.insert(idx + off, nr)


def text_runs(paragraph):
    """(run, text) for visible text runs in order: w:t only, skipping deleted text."""
    out = []
    for run in paragraph.iter(w("r")):
        if any(a.tag in (w("del"), w("moveFrom")) for a in run.iterancestors()):
            continue
        t = run.find(w("t"))
        if t is not None:
            out.append((run, t.text or ""))
    return out


def split_run(run, offset):
    """Split a single-<w:t> run at character offset; returns (left, right)."""
    t = run.find(w("t"))
    text = t.text or ""
    if offset <= 0 or offset >= len(text):
        return run, None
    right = copy.deepcopy(run)
    t.text = text[:offset]
    t.set(XML_SPACE, "preserve")
    rt = right.find(w("t"))
    rt.text = text[offset:]
    rt.set(XML_SPACE, "preserve")
    run.addnext(right)
    return run, right


def isolate(paragraph, start, end):
    """Make [start, end) of the paragraph's visible text exactly a list of whole runs."""
    normalize_runs(paragraph)
    pos = 0
    for run, text in text_runs(paragraph):
        rs, re_ = pos, pos + len(text)
        if rs < start < re_:
            split_run(run, start - rs)
            return isolate(paragraph, start, end)
        if rs < end < re_:
            split_run(run, end - rs)
            return isolate(paragraph, start, end)
        pos = re_
    pos, chosen = 0, []
    for run, text in text_runs(paragraph):
        if pos >= start and pos + len(text) <= end and text:
            chosen.append(run)
        pos += len(text)
    return chosen


def paragraph_text(p):
    return "".join(t for _, t in text_runs(p))


def next_revision_id(root_parts):
    mx = 0
    for root in root_parts:
        for el in root.iter():
            v = el.get(w("id"))
            if v is not None and v.lstrip("-").isdigit():
                mx = max(mx, int(v))
    return mx + 1
