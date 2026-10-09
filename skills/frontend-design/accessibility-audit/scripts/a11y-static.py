#!/usr/bin/env python3
"""Static accessibility scan for markup in HTML, JSX/TSX, Vue, and Svelte files.

Usage: a11y-static.py PATH [PATH ...] [--json]
Heuristic: finds common source-level failures. Components that add the
missing attribute internally will show up as false positives; confirm in the
rendered page. Exit 1 if any error-level finding exists.
"""
import json
import os
import re
import sys

EXTS = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte"}
SKIP = {"node_modules", ".git", "dist", "build", ".next", "coverage"}

# Attribute text may contain JSX expressions with ">" (arrow functions) and
# nested braces, so quoted strings and {...} groups are consumed as units.
TAG = re.compile(r"""<([a-zA-Z][\w.-]*)((?:\s(?:[^<>{}"']|"[^"]*"|'[^']*'|\{(?:[^{}]|\{[^{}]*\})*\})*?)?)(/?)>""", re.S)
ATTR = re.compile(r"""([:@\w-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|\{((?:[^{}]|\{[^{}]*\})*)\}|([^\s>]+)))?""")


def attrs(raw):
    """Map lower-cased attribute name -> value. JSX {expr} values are returned
    without braces and string literals unquoted ({true} -> "true", {'x'} -> "x");
    a bare attribute maps to ""."""
    out = {}
    for m in ATTR.finditer(raw or ""):
        val = next((g for g in m.group(2, 3, 4, 5) if g is not None), "")
        if m.group(4) is not None:
            val = val.strip().strip("\"'`")
        out[m.group(1).lower()] = val
    return out


def has(a, *names):
    return any(n in a for n in names)


def scan(path, text):
    out = []
    line_of = lambda pos: text.count("\n", 0, pos) + 1
    headings = []
    label_for = set(re.findall(r'(?:for|htmlFor)\s*=\s*["{\']?([\w-]+)', text))
    for m in TAG.finditer(text):
        name, a = m.group(1), attrs(m.group(2))
        tag = name.lower()
        ln = line_of(m.start())
        def add(level, rule, msg):
            out.append({"file": path, "line": ln, "level": level, "rule": rule, "message": msg})
        end = text.find(f"</{name}>", m.end())
        inner = text[m.end():end] if 0 <= end - m.end() < 2000 else ""
        inner_text = re.sub(r"<[^>]+>|\{[^}]*\}", "", inner).strip()
        if tag == "img" and not has(a, "alt"):
            add("error", "img-alt", "img without alt (use alt=\"\" if decorative)")
        if tag == "button" and m.group(3) != "/" and not inner_text and not has(a, "aria-label", "aria-labelledby", "title"):
            if not re.search(r"\{[^}]+\}", inner) or "<svg" in inner or "Icon" in inner:
                add("error", "button-name", "button with no text or aria-label")
        if tag == "a":
            if not has(a, "href"):
                add("warn", "anchor-href", "<a> without href is not keyboard focusable; use <button> for actions")
            elif a.get("href") in ("#", "javascript:void(0)"):
                add("warn", "anchor-href", "link to '#'; use a button for actions")
            if m.group(3) != "/" and not inner_text and not has(a, "aria-label", "aria-labelledby") and "<img" not in inner:
                if not re.search(r"\{[^}]+\}", inner):
                    add("error", "link-name", "link with no text")
        if tag in ("input", "select", "textarea"):
            t = (a.get("type") or "").lower()
            if t not in ("hidden", "submit", "button", "reset", "image"):
                ident = a.get("id")
                if not has(a, "aria-label", "aria-labelledby") and not (ident and ident in label_for):
                    before = text[max(0, m.start() - 300):m.start()]
                    if before.rfind("<label") <= before.rfind("</label>"):
                        add("error", "control-label", f"<{tag}> without associated label")
            if t in ("email", "tel") and not has(a, "autocomplete", "autoComplete".lower()):
                add("warn", "autocomplete", f"type={t} input without autocomplete")
        if tag in ("div", "span", "li", "td") and has(a, "onclick", "@click", "on:click", "v-on:click"):
            if not has(a, "role"):
                add("error", "click-events-have-roles", f"clickable <{tag}> without role; use <button>")
            if not has(a, "onkeydown", "onkeyup", "onkeypress", "@keydown", "on:keydown"):
                add("warn", "click-events-have-key-events", f"clickable <{tag}> without keyboard handler")
            if not has(a, "tabindex"):
                add("warn", "focusable", f"clickable <{tag}> not focusable (no tabindex)")
        ti = a.get("tabindex")
        if ti and re.fullmatch(r"[1-9]\d*", ti.strip()):
            add("error", "tabindex-positive", "positive tabindex breaks focus order")
        if a.get("aria-hidden") == "true" and (tag in ("button", "a", "input", "select", "textarea") or has(a, "tabindex")):
            add("error", "aria-hidden-focus", "aria-hidden on a focusable element")
        if tag in ("video", "audio") and has(a, "autoplay") and not has(a, "muted"):
            add("warn", "autoplay", "autoplaying media with sound")
        if tag == "html" and not has(a, "lang"):
            add("error", "html-lang", "<html> without lang")
        if re.fullmatch(r"h[1-6]", tag):
            headings.append((int(tag[1]), ln))
        if has(a, "role") and a.get("role") in ("button", "link", "checkbox", "tab", "menuitem", "switch") and tag in ("div", "span") and not has(a, "tabindex"):
            add("error", "role-focusable", f"role={a.get('role')} on <{tag}> without tabindex")
        if tag == "meta" and a.get("name") == "viewport" and re.search(r"user-scalable\s*=\s*no|maximum-scale\s*=\s*1(\.0)?\b", a.get("content") or ""):
            add("error", "zoom-disabled", "viewport disables zoom")
    prev = 0
    for level, ln in headings:
        if prev and level > prev + 1:
            out.append({"file": path, "line": ln, "level": "warn", "rule": "heading-order",
                        "message": f"heading jumps from h{prev} to h{level}"})
        prev = level
    return out


def main():
    args = [x for x in sys.argv[1:] if x != "--json"]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if args else 2
    missing = [p for p in args if not os.path.exists(p)]
    if missing:
        print(f"no such path: {', '.join(missing)}", file=sys.stderr)
        return 2
    findings = []
    for p in args:
        paths = [p] if os.path.isfile(p) else [os.path.join(r, f) for r, ds, fs in os.walk(p)
                                                 if not ds.__setitem__(slice(None), [d for d in ds if d not in SKIP])
                                                 for f in fs if os.path.splitext(f)[1] in EXTS]
        for f in paths:
            findings += scan(f, open(f, encoding="utf-8", errors="ignore").read())
    findings.sort(key=lambda f: (f["file"], f["line"]))
    if "--json" in sys.argv:
        json.dump(findings, sys.stdout, indent=2)
        print()
    else:
        for f in findings:
            print(f"{f['level']:<5} {f['file']}:{f['line']}  [{f['rule']}] {f['message']}")
        errs = sum(f["level"] == "error" for f in findings)
        print(f"\n{errs} error(s), {len(findings) - errs} warning(s). Confirm in the rendered page; components may add attributes.")
    return 1 if any(f["level"] == "error" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
