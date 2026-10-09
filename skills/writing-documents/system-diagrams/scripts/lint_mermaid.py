#!/usr/bin/env python3
"""Static checks for Mermaid source, fast and without a browser. Catches the
mistakes that make diagrams fail to parse or read badly; run render_mermaid.sh
--check afterwards for the real parser verdict.

Usage:
  lint_mermaid.py diagram.mmd [more.mmd ...]
  lint_mermaid.py design.md            # checks every ```mermaid fence in a Markdown file
  lint_mermaid.py --max-nodes 20 --json diagram.mmd

Output: file:line: LEVEL code message.  Exit 1 if any ERROR.

ERROR  unknown-type      first line is not a known diagram keyword
ERROR  unbalanced        (), [], {} or quotes do not balance on a line
ERROR  subgraph-end      subgraph/end (or alt/loop/opt/par/critical ... end) do not pair up
ERROR  inline-comment    a %% comment after code on the same line
ERROR  reserved-end      a node id written as lowercase `end` (breaks flowcharts)
ERROR  class-undefined   `class X name` / `:::name` uses a classDef that does not exist
WARN   classdef-color    classDef sets fill but no `color:` (text contrast left to chance)
WARN   unquoted-special  label contains ( ) [ ] { } # ; : without quotes
WARN   too-many-nodes    more nodes than --max-nodes (split the diagram)
WARN   unlabeled-edges   over half of the edges have no label (say what flows)
WARN   long-label        a node label line over 40 characters (break with <br/> or shorten)
WARN   undeclared-participant  sequence message uses a participant never declared
WARN   no-direction      flowchart without TD/TB/LR/RL/BT
"""
import argparse, json, re, sys
from pathlib import Path

# Diagram keywords as Mermaid 11.x / 12.x detects them (checked against mermaid 12.1.0, 2026-10).
# Several "-beta" types lost the suffix in 11.x but still accept it; older hosts (GitHub, GitLab,
# Confluence apps) may only know the -beta spelling or not know the type at all.
TYPES = ["flowchart", "graph", "flowchart-elk", "sequenceDiagram", "classDiagram", "classDiagram-v2", "stateDiagram",
         "stateDiagram-v2", "erDiagram", "journey", "gantt", "pie", "quadrantChart", "requirementDiagram",
         "requirement", "gitGraph", "C4Context", "C4Container", "C4Component", "C4Dynamic", "C4Deployment",
         "mindmap", "timeline", "sankey", "sankey-beta", "xychart", "xychart-beta", "block", "block-beta",
         "architecture", "architecture-beta", "packet", "packet-beta", "kanban", "radar-beta", "treemap",
         "treemap-beta", "venn-beta", "ishikawa", "ishikawa-beta", "wardley-beta", "treeView-beta", "zenuml"]
OPENERS_SEQ = ("alt", "loop", "opt", "par", "critical", "break", "rect", "box")
NODE_RE = re.compile(r'([A-Za-z_][\w-]*)\s*(\[\[|\[\(|\(\(|\[/|\[\\|\(\[|\[|\(|\{\{|\{|>)("[^"]*"|.*?)(\]\]|\)\]|\)\)|/\]|\\\]|\]\)|\]|\)|\}\}|\})')
EDGE_RE = re.compile(r"(-->|---|-\.->|-\.-|==>|===|--[ox]|<-->|~~~|--\s[^-]+?\s-->|==\s[^=]+?\s==>)")


def blocks_from(path):
    text = Path(path).read_text(encoding="utf-8")
    if path.endswith((".md", ".markdown")):
        out, cur, start = [], None, 0
        for i, line in enumerate(text.splitlines(), 1):
            if cur is None and re.match(r"^\s*```+\s*mermaid\s*$", line):
                cur, start = [], i + 1
            elif cur is not None and re.match(r"^\s*```+\s*$", line):
                out.append((start, "\n".join(cur)))
                cur = None
            elif cur is not None:
                cur.append(line)
        return out
    return [(1, text)]


