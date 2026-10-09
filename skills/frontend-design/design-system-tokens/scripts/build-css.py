#!/usr/bin/env python3
"""Generate tokens.css from a tokens.json (the layout used by templates/tokens.json).

Usage: build-css.py tokens.json [-o tokens.css] [--default-theme light] [--system-dark dark]

Layout expected:
  top-level groups      primitives  -> :root { --gray-50: #...; --space-4: 16px; }
  "themes": {name: {...}}  semantic  -> :root,[data-theme="light"] / [data-theme="dark"]
  "component": {...}       component -> :root { --button-primary-bg: var(--color-accent); }
  "contrast_pairs"         ignored (used by contrast-check.py)
$value may be DTCG 2025.10 objects (color, dimension, duration) or
legacy strings. References "{gray.900}" become var(--gray-900). The theme named by
--system-dark (default "dark", if present) is also applied under
prefers-color-scheme: dark when no data-theme attribute is set.
"""
import argparse
import json
import re
import sys

RESERVED = {"themes", "component", "contrast_pairs", "$schema", "$description"}
REF = re.compile(r"\{([^}]+)\}")


def flatten(node, prefix=()):
    """Yield (path_tuple, value) for every token (a dict with $value)."""
    if isinstance(node, dict) and "$value" in node:
        yield prefix, node["$value"]
        return
    if isinstance(node, dict):
        for k, v in node.items():
            if not k.startswith("$"):
                yield from flatten(v, prefix + (k,))


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


def var(path):
    return "--" + "-".join(path).replace(".", "-")


def css_value(v):
    v = to_css(v)
    if isinstance(v, (int, float)):
        return str(v)
    return REF.sub(lambda m: f"var(--{m.group(1).replace('.', '-')})", str(v))


def block(selector, pairs, indent="  ", extra=None):
    lines = [f"{selector} {{"]
    if extra:
        lines.append(f"{indent}{extra}")
    lines += [f"{indent}{var(p)}: {css_value(v)};" for p, v in pairs]
    lines.append("}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tokens")
    ap.add_argument("-o", "--out")
    ap.add_argument("--default-theme", default=None, help="theme applied on :root (default: first theme)")
    ap.add_argument("--system-dark", default="dark", help="theme used for prefers-color-scheme: dark")
    a = ap.parse_args()
    try:
        with open(a.tokens) as f:
            t = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"cannot read {a.tokens}: {e}", file=sys.stderr)
        return 2

    prim = [(p, v) for k, node in t.items() if k not in RESERVED for p, v in flatten(node, (k,))]
    themes = t.get("themes", {})
    default = a.default_theme or next(iter(themes), None)
    out = [f"/* GENERATED from {a.tokens.split('/')[-1]} by build-css.py. Do not edit by hand. */", ""]
    out += ["/* primitives */", block(":root", prim), ""]
    for name, tree in themes.items():
        pairs = list(flatten(tree))
        scheme = "dark" if "dark" in name else "light"
        sel = f':root, [data-theme="{name}"]' if name == default else f'[data-theme="{name}"]'
        out += [f"/* semantic: {name}{' (default)' if name == default else ''} */",
                block(sel, pairs, extra=f"color-scheme: {scheme};"), ""]
    if a.system_dark in themes and a.system_dark != default:
        pairs = list(flatten(themes[a.system_dark]))
        inner = block(":root:not([data-theme])", pairs, indent="    ", extra="color-scheme: dark;")
        inner = "\n".join("  " + l for l in inner.splitlines())
        out += [f"/* semantic: {a.system_dark} (system default when no explicit choice) */",
                "@media (prefers-color-scheme: dark) {", inner, "}", ""]
    comp = list(flatten(t.get("component", {})))
    if comp:
        out += ["/* component tokens (only where a component diverges) */", block(":root", comp), ""]

    # unresolved references are a build error, not a silent broken var()
    known = {p for p, _ in prim} | {p for tree in themes.values() for p, _ in flatten(tree)}
    bad = []
    for p, v in prim + comp + [pv for tree in themes.values() for pv in flatten(tree)]:
        for ref in (REF.findall(v) if isinstance(v, str) else []):
            if tuple(ref.split(".")) not in known:
                bad.append(f"{'.'.join(p)} -> {{{ref}}}")
    if bad:
        print("unresolved references:\n  " + "\n  ".join(bad), file=sys.stderr)
        return 1

    css = "\n".join(out).rstrip() + "\n"
    if a.out:
        open(a.out, "w").write(css)
        print(f"wrote {a.out}: {len(prim)} primitives, {len(themes)} themes, {len(comp)} component tokens")
    else:
        sys.stdout.write(css)
    return 0


if __name__ == "__main__":
    sys.exit(main())
