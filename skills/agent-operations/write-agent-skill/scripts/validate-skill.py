#!/usr/bin/env python3
"""Validate one or more skill folders.

Usage: validate-skill.py SKILL_DIR [SKILL_DIR ...] [--max-lines N] [--sections "## Inputs,## Output,## Done when"]
Checks: SKILL.md exists; frontmatter has name (== folder name, kebab-case) and
description (<= 1024 chars is an error; warns outside 200-420 chars, because
agents list descriptions in a small shared budget and truncate long ones; must
contain "Use when"; warns without a "Not for" cue);
required sections present; body length; relative links resolve (ignoring code).
Exit 1 if any error.
"""
import argparse
import os
import re
import sys


def parse_front(front):
    """Top-level `key: value` pairs, including YAML block scalars (`key: >-` / `key: |`)."""
    fields, lines, i = {}, front.splitlines(), 0
    while i < len(lines):
        m = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", lines[i])
        i += 1
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if re.fullmatch(r"[>|][+-]?", val):
            block = []
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            val = (" " if val[0] == ">" else "\n").join(b for b in block if b)
        fields[key] = val
    return fields


def check(skill_dir, max_lines, sections):
    errors, warns = [], []
    path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(path):
        return [f"{skill_dir}: no SKILL.md"], []
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return [f"{path}: missing frontmatter block"], []
    front, body = m.group(1), m.group(2)
    fields = parse_front(front)
    folder = os.path.basename(os.path.realpath(skill_dir))
    name = fields.get("name", "").strip().strip("\"'")
    if not name:
        errors.append("frontmatter: name missing")
    elif name != folder:
        errors.append(f"frontmatter: name '{name}' != folder '{folder}'")
    elif not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        errors.append(f"frontmatter: name '{name}' is not kebab-case")
    elif len(name) > 64:
        errors.append(f"frontmatter: name is {len(name)} chars (max 64)")
    desc = fields.get("description", "").strip()
    if len(desc) >= 2 and desc[0] == desc[-1] and desc[0] in "\"'":
        desc = desc[1:-1].replace('\\"', '"')
    if not desc:
        errors.append("frontmatter: description missing")
    else:
        if len(desc) > 1024:
            errors.append(f"description is {len(desc)} chars (max 1024)")
        elif len(desc) > 420:
            warns.append(f"description is {len(desc)} chars; aim for 200-380 (max 420) so it is not truncated in the skill listing")
        elif len(desc) < 200:
            warns.append(f"description is {len(desc)} chars; under 200 usually means too few triggers")
        if "use when" not in desc[:300].lower() and "use when" in desc.lower():
            warns.append("'Use when' starts after char 300; front-load the job and triggers")
        if "use when" not in desc.lower():
            errors.append("description lacks 'Use when' triggers")
        if not re.search(r"\bnot for\b", desc, re.I):
            warns.append("description has no 'Not for' cue")
        if re.search(r"\b(I|[Ww]e|[Mm]y|[Oo]ur)\b(?!/)", re.sub(r"\"[^\"]*\"", "", desc)):
            warns.append("description should be third person")
    for s in sections:
        if not re.search(rf"^{re.escape(s)}\b", body, re.M):
            errors.append(f"missing section '{s}'")
    lines = body.count("\n") + 1
    if lines > max_lines:
        warns.append(f"body is {lines} lines (limit {max_lines}); disclose reference into sibling files")
    stripped = re.sub(r"```.*?```", "", body, flags=re.S)
    stripped = re.sub(r"`[^`]*`", "", stripped)
    for target in re.findall(r"\]\(([^)\s]+)\)", stripped):
        t = target.split("#")[0]
        if not t or re.match(r"^(https?:|mailto:|/|<)", t):
            continue
        if not os.path.exists(os.path.join(skill_dir, t)):
            errors.append(f"broken link: {t}")
    for root, _, files in os.walk(skill_dir):
        for f in files:
            if f.endswith(".md") and f != "SKILL.md":
                rel = os.path.relpath(os.path.join(root, f), skill_dir)
                if rel not in text and not rel.startswith(("evals", "templates", "examples")):
                    warns.append(f"{rel} is not linked from SKILL.md")
    return [f"{path}: {e}" for e in errors], [f"{path}: {w}" for w in warns]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--max-lines", type=int, default=400)
    ap.add_argument("--sections", default="## Inputs,## Output,## Done when")
    a = ap.parse_args()
    sections = [s.strip() for s in a.sections.split(",") if s.strip()]
    all_err = 0
    for d in a.dirs:
        errs, warns = check(d, a.max_lines, sections)
        for e in errs:
            print("ERROR", e)
        for w in warns:
            print("warn ", w)
        if not errs:
            print("ok   ", d)
        all_err += len(errs)
    return 1 if all_err else 0


if __name__ == "__main__":
    sys.exit(main())
