#!/usr/bin/env python3
"""Decide whether a review loop should continue.

Usage: loop-decide.py [--gate 8] [--min 2] [--max 4] [--same-top-issue] SCORE [SCORE ...]
       loop-decide.py [options] --from-file critic-round-*.md   (first "Score: N/10" per file)
Scores are in round order; --from-file sorts names naturally (round-2 before round-10).
Rules, in order:
  rounds < min                                   -> continue
  last score >= gate                             -> stop: gate met
  rounds >= max                                  -> stop: max rounds
  no improvement on the previous round AND
    --same-top-issue (the critic's top issue is unchanged)  -> escalate: stalled
  two rounds in a row without improvement       -> escalate: stalled
    (last three scores non-increasing, any issues)
  otherwise                                      -> continue
Exit code 0 for stop, 10 for continue, 20 for escalate, 2 for bad input.
"""
import argparse
import re
import sys


def decide(scores, gate, lo, hi, same_top_issue=False):
    n = len(scores)
    if n < max(lo, 1):
        return "continue", 10
    if scores[-1] >= gate:
        return "stop: gate met", 0
    if n >= hi:
        return "stop: max rounds", 0
    if n >= 2 and scores[-1] <= scores[-2] and same_top_issue:
        return "escalate: stalled (no improvement, same top issue)", 20
    if n >= 3 and scores[-1] <= scores[-2] <= scores[-3]:
        return "escalate: stalled (no improvement for two rounds)", 20
    return "continue", 10


def natural_key(path):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", path)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gate", type=float, default=8)
    ap.add_argument("--min", type=int, default=2)
    ap.add_argument("--max", type=int, default=4)
    ap.add_argument("--same-top-issue", action="store_true",
                    help="the latest critique's top issue matches the previous round's")
    ap.add_argument("--from-file", nargs="+", metavar="FILE")
    ap.add_argument("scores", nargs="*", type=float)
    a = ap.parse_args()
    scores = list(a.scores)
    for path in sorted(a.from_file or [], key=natural_key):
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as e:
            print(f"cannot read {path}: {e}", file=sys.stderr)
            return 2
        m = re.search(r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10", text)
        if not m:
            print(f"no 'Score: N/10' in {path}", file=sys.stderr)
            return 2
        scores.append(float(m.group(1)))
    bad = [s for s in scores if not 0 <= s <= 10]
    if bad:
        print(f"scores must be 0-10, got {bad}", file=sys.stderr)
        return 2
    if a.min > a.max or a.max < 1:
        print("need 1 <= --min <= --max", file=sys.stderr)
        return 2
    verdict, code = decide(scores, a.gate, a.min, a.max, a.same_top_issue)
    trail = " → ".join(f"{s:g}" for s in scores) or "none"
    print(f"scores: {trail} | gate {a.gate:g}, rounds {len(scores)}/{a.max}")
    print(verdict)
    return code


if __name__ == "__main__":
    sys.exit(main())
