---
name: long-form-writing
description: "Draft and edit long-form prose (articles, blog posts, essays, explainers, docs pages) from raw notes. Use when the user says \"write a post/article/essay\", \"turn my notes into a piece\", \"help me figure out what I want to say\", \"review my prose\", \"make this sound less like AI\". Not for decision docs or specs (use cowrite-document) or marketing page copy (use marketing-copy)."
license: MIT
metadata:
  category: "writing-documents"
  version: "3.0.0"
---

# Long-form writing

Scope: four modes. Fragments mode interviews the author into an append-only pile. Shape mode builds the article paragraph by paragraph from the pile. Beats mode builds it one reader move at a time, choose-your-own-adventure style. Edit mode lints and reviews prose with file:line findings. A grounding ledger keeps any paragraph from leaning on an idea the reader hasn't met.

Boundaries: decision docs, design docs, RFCs and PRDs go to cowrite-document; short internal updates to internal-communications; landing, pricing and other marketing page copy to marketing-copy (its own "less AI-sounding" pass is page-specific; `prose_lint.py` here works on any prose).

Good prose comes from separating three jobs that fight when done at once. **Explore** collects more material than you need. **Exploit** commits to a path through that material, so the reader never meets an idea before it's been grounded. **Edit** makes each sentence plain, specific and the author's own. Run them as distinct modes, and let the user move between them.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `mode` | yes (inferred or asked) | fragments if there's no pile; shape if there's a pile; edit if there's a draft | `fragments`, `shape`, `beats`, `edit` |
| `topic` / request | yes for fragments | - | "why our deploys got slow" |
| `pile` | yes for shape and beats | - | `drafts/gate-debt-notes.md` (any shape: fragments, prose dump, transcript) |
| `article_path` | yes for shape and beats (asked once) | - | `drafts/gate-debt.md` |
| `reader` | yes for shape and beats | asked | "engineers who ship weekly" |
| `prerequisites` | yes for shape and beats | agreed with the user | "deploy pipeline, CI check" |
| `files` | yes for edit | - | `docs/**/*.md` |
| `style_sheet` | optional | REFERENCE §5 defaults | a filled templates/style-guide.md |
| `length` / venue | optional | none | "~1,200 words, team blog" |

## Output

| Mode | Output |
|---|---|
| fragments | an append-only Markdown pile: an H1 working title, fragments separated by `---`, and ideally a leading word |
| shape / beats | a separate article file, grown one agreed block or beat at a time; a grounding ledger (`ledger.json`); the pile untouched |
| edit | `prose_lint.py` findings and an edit report (must-fix / structure / style / kept on purpose); applied edits only if asked |

## Supporting files

- [REFERENCE.md](REFERENCE.md):
  - §1 fragments mode: interview moves, what a fragment is, the leading word, file rules;
  - §2 grounding;
  - §3 shape vs beats, with shared rules and push-back questions;
  - §4 choosing a block's form;
  - §5 default style rules and assistant tells;
  - §6 the review protocol;
  - §7 every lint rule.

  Read the section for your mode before starting.
- [templates/](templates/):
  - `fragments-file.md`: what a good pile looks like;
  - `shape-session.md`: settings, prerequisites, candidate openings, block log, gaps;
  - `beats-menu.md`: how to present the next-beat options;
  - `edit-report.md`;
  - `style-guide.md`: per-author overrides.
- [scripts/](scripts/):
  - `fragments.py init|add|list|show|edit|cut|title|check`: append-only pile that re-reads from disk; refuses to overwrite.
  - `ledger.py init|land|check|offer|undo|promote|show`: the grounding ledger. `land` refuses blocks that need ungrounded concepts, and `offer` ranks candidates as reachable or blocked and shows what unlocks them.
  - `prose_lint.py FILE… [--only|--skip|--max-words|--json|--strict]` gives `path:line:col: severity rule: message [suggestion]` for 20 rules, and exits 1 on `fix` findings.
- [examples/notes-to-post.md](examples/notes-to-post.md): a rant → pile → ledger-checked article → lint before and after, with real command output.

## Steps

1. **Pick the mode.**
   - No material yet → fragments.
   - A pile and no article → ask: shape (an editor arguing each paragraph) or beats (choose the next move each time).
   - A draft exists → edit.
   - The user can switch at any point; follow them.
2. **Fix the paths.** If a pile or article path is missing, ask once and reuse it for the session. In shape and beats mode, the pile is read-only. Never write to it.
3. **Fragments mode** (REFERENCE §1).
   - `fragments.py init <pile> "<working title>"`, then capture the request itself as fragment 1.
   - Interview for specifics: events, numbers, exact quotes, objections, opinions.
   - Append each fragment with `fragments.py add` as it appears, mention it in passing, and don't ask permission each time.
   - If an idea keeps recurring → push to coin a leading word (try 3-4 names).
   - If the user asks to cut, sharpen or merge → `fragments.py edit|cut` that fragment only.
   - Don't outline. When the user says the pile is ready → step 4.
