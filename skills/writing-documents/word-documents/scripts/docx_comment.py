#!/usr/bin/env python3
"""Add review comments to a .docx, anchored to a phrase.

Usage:
  docx_comment.py IN.docx -o OUT.docx --anchor "liability cap" --text "Cap is too low" [--author NAME] [--initials AJ]
  docx_comment.py unpacked/ --anchor "Section 4" --text "Agreed" --occurrence 2
  docx_comment.py IN.docx -o OUT.docx --batch comments.json
      comments.json: [{"anchor": "...", "text": "...", "author": "..."}]

Creates word/comments.xml when missing, registers its relationship and content
type, and places commentRangeStart/End plus the reference run around the anchor
(the anchor may span runs, but must sit within one paragraph). Multi-line comment
text: separate paragraphs with "\\n". A reply is simply another comment on the
same anchor; Word lists them together.
"""
import argparse, datetime as dt, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lxml import etree  # noqa: E402
from wordxml import Package, w, W_NS, PKG_REL_NS, CT_NS, isolate, paragraph_text  # noqa: E402

COMMENTS_PART = "word/comments.xml"
COMMENTS_CT = "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"
COMMENTS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"


def ensure_comments_part(pkg):
    if pkg.has(COMMENTS_PART):
        return pkg.xml(COMMENTS_PART)
    root = etree.Element(w("comments"), nsmap={"w": W_NS})
    ct = pkg.xml("[Content_Types].xml")
    if not any(o.get("PartName") == "/" + COMMENTS_PART for o in ct):
        o = etree.SubElement(ct, f"{{{CT_NS}}}Override")
        o.set("PartName", "/" + COMMENTS_PART)
        o.set("ContentType", COMMENTS_CT)
        pkg.write("[Content_Types].xml", ct)
    rels_name = "word/_rels/document.xml.rels"
    rels = pkg.xml(rels_name)
    if not any(r.get("Type") == COMMENTS_REL for r in rels):
        ids = {r.get("Id") for r in rels}
        n = 1
        while f"rId{n}" in ids:
            n += 1
        r = etree.SubElement(rels, f"{{{PKG_REL_NS}}}Relationship")
        r.set("Id", f"rId{n}"); r.set("Type", COMMENTS_REL); r.set("Target", "comments.xml")
        pkg.write(rels_name, rels)
    return root


def add_comment(doc, comments, anchor, text, author, initials, date, occurrence=1):
    cid = max([int(c.get(w("id"))) for c in comments.iter(w("comment"))] + [-1]) + 1
    seen = 0
    for p in doc.iter(w("p")):
        ptext = paragraph_text(p)
        start = ptext.find(anchor)
        while start != -1:
            seen += 1
            if seen == occurrence:
                runs = isolate(p, start, start + len(anchor))
                first, last = runs[0], runs[-1]
                rs = etree.Element(w("commentRangeStart")); rs.set(w("id"), str(cid))
                re_ = etree.Element(w("commentRangeEnd")); re_.set(w("id"), str(cid))
                first.addprevious(rs)
                last.addnext(re_)
                ref_run = etree.Element(w("r"))
                rpr = etree.SubElement(ref_run, w("rPr"))
                etree.SubElement(rpr, w("rStyle")).set(w("val"), "CommentReference")
                etree.SubElement(ref_run, w("commentReference")).set(w("id"), str(cid))
                re_.addnext(ref_run)
                c = etree.SubElement(comments, w("comment"))
                c.set(w("id"), str(cid)); c.set(w("author"), author)
                c.set(w("date"), date); c.set(w("initials"), initials)
                for i, line in enumerate(text.split("\n")):
                    cp = etree.SubElement(c, w("p"))
                    if i == 0:
                        ar = etree.SubElement(cp, w("r"))
                        arp = etree.SubElement(ar, w("rPr"))
                        etree.SubElement(arp, w("rStyle")).set(w("val"), "CommentReference")
                        etree.SubElement(ar, w("annotationRef"))
                    cr = etree.SubElement(cp, w("r"))
                    t = etree.SubElement(cr, w("t")); t.text = line
                    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                return cid
            start = ptext.find(anchor, start + 1)
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("-o", "--out")
    ap.add_argument("--anchor")
    ap.add_argument("--text")
    ap.add_argument("--author", default="Reviewer")
    ap.add_argument("--initials")
    ap.add_argument("--occurrence", type=int, default=1)
    ap.add_argument("--batch")
    ap.add_argument("--date", default=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    a = ap.parse_args()
    items = json.loads(Path(a.batch).read_text()) if a.batch else [{"anchor": a.anchor, "text": a.text}]
    if any(not i.get("anchor") or not i.get("text") for i in items):
        sys.exit("error: each comment needs anchor and text")
    pkg = Package(a.src)
    if not pkg.is_dir and not a.out:
        sys.exit("error: pass -o OUT.docx when the input is a file")
    doc = pkg.xml("word/document.xml")
    comments = ensure_comments_part(pkg)
    failed = 0
    for it in items:
        author = it.get("author", a.author)
        initials = it.get("initials") or a.initials or "".join(x[0] for x in author.split()[:3]).upper()
        cid = add_comment(doc, comments, it["anchor"], it["text"], author, initials, a.date, it.get("occurrence", a.occurrence))
        if cid is None:
            failed += 1
            print(f"not found: {it['anchor']!r}", file=sys.stderr)
        else:
            print(f"comment {cid} on {it['anchor']!r}")
    pkg.write("word/document.xml", doc)
    pkg.write(COMMENTS_PART, comments)
    pkg.save(a.out)
    sys.exit(2 if failed else 0)


if __name__ == "__main__":
    main()
