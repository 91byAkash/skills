#!/usr/bin/env python3
"""Voice-of-customer helpers (standard library only).

Subcommands
  tag   First-pass tagging of verbatim snippets into pain / trigger / outcome /
        alternative / objection / praise, with theme counts by source and
        segment, and a Markdown quote bank. Input: CSV with a `text` column and
        optional `source`, `segment`, `date`, `url` columns (or a .txt file,
        one snippet per line). Rules are keyword heuristics: always review.
  pmf   Product-market-fit survey scoring: share answering "very disappointed",
        95% confidence interval, and breakdown by segment. Input: CSV with an
        `answer` column (very/somewhat/not/na) and optional `segment`.
  sample Saturation check: how many new themes each additional interview added.
        Input: CSV with `interview` and `theme` columns.

Examples
  voc.py tag reviews.csv --out quote-bank.md
  voc.py tag notes.txt --extra-rule "pain:spreadsheet,copy paste"
  voc.py pmf survey.csv
  voc.py sample coded-interviews.csv
"""
import argparse
import csv
import math
import re
import sys
from collections import Counter, defaultdict

RULES = {
    "pain": ["frustrat", "annoy", "hate", "painful", "waste", "drowning", "manual", "tedious", "struggl",
             "nightmare", "slow", "confus", "broken", "can't", "cannot", "hard to", "takes forever", "headache",
             "workaround", "error-prone", "mess", "chasing", "crash", "bug", "dread", "losing", "stuck", "fed up"],
    "trigger": ["when we", "after we", "once we", "started looking", "switched", "new hire", "hired", "grew",
                "scaling", "audit", "deadline", "last straw", "finally", "had to find", "our team doubled",
                "funding", "migrat", "renewal"],
    "outcome": ["so that", "i want", "we want", "i need", "we need", "goal", "would love", "saves", "saved",
                "faster", "peace of mind", "finally able", "without having to", "in minutes", "on time"],
    "alternative": ["instead of", "used to use", "switched from", "compared to", "vs ", "versus", "spreadsheet",
                    "excel", "an agency", "freelancer", "we were using", "currently use", "we use", "built our own", "in-house", "alternative", "tried"],
    "objection": ["too expensive", "pricey", "price", "cost", "worried", "concern", "not sure", "risk",
                  "security", "learning curve", "integrat", "contract", "lock-in", "trust", "doubt",
                  "dealbreaker", "deal breaker", "will it", "does it work with", "sync with"],
    "praise": ["love", "great", "amazing", "easy to", "game", "best", "recommend", "life saver", "lifesaver",
               "intuitive", "support team"],
    "wish": ["i wish", "wish it", "would be better if", "if only", "missing", "doesn't have", "lacks", "feature request"],
}
EMOTION = ["hate", "love", "nightmare", "drowning", "!!", "finally", "amazing", "awful", "terrible", "frustrat",
           "life saver", "lifesaver", "obsessed", "furious", "relief"]


def load(path):
    rows = []
    if path.endswith(".csv"):
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                t = (r.get("text") or "").strip()
                if t:
                    rows.append({"text": t, "source": r.get("source", "") or "unknown",
                                 "segment": r.get("segment", "") or "all", "date": r.get("date", ""),
                                 "url": r.get("url", "")})
    else:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append({"text": line.strip(), "source": "unknown", "segment": "all", "date": "", "url": ""})
    return rows


def classify(text, rules):
    low = text.lower()
    tags = [k for k, words in rules.items() if any(w in low for w in words)]
    intensity = sum(low.count(w) for w in EMOTION) + text.count("!")
    return tags, intensity