4. **Settle the reader and the prerequisites** (both exploit modes).
   - Read the pile end to end.
   - Agree on the reader, the takeaway, and what the reader walks in knowing.
   - `ledger.py init ledger.json --prereq "…"`.
5. **Open.**
   - Shape: draft 2-3 candidate openings, each implying a different thesis. Show them all and make the user pick or combine.
   - Beats: offer 2-3 starting beats, each noting what it grounds and unlocks (templates/beats-menu.md).
   - Write only the chosen opening to the article file, then `ledger.py land …`.
6. **Grow the article one unit at a time.**
   1. Re-read the article from disk; the user may have edited it.
   2. Ask what the reader needs next.
   3. Shape: propose the next block and argue its form (REFERENCE §4).
      Beats: offer 2-3 reachable next beats.
   4. Check each candidate with `ledger.py check` or `offer`. If it's blocked, ground the concept first or promote it to a prerequisite, and decide which with the user.
   5. Once agreed, append that one unit and `land` it.
   - If the pile lacks something, name the gap and ask for it, or cut the section. Never invent anecdotes, numbers or quotes.
   - If a unit grows to several jobs, split it.
   - Stop when the user says it's done (shape) or at the natural end of the journey (beats), even with fragments left over.
7. **Edit mode** (REFERENCE §5-6).
   1. Read the whole piece and state its takeaway in one sentence. If you can't, the structure is the first finding.
   2. Run `prose_lint.py <files>` with the author's style sheet settings (`--skip`, `--max-words`).
   3. Triage: `fix` is must-fix; `style` usually changes; `note` is a judgement call.
   4. Fix structure before sentences.
   5. Write the edit report. If asked to apply the edits, make the smallest change per finding, keep the author's voice, and re-run the lint.
8. **Verify.** Check every number, quote and link against its source. Make sure no concept is used before it's grounded: walk the ledger against the article order.

## Checkpoints

- Fragments: `fragments.py check` reports 0 problems; the pile has an H1 and `---` separators only.
- Before the opening: the reader, the takeaway and the prerequisites are agreed, and the ledger exists.
- Every write in shape or beats mode: the article was re-read from disk first; only one unit was appended; the ledger was updated.
- Edit: `prose_lint.py` exits 0 (no `fix` findings), and every remaining `style`/`note` finding is fixed or listed under "kept on purpose".

## Worked example

The user wants a post about slow deploys. Fragments mode captures 5 fragments (101 words), including the number (6 → 14 minutes), an overheard line ("we don't know who owns it") and the leading word *gate debt*. Shape mode sets the prerequisites to "deploy pipeline, CI check" and offers three openings; the user picks "Our deploys take 14 minutes. A year ago they took six." Two blocks land. Then `ledger.py check --requires "gate debt"` returns BLOCKED, so the next block coins the term before the cleanup rule can use it. An early draft lints at `fix=1 style=6 note=1`: a throat-clearing opener, "not just X, it's Y", "delve", "many people say", "made a decision", a passive, and a "here" link. The rewrite, at the same length, lints clean at `fix=0 style=0 note=0`. The full run is in [examples/notes-to-post.md](examples/notes-to-post.md).

## Pitfalls

- **Structuring during explore.** Outlines in fragments mode kill the material that doesn't fit yet.
- **Overwriting the pile or the article.** Always re-read from disk and append. User edits win.
- **Writing ahead.** In beats mode, write one beat and stop. Batching takes the steering away from the user.
- **Ungrounded leaps.** A paragraph that leans on an idea the reader hasn't met loses them, even with no jargon. Check the ledger.
- **Inventing to fill gaps.** Name the gap and ask. Made-up anecdotes and numbers poison the whole piece.
- **Polishing a broken structure.** Fix the order and the cuts before the sentences.
- **Over-editing the voice away.** The goal is the author on a good day, not your house style.
- **Treating lint as a verdict.** `note` findings are prompts. A passive with an unknown actor is fine.
- **Assistant tells**: stock words, "not just X, it's Y", triads, em-dash storms, and a moral at the end of every paragraph.

## Done when

- [ ] The mode matched the material, and the paths were fixed once.
- [ ] Fragments: the pile passes `fragments.py check`, has a working title, and (ideally) a leading word.
- [ ] Shape or beats: the prerequisites were agreed; every unit was appended one at a time after a re-read; the ledger shows no unit requiring an ungrounded concept; the pile is unchanged.
- [ ] Gaps were named and filled by the user or cut. Nothing was invented.
- [ ] Edit: `prose_lint.py` exits 0; the edit report separates must-fix, structure and style, and lists what was kept on purpose.
- [ ] Numbers, quotes and links have been checked against their sources.

Related skills: cowrite-document (structured docs for decisions and reviews), internal-communications (short updates and announcements), system-diagrams (when a block should be a diagram), word-documents, pdf-files and powerpoint-decks (publishing the finished text).
