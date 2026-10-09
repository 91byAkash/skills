#!/usr/bin/env python3
"""Content planning helpers (standard library only).

Subcommands
  score     Rank content ideas. CSV columns: idea, impact, fit, search, resources
            (each 1-10; resources = 10 means cheap/easy) plus optional type
            (searchable/shareable/experimental), stage, keyword.
            Weights default 0.4/0.3/0.2/0.1 and can be changed with --weights.
  calendar  Turn a scored CSV into a dated calendar honoring a mix
            (default 60% searchable / 30% shareable / 10% experimental).
  post      Check social post text against platform limits and the
            "see more" fold. Reads a file or stdin; one post per blank-line block.

Examples
  content_tool.py score ideas.csv
  content_tool.py score ideas.csv --weights 0.5,0.3,0.1,0.1 --out ranked.csv
  content_tool.py calendar ranked.csv --start 2026-11-02 --per-week 3 --weeks 8
  content_tool.py post drafts.txt --platform linkedin
"""
import argparse
import csv
import datetime as dt
import re
import sys

LIMITS = {  # max chars, approx visible before "more", recommended hashtags
    "linkedin": (3000, 210, "3-5 at end"),
    "x": (280, 280, "0-2"),
    "threads": (500, 120, "1 topic tag"),
    "instagram": (2200, 125, "3-5"),
    "tiktok": (4000, 150, "3-5"),
    "facebook": (63206, 120, "0-2"),
    "youtube-title": (100, 70, "n/a"),
    "youtube-description": (5000, 100, "3-5 (15+ voids all)"),
    "pinterest": (500, 50, "use keywords, not tags"),
}


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def score(a):
    w = [float(x) for x in a.weights.split(",")]
    if len(w) != 4 or abs(sum(w) - 1) > 1e-6:
        sys.exit("--weights needs 4 numbers summing to 1")
    rows = read_rows(a.file)
    for r in rows:
        try:
            vals = [float(r[k]) for k in ("impact", "fit", "search", "resources")]
        except (KeyError, ValueError):
            sys.exit(f"bad row (need impact, fit, search, resources 1-10): {r}")
        r["score"] = round(sum(v * wt for v, wt in zip(vals, w)), 2)
    rows.sort(key=lambda r: -r["score"])
    cols = ["rank", "idea", "score", "type", "stage", "keyword", "impact", "fit", "search", "resources"]
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    if a.out:
        with open(a.out, "w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            wr.writeheader()
            wr.writerows(rows)
        print(f"wrote {a.out}")
    print(f"{'#':>3} {'score':>5}  {'type':<12} {'stage':<14} idea")
    for r in rows:
        print(f"{r['rank']:>3} {r['score']:>5}  {r.get('type', ''):<12} {r.get('stage', ''):<14} {r['idea']}")
    types = {}
    for r in rows:
        types[r.get("type", "") or "untyped"] = types.get(r.get("type", "") or "untyped", 0) + 1
    print("\nmix:", ", ".join(f"{k}={v}" for k, v in types.items()))


def calendar(a):
    rows = read_rows(a.file)
    rows.sort(key=lambda r: -float(r.get("score") or 0))
    mix = [float(x) for x in a.mix.split(",")]
    buckets = {"searchable": [], "shareable": [], "experimental": []}
    for r in rows:
        t = (r.get("type") or "searchable").lower()
        buckets.get(t, buckets["searchable"]).append(r)
    total = a.per_week * a.weeks
    quota = {"searchable": round(total * mix[0]), "shareable": round(total * mix[1])}
    quota["experimental"] = total - quota["searchable"] - quota["shareable"]
    # interleave by type so each week gets a blend: each slot goes to the type
    # furthest behind its share of the slots so far; best idea of that type first
    avail = {t: buckets[t][: quota[t]] for t in quota}
    order, used = [], {t: 0 for t in quota}
    share = {t: quota[t] / total if total else 0 for t in quota}
    while any(avail.values()):
        k = len(order) + 1
        t = max((t for t in avail if avail[t]), key=lambda t: share[t] * k - used[t])
        order.append((t, avail[t].pop(0)))
        used[t] += 1
    start = dt.date.fromisoformat(a.start)
    days = sorted([0, 2, 4, 1, 3][: a.per_week]) if a.per_week <= 5 else list(range(a.per_week))
    print("date        type          score  idea")
    for i, (t, r) in enumerate(order):
        week, slot = divmod(i, a.per_week)
        d = start + dt.timedelta(weeks=week, days=days[slot % len(days)])
        print(f"{d}  {t:<12} {r.get('score', ''):>6}  {r['idea']}")
    short = {t: quota[t] - len(buckets[t][: quota[t]]) for t in quota}
    gaps = [f"{t} short by {n}" for t, n in short.items() if n > 0]
    if gaps:
        print("\nnot enough ideas: " + "; ".join(gaps))


def post(a):
    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    blocks = [b.strip() for b in re.split(r"\n\s*\n(?=\S)", text) if b.strip()] if a.split else [text.strip()]
    mx, fold, tags = LIMITS[a.platform]
    for i, b in enumerate(blocks, 1):
        n = len(b)
        first = b.split("\n")[0]
        hashtags = re.findall(r"(?<!\w)#\w+", b)
        links = re.findall(r"https?://\S+", b)
        issues = []
        if n > mx:
            issues.append(f"over limit by {n - mx}")
        if len(first) > fold:
            issues.append(f"hook line {len(first)} chars; fold at ~{fold}")
        if links and a.platform in ("linkedin", "x"):
            issues.append("external link in body (often reduces reach; consider first comment/reply)")
        if "—" in b:
            issues.append("em dash")
        if re.search(r"\b(agree\?|thoughts\?|let that sink in|read that again|comment [\"']?(yes|below|\w+)[\"']? (if|to|and)|tag (someone|a friend)|like if|share if|repost if)", b.lower()):
            issues.append("engagement-bait phrase")
        lines = [l for l in b.split("\n") if l.strip()]
        if len(lines) >= 8 and sum(len(l.split()) <= 8 for l in lines) / len(lines) > 0.8:
            issues.append("one-short-line-per-line pattern; use real paragraphs")
        print(f"post {i}: {n}/{mx} chars, hashtags={len(hashtags)} (rec {tags}), links={len(links)}")
        print("   " + ("; ".join(issues) if issues else "ok"))
        print(f"   visible before fold: {b[:fold].replace(chr(10), ' / ')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = ap.add_subparsers(dest="cmd", required=True)
    p = s.add_parser("score"); p.add_argument("file"); p.add_argument("--weights", default="0.4,0.3,0.2,0.1"); p.add_argument("--out")
    p.set_defaults(f=score)
    p = s.add_parser("calendar"); p.add_argument("file"); p.add_argument("--start", default=dt.date.today().isoformat())
    p.add_argument("--per-week", type=int, default=3); p.add_argument("--weeks", type=int, default=8)
    p.add_argument("--mix", default="0.6,0.3,0.1"); p.set_defaults(f=calendar)
    p = s.add_parser("post"); p.add_argument("file"); p.add_argument("--platform", choices=sorted(LIMITS), default="linkedin")
    p.add_argument("--no-split", dest="split", action="store_false", help="treat whole file as one post"); p.set_defaults(f=post)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
