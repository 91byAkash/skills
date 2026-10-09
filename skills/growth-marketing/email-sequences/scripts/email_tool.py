#!/usr/bin/env python3
"""Email sequence helpers (standard library only).

Subcommands
  plan     Check a sequence plan CSV with columns:
           email, day, goal, subject, preview, cta[, segment][, body_words][, type]
           type = transactional | educational | story | sales (common names like
           welcome, onboarding, case-study, promo, trial-end, dunning are mapped)
           Flags: subject length (aim ~30-60 chars), preview length (~40-140,
           not repeating the subject), missing/multiple CTAs, gaps between sends,
           weekend sends (B2B), body length by type, bait patterns in subjects.
  subject  Lint subject lines passed as arguments or one per line on stdin.
  health   Deliverability and engagement health from campaign counts.

Exit status: 0 clean, 1 when any row, subject or rate is flagged.

Examples
  email_tool.py plan sequence.csv --start 2026-11-02 --b2b
  email_tool.py subject "Re: quick question" "Your receipts are ready, Maya"
  email_tool.py health --sent 12000 --delivered 11820 --bounced 180 --complaints 9 \
      --unsubs 70 --clicks 410 --conversions 52
"""
import argparse
import csv
import datetime as dt
import re
import sys

BAIT = [r"^\s*(re|fwd?):", r"\bfree!+", r"you won'?t believe", r"\burgent\b", r"act now", r"\bguarantee",
        r"\$\$+", r"!!+", r"\bcongratulations\b", r"\bwinner\b", r"risk[- ]free", r"100% free", r"click here",
        r"limited time", r"last chance"]
LENGTH = {"transactional": (50, 125), "educational": (150, 300), "story": (300, 500), "sales": (150, 400)}
# sequence/email names people actually put in the type column -> length class
TYPE_ALIAS = {"welcome": "transactional", "onboarding": "educational", "nurture": "educational",
              "newsletter": "educational", "re-engagement": "educational", "story-driven": "story",
              "case": "story", "case-study": "story", "promo": "sales", "trial-end": "sales",
              "trial-to-paid": "sales", "upgrade": "sales", "win-back": "sales", "dunning": "transactional",
              "receipt": "transactional", "confirmation": "transactional"}


