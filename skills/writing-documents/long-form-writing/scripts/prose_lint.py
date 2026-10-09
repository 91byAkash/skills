#!/usr/bin/env python3
"""Style lint for prose (Markdown or plain text), terse file:line output.

  prose_lint.py FILE... [--only rule,rule] [--skip rule,rule] [--max-words 30] [--json] [--strict]

Output: path:line:col: severity rule: message  [suggestion]
Severities: fix (almost always wrong: doubled word, placeholder, 'click here', broken emphasis),
            style (usually better changed), note (judgement call: worth a look).
Skips frontmatter, fenced code, indented code, inline code, URLs, HTML comments, and table separator rows.
Exit 1 if any 'fix' finding (or any finding at all with --strict).

Rules: doubled, placeholder, click-here, filler, hedge, intensifier, ai-phrase, throat-clear, empty-close,
       not-x-but-y, long-sentence, passive, em-dash, exclaim, weasel, triad, nominal, sentence-start,
       heading-case, repeat-word
"""
import argparse, json, re, sys
from pathlib import Path

W = r"\b"
FILLER = {"basically": "", "actually": "", "really": "", "just": "", "simply": "", "literally": "",
          "in order to": "to", "due to the fact that": "because", "at this point in time": "now", "at the end of the day": "",
          "it is important to note that": "", "it's important to note that": "", "it is worth noting that": "", "it's worth noting that": "",
          "needless to say": "", "the fact that": "that", "for all intents and purposes": "", "in terms of": "for/in",
          "a number of": "some/several (or the number)", "the vast majority of": "most", "has the ability to": "can", "is able to": "can",
          "in the event that": "if", "with regard to": "about", "on a daily basis": "daily", "prior to": "before", "make use of": "use"}
HEDGE = ["somewhat", "arguably", "perhaps", "it seems that", "it appears that", "sort of", "kind of", "more or less", "to some extent",
         "in a sense", "i think that", "i believe that", "may potentially", "could potentially", "might possibly", "relatively"]
INTENS = ["very", "extremely", "incredibly", "super", "totally", "absolutely", "truly", "highly", "deeply", "hugely"]
AI = {"delve": "look at / dig into", "delves": "looks at", "tapestry": "mix", "testament to": "shows", "in today's fast-paced": "(cut)",
      "ever-evolving": "changing", "ever-changing": "changing", "landscape": "field / market (or name it)", "realm": "area", "navigate the": "handle the",
      "unlock": "enable / allow", "unleash": "use", "harness": "use", "leverage": "use", "seamless": "smooth (or say what doesn't break)",
      "seamlessly": "(cut or be specific)", "robust": "(say what it withstands)", "cutting-edge": "new (or name it)", "game-changer": "(say what changed)",
      "game-changing": "(say what changed)", "elevate": "improve", "empower": "let", "embark": "start", "journey": "process (or cut)",
      "paradigm": "model", "synergy": "(cut)", "holistic": "whole / complete", "pivotal": "key", "crucial": "important (or say why)",
      "vibrant": "(cut)", "bustling": "(cut)", "meticulous": "careful", "meticulously": "carefully", "underscore": "show", "underscores": "shows",
      "showcase": "show", "showcases": "shows", "foster": "encourage", "fosters": "encourages", "intricate": "complex", "nuanced": "(say the nuance)",
      "let's dive in": "(cut)", "dive into": "look at", "deep dive": "close look", "buckle up": "(cut)", "in the world of": "in",
      "when it comes to": "for", "a myriad of": "many", "plethora": "many", "stands as": "is", "serves as": "is", "boasts": "has",
      "commendable": "(cut)", "invaluable": "useful (or say how)", "moreover": "also (or cut)", "furthermore": "also (or cut)"}
THROAT = [r"^in this (article|post|guide|piece|section),? (we|i)('ll| will)", r"^(this|the following) (article|post|guide) (will|aims to)",
          r"^(let's|let us) (take a look|explore|dive|discuss)", r"^(have you ever (wondered|thought))", r"^i wanted to (share|write|talk)",
          r"^as (we all know|everyone knows)", r"^imagine (a world|this)"]
CLOSE = [r"^in conclusion", r"^to (sum up|summarize|summarise|conclude)", r"^in summary", r"^all in all", r"^ultimately,", r"^at the end of the day",
         r"^overall,", r"^the bottom line is"]
