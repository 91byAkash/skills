#!/usr/bin/env python3
"""Check contrast pairs declared in a tokens.json for every theme.

Usage: contrast-check.py tokens.json [--theme NAME]
       contrast-check.py --pair FG BG [--min 4.5]   (ad hoc, e.g. a palette draft)
Expects primitives at the top level, semantic roles under themes.<name>,
and a "contrast_pairs" list of {"fg": "color.x", "bg": "color.y", "min": 4.5}.
References use {path.to.token}. Exit 1 if any pair fails.
"""
import json
import re
import sys

REF = re.compile(r"^\{([^}]+)\}$")


def lookup(tree, path):
    node = tree
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def resolve(tokens, theme, path, depth=0):
    if depth > 20:
        raise ValueError(f"reference loop at {path}")
    node = lookup(tokens.get("themes", {}).get(theme, {}), path)
    if node is None:
        node = lookup(tokens, path)
    if node is None:
        raise KeyError(path)
    value = node["$value"] if isinstance(node, dict) and "$value" in node else node
    m = REF.match(str(value)) if isinstance(value, str) else None
    return resolve(tokens, theme, m.group(1), depth + 1) if m else to_css(value)


def to_css(v):
    """Turn a DTCG 2025.10 $value into a CSS string. Accepts the legacy string
    shorthand ("#fff", "16px") too. Color objects use hex when present, else
    srgb components (other color spaces need a build tool)."""
    if isinstance(v, dict):
        if "hex" in v:
            return v["hex"]
        if "components" in v:
            space = v.get("colorSpace", "srgb")
            if space != "srgb":
                raise ValueError(f"colorSpace {space!r} without hex: add a hex fallback")
            r, g, b = (round(c * 255) for c in v["components"][:3])
            a = v.get("alpha", 1)
            return f"#{r:02x}{g:02x}{b:02x}" + (f"{round(a * 255):02x}" if a != 1 else "")
        if "value" in v and "unit" in v:
            return f"{v['value']}{v['unit']}"
        raise ValueError(f"unsupported $value object: {v}")
    if isinstance(v, list):  # fontFamily array, cubicBezier
        if all(isinstance(x, (int, float)) for x in v):
            return "cubic-bezier(" + ", ".join(str(x) for x in v) + ")"
        return ", ".join(f'"{x}"' if " " in x else x for x in v)
    return v


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h[:3])
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def luminance(rgb):
    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = sorted((luminance(hex_to_rgb(a)), luminance(hex_to_rgb(b))), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    if args[0] == "--pair":
        if len(args) < 3:
            print("usage: contrast-check.py --pair FG BG [--min 4.5]", file=sys.stderr)
            return 2
        fg, bg = args[1], args[2]
        need = float(args[args.index("--min") + 1]) if "--min" in args else 4.5
        r = ratio(fg, bg)
        verdict = "ok" if r >= need else "FAIL"
        print(f"{verdict}  {r:.2f}:1 (min {need})  {fg} on {bg}"
              f"  [AA body 4.5: {'pass' if r >= 4.5 else 'fail'} | large/UI 3.0: {'pass' if r >= 3 else 'fail'}]")
        return 0 if r >= need else 1
    tokens = json.load(open(args[0]))
    themes = list(tokens.get("themes", {}))
    if "--theme" in args:
        themes = [args[args.index("--theme") + 1]]
    failures = 0
    for theme in themes:
        print(f"[{theme}]")
        for p in tokens.get("contrast_pairs", []):
            try:
                fg, bg = resolve(tokens, theme, p["fg"]), resolve(tokens, theme, p["bg"])
            except KeyError as e:
                print(f"  MISSING  {p['fg']} on {p['bg']}: no token {e}")
                failures += 1
                continue
            r = ratio(fg, bg)
            ok = r >= p.get("min", 4.5)
            failures += not ok
            print(f"  {'ok  ' if ok else 'FAIL'}  {r:5.2f}:1 (min {p.get('min', 4.5)})  "
                  f"{p['fg']} {fg} on {p['bg']} {bg}")
    print(f"failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
