#!/usr/bin/env python3
"""Grounding ledger for shape mode and beats mode.

A concept is grounded if the reader walked in with it (prerequisite) or an earlier block/beat introduced it.
A block may only *require* grounded concepts; when it lands, the concepts it *grounds* become available.

  ledger.py init   ledger.json --prereq "deploy pipeline,CI" [--article draft.md]
  ledger.py check  ledger.json --requires "gate,gate debt"            is a candidate reachable? exit 1 if not
  ledger.py offer  ledger.json cand.json                              rank candidate next blocks: reachable or blocked, what each unlocks
  ledger.py land   ledger.json "one-line summary" --requires a,b --grounds c,d [--kind beat|paragraph|list|table|quote|code|callout]
  ledger.py undo   ledger.json                                         drop the last landed block (user rewrote/removed it)
  ledger.py promote ledger.json "concept"                               make a concept a prerequisite (narrows the audience)
  ledger.py show   ledger.json [--md]

cand.json: [{"id":"A","summary":"...","requires":["x"],"grounds":["y"]}, ...]
Concept names are matched case-insensitively.
"""
import argparse, json, sys
from pathlib import Path


def norm(xs):
    return [x.strip() for x in (xs or "").split(",") if x.strip()] if isinstance(xs, str) or xs is None else [x.strip() for x in xs]


def load(p):
    return json.loads(Path(p).read_text())


def save(p, d):
    Path(p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")


def grounded(d):
    g = {c.lower(): "prerequisite" for c in d["prerequisites"]}
    for i, b in enumerate(d["blocks"], 1):
        for c in b["grounds"]:
            g.setdefault(c.lower(), f"block {i}")
    return g


def missing(d, req):
    g = grounded(d)
    return [r for r in req if r.lower() not in g]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("ledger"); s.add_argument("--prereq", default=""); s.add_argument("--article", default=""); s.add_argument("--force", action="store_true")
    s = sub.add_parser("check"); s.add_argument("ledger"); s.add_argument("--requires", default="")
    s = sub.add_parser("offer"); s.add_argument("ledger"); s.add_argument("candidates")
    s = sub.add_parser("land"); s.add_argument("ledger"); s.add_argument("summary"); s.add_argument("--requires", default=""); s.add_argument("--grounds", default=""); s.add_argument("--kind", default="paragraph"); s.add_argument("--force", action="store_true")
    s = sub.add_parser("undo"); s.add_argument("ledger")
    s = sub.add_parser("promote"); s.add_argument("ledger"); s.add_argument("concept")
    s = sub.add_parser("show"); s.add_argument("ledger"); s.add_argument("--md", action="store_true")
    a = ap.parse_args()

    if a.cmd == "init":
        if Path(a.ledger).exists() and not a.force:
            sys.exit(f"{a.ledger} exists (use --force to reset)")
        save(a.ledger, {"article": a.article, "prerequisites": norm(a.prereq), "blocks": []})
        print(f"ledger with {len(norm(a.prereq))} prerequisite(s)")
        return
    d = load(a.ledger)
    if a.cmd == "check":
        m = missing(d, norm(a.requires))
        if m:
            print("BLOCKED: not grounded yet: " + ", ".join(m) + "  -> add a grounding block first, or promote to prerequisite")
            sys.exit(1)
        print("REACHABLE")
    elif a.cmd == "offer":
        cands = json.loads(Path(a.candidates).read_text())
        g = grounded(d)
        for c in cands:
            m = [r for r in c.get("requires", []) if r.lower() not in g]
            new = [x for x in c.get("grounds", []) if x.lower() not in g]
            state = "reachable" if not m else "BLOCKED (needs " + ", ".join(m) + ")"
            print(f"{c['id']}: {state}; grounds {', '.join(new) or 'nothing new'}  | {c['summary']}")
            if m:
                unlockers = [o["id"] for o in cands if o is not c and set(x.lower() for x in o.get("grounds", [])) & set(x.lower() for x in m)]
                if unlockers:
                    print(f"   would be unlocked by: {', '.join(unlockers)}")
        if not any(not [r for r in c.get("requires", []) if r.lower() not in g] for c in cands):
            sys.exit(1)
    elif a.cmd == "land":
        req, gr = norm(a.requires), norm(a.grounds)
        m = missing(d, req)
        if m and not a.force:
            sys.exit("refusing to land: requires ungrounded " + ", ".join(m) + " (ground it first, promote it, or --force)")
        dup = [x for x in gr if x.lower() in grounded(d)]
        d["blocks"].append({"summary": a.summary, "kind": a.kind, "requires": req, "grounds": gr})
        save(a.ledger, d)
        print(f"landed block {len(d['blocks'])}" + (f"; already grounded (re-grounding is a repeat?): {', '.join(dup)}" if dup else ""))
    elif a.cmd == "undo":
        if not d["blocks"]:
            sys.exit("nothing to undo")
        b = d["blocks"].pop(); save(a.ledger, d); print(f"removed: {b['summary']}")
    elif a.cmd == "promote":
        d["prerequisites"].append(a.concept); save(a.ledger, d); print(f"'{a.concept}' is now a prerequisite")
    elif a.cmd == "show":
        g = grounded(d)
        if a.md:
            print("| # | Kind | Block | Requires | Grounds |\n|---|---|---|---|---|")
            print(f"| 0 | - | (reader walks in with) | - | {', '.join(d['prerequisites'])} |")
            for i, b in enumerate(d["blocks"], 1):
                print(f"| {i} | {b['kind']} | {b['summary']} | {', '.join(b['requires']) or '-'} | {', '.join(b['grounds']) or '-'} |")
        else:
            print("Prerequisites: " + ", ".join(d["prerequisites"]))
            for i, b in enumerate(d["blocks"], 1):
                print(f"{i:2}. [{b['kind']}] {b['summary']}  requires: {', '.join(b['requires']) or '-'}  grounds: {', '.join(b['grounds']) or '-'}")
            print(f"Grounded now ({len(g)}): " + ", ".join(sorted(g)))


if __name__ == "__main__":
    main()
