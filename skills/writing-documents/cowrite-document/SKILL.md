---
name: cowrite-document
description: "Co-write a structured document (design doc, RFC, decision doc, PRD, proposal, ADR, one-pager) section by section, then test it on a fresh reader. Use when someone says \"help me write a doc/RFC/proposal\", \"draft a decision doc\", \"turn these notes into a design doc\". Not for a spec from settled decisions (use write-spec) or short updates (use internal-communications)."
license: MIT
metadata:
  category: "writing-documents"
  version: "3.0.0"
---

# Co-write a document

The user knows the context and you know how to structure and test a document, so the workflow moves the context across fast, builds the document one section at a time in the user's voice, and then checks it on a reader who knows nothing else. Offer the workflow in two sentences at the start. If the user prefers freeform, keep the same quality bar without the stages.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `doc_type` | yes (asked) | - | decision doc, design doc, PRD, proposal, ADR, one-pager |
| `audience` | yes (asked) | - | "finance lead and head of platform decide" |
| `desired_impact` | yes (asked) | - | "approve two engineers for Q4" |
| `context` | yes | - | notes, threads, prior docs, a brain dump |
| `template` | optional | `templates/<type>.md` | the team's own template or an example doc |
| `existing_draft` | optional | none | `docs/search-v2.md` |
| `output` | optional | `<slug>.md` in the working folder | `docs/decisions/invoicing.md` |
| `constraints` | optional | none | length cap, deadline, confidentiality |

## Output