def strip_quoted(s):
    return re.sub(r'"[^"]*"', '""', s)


def lint(src, base, max_nodes):
    issues = []
    add = lambda ln, lvl, code, msg: issues.append((base + ln - 1, lvl, code, msg))
    lines = src.splitlines()
    body = [(i, l) for i, l in enumerate(lines, 1) if l.strip() and not l.strip().startswith("%%")]
    # skip front matter / init directives
    while body and (body[0][1].strip() == "---" or body[0][1].strip().startswith("%%{")):
        if body[0][1].strip() == "---":
            body = body[1:]
            while body and body[0][1].strip() != "---":
                body = body[1:]
        body = body[1:]
    if not body:
        add(1, "ERROR", "empty", "no diagram content")
        return issues
    first_ln, first = body[0]
    kw = first.strip().split()[0].rstrip(":;")
    if kw not in TYPES:
        add(first_ln, "ERROR", "unknown-type", f"first keyword {kw!r} is not a Mermaid diagram type")
        return issues
    is_flow = kw in ("flowchart", "graph")
    is_seq = kw == "sequenceDiagram"
    if is_flow and len(first.split()) < 2:
        add(first_ln, "WARN", "no-direction", "add a direction, e.g. `flowchart LR`")
    depth, stack = 0, []
    classdefs, used_classes = set(), []
    nodes, edges, labeled = set(), 0, 0
    participants, msgs = set(), []
    for ln, raw in body[1:]:
        line = raw.strip()
        q = strip_quoted(line)
        if "%%" in q:
            add(ln, "ERROR", "inline-comment", "`%%` comment after code; Mermaid only allows comments on their own line")
            q = q.split("%%")[0]
            line = line.split("%%")[0].strip()
            if not line:
                continue
        if line.count('"') % 2:
            add(ln, "ERROR", "unbalanced", "odd number of double quotes")
        pairs = ("()", "[]", "{}") if is_flow else ("()", "[]")  # ER/class/state braces span lines
        qb = re.sub(r"\b[A-Za-z_]\w*>[^\]]*\]", "x", q) if is_flow else q  # asymmetric node a>label] has no opening [
        if is_seq:
            qb = re.sub(r"--?\)", "->", qb)  # async arrows -) and --)
        for o, c in pairs:
            if qb.count(o) != qb.count(c):
                add(ln, "ERROR", "unbalanced", f"{o} and {c} do not balance")
                break
        word = line.split()[0]
        if kw.startswith("state") and re.match(r"^note\s+(left|right)\s+of\s+\S+\s*$", line):
            stack.append(ln)  # multi-line note, closed by `end note`
        elif is_flow or kw.startswith("state"):
            if word == "subgraph" or (kw.startswith("state") and re.match(r"^state\s+.*\{\s*$", line)):
                stack.append(ln)
            elif word == "end" or (kw.startswith("state") and line == "}"):
                if not stack:
                    add(ln, "ERROR", "subgraph-end", "`end` without an open subgraph")
                else:
                    stack.pop()
        if is_seq:
            if word in OPENERS_SEQ:
                stack.append(ln)
            elif word == "end":
                if not stack:
                    add(ln, "ERROR", "subgraph-end", "`end` without an open alt/loop/opt/par block")
                else:
                    stack.pop()
            m = re.match(r"^(?:create\s+)?(participant|actor)\s+(\S+)", line)
            if m:
                participants.add(m.group(2))
            m = re.match(r"^([^\s:>-]+)\s*(-->>|->>|-->|->|--x|-x|--\)|-\))[+-]?\s*([^\s:]+)\s*:", line)
            if m:
                msgs.append((ln, m.group(1), m.group(3)))
        if word == "classDef":
            parts = line.split(None, 2)
            if len(parts) >= 2:
                for name in parts[1].split(","):
                    classdefs.add(name)
                style = parts[2] if len(parts) > 2 else ""
                if "fill" in style and "color:" not in style.replace(" ", ""):
                    add(ln, "WARN", "classdef-color", f"classDef {parts[1]} sets fill without color:")
            continue
        if word == "class" and is_flow:
            parts = line.split()
            if len(parts) >= 3:
                used_classes.append((ln, parts[-1].rstrip(";")))
            continue
        for m in re.finditer(r":::([\w-]+)", line):
            used_classes.append((ln, m.group(1)))
        if is_flow:
            if re.search(r"(^|[\s;&>-])end([\[\(\{]|\s*-->|\s*---)", line) or re.search(r"(-->|---|==>|-\.->|\|)\s*end\s*;?\s*$", q):
                add(ln, "ERROR", "reserved-end", "`end` as a node id breaks the parser; use End or done")
            for m in NODE_RE.finditer(line):
                nodes.add(m.group(1))
                label = m.group(3).strip()
                if not (label.startswith('"') and label.endswith('"')):
                    if re.search(r"[()\[\]{};#]", label):
                        add(ln, "WARN", "unquoted-special", f"label {label[:30]!r} has special characters; wrap it in quotes")
                if max(len(part) for part in re.split(r"<br\s*/?>", label.strip('"'))) > 40:
                    add(ln, "WARN", "long-label", f"label {label[:30]!r}... is long; shorten or break with <br/>")
            n_edges = len(EDGE_RE.findall(q))
            if n_edges:
                edges += n_edges
                labeled += len(re.findall(r"\|[^|]+\|", line)) + len(re.findall(r"--\s[^->|]+?\s-->", line))
                for ident in re.findall(r"(?:^|-->|---|==>|-\.->|\|)\s*([A-Za-z_][\w-]*)", q):
                    nodes.add(ident)
    if not is_flow:
        whole = strip_quoted("\n".join(l for _, l in body))
        whole = re.sub(r"[|}o{]{1,2}(--|\.\.)[|}o{]{1,2}", " ", whole)  # ER cardinality markers use braces
        if whole.count("{") != whole.count("}"):
            add(first_ln, "ERROR", "unbalanced", "{ and } do not balance across the diagram")
    for ln in stack:
        add(ln, "ERROR", "subgraph-end", "block opened here is never closed with `end`")
    for ln, c in used_classes:
        if c not in classdefs:
            add(ln, "ERROR", "class-undefined", f"class {c!r} has no classDef")
    if is_flow and len(nodes) > max_nodes:
        add(first_ln, "WARN", "too-many-nodes", f"{len(nodes)} nodes (> {max_nodes}); split by level or concern")
    if is_flow and edges >= 4 and labeled * 2 < edges:
        add(first_ln, "WARN", "unlabeled-edges", f"{edges - labeled} of {edges} edges unlabeled; label what flows or happens")
    if is_seq and participants:
        for ln, a, b in msgs:
            for p in (a, b):
                if p not in participants:
                    add(ln, "WARN", "undeclared-participant", f"{p!r} not declared; declare participants to fix their order")
    return issues


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--max-nodes", type=int, default=20)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    allissues = []
    for f in a.files:
        blocks = blocks_from(f)
        if not blocks:
            print(f"{f}: no mermaid blocks", file=sys.stderr)
        for start, src in blocks:
            for ln, lvl, code, msg in lint(src, start, a.max_nodes):
                allissues.append({"file": f, "line": ln, "level": lvl, "code": code, "message": msg})
    if a.json:
        print(json.dumps(allissues, indent=2))
    else:
        for i in allissues:
            print(f"{i['file']}:{i['line']}: {i['level']} {i['code']} {i['message']}")
        print(f"{sum(i['level'] == 'ERROR' for i in allissues)} error(s), {sum(i['level'] == 'WARN' for i in allissues)} warning(s)")
    sys.exit(1 if any(i["level"] == "ERROR" for i in allissues) else 0)


if __name__ == "__main__":
    main()
