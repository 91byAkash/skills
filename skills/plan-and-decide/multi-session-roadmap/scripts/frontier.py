#!/usr/bin/env python3
"""frontier.py - compute the frontier of a local Markdown map.

Usage: scripts/frontier.py .maps/<map-slug>        (prints a report)
       scripts/frontier.py .maps/<map-slug> --json

Reads tickets/NNN-*.md, each starting with front matter such as:
    ---
    title: Which token format and lifetime?
    type: interview            # research | prototype | interview | task
    status: open               # open | closed
    assignee:                  # empty = unclaimed
    blocked_by: [002, 004]     # ids = the NNN prefix of other ticket files
    ---
Reports open / claimed / blocked / frontier tickets, and fails (exit 1) on
unknown blocker ids, invalid types, or blocking cycles.
"""
import json, os, re, sys

TYPES = {"research", "prototype", "interview", "task"}


def norm(tid):
    """'002', '2' and 2 name the same ticket; keep the 3-digit file form."""
    return f"{int(tid):03d}" if tid.isdigit() else tid


def parse(path):
    text = open(path, encoding="utf-8-sig").read().replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            line = re.sub(r"\s+#.*$", "", line).rstrip()
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    raw = meta.get("blocked_by", "").strip("[] ")
    meta["blocked_by"] = [norm(b.strip().strip("'\"")) for b in raw.split(",") if b.strip()]
    return meta


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__.strip()); return 2
    tdir = os.path.join(args[0], "tickets")
    if not os.path.isdir(tdir):
        print(f"no tickets/ folder under {args[0]}", file=sys.stderr); return 2
    tickets, problems = {}, []
    for fn in sorted(os.listdir(tdir)):
        m = re.match(r"^(\d+)-.*\.md$", fn)
        if not m:
            continue
        meta = parse(os.path.join(tdir, fn))
        meta["file"] = fn
        if not meta.get("title"):
            meta["title"] = fn[len(m.group(1)) + 1:-3].replace("-", " ")
        meta["title"] = meta["title"].strip("'\"")
        tid = norm(m.group(1))
        if tid in tickets:
            problems.append(f"{fn}: duplicate id {tid} (also {tickets[tid]['file']})")
        tickets[tid] = meta
        if meta.get("type") not in TYPES:
            problems.append(f"{fn}: type '{meta.get('type', '')}' not one of {sorted(TYPES)}")
        if meta.get("status", "open") not in ("open", "closed"):
            problems.append(f"{fn}: status '{meta.get('status')}' not open|closed")
    for tid, t in tickets.items():
        for b in t["blocked_by"]:
            if b not in tickets:
                problems.append(f"{t['file']}: blocked_by unknown id {b}")
    # cycle detection (DFS over open blockers)
    state = {}
    def visit(tid, stack):
        state[tid] = 1
        for b in tickets[tid]["blocked_by"]:
            if b not in tickets:
                continue
            if state.get(b) == 1:
                problems.append("cycle: " + " -> ".join(stack + [tid, b]))
            elif not state.get(b):
                visit(b, stack + [tid])
        state[tid] = 2
    for tid in tickets:
        if not state.get(tid):
            visit(tid, [])

    groups = {"frontier": [], "claimed": [], "blocked": [], "closed": []}
    for tid, t in tickets.items():
        if t.get("status", "open") == "closed":
            groups["closed"].append(tid)
        elif any(tickets.get(b, {}).get("status", "open") != "closed" for b in t["blocked_by"]):
            groups["blocked"].append(tid)
        elif t.get("assignee"):
            groups["claimed"].append(tid)
        else:
            groups["frontier"].append(tid)

    if "--json" in sys.argv:
        print(json.dumps({"groups": groups, "problems": problems,
                          "tickets": tickets}, indent=2))
    else:
        for g in ("frontier", "claimed", "blocked", "closed"):
            print(f"{g.upper()} ({len(groups[g])})")
            for tid in groups[g]:
                t = tickets[tid]
                extra = ""
                if g == "blocked":
                    open_b = [b for b in t["blocked_by"] if tickets.get(b, {}).get("status", "open") != "closed"]
                    extra = "  <- blocked by " + ", ".join(tickets[b]["title"] if b in tickets else b for b in open_b)
                if g == "claimed":
                    extra = f"  [{t['assignee']}]"
                print(f"  {tid} [{t.get('type', '?')}] {t['title']}{extra}")
        for p in problems:
            print("PROBLEM: " + p)
        if not groups["frontier"] and not groups["claimed"] and groups["blocked"]:
            print("PROBLEM: nothing on the frontier but open tickets remain (check blockers)")
            problems.append("empty frontier")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
