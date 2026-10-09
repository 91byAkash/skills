#!/usr/bin/env python3
"""Create a document skeleton with every section marked [To be written], so
drafting proceeds section by section and doc_status.py can track progress.

Usage:
  scaffold_doc.py --list
  scaffold_doc.py decision-doc "Move billing to the new ledger" --owner "Priya Rao" -o billing-decision.md
  scaffold_doc.py design-doc "Search v2" --sections "Summary,Problem,Proposal,Rollout,Open questions" -o search.md
  scaffold_doc.py adr "Use Postgres for events" --number 12 -o docs/adr/0012-postgres-events.md

Types come from ../templates/*.md (design-doc, decision-doc, prd, proposal, adr,
one-pager). --sections overrides the template's sections (their guidance text is
reused when the heading matches). Refuses to overwrite an existing file unless --force.
"""
import argparse, datetime, re, sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
SKIP = {"reader-test-prompts"}


def types():
    return sorted(p.stem for p in TEMPLATES.glob("*.md") if p.stem not in SKIP)


def sections_of(text):
    """Split a template into (heading, body) pairs at level-2 headings."""
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    head, rest = parts[0], parts[1:]
    return head, [(rest[i].strip(), rest[i + 1].strip()) for i in range(0, len(rest), 2)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("type", nargs="?")
    ap.add_argument("title", nargs="?")
    ap.add_argument("--owner", default="[Owner]")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--number", default="NNN")
    ap.add_argument("--sections")
    ap.add_argument("-o", "--out")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list or not a.type:
        for t in types():
            _, secs = sections_of((TEMPLATES / f"{t}.md").read_text(encoding="utf-8"))
            print(f"{t:<14} {', '.join(h for h, _ in secs)}")
        return
    aliases = {"decision": "decision-doc", "design": "design-doc", "rfc": "design-doc", "spec": "design-doc",
               "onepager": "one-pager", "1-pager": "one-pager", "pitch": "proposal"}
    a.type = aliases.get(a.type.lower(), a.type.lower())
    if a.type not in types():
        sys.exit(f"unknown type {a.type!r}; choose from: {', '.join(types())}")
    if not a.title:
        sys.exit("give a title")
    text = (TEMPLATES / f"{a.type}.md").read_text(encoding="utf-8")
    text = text.replace("{title}", a.title).replace("{owner}", a.owner).replace("{date}", a.date).replace("{number}", str(a.number))
    head, secs = sections_of(text)
    if a.sections:
        known = {h.lower(): b for h, b in secs}
        secs = [(h.strip(), known.get(h.strip().lower(), "[To be written]")) for h in a.sections.split(",") if h.strip()]
    doc = head.rstrip() + "\n\n" + "\n\n".join(f"## {h}\n\n{b}" for h, b in secs) + "\n"
    out = Path(a.out or re.sub(r"[^a-z0-9]+", "-", a.title.lower()).strip("-") + ".md")
    if out.exists() and not a.force:
        sys.exit(f"{out} exists; pass --force to overwrite")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out}: {len(secs)} sections ({', '.join(h for h, _ in secs)})")


if __name__ == "__main__":
    main()