def tag(a):
    rules = {k: list(v) for k, v in RULES.items()}
    for spec in a.extra_rule or []:
        k, _, words = spec.partition(":")
        rules.setdefault(k.strip(), []).extend(w.strip().lower() for w in words.split(",") if w.strip())
    rows = load(a.file)
    if not rows:
        sys.exit("no snippets found")
    by_tag = defaultdict(list)
    src_count = defaultdict(set)
    seg_count = defaultdict(Counter)
    untagged = 0
    for r in rows:
        tags, inten = classify(r["text"], rules)
        if not tags:
            untagged += 1
        for t in tags:
            by_tag[t].append((inten, r))
            src_count[t].add(r["source"])
            seg_count[t][r["segment"]] += 1
    out = [f"# Quote bank ({len(rows)} snippets, {untagged} untagged)", "",
           "Heuristic first pass. Re-read every quote, merge into themes, and set confidence by hand.", "",
           "| Tag | Snippets | Distinct sources | Top segments | Confidence hint |", "|---|---|---|---|---|"]
    for t, items in sorted(by_tag.items(), key=lambda kv: -len(kv[1])):
        ns = len(src_count[t])
        hint = "high" if ns >= 3 and len(items) >= 5 else "medium" if ns >= 2 else "low"
        segs = ", ".join(f"{s} ({n})" for s, n in seg_count[t].most_common(3))
        out.append(f"| {t} | {len(items)} | {ns} | {segs} | {hint} |")
    for t, items in sorted(by_tag.items(), key=lambda kv: -len(kv[1])):
        out += ["", f"## {t}", ""]
        for inten, r in sorted(items, key=lambda x: -x[0])[: a.top]:
            meta = ", ".join(x for x in (r["source"], r["segment"], r["date"], r["url"]) if x and x not in ("unknown", "all"))
            out.append(f'- "{r["text"]}"' + (f" ({meta})" if meta else "") + (" [strong emotion]" if inten >= 2 else ""))
    text = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
        print(f"wrote {a.out}")
    else:
        print(text)


def wilson(k, n, z=1.96):
    if n == 0:
        return 0, 0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - m) / d, (c + m) / d


def norm_answer(s):
    s = (s or "").strip().lower()
    if s.startswith("very"):
        return "very"
    if s.startswith("somewhat"):
        return "somewhat"
    if s.startswith("not"):
        return "not"
    return "na"


def pmf(a):
    seg = defaultdict(Counter)
    with open(a.file, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ans = norm_answer(r.get("answer"))
            seg["ALL"][ans] += 1
            if r.get("segment"):
                seg[r["segment"]][ans] += 1
    print("segment            n   very%   95% CI          somewhat%  not%   verdict")
    for s, c in sorted(seg.items(), key=lambda kv: (kv[0] != "ALL", kv[0])):
        n = c["very"] + c["somewhat"] + c["not"]  # exclude "no longer use"
        if n == 0:
            continue
        lo, hi = wilson(c["very"], n)
        v = c["very"] / n
        if lo >= 0.40:
            verdict = "above 40% benchmark"
        elif hi < 0.40:
            verdict = "below 40%"
        elif v >= 0.40:
            verdict = "near/above 40%, not yet conclusive"
        else:
            verdict = "under 40%, not yet conclusive"
        print(f"{s:<16} {n:>4}  {v:6.1%}  {lo:5.1%}-{hi:5.1%}   {c['somewhat'] / n:7.1%}  {c['not'] / n:5.1%}   {verdict}")
        if n < 40:
            print(f"{'':<16}       (small sample; aim for 40+ responses per segment)")
    print("\nNext: read the 'main benefit' answers from the very-disappointed group; that is your positioning in their words.")


def sample(a):
    seen, order = set(), []
    per = defaultdict(set)
    with open(a.file, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("interview") not in order:
                order.append(r.get("interview"))
            per[r.get("interview")].add((r.get("theme") or "").strip().lower())
    print("interview  new themes  cumulative")
    tail = []
    for i in order:
        new = per[i] - seen
        seen |= per[i]
        tail.append(len(new))
        print(f"{i:<10} {len(new):>10}  {len(seen):>10}")
    if len(tail) >= 3 and sum(tail[-3:]) == 0:
        print("saturation: last 3 interviews added no new themes; stop recruiting for this segment")
    else:
        print("still finding new themes; keep going (typical saturation is 5-12 interviews per segment)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = ap.add_subparsers(dest="cmd", required=True)
    p = s.add_parser("tag"); p.add_argument("file"); p.add_argument("--out"); p.add_argument("--top", type=int, default=8)
    p.add_argument("--extra-rule", action="append", help="tag:word1,word2 (adds or extends a tag)"); p.set_defaults(f=tag)
    p = s.add_parser("pmf"); p.add_argument("file"); p.set_defaults(f=pmf)
    p = s.add_parser("sample"); p.add_argument("file"); p.set_defaults(f=sample)
    a = ap.parse_args()
    try:
        a.f(a)
    except FileNotFoundError as e:
        sys.exit(f"error: file not found: {e.filename}")


if __name__ == "__main__":
    main()