def subject_issues(s):
    out = []
    n = len(s)
    if n > 60:
        out.append(f"{n} chars (often truncated on mobile beyond ~40-60)")
    if n < 15:
        out.append(f"{n} chars (very short; make sure it's specific)")
    letters = [c for c in s if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.5:
        out.append("mostly capitals")
    for rx in BAIT:
        if re.search(rx, s.lower()):
            out.append(f"bait/spam pattern: {rx}")
    emojis = len(re.findall(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", s))
    if emojis > 1:
        out.append(f"{emojis} emoji")
    if "—" in s:
        out.append("em dash")
    return out


def plan(a):
    try:
        with open(a.file, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except OSError as e:
        sys.exit(f"cannot read {a.file}: {e.strerror}")
    if not rows:
        sys.exit("empty plan")
    start = dt.date.fromisoformat(a.start) if a.start else None
    prev_day = None
    total = 0
    flagged = 0
    for r in rows:
        issues = []
        try:
            day = int(float(r.get("day") or 0))
        except ValueError:
            sys.exit(f"row {total + 1}: 'day' must be a number, got {r.get('day')!r}")
        subj = (r.get("subject") or "").strip()
        prev = (r.get("preview") or "").strip()
        cta = (r.get("cta") or "").strip()
        issues += subject_issues(subj)
        if not prev:
            issues.append("no preview text")
        else:
            if len(prev) < 40 or len(prev) > 140:
                issues.append(f"preview {len(prev)} chars (aim ~40-140)")
            if subj and prev.lower().startswith(subj.lower()[:20]):
                issues.append("preview repeats subject")
        if not cta:
            issues.append("no CTA")
        elif re.search(r"\s(?:and|\+|/)\s|[;|]", cta):
            issues.append("more than one CTA?")
        if prev_day is not None:
            gap = day - prev_day
            if gap < 1 and r.get("type", "") != "transactional":
                issues.append("same-day as previous email")
            if gap > 14:
                issues.append(f"{gap}-day gap; momentum may fade")
        if start and a.b2b:
            send = start + dt.timedelta(days=day)
            if send.weekday() >= 5:
                issues.append(f"lands on {send:%A} ({send})")
        t = (r.get("type") or "").strip().lower()
        t = TYPE_ALIAS.get(t, t)
        if r.get("body_words") and t and t not in LENGTH:
            issues.append(f"type '{t}' unknown; use transactional/educational/story/sales to check length")
        if r.get("body_words") and t in LENGTH:
            w = int(r["body_words"])
            lo, hi = LENGTH[t]
            if not lo * 0.7 <= w <= hi * 1.3:
                issues.append(f"{w} words for {t} (typical {lo}-{hi})")
        prev_day = day
        total += 1
        print(f"#{r.get('email', total)} day {day:>3}  {r.get('goal', '')[:40]:<40}  {subj[:50]}")
        for i in issues:
            print(f"      - {i}")
        flagged += bool(issues)
    print(f"\n{total} emails over {prev_day} days; {flagged} with issues")
    return 1 if flagged else 0


def subject(a):
    lines = a.subjects or [l.strip() for l in sys.stdin if l.strip()]
    bad = 0
    for s in lines:
        iss = subject_issues(s)
        bad += bool(iss)
        print(f"{len(s):>3}  {s}")
        for i in iss:
            print(f"     - {i}")
        if not iss:
            print("     ok")
    return 1 if bad else 0


def rate(n, d):
    return n / d if d else 0


def health(a):
    delivered = a.delivered or (a.sent - a.bounced)
    rows = [
        ("bounce rate", rate(a.bounced, a.sent), 0.02, "above ~2%: clean list, verify capture, check for purchased data"),
        ("complaint (spam) rate", rate(a.complaints, delivered), 0.001, "keep under 0.1%; never reach 0.3% (major inbox providers' bulk-sender limit)"),
        ("unsubscribe rate", rate(a.unsubs, delivered), 0.005, "above ~0.5% per send: relevance or frequency problem"),
    ]
    print(f"delivered {delivered:,} of {a.sent:,} ({rate(delivered, a.sent):.1%})")
    worst = 0
    for name, v, limit, msg in rows:
        flag = "OK" if v <= limit else "CHECK"
        if name.startswith("complaint") and v >= 0.003:
            flag = "FAIL"
        worst = max(worst, {"OK": 0, "CHECK": 1, "FAIL": 2}[flag])
        print(f"{name:<22} {v:7.3%}  [{flag}]  {msg if flag != 'OK' else ''}")
    if a.clicks:
        print(f"{'click rate':<22} {rate(a.clicks, delivered):7.2%}  (typical 1-5%; opens are inflated by privacy proxies, so judge by clicks)")
    if a.opens:
        print(f"{'open rate (directional)':<22} {rate(a.opens, delivered):7.1%}")
    if a.conversions:
        print(f"{'conversion rate':<22} {rate(a.conversions, delivered):7.2%}  ({a.conversions} conversions)")
        if a.clicks:
            print(f"{'click-to-conversion':<22} {rate(a.conversions, a.clicks):7.1%}")
    if a.revenue:
        print(f"{'revenue per delivered':<22} {a.revenue / delivered:7.3f}")
    return 1 if worst else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = ap.add_subparsers(dest="cmd", required=True)
    p = s.add_parser("plan"); p.add_argument("file"); p.add_argument("--start"); p.add_argument("--b2b", action="store_true")
    p.set_defaults(f=plan)
    p = s.add_parser("subject"); p.add_argument("subjects", nargs="*"); p.set_defaults(f=subject)
    p = s.add_parser("health")
    for k in ("sent", "delivered", "bounced", "complaints", "unsubs", "clicks", "opens", "conversions"):
        p.add_argument("--" + k, type=int, default=0)
    p.add_argument("--revenue", type=float, default=0)
    p.set_defaults(f=health)
    a = ap.parse_args()
    if a.cmd == "health" and not a.sent:
        sys.exit("--sent is required")
    sys.exit(a.f(a) or 0)


if __name__ == "__main__":
    main()