WEASEL = [r"\bmany (people|experts|developers|users) (say|believe|think|agree)", r"\bit is (widely|generally|often) (said|believed|known|accepted)",
          r"\bstudies (show|have shown)\b", r"\bsome (say|argue|would argue)\b", r"\bexperts (agree|say)\b", r"\beveryone knows\b"]
NOT_X = [r"\b(it'?s|this is|that'?s|isn'?t|is) not (just |only |merely )?(about )?[^.;:!?]{1,50}[,;—–-]+\s*(it'?s|but|this is|that'?s)\b",
         r"\bnot (just|only|merely) [^.;!?]{1,50},? but( also)?\b", r"\bisn'?t (just |only )?[^.;!?]{1,40}[—–-]\s*it'?s\b",
         r"\bless about [^.;!?]{1,40} and more about\b"]
NOMINAL = {"make a decision": "decide", "give consideration to": "consider", "conduct an investigation": "investigate",
           "perform an analysis": "analyse", "provide assistance": "help", "reach a conclusion": "conclude", "make an improvement": "improve",
           "take into consideration": "consider", "have a discussion": "discuss", "come to an agreement": "agree", "make a recommendation": "recommend"}
IRREG = "been|done|gone|seen|made|known|shown|given|taken|written|built|found|held|kept|left|lost|paid|put|read|run|said|sent|set|sold|spent|told|thought|understood|won|chosen|driven|broken|hidden|drawn|grown|thrown|forgotten|begun|caught|bought|brought|taught|felt|meant|met|led|cut|hit|let|shut|split|spread"
PASSIVE = re.compile(rf"\b(am|is|are|was|were|be|been|being|is being|are being|was being|were being)\s+(?:(?:\w+ly|never|not|also|always|often|rarely|already|still|then|all|both)\s+)?(\w+ed|{IRREG})\b(?!\s+(?:to|that)\b)", re.I)
NOT_PASSIVE_ADJ = {"interested", "tired", "excited", "bored", "pleased", "worried", "concerned", "used", "supposed", "based", "related", "involved",
                   "required", "needed", "located", "married", "prepared", "done", "experienced", "advanced", "detailed", "limited", "complicated",
                   "allowed", "expected", "focused", "aligned", "skilled", "talented", "red", "bed", "need", "seed", "feed", "speed", "shed", "ted"}
PH = re.compile(r"\b(TODO|TK|TBD|FIXME|XXX|lorem ipsum)\b|\[(insert|add|link|citation needed|cite|todo)[^\]]*\]", re.I)


def strip_inline(s):
    s = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), s)
    s = re.sub(r"<!--.*?-->", lambda m: " " * len(m.group(0)), s)
    s = re.sub(r"\]\([^)]*\)", lambda m: "]" + " " * (len(m.group(0)) - 1), s)
    s = re.sub(r"https?://\S+", lambda m: " " * len(m.group(0)), s)
    return s


def prose_lines(text):
    """Yield (lineno, text, kind) for lines that are prose. kind: heading|prose."""
    in_code = False; fm = False
    lines = text.splitlines()
    for i, l in enumerate(lines, 1):
        if i == 1 and l.strip() == "---":
            fm = True; continue
        if fm:
            if l.strip() in ("---", "..."):
                fm = False
            continue
        if re.match(r"^\s*(```|~~~)", l):
            in_code = not in_code; yield i, "", "break"; continue
        if not in_code and not l.strip():
            yield i, "", "break"; continue
        if in_code or re.match(r"^( {4}|\t)\S", l) or re.match(r"^\s*\|?\s*:?-{3,}", l):
            continue
        if re.match(r"^\s*<!--", l):
            continue
        kind = "heading" if re.match(r"^\s*#{1,6}\s", l) else "prose"
        yield i, strip_inline(l), kind


def sentence_spans(paragraph_lines):
    """paragraph_lines: list of (lineno, text). Returns list of (start_line, sentence)."""
    joined, starts = "", []
    for ln, t in paragraph_lines:
        starts.append((len(joined), ln)); joined += t.strip() + " "
    out = []
    for m in re.finditer(r"[^.!?]+(?:[.!?]+[\"')\]]*|$)", joined):
        s = m.group(0).strip()
        if not s:
            continue
        ln = max(l for off, l in starts if off <= m.start() + (len(m.group(0)) - len(m.group(0).lstrip())))
        out.append((ln, s))
    return out


