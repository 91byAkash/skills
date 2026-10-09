#!/usr/bin/env python3
"""Check that a compressed prose file kept everything that must survive.

Usage: compress-check.py ORIGINAL COMPRESSED [--allow TEXT ...]
  --allow TEXT   an item deliberately removed with the user's agreement (a stale path,
                 number, or heading, exactly as reported); "negations" accepts a lower
                 negation count after merging duplicate rules. Repeatable.
Fails (exit 1) when any of these from ORIGINAL is missing or changed in COMPRESSED:
  - fenced code blocks (must be byte-identical, same order)
  - inline code spans, URLs, file paths, env vars, numbers/versions
  - markdown headings (exact text) and frontmatter
  - negation words (count must not drop)
Prints word counts and savings either way.
"""
import re
import sys

FENCE = re.compile(r"^(```|~~~).*?^\1[ \t]*$", re.M | re.S)
NEGATIONS = re.compile(r"\b(not|never|no|none|nor|only|except|without|cannot|can't|don't|doesn't|won't|isn't|aren't|mustn't|shouldn't)\b", re.I)


def parts(text):
    fences = [m.group(0) for m in FENCE.finditer(text)]
    prose = FENCE.sub("", text)
    inline = re.findall(r"`[^`\n]+`", prose)
    prose_no_inline = re.sub(r"`[^`\n]+`", "", prose)
    urls = [u.rstrip(".,;:!?'\"") for u in re.findall(r"https?://[^\s)>\]]+", prose_no_inline)]
    prose_plain = re.sub(r"https?://[^\s)>\]]+", "", prose_no_inline)
    paths = [p.rstrip(".") for p in re.findall(r"(?<![\w/])(?:\.{0,2}/)?(?:[\w.-]+/)+[\w.-]+", prose_plain)]
    envs = re.findall(r"\$\{?[A-Z_][A-Z0-9_]*\}?|\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b", prose_plain)
    nums = re.findall(r"\b\d+(?:[.,:]\d+)*(?: ?(?:%|ms|s|min|h|kb|mb|gb|tb|px|rem|em)\b)?", prose_plain, re.I)
    heads = re.findall(r"^#{1,6} .+$", prose, re.M)
    front = re.match(r"^---\n.*?\n---\n", text, re.S)
    return {
        "fences": fences, "inline": inline, "urls": urls, "paths": paths,
        "env vars": envs, "numbers": nums, "headings": heads,
        "frontmatter": [front.group(0)] if front else [],
        "negations": NEGATIONS.findall(prose_plain),
        "words": len(re.findall(r"\S+", text)),
    }


def main():
    args, allow = [], set()
    argv = sys.argv[1:]
    while argv:
        x = argv.pop(0)
        if x in ("-h", "--help"):
            print(__doc__)
            return 0
        if x == "--allow":
            if not argv:
                print("--allow needs a value", file=sys.stderr)
                return 2
            allow.add(argv.pop(0))
        else:
            args.append(x)
    if len(args) != 2:
        print(__doc__)
        return 2
    try:
        a = parts(open(args[0], encoding="utf-8").read())
        b = parts(open(args[1], encoding="utf-8").read())
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    problems = []
    if a["fences"] != b["fences"]:
        missing = [f.splitlines()[0] + " …" for f in a["fences"] if f not in b["fences"]]
        problems.append(f"fenced code changed/missing ({len(a['fences'])} → {len(b['fences'])}): {missing[:3]}")
    if a["frontmatter"] != b["frontmatter"]:
        problems.append("frontmatter changed")
    for key in ("inline", "urls", "paths", "env vars", "numbers", "headings"):
        missing = sorted(set(a[key]) - set(b[key]) - allow)
        if missing:
            problems.append(f"{key} missing: {missing[:8]}{' …' if len(missing) > 8 else ''}")
    if len(b["negations"]) < len(a["negations"]) and "negations" not in allow:
        problems.append(f"negations dropped: {len(a['negations'])} → {len(b['negations'])} (check meaning)")
    saved = a["words"] - b["words"]
    pct = (saved / a["words"] * 100) if a["words"] else 0
    print(f"words: {a['words']} → {b['words']} ({-pct:+.0f}%)")
    for p in problems:
        print("LOSS:", p)
    if allow:
        print("allowed removals:", ", ".join(sorted(allow)))
    print("ok: nothing lost" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