A Markdown document (or the user's existing file, edited in place section by section) that:

- has every section drafted with no placeholders, and passes `doc_status.py --final`;
- has had a whole-document review;
- has passed a reader test (`reader_test.py report` says READY), or the user explicitly skipped it.

Boundaries: if the decisions are already made and only need writing up as a feature spec or issue, use write-spec. For sentence-level polish of a finished draft, use long-form-writing's edit mode. For the announcement after the decision, use internal-communications.

Convert the format afterwards with word-documents, pdf-files or powerpoint-decks if needed.

## Supporting files

- [REFERENCE.md](REFERENCE.md): opening questions and context sources, clarifying-question banks per doc type, section order per type, brainstorm/curation conventions, editing rules, review checklist, reader-test protocol, how to handle deviations, using connectors. Read sections 2-4 before Stage 2 and section 7 before Stage 3.
- [templates/](templates/): `design-doc.md`, `decision-doc.md`, `prd.md`, `proposal.md`, `adr.md`, `one-pager.md` (section guidance inside each placeholder) and `reader-test-prompts.md` (question test, six whole-document checks, question ideas, results table).
- [scripts/](scripts/):
  - `scaffold_doc.py <type> "<title>" --owner … -o file.md` (`--list`, `--sections`, `--number`; also accepts `rfc`, `spec`, `design`, `decision` as aliases): skeleton with `[To be written]` placeholders.
  - `doc_status.py doc.md [--final|--json]`: per-section words and status. Also flags leftover placeholders (`[check: …]` included), empty sections, missing alt text, broken relative links, long and repeated sentences, unexpanded acronyms, a missing summary, and reading time.
  - `reader_test.py prepare doc.md --questions q.txt -o rt/` and `reader_test.py report rt/results.json`: fresh-reader prompts and a readiness verdict.
- [examples/decision-doc-session.md](examples/decision-doc-session.md): a full session with outputs; [examples/invoicing-decision.md](examples/invoicing-decision.md) is the finished document.

## Steps

### Stage 1: Context

1. **Ask the five opening questions** (REFERENCE section 1) in one numbered message and accept shorthand.
   - If they name a template or link a doc, read it now.
   - If they are editing an existing doc, read it and run `doc_status.py` on it. For images without alt text, ask what each shows and offer to write descriptions.
2. **Invite a context dump** and say it needn't be organised. If they point at threads or documents and a connector exists, say what you'll read, then read it. Otherwise ask for a paste. Ask before searching for unknown names.
3. **Ask 5-10 numbered clarifying questions** aimed at the gaps (REFERENCE section 2), and accept answers like "1: yes, 2: see thread, 3: no, backwards compat".
4. **Exit test.** If your next questions are about edge cases and trade-offs, move on. If they are still about basics, repeat step 3. Ask once whether there is more context, then go to Stage 2.

### Stage 2: Structure and sections

5. **Agree the structure.** If the type has a template, propose its sections (`scaffold_doc.py --list`). If the user has their own template, use its headings. Then scaffold: `python scripts/scaffold_doc.py <type> "<title>" --owner "<name>" -o <file>.md` (or `--sections "A,B,C"`).
6. **Pick the order.** Start with the section that has the most unknowns (REFERENCE section 3) and leave summaries until last.
7. **For each section:**
   1. Ask 5-10 clarifying questions specific to the section.
   2. Brainstorm 5-20 numbered candidate points, including forgotten context and angles nobody raised.
   3. Ask the user to keep, drop or merge points, with brief reasons. If they answer in prose, translate it into a list and confirm in one line.
   4. Ask "anything missing?"
   5. Draft by replacing only that section's placeholder. With the first section, ask the user to say what to change rather than edit the file. If they edit anyway, re-read the file and adopt their preferences.
   6. Refine with surgical edits. After 3 rounds of small changes, ask what can be cut.
   7. Confirm the section is done.
8. **Review the whole document** when about 80% of sections are done, and again at the end, using the REFERENCE section 6 checklist. Then run `python scripts/doc_status.py <file>.md`. Fix contradictions and filler, and expand or confirm the acronyms it lists.

### Stage 3: Reader test

9. **Predict 5-10 reader questions,** each with the intended answer, in `q.txt` as `question || intended answer`.
10. **Prepare** with `python scripts/reader_test.py prepare <file>.md --questions q.txt -o rt/`, then run the prompts:
    - If you can start sub-agents, give each `rt/*.txt` to a new one with no conversation history.
    - Otherwise the user pastes the document and prompts into a fresh chat session and returns the replies.
    - Never act as the reader yourself.
11. **Score and report.** Enter scores and the section to fix in `rt/results.json`, then run `python scripts/reader_test.py report rt/results.json`.
    - If NOT READY, go back to step 7 for the named sections and re-test the failed questions with a new fresh reader.
    - If READY, continue to the hand-off.
12. **Hand off.** Run `doc_status.py --final` (exit 0). Ask the user to do their own read-through and check facts, numbers and links; they own the document. Suggest appendices for depth, and updating the doc as real readers respond.

## Checkpoints

- End of Stage 1: you can state the doc's purpose, audience, desired impact and main tension in four lines, and the user agrees.
- After each section: the user has confirmed it, and `doc_status.py` shows it as `done`.
- Before Stage 3: whole-document review done; no contradictions between Recommendation, Risks and Ask.
- After Stage 3: READY, or the user chose to stop, recorded in the hand-off.

## Worked example

Decision doc "Move invoicing to the new ledger" ([session](examples/decision-doc-session.md)):

1. Five opening answers in shorthand, plus a dump. Seven clarifying questions surfaced the patch-only option, the credit-note agreement and the unconfirmed LRS review.
2. `scaffold_doc.py decision-doc …` produced 6 sections. Options was drafted first from a 9-item brainstorm, using "keep 1,2,5; drop 3,7,8; merge 4 into 1".
3. The 80% review caught two different decide-by dates. `doc_status.py` flagged `acronym LRS is never expanded`.
4. Reader test, 7 questions: `5 pass, 1 partial, 1 fail` (rollback unclear, LRS unknown), so NOT READY. Two surgical edits in Risks, then a new fresh reader gave `7 pass` and READY. `doc_status.py --final` exit 0.

## Pitfalls

- **Drafting before the context is in.** Fluent text built on guesses then needs a rewrite. Hold off until the exit test passes.
- **Regenerating the whole document** for one change. Users lose trust when untouched sections change. Edit only what was asked.
- **Brainstorms in the document.** Option lists belong in the conversation; only the curated content goes in the file.
- **Testing with yourself.** You share the context, so you'll "understand" gaps a real reader can't. Use a fresh reader.
- **Questions only you would ask.** Reader questions should be what the decider or implementer needs, not a quiz on details.
- **Unverified inferences.** Mark them `[check: …]` so `doc_status.py --final` blocks until the user confirms.
- **Filler and repetition.** Generic importance claims, recap sentences, the same point in two sections. Cut them in the review.
- **Images without alt text.** They're invisible to assistant-based readers and screen readers.
- **Overselling the process.** Explain it in two sentences and get on with the work. If the user wants to skip a stage, skip it.

## Done when

- [ ] Purpose, audience and desired impact were confirmed in Stage 1.
- [ ] Every section was built and confirmed with the user; no `[To be written]` or `[check: …]` left.
- [ ] Whole-document review done: consistent numbers, dates and names; no contradictions; filler cut.
- [ ] `doc_status.py <file> --final` exits 0, with acronyms expanded or confirmed and every image's alt text present.
- [ ] `reader_test.py report` says READY with a fresh reader (or the user explicitly skipped the test).
- [ ] The user has been asked to do the final read-through and fact check.

Related skills: long-form-writing (sentence-level drafting and style), internal-communications (announcing the decision), system-diagrams (diagrams inside the doc), word-documents, pdf-files and powerpoint-decks (delivering it in another format), excel-spreadsheets (the numbers behind a comparison).
