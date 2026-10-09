#!/usr/bin/env python3
"""Check an internal message against its format before it goes out.

Usage:
  comms_check.py draft.md --type 3p|newsletter|faq|status|leadership|incident|announcement|general
                 [--channel slack|email|doc] [--json]

Common checks (every type):
  read-time      estimated reading time (230 wpm) vs the type's budget
  bottom-line    the first line/sentence should carry the status, decision or ask
  ask            a request without an owner or a date ("please review" -> who, by when?)
  relative-date  "tomorrow", "next Friday", "EOD" without an absolute date (readers are in other weeks/zones)
  time-zone      clock times without a zone
  acronym        ALL-CAPS terms never expanded
  vague          activity words without outcomes ("worked on", "made progress", "various")
  placeholder    [..], TBD, TODO, XXX left in
  channel        Slack: **double asterisks** don't bold in Slack mrkdwn; very long paragraphs; email: missing subject line
Type checks:
  3p          header "<emoji> <Team> (<dates>)", exactly Progress/Plans/Problems lines, 1-3 sentences each, numbers present
  newsletter  ~20-25 bullets, sections with headers, bullets <= 2 sentences, links present, "we" voice
  faq         Question/Answer pairs, answers <= 3 sentences, uncertain answers flagged, sources linked
  status      a Status: On track | At risk | Off track line, risks with impact and help needed
  leadership  <= 3 headline bullets before detail, a decisions/asks section
  incident    Impact, Timeline (timestamps with zone), Root cause, Resolution, Action items (owner + date); blame wording
  announcement  what / why / who is affected / when / what to do / where to ask
Exit 1 if any ERROR.
"""
import argparse, json, re, sys
from pathlib import Path

BUDGET = {"3p": 60, "newsletter": 240, "faq": 300, "status": 120, "leadership": 90, "incident": 300, "announcement": 120, "general": 120}
REL = re.compile(r"\b(today|tonight|tomorrow|yesterday|this (week|weekend|month)|next (week|month|monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
                 r"last (week|month|monday|tuesday|wednesday|thursday|friday)|EOD|EOW|end of (day|week)|soon|ASAP)\b", re.I)
ABS_DATE = re.compile(r"\b(\d{4}-\d{2}-\d{2}|\d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}|\d{1,2}/\d{1,2})\b")
TIME = re.compile(r"\b([01]?\d|2[0-3])(:[0-5]\d)\s*(am|pm)?\b|\b(1[0-2]|[1-9])\s*(am|pm)\b", re.I)
ZONE = re.compile(r"\b(UTC|GMT|IST|PT|PST|PDT|ET|EST|EDT|CET|CEST|BST|JST|SGT|AEST|AEDT|[+-]\d{2}:?\d{2})\b|\bZ\b")
VAGUE = re.compile(r"\b(worked on|working on|made progress|various|some progress|continued to|looked into|synced on|aligned on|touched base)\b", re.I)
ASK = re.compile(r"\b(please|can you|could you|need (you|your|someone|a decision|approval|help)|we need|asking for|requesting|action required|we're asking)\b", re.I)
OWNER = re.compile(r"@\w+|\b[A-Z][a-z]+ [A-Z][a-z]+\b|\b(?i:owner|assignee|DRI)\s*:|\((?:asked|owner:?) [A-Z][a-z]+")
PH = re.compile(r"\[[^\]]*\.\.\.?[^\]]*\]|\[(insert|link|name|date|tbd)[^\]]*\]|\bTBD\b|\bTODO\b|\bXXX\b", re.I)
BLAME = re.compile(r"\b(fault|blame|careless|negligen\w*|should have known|human error|screwed up|incompetent)\b", re.I)
# a named person as the subject of a mistake: "John forgot to run the migration"
PERSON_ERR = re.compile(r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)? (forgot|missed|failed to|didn't|did not|neglected|broke|ignored|messed up)\b")
COMMON_ACR = {"API", "URL", "FAQ", "CEO", "CTO", "CFO", "COO", "VP", "HR", "PR", "QA", "ETA", "UTC", "GMT", "IST", "PST", "PDT", "EST", "EDT",
              "CET", "BST", "OKR", "KPI", "SLA", "SLO", "TBD", "TODO", "EOD", "EOW", "ASAP", "USD", "EUR", "INR", "GBP", "ARR", "MRR", "NPS",
              "Q1", "Q2", "Q3", "Q4", "H1", "H2", "AI", "UI", "UX", "iOS", "PDF", "CSV", "SQL", "AWS", "GCP", "RCA", "DRI", "WIP"}


def sentences(text):
    t = re.sub(r"\s+", " ", re.sub(r"https?://\S+", "URL", text))
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(:])", t.strip()) if s.strip()]