def lint(path, text, a):
    F = []

    def add(ln, col, sev, rule, msg, sug=""):
        if (a.only and rule not in a.only) or rule in a.skip:
            return
        F.append({"file": str(path), "line": ln, "col": col + 1, "severity": sev, "rule": rule, "message": msg, "suggestion": sug})

    paras, cur, headings = [], [], []
    words_total = 0
    for ln, t, kind in prose_lines(text):
        if kind == "break":
            if cur: paras.append(cur); cur = []
            continue
        if kind == "heading":
            headings.append((ln, re.sub(r"^\s*#+\s*", "", t).strip()))
            if cur: paras.append(cur); cur = []
            continue
        body = re.sub(r"^\s*([-*+]|\d+[.)])\s+", "", t)
        if re.match(r"^\s*([-*+]|\d+[.)]|>|\|)", t) and cur:
            paras.append(cur); cur = []
        cur.append((ln, body))
        words_total += len(body.split())
        low = t.lower()
        for m in re.finditer(r"\b(\w+)\s+\1\b", t, re.I):
            if m.group(1).lower() not in ("that", "had", "is", "very", "bye", "ha", "no", "so"):
                add(ln, m.start(), "fix", "doubled", f"doubled word '{m.group(0)}'", m.group(1))
        for m in PH.finditer(t):
            add(ln, m.start(), "fix", "placeholder", f"placeholder left in: {m.group(0)}")
        for m in re.finditer(r"\[(click )?here\]|\bclick here\b|\[(this|link|this link)\]", t, re.I):
            add(ln, m.start(), "fix", "click-here", "link text should say where it goes", "[descriptive text](url)")
        for phrase, rep in FILLER.items():
            for m in re.finditer(W + re.escape(phrase) + W, low):
                add(ln, m.start(), "style", "filler", f"'{phrase}' adds nothing", rep or "(cut)")
        for h in HEDGE:
            for m in re.finditer(W + re.escape(h) + W, low):
                add(ln, m.start(), "note", "hedge", f"hedge '{h}': commit, or say what you're unsure of", "(cut or be specific)")
        for w_ in INTENS:
            for m in re.finditer(W + w_ + r"\s+(\w+)", low):
                add(ln, m.start(), "note", "intensifier", f"'{m.group(0)}': use a stronger word or a number")
        for phrase, rep in AI.items():
            for m in re.finditer(W + re.escape(phrase) + W, low):
                add(ln, m.start(), "style", "ai-phrase", f"stock phrase '{phrase}'", rep)
        for phrase, rep in NOMINAL.items():
            verb, rest = phrase.split(" ", 1)
            forms = {"make": "make|makes|made|making", "give": "give|gives|gave|giving", "conduct": "conducts?|conducted|conducting",
                     "perform": "performs?|performed|performing", "provide": "provides?|provided|providing", "reach": "reach|reaches|reached|reaching",
                     "take": "take|takes|took|taking", "have": "have|has|had|having", "come": "come|comes|came|coming"}.get(verb, verb)
            for m in re.finditer(rf"\b(?:{forms}) {re.escape(rest)}\b", low):
                add(ln, m.start(), "style", "nominal", f"'{m.group(0)}' hides the verb", rep)
        for pat in WEASEL:
            for m in re.finditer(pat, low):
                add(ln, m.start(), "style", "weasel", f"unsourced appeal '{m.group(0)}': cite it or own the claim")
        n_dash = t.count("—") + len(re.findall(r"\s--\s|\s–\s", t))
        if n_dash >= 2:
            add(ln, t.find("—") if "—" in t else 0, "style", "em-dash", f"{n_dash} dashes on one line; use commas, parentheses, or two sentences")
        for m in re.finditer(r"!+", t):
            if not re.match(r"^\s*!\[", t[m.start():]) and kind == "prose":
                add(ln, m.start(), "note", "exclaim", "exclamation mark: let the content carry the energy"); break
    if cur: paras.append(cur)

    em_total = sum(t.count("—") for _, t, k in prose_lines(text) if k != "break")
    if words_total >= 250 and em_total / max(words_total, 1) * 1000 > a.dash_per_1k:
        add(None, 0, "style", "em-dash", f"{em_total} em dashes in {words_total} words (> {a.dash_per_1k}/1000); vary the punctuation")

    starts = []
    for para in paras:
        sents = sentence_spans(para)
        for idx, (ln, s) in enumerate(sents):
            low = s.lower()
            n = len(s.split())
            if n > a.max_words:
                add(ln, 0, "style", "long-sentence", f"{n} words; split it (limit {a.max_words})")
            for m in PASSIVE.finditer(s):
                if m.group(2).lower() not in NOT_PASSIVE_ADJ:
                    add(ln, 0, "note", "passive", f"passive '{m.group(0)}': who does it?")
            for pat in NOT_X:
                if re.search(pat, low):
                    add(ln, 0, "style", "not-x-but-y", "'not X, but Y' framing: state Y directly"); break
            if idx == 0 and any(re.search(p, low) for p in THROAT):
                add(ln, 0, "style", "throat-clear", "warm-up opener: start with the point")
            if any(re.search(p, low) for p in CLOSE):
                add(ln, 0, "style", "empty-close", "summary signpost: end on the last real point, or make the summary earn its place")
            if re.search(r"\b(a|an|the|is|are|was|were) (\w+), (\w+),? and (\w+)\b", low):
                add(ln, 0, "note", "triad", "three stacked descriptors: keep the one that matters")
            fw = re.match(r"\W*(\w+)", s)
            starts.append((ln, fw.group(1).lower() if fw else ""))
    run_flagged = -1
    for i in range(2, len(starts)):
        if i - 1 == run_flagged and starts[i][1] == starts[i - 1][1]:
            run_flagged = i; continue
        if starts[i][1] and starts[i][1] == starts[i - 1][1] == starts[i - 2][1] and starts[i][1] not in ("the", "a"):
            run_flagged = i
            add(starts[i][0], 0, "note", "sentence-start", f"three sentences in a row start with '{starts[i][1]}'")

    styles = []
    for ln, h in headings:
        ws = [w for w in re.findall(r"[A-Za-z][\w'-]*", h)]
        if len(ws) < 3:
            continue
        small = {"a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "with", "vs", "by", "at", "is"}
        tc = all(w[0].isupper() for w in ws[1:] if w.lower() not in small)
        styles.append((ln, "title" if tc else "sentence"))
    if styles and len({s for _, s in styles}) > 1:
        major = max(("title", "sentence"), key=lambda k: sum(1 for _, s in styles if s == k))
        for ln, s in styles:
            if s != major:
                add(ln, 0, "note", "heading-case", f"heading in {s} case; others use {major} case")

    for para in paras:
        text_p = " ".join(t for _, t in para)
        wl = [w.lower() for w in re.findall(r"[A-Za-z]+", text_p)]
        seen = {}
        for i, w in enumerate(wl):
            if len(w) < 6:
                continue
            if w in seen and i - seen[w] <= 12 and w not in ("should", "because", "before", "people", "something"):
                add(para[0][0], 0, "note", "repeat-word", f"'{w}' repeated within a few words"); seen[w] = 10 ** 9
            else:
                seen.setdefault(w, i)
    return F, words_total


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--only", default="")
    ap.add_argument("--skip", default="")
    ap.add_argument("--max-words", type=int, default=30)
    ap.add_argument("--dash-per-1k", type=float, default=4.0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    a.only = set(filter(None, a.only.split(","))); a.skip = set(filter(None, a.skip.split(",")))
    allf, words = [], 0
    for f in a.files:
        p = Path(f)
        if not p.is_file():
            print(f"prose_lint.py: no such file: {f}", file=sys.stderr); sys.exit(2)
        fs, w = lint(p, p.read_text(encoding="utf-8"), a)
        allf += sorted(fs, key=lambda x: (x["line"] or 0, x["col"])); words += w
    if a.json:
        print(json.dumps(allf, indent=2))
    else:
        for x in allf:
            loc = f"{x['file']}:{x['line']}:{x['col']}" if x["line"] else x["file"]
            print(f"{loc}: {x['severity']} {x['rule']}: {x['message']}" + (f"  [{x['suggestion']}]" if x["suggestion"] else ""))
        c = {s: sum(1 for x in allf if x["severity"] == s) for s in ("fix", "style", "note")}
        print(f"{words} words; fix={c['fix']} style={c['style']} note={c['note']}")
    sys.exit(1 if any(x["severity"] == "fix" for x in allf) or (a.strict and allf) else 0)


if __name__ == "__main__":
    main()
