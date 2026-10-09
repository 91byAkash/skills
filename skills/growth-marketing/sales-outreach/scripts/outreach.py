#!/usr/bin/env python3
"""Outbound helpers (standard library only).

Subcommands
  lint      Check a cold email draft (first line may be "Subject: ..."); exit 1 if flagged.
            Flags length (>80 words for a first touch), reading grade, I/we vs
            you balance, links/images, stock openers, weak follow-up phrases,
            meeting asks in a first touch, fake Re:/Fwd:, subject shape.
  score     Score leads from CSV with fit and engagement columns using a
            points table (JSON) and assign Hot/Warm/Cold/Skip. Default columns:
            industry (target/secondary), size_band (11-50, 51-200, 201-1000),
            title_level (c-suite/vp/director/manager), signal_type (usage,
            champion_job_change, pricing_visit, new_leader, hiring, funding,
            tech_change, intent; several allowed, separated by ';'),
            email_status (invalid/catch-all), disqualifier (yes). A --rules
            JSON with the same shape replaces the table.
  capacity  Domains and mailboxes needed for a target weekly volume.
  funnel    Contacts needed for a meeting or revenue target, from your rates.

Examples
  outreach.py lint draft.txt --touch 1
  outreach.py score leads.csv --rules rules.json --out scored.csv
  outreach.py capacity --contacts-per-week 600 --touches 4 --per-mailbox 25
  outreach.py funnel --deals 6 --reply 0.034 --positive 0.4 --meeting 0.6 --close 0.2
"""
import argparse
import csv
import json
import math
import re
import sys

OPENERS = ["i hope this email finds you well", "hope this finds you", "we are the leading", "the leading platform", "i hope you're well", "i hope you are well", "my name is",
           "i came across your profile", "i wanted to reach out", "quick question", "i'll be honest",
           "here's the thing", "allow me to introduce", "we are a leading", "i am reaching out"]
FOLLOWUP_BAD = ["just checking in", "bumping this", "did you see my last", "following up on my previous",
                "i never heard back", "circling back", "touching base"]
JARGON = ["synergy", "leverage", "best-in-class", "leading provider", "circle back", "world-class",
          "cutting-edge", "solution", "revolutionary", "game-changer", "unlock", "seamless"]
MEETING = [r"\b(15|20|30|45|60)[- ]?min", r"\bhop on a call\b", r"\bbook a (call|meeting|demo)\b",
           r"\bcalendar link\b", r"\bschedule a (call|meeting|demo)\b"]


def syllables(word):
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee")):
        n -= 1
    return max(1, n)


def lint(a):
    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    lines = text.strip().splitlines()
    subject = ""
    if lines and lines[0].lower().startswith("subject:"):
        subject = lines[0].split(":", 1)[1].strip()
        lines = lines[1:]
    body = "\n".join(lines).strip()
    low = body.lower()
    words = re.findall(r"[A-Za-z']+", body)
    sents = [s for s in re.split(r"(?<=[.!?])\s+", body) if re.search(r"[A-Za-z]", s)]
    issues = []
    n = len(words)
    limit = 80 if a.touch == 1 else 100
    if n > limit:
        issues.append(f"{n} words (aim 25-75; under ~{limit} for touch {a.touch})")
    if sents and words:
        grade = 0.39 * (n / len(sents)) + 11.8 * (sum(syllables(w) for w in words) / n) - 15.59
        if grade > 8:
            issues.append(f"reading grade ~{grade:.1f} (simpler reads better; aim ~5-7)")
    you = len(re.findall(r"\b(you|your|you're)\b", low))
    me = len(re.findall(r"\b(i|we|our|us|my|i'm|we're)\b", low))
    if me > you and me >= 3:  # one "I" (e.g. in the opt-out line) is fine
        issues.append(f"self-focused: I/we {me} vs you {you}")
    links = re.findall(r"https?://\S+|www\.\S+", body)
    if a.touch == 1 and links:
        issues.append("link in first touch (hurts deliverability; offer to send instead)")
    elif len(links) > 1:
        issues.append(f"{len(links)} links (max 1)")
    if re.search(r"<img|<table|<div", body, re.I):
        issues.append("HTML/images (send plain text)")
    for p in OPENERS:
        if p in low:
            issues.append(f"stock opener/phrase: '{p}'")
    for p in FOLLOWUP_BAD:
        if p in low:
            issues.append(f"weak follow-up phrase: '{p}'")
    for p in JARGON:
        if re.search(r"\b" + re.escape(p) + r"\b", low):
            issues.append(f"jargon: '{p}'")
    if a.touch == 1:
        for rx in MEETING:
            if re.search(rx, low):
                issues.append("asks for a meeting in first touch (prefer an interest question)")
                break
    if "—" in body:
        issues.append("em dash")
    qs = body.count("?")
    if qs == 0:
        issues.append("no question/CTA")
    elif qs > 2:
        issues.append(f"{qs} questions (one clear ask)")
    if not re.search(r"(reply|let me know).{0,40}(no|stop|not relevant)|unsubscribe|opt.?out|won't follow up", low):
        issues.append("no plain opt-out line (add e.g. 'If this isn't relevant, reply \"no\" and I won't follow up')")
    if subject:
        sw = subject.split()
        if re.match(r"^\s*(re|fwd?):", subject, re.I):
            issues.append("fake Re:/Fwd: subject")
        if len(sw) > 5:
            issues.append(f"subject {len(sw)} words (2-4 internal-looking words work best)")
        if any(c in subject for c in "!?$%") or re.search(r"[\U0001F300-\U0001FAFF]", subject):
            issues.append("subject punctuation/emoji")
    print(f"words={n} sentences={len(sents)} you={you} i/we={me} links={len(links)}")
    print("\n".join("- " + i for i in issues) if issues else "ok")
    return 1 if issues else 0