def words(text):
    return len(re.findall(r"[A-Za-z0-9][\w'’-]*", re.sub(r"https?://\S+", "", text)))


class Checker:
    def __init__(self, text, kind, channel):
        self.t, self.kind, self.ch = text, kind, channel
        self.lines = text.splitlines()
        self.issues = []

    def add(self, lvl, code, msg, line=None):
        self.issues.append({"level": lvl, "code": code, "line": line, "message": msg})

    def common(self):
        t = self.t
        w = words(t)
        secs = round(w / 230 * 60)
        budget = BUDGET[self.kind]
        self.read = (w, secs)
        if secs > budget * 1.25:
            self.add("ERROR" if self.kind == "3p" else "WARN", "read-time", f"~{secs}s to read ({w} words); budget for {self.kind} is ~{budget}s")
        for i, line in enumerate(self.lines, 1):
            for m in PH.finditer(line):
                self.add("ERROR", "placeholder", f"left in: {m.group(0)}", i)
            for m in REL.finditer(line):
                if not ABS_DATE.search(line):
                    self.add("WARN", "relative-date", f"'{m.group(0)}' without an absolute date; add one (e.g. 'Fri 16 Oct')", i)
            if TIME.search(re.sub(r"https?://\S+", "", line)) and not ZONE.search(line):
                self.add("WARN", "time-zone", f"time without a zone: {TIME.search(line).group(0).strip()}", i)
            for m in VAGUE.finditer(line):
                self.add("WARN", "vague", f"'{m.group(0)}' describes activity; state the outcome or number", i)
            if ASK.search(line) and not (OWNER.search(line) or ABS_DATE.search(line) or REL.search(line)):
                self.add("WARN", "ask", "request without a named owner or a date", i)
        expanded = set(re.findall(r"\(([A-Z][A-Z0-9]{1,}s?)\)", t))
        for acr in sorted(set(re.findall(r"\b[A-Z][A-Z0-9]{2,}\b", t)) - COMMON_ACR - expanded):
            if not re.fullmatch(r"[A-Z]+-\d+|\d+", acr):
                self.add("WARN", "acronym", f"{acr} is never expanded; spell it out once for readers outside the team")
        if self.ch == "slack":
            if "**" in t:
                self.add("WARN", "channel", "Slack bolds with *single* asterisks; **double** shows literally in many clients")
            for i, para in enumerate(re.split(r"\n\s*\n", t), 1):
                if words(para) > 90 and not re.search(r"^\s*[-*•]", para, re.M):
                    self.add("WARN", "channel", f"paragraph {i} is {words(para)} words; break it up or use bullets for chat")
        if self.ch == "email" and not re.match(r"^\s*(subject|title)\s*:", t, re.I):
            self.add("WARN", "channel", "no 'Subject:' line; the subject is the first thing read, so make it carry the point")

    def bottom_line(self):
        subj = next((re.sub(r"^\s*subject\s*:\s*", "", l, flags=re.I) for l in self.lines if re.match(r"^\s*subject\s*:", l, re.I)), None)
        first = subj or next((l.strip() for l in self.lines if l.strip() and not re.match(r"^\s*(to|cc)\s*:", l, re.I)
                              and not re.match(r"^\W*(tl;?dr|summary|bottom line)\W*$", l, re.I)), "")
        first = re.sub(r"^[#*>\s]+", "", first)
        if self.kind in ("status", "leadership", "announcement", "general", "incident") and words(first) < 4:
            self.add("WARN", "bottom-line", f"first line '{first[:40]}' is a label; lead with the status, decision or ask")

    # ---- per type
    def t_3p(self):
        body = [l for l in self.lines if l.strip()]
        if not body:
            return self.add("ERROR", "3p", "empty")
        head = body[0]
        if not re.match(r"^\s*(\S+)\s+.+\(.+\)\s*$", head) or re.match(r"^\s*(progress|plans|problems)\b", head, re.I):
            self.add("ERROR", "3p-header", "first line must be '<emoji> <Team name> (<dates covered>)'", 1)
        elif not re.match(r"^\s*(:[a-z0-9_+-]+:|[^\w\s(])", head):
            self.add("ERROR", "3p-header", "header must start with an emoji", 1)
        elif not ABS_DATE.search(head):
            self.add("WARN", "3p-header", "dates in the header should be absolute, e.g. (Oct 1-7)", 1)
        labels = []
        for i, l in enumerate(body[1:], 2):
            m = re.match(r"^\s*\*{0,2}(Progress|Plans|Problems)\*{0,2}\s*:\s*(.*)$", l, re.I)
            if not m:
                self.add("ERROR", "3p-format", f"unexpected line (only Progress/Plans/Problems lines allowed): {l[:50]!r}", i)
                continue
            labels.append(m.group(1).capitalize())
            n = len(sentences(m.group(2)))
            if n == 0:
                self.add("ERROR", "3p-format", f"{m.group(1)} is empty (write 'None this week' if so)", i)
            elif n > 3:
                self.add("ERROR", "3p-length", f"{m.group(1)} has {n} sentences; 1-3 allowed", i)
            if m.group(1).lower() == "progress" and not re.search(r"\d", m.group(2)):
                self.add("WARN", "3p-data", "Progress has no number; add a metric where one exists", i)
        if labels != ["Progress", "Plans", "Problems"]:
            self.add("ERROR", "3p-format", f"sections must be Progress, Plans, Problems in that order (found {labels})")

    def t_newsletter(self):
        bullets = [(i, l) for i, l in enumerate(self.lines, 1) if re.match(r"^\s*[-*•]\s+", l)]
        heads = [l for l in self.lines if re.match(r"^\s*(#+\s|:[a-z_]+:|[^\w\s-]{1,3}\s+\S)", l) and not re.match(r"^\s*[-*•]", l)]
        if not 15 <= len(bullets) <= 30:
            self.add("WARN", "newsletter-length", f"{len(bullets)} bullets; aim for about 20-25")
        if len(heads) < 3:
            self.add("WARN", "newsletter-sections", "fewer than 3 section headers; group bullets by area")
        for i, l in bullets:
            if len(sentences(re.sub(r"^\s*[-*•]\s+", "", l))) > 2:
                self.add("WARN", "newsletter-bullet", "bullet over 2 sentences", i)
        links = len(re.findall(r"https?://|<[^>]+\|[^>]+>|\]\(", self.t))
        if links < max(3, len(bullets) // 4):
            self.add("WARN", "newsletter-links", f"only {links} links; link the source doc/announcement for major items")
        if not re.search(r"\b(we|our|we're|we've)\b", self.t, re.I):
            self.add("WARN", "newsletter-voice", "no 'we' voice; the newsletter speaks as the company")

    def t_faq(self):
        qs = [(i, l) for i, l in enumerate(self.lines, 1) if re.match(r"^\s*[-*]?\s*\*{0,2}_?Q(uestion)?_?\*{0,2}\s*[:.]", l, re.I)]
        ans = [(i, l) for i, l in enumerate(self.lines, 1) if re.match(r"^\s*[-*]?\s*\*{0,2}_?A(nswer)?_?\*{0,2}\s*[:.]", l, re.I)]
        if not qs:
            self.add("ERROR", "faq-format", "no 'Question:' lines found")
        if len(qs) != len(ans):
            self.add("ERROR", "faq-format", f"{len(qs)} questions but {len(ans)} answers")
        for i, l in ans:
            n = len(sentences(re.sub(r"^.*?:\s*", "", l, count=1)))
            if n > 3:
                self.add("WARN", "faq-answer", f"answer has {n} sentences; 1-2 plus a link is easier to scan", i)
            if re.search(r"\b(probably|likely|we think|might|unclear|not yet (decided|confirmed)|unconfirmed)\b", l, re.I) and not re.search(r"\b(not (yet )?confirmed|unconfirmed|to be confirmed|we'll update|tbc)\b", l, re.I):
                self.add("WARN", "faq-uncertain", "uncertain answer; say plainly it is unconfirmed and when an answer is expected", i)
            if not re.search(r"https?://|\]\(|<[^>]+\|", l) and not re.search(r"\b(see|source|per)\b", l, re.I):
                self.add("WARN", "faq-source", "no source linked for this answer", i)

    def t_status(self):
        if not re.search(r"^\s*\*{0,2}status\*{0,2}\s*:\s*\*{0,2}(on track|at risk|off track|done|blocked)", self.t, re.I | re.M):
            self.add("ERROR", "status-line", "missing 'Status: On track | At risk | Off track' line")
        if re.search(r"(at risk|off track|blocked)", self.t, re.I) and not re.search(r"\b(help|need|ask|decision)\b", self.t, re.I):
            self.add("WARN", "status-help", "at risk/off track without saying what help is needed")
        if not re.search(r"\d", self.t):
            self.add("WARN", "status-metrics", "no numbers; add the key metric vs target")

    def t_leadership(self):
        bullets_top = 0
        for l in self.lines:
            if re.match(r"^\s*#{1,3}\s", l) and bullets_top:
                break
            if re.match(r"^\s*[-*•]\s+", l):
                bullets_top += 1
        if bullets_top > 5:
            self.add("WARN", "leadership-top", f"{bullets_top} bullets before the first section; keep the headline to 3")
        if not re.search(r"\b(decision|decide|approve|ask|need from you|input needed)\b", self.t, re.I):
            self.add("WARN", "leadership-ask", "no decisions or asks section; say what you need from leadership, or 'no decisions needed'")

    def t_incident(self):
        for sec in ("impact", "timeline", "root cause", "resolution", "action items"):
            if not re.search(rf"^\s*(#+\s*|\*\*)?{sec}", self.t, re.I | re.M):
                self.add("ERROR", "incident-sections", f"missing section: {sec.title()}")
        tl = re.search(r"timeline(.*?)(^\s*#+|\Z)", self.t, re.I | re.S | re.M)
        if tl and TIME.search(tl.group(1)) and not ZONE.search(tl.group(1)):
            self.add("ERROR", "incident-zone", "timeline times have no time zone")
        ai = re.search(r"action items(.*?)(^\s*#+|\Z)", self.t, re.I | re.S | re.M)
        if ai:
            for l in ai.group(1).splitlines():
                if re.match(r"^\s*[-*|]\s*\S", l) and not re.match(r"^\s*\|\s*-", l) and not re.search(r"owner", l, re.I):
                    if not (OWNER.search(l) and ABS_DATE.search(l)):
                        self.add("WARN", "incident-actions", f"action item without owner and due date: {l.strip()[:60]}")
        for i, l in enumerate(self.lines, 1):
            hit = BLAME.search(l) or PERSON_ERR.search(l)
            if hit:
                self.add("WARN", "incident-blame", f"'{hit.group(0)}': describe what the system allowed, not who erred", i)

    def t_announcement(self):
        need = {"what changes": r"\b(changing|change|will|new|starting|launch|moving|replac)", "why": r"\b(because|so that|why|to (reduce|improve|make|give|help))\b",
                "who is affected": r"\b(you|everyone|teams?|all|anyone|customers|employees|if you)\b", "when": ABS_DATE.pattern,
                "what to do": r"\b(please|you('ll)? need to|action|no action|do nothing|what to do|sign up|register|update)\b",
                "where to ask": r"(#[\w-]+|\bquestions?\b|\bask\b|\breach out\b|\bcontact\b)"}
        for k, pat in need.items():
            if not re.search(pat, self.t, re.I):
                self.add("WARN", "announcement", f"doesn't say {k}")

    def t_general(self):
        pass

    def run(self):
        self.common()
        self.bottom_line()
        getattr(self, "t_" + self.kind)()
        return self.issues


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("draft")
    ap.add_argument("--type", required=True, choices=list(BUDGET))
    ap.add_argument("--channel", choices=["slack", "email", "doc"], default="doc")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.draft != "-" and not Path(a.draft).is_file():
        print(f"comms_check.py: no such file: {a.draft}", file=sys.stderr); sys.exit(2)
    text = Path(a.draft).read_text(encoding="utf-8") if a.draft != "-" else sys.stdin.read()
    c = Checker(text, a.type, a.channel)
    issues = c.run()
    if a.json:
        print(json.dumps({"words": c.read[0], "read_seconds": c.read[1], "issues": issues}, indent=2))
    else:
        for i in issues:
            loc = f"{a.draft}:{i['line']}" if i["line"] else a.draft
            print(f"{loc}: {i['level']} {i['code']} {i['message']}")
        print(f"{c.read[0]} words, ~{c.read[1]}s read; {sum(i['level'] == 'ERROR' for i in issues)} error(s), {sum(i['level'] == 'WARN' for i in issues)} warning(s)")
    sys.exit(1 if any(i["level"] == "ERROR" for i in issues) else 0)


if __name__ == "__main__":
    main()
