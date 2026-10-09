#!/usr/bin/env python3
"""Lint marketing copy for machine-sounding patterns, weak wording and readability.

Reads a text or Markdown file (or stdin with '-'). Lines starting with '#' are
treated as headings (short copy); everything else as body copy. Reports each
hit with its line number, then a summary: Flesch reading ease, average sentence
length, you/we ratio, and counts by category.

This is a flagging tool, not a judge. A hit means "look again", and the fix is
to rewrite from the facts (number, name, mechanism, step), not to swap synonyms.

Usage
  copy_lint.py page.md
  copy_lint.py page.md --short        # treat every line as short copy (ads, subject lines)
  copy_lint.py page.md --json
  copy_lint.py --vocab                # print the cliché vocabulary block used in ai-tells.md
"""
import argparse
import json
import re
import sys

# Cliché vocabulary, grouped by what each group does to a sentence. "never" groups are flagged on every
# hit; "limit" groups are tolerated once and flagged as a buzzword-stack when two share a line.
# ai-tells.md section D must list exactly these entries: `copy_lint.py --vocab` prints the block to paste.
# Single words also match their common inflections (unlocks, elevated, seamlessly); hyphens match spaces.
WORD_GROUPS = {
    "hype-verb": ("limit", ["unlock", "elevate", "empower", "harness", "supercharge", "unleash", "streamline",
                            "revolutionize", "reimagine", "skyrocket", "amplify", "democratize", "future-proof",
                            "level up"]),
    "inflated-adjective": ("limit", ["seamless", "robust", "cutting-edge", "world-class", "revolutionary",
                                     "game-changing", "next-gen", "state-of-the-art", "groundbreaking",
                                     "unparalleled", "unmatched", "frictionless", "effortless", "intuitive",
                                     "industry-leading", "mission-critical"]),
    "vague-abstraction": ("limit", ["solution", "ecosystem", "synergy", "paradigm shift", "actionable insights",
                                    "end-to-end", "one-stop shop", "value-add", "touchpoint", "north star",
                                    "move the needle", "low-hanging fruit"]),
    "filler-intensifier": ("limit", ["truly", "incredibly", "literally", "actually", "really", "very", "just",
                                     "basically", "extremely", "absolutely", "remarkably", "exceptionally",
                                     "undeniably", "profoundly"]),
    "chatbot-vocabulary": ("never", ["delve", "tapestry", "testament to", "realm", "embark", "meticulous", "myriad",
                                     "underscore", "bustling", "symphony of", "labyrinth", "treasure trove",
                                     "navigate the complexities", "unwavering"]),
    "stock-opener": ("never", ["in today's fast-paced", "in today's digital age", "in an era of",
                               "look no further", "are you tired of", "ready to take your", "let's dive in",
                               "here's the thing", "rest assured", "simply put", "without further ado"]),
    "stock-claim": ("never", ["game-changer", "take it to the next level", "the future of", "transform the way",
                              "everything you need", "all-in-one", "join thousands", "you deserve",
                              "unlock the power", "this changes everything", "peace of mind", "at your fingertips",
                              "like never before", "the possibilities are endless"]),
    "unsourced-proof": ("never", ["studies show", "research shows", "experts agree", "leading experts",
                                  "widely regarded"]),
    "connective-filler": ("never", ["additionally", "moreover", "furthermore", "it's worth noting",
                                    "it's important to note", "in conclusion", "at the end of the day",
                                    "great question"]),
}
STACKING = ("hype-verb", "inflated-adjective", "vague-abstraction")
NO_INFLECT = ("filler-intensifier",)


def term_regex(term, inflect=True):
    """Regex for one vocabulary entry: hyphen/space interchangeable, straight or curly apostrophe,
    and for single words the usual suffixes."""
    if inflect and re.fullmatch(r"[a-z]+", term):
        if term.endswith("e"):
            core = re.escape(term[:-1]) + r"(?:e|es|ed|ing|ely)"
        elif term.endswith("y") and term[-2:] not in ("ay", "ey", "oy"):
            core = re.escape(term[:-1]) + r"(?:y|ies|ied|ying)"
        else:
            core = re.escape(term) + r"(?:s|es|ed|ing|ly)?"
    else:
        core = re.sub(r"\\-|\\? ", r"[-\\s]", re.escape(term)).replace("'", "['’]")
    return re.compile(r"(?<![\w-])" + core + r"(?![\w-])")


VOCAB = {g: (sev, [(t, term_regex(t, g not in NO_INFLECT)) for t in terms]) for g, (sev, terms) in WORD_GROUPS.items()}


def vocab_markdown():
    return "\n".join(f"- **`{g}`** ({sev}): " + " · ".join(terms) + "." for g, (sev, terms) in WORD_GROUPS.items())


WEAK_CTA = ["submit", "sign up", "learn more", "click here", "get started", "read more"]
PLAIN = {"utilize": "use", "facilitate": "help", "commence": "start", "approximately": "about",
         "in order to": "to", "assistance": "help", "purchase": "buy", "additional": "more", "demonstrate": "show",
         "endeavor": "try", "prior to": "before", "subsequently": "later", "at this point in time": "now",
         "in the event that": "if", "with regard to": "about", "due to the fact that": "because",
         "a large number of": "many", "has the ability to": "can", "is able to": "can", "functionality": "features",
         "obtain": "get", "terminate": "end", "numerous": "many", "sufficient": "enough", "initiate": "start"}
