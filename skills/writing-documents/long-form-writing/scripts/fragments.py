#!/usr/bin/env python3
"""Append-only fragment file for fragments mode.

File shape: one H1 working title, then fragments separated by a line containing only '---'.
No headings inside the body, no tags, no metadata.

  fragments.py init  notes.md "Working title"     create (refuses if the file exists)
  fragments.py add   notes.md [--text "..."|-]     re-read from disk, then append one fragment (stdin with '-')
  fragments.py list  notes.md                      numbered fragments with first line and word count
  fragments.py show  notes.md N                    print fragment N
  fragments.py edit  notes.md N [--text|-]         replace fragment N in place (only when the user asked)
  fragments.py cut   notes.md N                    delete fragment N (only when the user asked)
  fragments.py title notes.md "New title"          change the working title
  fragments.py check notes.md                      format problems: missing/extra H1, headings in body, empty fragments, duplicates
"""
import argparse, re, sys
from pathlib import Path

SEP = "\n\n---\n\n"


def load(p):
    text = Path(p).read_text(encoding="utf-8")
    m = re.match(r"\s*# (.+)\n", text)
    title = m.group(1).strip() if m else None
    body = text[m.end():] if m else text
    frags = [f.strip("\n") for f in re.split(r"\n[ \t]*---[ \t]*\n", "\n" + body + "\n")]
    frags = [f for f in frags if f.strip()]
    return title, frags


def save(p, title, frags):
    out = f"# {title}\n\n" + SEP.join(f.strip("\n") for f in frags) + ("\n" if frags else "")
    Path(p).write_text(out, encoding="utf-8")


def read_text(a):
    if a.text is not None and a.text != "-":
        return a.text
    if a.dash not in (None, "-"):
        return a.dash  # positional text: `add notes.md "fragment"`
    if sys.stdin.isatty():
        sys.exit("give the fragment with --text \"...\", as a quoted argument, or pipe it in with '-'")
    return sys.stdin.read()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("file"); s.add_argument("title")
    s = sub.add_parser("add"); s.add_argument("file"); s.add_argument("dash", nargs="?"); s.add_argument("--text")
    s = sub.add_parser("list"); s.add_argument("file")
    s = sub.add_parser("show"); s.add_argument("file"); s.add_argument("n", type=int)
    s = sub.add_parser("edit"); s.add_argument("file"); s.add_argument("n", type=int); s.add_argument("dash", nargs="?"); s.add_argument("--text")
    s = sub.add_parser("cut"); s.add_argument("file"); s.add_argument("n", type=int)
    s = sub.add_parser("title"); s.add_argument("file"); s.add_argument("title")
    s = sub.add_parser("check"); s.add_argument("file")
    a = ap.parse_args()
    p = Path(a.file)

    if a.cmd == "init":
        if p.exists():
            sys.exit(f"{p} exists; not overwriting (use add)")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"# {a.title}\n", encoding="utf-8")
        print(f"created {p}")
        return
    if not p.exists():
        sys.exit(f"{p} not found; run init first")
    title, frags = load(p)

    if a.cmd == "add":
        new = read_text(a).strip("\n")
        if not new.strip():
            sys.exit("empty fragment; nothing added")
        if re.search(r"^[ \t]*---[ \t]*$", new, re.M):
            sys.exit("fragment contains a '---' line, which would split it; use *** or rephrase")
        raw = p.read_text(encoding="utf-8")  # append to what is on disk now, never rewrite
        k = len(raw) - len(raw.rstrip("\n"))
        joiner = "\n" * max(0, 2 - k) + ("---\n\n" if frags else "")
        with p.open("a", encoding="utf-8") as fh:
            fh.write(joiner + new + "\n")
        print(f"added fragment {len(frags) + 1} ({len(new.split())} words)")
    elif a.cmd == "list":
        print(f"# {title}")
        for i, f in enumerate(frags, 1):
            first = next((l for l in f.splitlines() if l.strip()), "")
            print(f"{i:3}. [{len(f.split()):3}w] {first[:80]}")
    elif a.cmd == "show":
        print(frags[a.n - 1])
    elif a.cmd in ("edit", "cut"):
        if not 1 <= a.n <= len(frags):
            sys.exit(f"no fragment {a.n} (have {len(frags)})")
        if a.cmd == "edit":
            frags[a.n - 1] = read_text(a).strip("\n")
        else:
            del frags[a.n - 1]
        save(p, title, frags)
        print(f"{a.cmd} fragment {a.n}; {len(frags)} fragments")
    elif a.cmd == "title":
        save(p, a.title, frags)
        print("title updated")
    elif a.cmd == "check":
        problems = []
        raw = p.read_text(encoding="utf-8")
        if not title:
            problems.append("no H1 working title on the first line")
        if len(re.findall(r"^# ", raw, re.M)) > 1:
            problems.append("more than one H1")
        for i, f in enumerate(frags, 1):
            if re.search(r"^#{1,6} ", f, re.M):
                problems.append(f"fragment {i}: heading inside the body (fragments carry no structure)")
            if re.search(r"^(tags?|date|status)\s*:", f, re.M | re.I):
                problems.append(f"fragment {i}: metadata line")
        seen = {}
        for i, f in enumerate(frags, 1):
            k = re.sub(r"\W+", " ", f.lower()).strip()
            if k in seen:
                problems.append(f"fragment {i} duplicates fragment {seen[k]}")
            seen.setdefault(k, i)
        for pr in problems:
            print("WARN", pr)
        print(f"{len(frags)} fragments, {sum(len(f.split()) for f in frags)} words; {len(problems)} problem(s)")
        sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