def score(a):
    rules = json.load(open(a.rules)) if a.rules else {
        "fit": {"industry": {"target": 20, "secondary": 10}, "size_band": {"11-50": 10, "51-200": 20, "201-1000": 15},
                "title_level": {"c-suite": 20, "vp": 20, "director": 15, "manager": 10}},
        "signal": {"signal_type": {"usage": 30, "champion_job_change": 25, "pricing_visit": 25, "new_leader": 20,
                                   "hiring": 15, "funding": 10, "tech_change": 10, "intent": 5}},
        "negative": {"email_status": {"invalid": -100, "catch-all": -10}, "disqualifier": {"yes": -100}},
        "thresholds": {"hot": 60, "warm": 35},
    }
    with open(a.file, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("no leads in file")
    th = rules.get("thresholds", {"hot": 60, "warm": 35})
    wanted = [c for g in ("fit", "signal", "negative") for c in rules.get(g, {})]
    missing = [c for c in wanted if c not in rows[0]]
    if len(missing) == len(wanted):
        sys.exit(f"none of the scoring columns are in the CSV; expected: {', '.join(wanted)} "
                 "(or pass --rules with your own column names)")
    if missing:
        print(f"note: columns not in CSV, scored as 0: {', '.join(missing)}", file=sys.stderr)
    for r in rows:
        total = 0
        for group in ("fit", "signal", "negative"):
            for col, table in rules.get(group, {}).items():
                # several values in one cell ("hiring; pricing_visit") each add their points
                for v in re.split(r"[;|]", r.get(col) or ""):
                    total += table.get(v.strip().lower(), 0)
        r["points"] = total
        r["grade"] = "Skip" if total < 0 else "Hot" if total >= th["hot"] else "Warm" if total >= th["warm"] else "Cold"
    rows.sort(key=lambda r: -r["points"])
    counts = {}
    for r in rows:
        counts[r["grade"]] = counts.get(r["grade"], 0) + 1
        print(f"{r['grade']:<5} {r['points']:>4}  {r.get('company', r.get('name', ''))}")
    print("\n" + ", ".join(f"{k}={v}" for k, v in counts.items()), "(typical target ~20% Hot, ~30% Warm)")
    if a.out:
        with open(a.out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {a.out}")


def capacity(a):
    emails_week = a.contacts_per_week * a.touches
    per_day = emails_week / a.days
    mailboxes = math.ceil(per_day / a.per_mailbox)
    domains = math.ceil(mailboxes / a.mailboxes_per_domain)
    print(f"{a.contacts_per_week} new contacts/week × {a.touches} touches ≈ {emails_week:,} emails/week "
          f"({per_day:,.0f}/sending day at steady state)")
    print(f"mailboxes needed: {mailboxes} at {a.per_mailbox}/day each; domains: {domains} at {a.mailboxes_per_domain} per domain")
    print(f"add ~20-30% spare mailboxes for rotation/rest; warm 3-4 weeks before cold sends (start 5-10/day).")


def funnel(a):
    per_meeting = 1 / (a.reply * a.positive * a.meeting)
    meetings = a.deals / a.close if a.deals else a.meetings
    contacts = meetings * per_meeting
    print(f"contacts per meeting: {per_meeting:,.0f} (reply {a.reply:.1%} × positive {a.positive:.0%} × booked {a.meeting:.0%})")
    if a.deals:
        print(f"{a.deals} deals at {a.close:.0%} close → {meetings:,.0f} meetings → {contacts:,.0f} contacts")
    else:
        print(f"{meetings:,.0f} meetings → {contacts:,.0f} contacts")
    if a.acv and a.deals:
        print(f"pipeline value: {a.deals * a.acv:,.0f}; revenue per contacted account: {a.deals * a.acv / contacts:,.2f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = ap.add_subparsers(dest="cmd", required=True)
    p = s.add_parser("lint"); p.add_argument("file"); p.add_argument("--touch", type=int, default=1); p.set_defaults(f=lint)
    p = s.add_parser("score"); p.add_argument("file"); p.add_argument("--rules"); p.add_argument("--out"); p.set_defaults(f=score)
    p = s.add_parser("capacity"); p.add_argument("--contacts-per-week", type=int, required=True)
    p.add_argument("--touches", type=int, default=4); p.add_argument("--per-mailbox", type=int, default=25)
    p.add_argument("--mailboxes-per-domain", type=int, default=3); p.add_argument("--days", type=int, default=5)
    p.set_defaults(f=capacity)
    p = s.add_parser("funnel"); p.add_argument("--reply", type=float, default=0.034); p.add_argument("--positive", type=float, default=0.4)
    p.add_argument("--meeting", type=float, default=0.6); p.add_argument("--close", type=float, default=0.2)
    p.add_argument("--deals", type=float, default=0); p.add_argument("--meetings", type=float, default=10)
    p.add_argument("--acv", type=float, default=0); p.set_defaults(f=funnel)
    a = ap.parse_args()
    try:
        sys.exit(a.f(a) or 0)
    except FileNotFoundError as e:
        sys.exit(f"cannot read {e.filename}: no such file")
    except json.JSONDecodeError as e:
        sys.exit(f"rules file is not valid JSON: {e}")


if __name__ == "__main__":
    main()