PATTERNS = [
    ("contrast-reveal", r"\b(?:it'?s|this is|that'?s)\s+not\s+(?:just\s+)?[^.?!—–]{1,60}(?:[,;.]|\s*[—–]|\s--?)\s*(?:it'?s|this is|that'?s)\b"),
    ("contrast-reveal", r"\bnot because\b[^.?!]{1,80}[.?!]\s*because\b"),
    ("contrast-reveal", r"\bnot (?:just|only|merely)\b[^.?!]{1,60}\bbut\b"),
    ("negation-list", r"\bno [a-z][^,.]{0,30},\s*no [a-z][^,.]{0,30},\s*(?:and\s+)?no\b"),
    ("self-answered-question", r"\b(?:the result|the catch|the best part|the secret|the answer|the kicker|why)\?\s+\S"),
    ("colon-reveal", r"\b(?:the best part|here'?s why|the result|the secret|the twist|the difference|the truth)\s*:"),
    ("stock-opener", r"^(?:imagine\b|whether you'?re\b|when it comes to\b|in a world\b|picture this\b)"),
    ("fake-kicker", r"\b(?:and that changes everything|because \w+ shouldn'?t wait|that'?s the power of)\b"),
    ("hype-punctuation", r"[!?]{2,}|\?!|!\s*$"),
    ("vague-proof", r"\b(?:trusted|loved|used|chosen)\s+by\s+(?:thousands|millions|hundreds|countless|teams everywhere|leading (?:brands|companies))\b"),
    ("passive-voice", r"\b(?:is|are|was|were|be|been|being)\s+\w+ed\b(?:\s+by\b)?"),
]


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if re.search(r"[A-Za-z]", s)]


def syllables(word):
    w = word.lower().strip(".,;:!?\"'()")
    if not w:
        return 0
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee")):
        n -= 1
    return max(1, n)


def lint(lines, all_short=False):
    hits = []
    for i, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        short = all_short or line.lstrip().startswith("#") or len(line.split()) <= 12
        low = line.lower()
        text = re.sub(r"^#+\s*", "", line).strip()
        stack = []
        for group, (sev, terms) in VOCAB.items():
            found = [t for t, rx in terms if rx.search(low)]
            if not found:
                continue
            if group in STACKING:
                stack += [(group, t) for t in found]
            elif group in NO_INFLECT:
                hits.append((i, group, ", ".join(found)))
            else:
                hits += [(i, group, t) for t in found]
        if len(stack) >= 2:
            hits.append((i, "buzzword-stack", "; ".join(f"{g}: {t}" for g, t in stack)))
        elif stack:
            hits.append((i, stack[0][0], stack[0][1]))
        for phrase, alt in PLAIN.items():
            if re.search(r"\b" + re.escape(phrase) + r"\b", low):
                hits.append((i, "plain-english", f"{phrase} → {alt}"))
        for name, rx in PATTERNS:
            if re.search(rx, low.strip()):
                hits.append((i, name, text[:70]))
        if short and ("—" in line or " -- " in line):
            hits.append((i, "em-dash-in-short-copy", text[:70]))
        stripped = low.strip(" #*[]()`>-")
        if stripped in WEAK_CTA:
            hits.append((i, "weak-cta", stripped))
        for s in sentences(text):
            words = s.split()
            if len(words) > 25 or (len(words) > 20 and s.count(",") > 2):
                hits.append((i, "long-sentence", f"{len(words)} words, {s.count(',')} commas"))
            if s.count(",") >= 3 and re.search(r",\s*(?:no|ensuring|making|so that|without)\b[^,]*$", s.lower()):
                hits.append((i, "trailing-pile-on", s[:70]))
        threes = re.findall(r"\b\w+,\s+\w+,?\s+and\s+\w+\b", low)
        if len(threes) > 1:
            hits.append((i, "reflexive-threes", f"{len(threes)} lists of three"))
    return hits


def summary(lines):
    body = " ".join(re.sub(r"^#+\s*", "", l) for l in lines if l.strip())
    sents = sentences(body)
    words = re.findall(r"[A-Za-z']+", body)
    if not sents or not words:
        return {}
    syl = sum(syllables(w) for w in words)
    flesch = 206.835 - 1.015 * (len(words) / len(sents)) - 84.6 * (syl / len(words))
    you = len(re.findall(r"\b(?:you|your|you're|yours)\b", body, re.I))
    we = len(re.findall(r"\b(?:we|our|us|we're)\b", body, re.I))
    return {"words": len(words), "sentences": len(sents), "avg_sentence_words": round(len(words) / len(sents), 1),
            "flesch_reading_ease": round(flesch, 1), "you_count": you, "we_count": we,
            "exclamations": body.count("!")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?")
    ap.add_argument("--short", action="store_true", help="treat all lines as short copy")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--vocab", action="store_true", help="print the vocabulary block that ai-tells.md section D must match")
    a = ap.parse_args()
    if a.vocab:
        print(vocab_markdown())
        return
    if not a.file:
        ap.error("a file (or '-') is required")
    lines = sys.stdin.readlines() if a.file == "-" else open(a.file, encoding="utf-8").readlines()
    hits = lint(lines, a.short)
    summ = summary(lines)
    if a.json:
        print(json.dumps({"hits": [{"line": l, "type": t, "detail": d} for l, t, d in hits], "summary": summ}, indent=2))
        return
    for l, t, d in hits:
        print(f"L{l:<4} {t:<24} {d}")
    counts = {}
    for _, t, _ in hits:
        counts[t] = counts.get(t, 0) + 1
    print("\nsummary:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])) or "no hits")
    if summ:
        print(f"words={summ['words']} sentences={summ['sentences']} avg_sentence={summ['avg_sentence_words']} "
              f"flesch={summ['flesch_reading_ease']} (60-70 plain; 70+ easy) you/we={summ['you_count']}/{summ['we_count']} "
              f"exclamations={summ['exclamations']}")
        if summ["we_count"] > summ["you_count"]:
            print("note: more 'we' than 'you'; rewrite toward the reader.")


if __name__ == "__main__":
    main()
