#!/usr/bin/env python3
"""Extract design values from stylesheets and components and cluster them.

Usage: extract-tokens.py PATH [PATH ...] [--threshold 3.0] [--json]
Scans .css .scss .less .tsx .jsx .vue .svelte .html. Collects colors (hex,
rgb/rgba, hsl), font families, font sizes, spacing (margin/padding/gap),
radii, and box-shadows. Colors are clustered by perceptual distance
(CIE76 delta-E in Lab); members of a cluster are candidates to merge into one
token. Values in node_modules, dist, build, and .git are skipped.
"""
import argparse
import colorsys
import collections
import json
import os
import re
import sys

EXTS = {".css", ".scss", ".less", ".tsx", ".jsx", ".vue", ".svelte", ".html"}
SKIP = {"node_modules", "dist", "build", ".git", ".next", "coverage", "vendor"}
HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
RGB = re.compile(r"rgba?\(\s*(\d{1,3})[\s,]+(\d{1,3})[\s,]+(\d{1,3})")
HSL = re.compile(r"hsla?\(\s*([\d.]+)(?:deg)?[\s,]+([\d.]+)%[\s,]+([\d.]+)%")
PROPS = {
    "font_family": re.compile(r"font-family\s*:\s*([^;}{\n]+)"),
    "font_size": re.compile(r"font-size\s*:\s*([\d.]+(?:px|rem|em))"),
    "spacing": re.compile(r"(?:margin|padding|gap|row-gap|column-gap)(?:-(?:top|right|bottom|left|inline|block))?\s*:\s*([^;}{\n]+)"),
    "radius": re.compile(r"border-radius\s*:\s*([^;}{\n]+)"),
    "shadow": re.compile(r"box-shadow\s*:\s*([^;}{\n]+)"),
}


def walk(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if d not in SKIP]
            for f in files:
                if os.path.splitext(f)[1] in EXTS:
                    yield os.path.join(root, f)


def norm_hex(h):
    h = h.lower()
    return "#" + "".join(c * 2 for c in h) if len(h) == 3 else "#" + h


def to_lab(hexv):
    r, g, b = (int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5))
    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = lin(r), lin(g), lin(b)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a, b):
    return sum((p - q) ** 2 for p, q in zip(a, b)) ** 0.5


def cluster(colors, threshold):
    """Greedy clustering: most frequent color seeds a cluster."""
    labs = {c: to_lab(c) for c in colors}
    remaining = [c for c, _ in colors.most_common()]
    clusters = []
    while remaining:
        seed = remaining.pop(0)
        members = [seed] + [c for c in remaining if delta_e(labs[seed], labs[c]) <= threshold]
        remaining = [c for c in remaining if c not in members]
        clusters.append({"token_candidate": seed, "members": members,
                         "uses": sum(colors[m] for m in members),
                         "lightness": round(labs[seed][0], 1)})
    return clusters


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--threshold", type=float, default=3.0, help="delta-E merge distance (2-5 typical)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    colors = collections.Counter()
    props = {k: collections.Counter() for k in PROPS}
    n = 0
    for path in walk(a.paths):
        text = open(path, encoding="utf-8", errors="ignore").read()
        n += 1
        for m in HEX.finditer(text):
            colors[norm_hex(m.group(1))] += 1
        for m in RGB.finditer(text):
            r, g, b = (min(255, int(v)) for v in m.groups())
            colors[f"#{r:02x}{g:02x}{b:02x}"] += 1
        for m in HSL.finditer(text):
            h, s, l = float(m.group(1)) / 360, float(m.group(2)) / 100, float(m.group(3)) / 100
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            colors[f"#{round(r * 255):02x}{round(g * 255):02x}{round(b * 255):02x}"] += 1
        for k, rx in PROPS.items():
            for m in rx.finditer(text):
                v = re.sub(r"\s*!important\s*$", "", m.group(1).strip())
                if k == "spacing":
                    for part in v.split():
                        if re.match(r"^-?[\d.]+(px|rem|em)$", part):
                            props[k][part] += 1
                else:
                    props[k][v] += 1

    clusters = cluster(colors, a.threshold) if colors else []
    grays = [c for c in clusters if abs(to_lab(c["token_candidate"])[1]) < 6 and abs(to_lab(c["token_candidate"])[2]) < 6]
    result = {
        "files": n,
        "distinct_colors": len(colors),
        "color_clusters": clusters,
        "neutral_clusters": len(grays),
        **{k: v.most_common() for k, v in props.items()},
    }
    if a.json:
        json.dump(result, sys.stdout, indent=2)
        print()
        return
    print(f"files: {n}   distinct colors: {len(colors)}   clusters (dE<={a.threshold}): {len(clusters)}   neutral clusters: {len(grays)}")
    print("\ncolor clusters (candidate token ← merge members), by use:")
    for c in sorted(clusters, key=lambda c: -c["uses"]):
        extra = f" ← {', '.join(c['members'][1:])}" if len(c["members"]) > 1 else ""
        print(f"  {c['token_candidate']}  L={c['lightness']:<5} uses={c['uses']:<4}{extra}")
    for k, v in props.items():
        if v:
            print(f"\n{k} ({len(v)} distinct):")
            print("  " + "; ".join(f"{val} ×{cnt}" for val, cnt in v.most_common(15)))


if __name__ == "__main__":
    main()
