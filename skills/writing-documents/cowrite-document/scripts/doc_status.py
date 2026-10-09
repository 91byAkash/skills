#!/usr/bin/env python3
"""Progress and readiness report for a Markdown document being co-authored.

Usage:
  doc_status.py doc.md                 # per-section table + document checks
  doc_status.py doc.md --final         # exit 1 if anything blocks sharing
  doc_status.py doc.md --json

Per section: words, status (todo / draft / done), placeholders left, longest
sentence. Status is "todo" while the section still has its [To be written]
text, "draft" if it has other placeholders (TODO, TBD, XXX, [..], ???), else "done".

Document checks:
  placeholders   any [To be written], [check: ...], TODO, TBD, XXX, ???, [insert ...], {braces} left
  empty          a heading with nothing under it
  alt-text       images with empty alt text (readers using assistants or screen readers miss them)
  links          relative links to files that don't exist
  long           sentences over 35 words
  repeats        the same sentence appearing twice
  undefined      ALL-CAPS acronyms (3+ letters) used without ever being expanded "Xxx Yyy (XY)"
  summary        no Summary / TL;DR / Recommendation section near the top
Also prints total words and reading time (230 wpm).
"""
import argparse, json, re, sys
from pathlib import Path

PH = re.compile(r"\[To be written[^\]]*\]|\[check:[^\]]*\]|\bTODO\b|\bTBD\b|\bXXX\b|\?\?\?|\[insert[^\]]*\]|\[\.\.\.?\]|\{[a-z_]+\}", re.I)
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")
COMMON_ACR = {"API", "URL", "HTTP", "HTTPS", "JSON", "SQL", "CSV", "PDF", "USA", "CEO", "CTO", "CFO", "FAQ", "ETA", "UTC", "IST", "PST",
              "TBD", "TODO", "XXX", "ADR", "PRD", "RFC", "OKR", "KPI", "SLA", "SLO", "UI", "UX", "AWS", "GCP", "EOD", "EOW", "NNN", "MVP", "ROI", "ERP", "CRM", "SDK", "CLI", "PII", "GDPR"}


def strip_code(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


def split_sections(text):
    secs, cur, buf = [], "(preamble)", []
    for line in text.splitlines():
        m = re.match(r"^(#{1,3})\s+(.*)", line)
        if m and len(m.group(1)) >= 2:
            secs.append((cur, "\n".join(buf)))
            cur, buf = m.group(2).strip(), []
        else:
            buf.append(line)
    secs.append((cur, "\n".join(buf)))
    return secs


def sentences(text):
    """Prose sentences only: table rows and headings are skipped; each list item stands alone."""
    units, para = [], []
    for line in text.splitlines():
        t = line.strip()
        if not t or t.startswith(("|", "#")) or re.match(r"^([-*+]|\d+[.)])\s", t):
            if para:
                units.append(" ".join(para))
                para = []
            if re.match(r"^([-*+]|\d+[.)])\s", t):
                units.append(re.sub(r"^([-*+]|\d+[.)])\s+", "", t))
            continue
        para.append(t)
    if para:
        units.append(" ".join(para))
    out = []
    for u in units:
        u = re.sub(r"\*\*|__", "", u)
        out += [x.strip() for x in SENT.split(u) if len(x.split()) >= 3]
    return out


def words(text):
    return len(re.findall(r"[A-Za-z0-9][\w'’-]*", text))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("doc")
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--long", type=int, default=35)
    a = ap.parse_args()
    path = Path(a.doc)
    if not path.is_file():
        print(f"doc_status.py: no such file: {a.doc}", file=sys.stderr); sys.exit(2)
    raw = path.read_text(encoding="utf-8")
    text = strip_code(raw)
    rows, issues = [], []
    for name, body in split_sections(text):
        if name == "(preamble)" and not body.strip():
            continue
        ph = PH.findall(body)
        w = words(PH.sub("", body))
        sl = max((len(s.split()) for s in sentences(PH.sub("", body))), default=0)
        status = "todo" if re.search(r"\[To be written", body) else "draft" if ph else ("empty" if w == 0 else "done")
        rows.append({"section": name, "words": w, "status": status, "placeholders": len(ph), "longest_sentence": sl})
        if w == 0 and not ph and name != "(preamble)":
            issues.append(("empty", f"section '{name}' has no content"))
    for i, line in enumerate(raw.splitlines(), 1):
        for m in PH.finditer(line):
            issues.append(("placeholders", f"line {i}: {m.group(0)}"))
        for m in re.finditer(r"!\[(.*?)\]\(([^)\s]+)", line):
            if not m.group(1).strip():
                issues.append(("alt-text", f"line {i}: image {m.group(2)} has no alt text"))
        for m in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)\s#]+)(#[^)]*)?\)", line):
            target = m.group(1)
            if not re.match(r"^[a-z]+:", target) and not (path.parent / target).exists():
                issues.append(("links", f"line {i}: link target {target} not found"))
    seen = {}
    for s in sentences(text):
        n = len(s.split())
        if n > a.long:
            issues.append(("long", f"{n} words: {s[:90]}..."))
        key = re.sub(r"\W+", " ", s.lower()).strip()
        if len(key.split()) >= 6:
            if key in seen:
                issues.append(("repeats", f"repeated sentence: {s[:90]}"))
            seen[key] = True
    plain = PH.sub("", text)
    expanded = set(re.findall(r"\(([A-Z]{2,}s?)\)", plain))
    for acr in sorted(set(re.findall(r"\b[A-Z]{3,}\b", plain)) - COMMON_ACR - expanded):
        issues.append(("undefined", f"acronym {acr} is never expanded"))
    heads = [r["section"].lower() for r in rows[:3]]
    if not any(re.search(r"summary|tl;?dr|recommendation|the ask|decision$|context", h) for h in heads):
        issues.append(("summary", "no Summary / TL;DR / Recommendation in the first sections"))
    total = sum(r["words"] for r in rows)
    blocking = {"placeholders", "empty", "alt-text", "links"}
    report = {"doc": str(path), "words": total, "reading_minutes": round(total / 230, 1), "sections": rows,
              "issues": [{"check": c, "detail": d, "blocking": c in blocking} for c, d in issues]}
    if a.json:
        print(json.dumps(report, indent=2))
    else:
        done = sum(r["status"] == "done" for r in rows if r["section"] != "(preamble)")
        n = sum(1 for r in rows if r["section"] != "(preamble)")
        print(f"{path}: {total} words, ~{report['reading_minutes']} min read, {done}/{n} sections done\n")
        print(f"{'section':<32} {'status':<6} {'words':>6} {'ph':>3} {'longest':>8}")
        for r in rows:
            print(f"{r['section'][:32]:<32} {r['status']:<6} {r['words']:>6} {r['placeholders']:>3} {r['longest_sentence']:>8}")
        if issues:
            print()
            for c, d in issues:
                print(f"{'BLOCK' if c in blocking else 'note '} {c:<12} {d}")
    if a.final and any(c in blocking for c, _ in issues):
        sys.exit(1)


if __name__ == "__main__":
    main()
