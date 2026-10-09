#!/usr/bin/env python3
"""Prepare a reader test: one self-contained prompt file per predicted question
plus the whole-document checks, ready to hand to fresh sub-agents (or to paste
into a fresh chat). Then tabulate the scored results.

Usage:
  reader_test.py prepare doc.md --questions questions.txt -o reader-test/
  reader_test.py report reader-test/results.json

questions.txt: one question per line; optionally "question || intended answer".
prepare writes reader-test/q01.txt ... (doc + question + answer format),
reader-test/check-*.txt (ambiguity, assumptions, contradictions, ask, skim,
hostile reviewer) and reader-test/results.json to fill in with each reply's
"score": "pass" | "partial" | "fail" and "fix" (section to change).
Prompts contain only the document: never paste drafting notes or chat history.
"""
import argparse, json, sys
from pathlib import Path

Q_PROMPT = """{doc}

---
You are reading the document above for the first time. You have no other
context about the project, team or company.

Question: {q}

Reply in exactly this format:
ANSWER: <your answer, citing the section heading you relied on>
CONFIDENCE: high | medium | low
UNCLEAR: <anything in the document that was ambiguous for this question, or "none">
ASSUMED: <knowledge the document expects you to already have, or "none">
"""
CHECKS = {
    "ambiguity": "List every sentence or term in the document above that a reader could reasonably interpret in two different ways. Quote it and give both readings.",
    "assumptions": "List the acronyms, names, systems, past events and decisions the document refers to without explaining. For each, say whether the document still makes sense without knowing it.",
    "contradictions": "List any statements in the document that contradict each other: numbers, dates, scope, owners or recommendations. Quote both sides. Say 'none found' if there are none.",
    "ask": "In one sentence each: what does this document want the reader to do or decide, by when, and why? If you can't tell, say so.",
    "skim": "Read only the title, the headings and the first sentence of each section. What is the main point and the main argument?",
    "hostile": "You are a sceptical senior reviewer. Name the three weakest points in the argument and the evidence needed to fix each.",
}


def prepare(a):
    for f in (a.doc, a.questions):
        if not Path(f).is_file():
            sys.exit(f"reader_test.py: no such file: {f}")
    doc = Path(a.doc).read_text(encoding="utf-8").strip()
    lines = [l.strip() for l in Path(a.questions).read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    if not 5 <= len(lines) <= 12:
        print(f"note: {len(lines)} questions; 5-10 realistic reader questions work best", file=sys.stderr)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for i, line in enumerate(lines, 1):
        q, _, intended = (part.strip() for part in line.partition("||"))
        (out / f"q{i:02d}.txt").write_text(Q_PROMPT.format(doc=doc, q=q), encoding="utf-8")
        results.append({"id": f"q{i:02d}", "question": q, "intended": intended, "reply": "", "score": "", "fix": ""})
    for name, prompt in CHECKS.items():
        (out / f"check-{name}.txt").write_text(f"{doc}\n\n---\n{prompt}\n", encoding="utf-8")
        results.append({"id": f"check-{name}", "question": prompt, "intended": "", "reply": "", "score": "", "fix": ""})
    (out / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"wrote {len(lines)} question prompts and {len(CHECKS)} checks to {out}/ (fill results.json with replies and scores)")


def report(a):
    res = json.loads(Path(a.results).read_text(encoding="utf-8"))
    qs = [r for r in res if r["id"].startswith("q")]
    for r in qs:
        r["score"] = str(r.get("score") or "").strip().lower()
        if r["score"] and r["score"] not in ("pass", "partial", "fail"):
            sys.exit(f"error: {r['id']} score {r['score']!r}; use pass, partial or fail")
    scored = [r for r in qs if r.get("score")]
    counts = {s: sum(r["score"] == s for r in scored) for s in ("pass", "partial", "fail")}
    print(f"| # | Question | Score | Fix in |\n|---|---|---|---|")
    for r in qs:
        print(f"| {r['id']} | {r['question']} | {r.get('score') or '-'} | {r.get('fix') or ''} |")
    print(f"\n{counts['pass']} pass, {counts['partial']} partial, {counts['fail']} fail, {len(qs) - len(scored)} unscored")
    # a check counts as an open finding if it names a fix or was scored fail/partial
    flagged = [r for r in res if r["id"].startswith("check")
               and (r.get("fix") or str(r.get("score") or "").strip().lower() in ("fail", "partial"))]
    for r in flagged:
        print(f"- {r['id']}: fix {r.get('fix') or '(scored ' + str(r.get('score')) + '; name the section to change)'}")
    ready = len(scored) == len(qs) and counts["fail"] == 0 and counts["partial"] <= max(1, len(qs) // 5) and not flagged
    if len(scored) < len(qs):
        print("NOT READY: score every question (pass / partial / fail) before deciding")
    else:
        print("READY: the document answers its readers' questions" if ready else "NOT READY: revise the sections listed, then re-test with a fresh reader")
    sys.exit(0 if ready else 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare"); p.add_argument("doc"); p.add_argument("--questions", required=True); p.add_argument("-o", "--out", default="reader-test")
    r = sub.add_parser("report"); r.add_argument("results")
    a = ap.parse_args()
    prepare(a) if a.cmd == "prepare" else report(a)


if __name__ == "__main__":
    main()
