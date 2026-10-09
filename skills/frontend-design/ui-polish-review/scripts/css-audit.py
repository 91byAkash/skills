#!/usr/bin/env python3
"""Static polish scan for style drift and common UI smells.

Usage: css-audit.py [PATH ...] [--json] [--top N]
Scans .css .scss .sass .less .tsx .jsx .ts .js .vue .svelte .html files.
Reports distinct color / font-size / radius / spacing / z-index values and
smells such as `transition: all`, outlines removed without a focus-visible
replacement, `!important`, tiny font sizes, and `will-change` overuse.
Exit 1 when outlines are removed with no :focus-visible style anywhere (HIGH),
2 on a missing path, else 0. An aid for review, not a gate on its own.
"""
import argparse
import collections
import json
import os
import re
import sys

EXTS = {".css", ".scss", ".sass", ".less", ".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte", ".html"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "out", "coverage", "vendor"}

COLOR = re.compile(r"#(?:[0-9a-fA-F]{3,4}){1,2}\b|rgba?\([^)]*\)|hsla?\([^)]*\)|oklch\([^)]*\)")
FONT_SIZE = re.compile(r"font-size\s*:\s*([0-9.]+(?:px|rem|em))|\btext-\[([0-9.]+(?:px|rem))\]")
RADIUS = re.compile(r"border-radius\s*:\s*([^;}\n]+)|\brounded-\[([^\]]+)\]")
SPACING = re.compile(r"(?:margin|padding|gap)(?:-[a-z]+)?\s*:\s*([^;}\n]+)")
PX = re.compile(r"(?<![\w.-])([0-9.]+px)\b")
ZINDEX = re.compile(r"z-index\s*:\s*(-?\d+)|\bz-\[(\d+)\]")
SMELLS = {
    "transition: all": re.compile(r"transition(?:-property)?\s*:\s*all\b|\btransition-all\b"),
    "!important": re.compile(r"!important"),
    "outline removed": re.compile(r"outline\s*:\s*(?:none|0)\b|\boutline-none\b"),
    "will-change": re.compile(r"will-change\s*:"),
    "animates layout prop": re.compile(r"transition[^;]*\b(?:width|height|top|left|right|bottom|margin)\b"),
    "custom cursor": re.compile(r"cursor\s*:\s*url\("),
}
FOCUS_VISIBLE = re.compile(r":focus-visible|focus-visible:")


def files(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for root, dirs, names in os.walk(p):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for n in names:
                if os.path.splitext(n)[1] in EXTS:
                    yield os.path.join(root, n)


def to_px(v):
    m = re.match(r"([0-9.]+)(px|rem|em)", v)
    if not m:
        return None
    n = float(m.group(1))
    return n if m.group(2) == "px" else n * 16


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", default=["."])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--top", type=int, default=12)
    a = ap.parse_args()
    missing = [p for p in a.paths if not os.path.exists(p)]
    if missing:
        print(f"no such path: {', '.join(missing)}", file=sys.stderr)
        return 2

    vals = {k: collections.Counter() for k in ("colors", "font_sizes", "radii", "spacing_px", "z_index")}
    smells = collections.defaultdict(list)
    has_focus_visible = False
    scanned = 0
    for f in files(a.paths):
        try:
            text = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        scanned += 1
        if FOCUS_VISIBLE.search(text):
            has_focus_visible = True
        for i, line in enumerate(text.splitlines(), 1):
            for m in COLOR.finditer(line):
                vals["colors"][m.group(0).lower().replace(" ", "")] += 1
            for m in FONT_SIZE.finditer(line):
                v = m.group(1) or m.group(2)
                vals["font_sizes"][v] += 1
                px = to_px(v)
                if px is not None and px < 12:
                    smells["font-size under 12px"].append(f"{f}:{i}")
            for m in RADIUS.finditer(line):
                vals["radii"][(m.group(1) or m.group(2)).strip()] += 1
            for m in SPACING.finditer(line):
                # every px value in shorthands such as `padding: 10px 14px`
                off = False
                for v in PX.findall(m.group(1)):
                    vals["spacing_px"][v] += 1
                    px = to_px(v)
                    off = off or (px is not None and px % 4 != 0 and px > 2)
                if off:
                    smells["spacing off 4px grid"].append(f"{f}:{i}")
            for m in ZINDEX.finditer(line):
                vals["z_index"][m.group(1) or m.group(2)] += 1
            for name, rx in SMELLS.items():
                if rx.search(line):
                    smells[name].append(f"{f}:{i}")

    report = {
        "files_scanned": scanned,
        "distinct": {k: len(v) for k, v in vals.items()},
        "top": {k: v.most_common(a.top) for k, v in vals.items()},
        "smells": {k: {"count": len(v), "examples": v[:8]} for k, v in smells.items()},
        "outline_removed_without_focus_visible": bool(smells.get("outline removed")) and not has_focus_visible,
    }
    if a.json:
        json.dump(report, sys.stdout, indent=2)
        print()
        return 1 if report["outline_removed_without_focus_visible"] else 0
    print(f"files scanned: {scanned}")
    hints = {"colors": 20, "font_sizes": 10, "radii": 5, "spacing_px": 12, "z_index": 6}
    print("\ndistinct values (high counts suggest token drift):")
    for k, n in report["distinct"].items():
        flag = "  <- check" if n > hints[k] else ""
        print(f"  {k:<11} {n:>4}{flag}")
        if vals[k]:
            print("    " + ", ".join(f"{v} ×{c}" for v, c in vals[k].most_common(a.top)))
    print("\nsmells:")
    if not smells:
        print("  none found")
    for k, v in sorted(smells.items(), key=lambda kv: -len(kv[1])):
        print(f"  {k:<24} {len(v):>4}   e.g. {', '.join(v[:3])}")
    if report["outline_removed_without_focus_visible"]:
        print("\nHIGH: outlines are removed and no :focus-visible style exists anywhere")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
