# Co-authoring reference

## Contents

1. Opening questions and context sources
2. Clarifying-question banks by document type
3. Section order by document type
4. Brainstorm and curation conventions
5. Drafting and editing rules
6. Whole-document review checklist
7. Reader testing details
8. Handling deviations
9. Using connected tools for context

## 1. Opening questions and context sources

Ask these together, numbered, and say shorthand answers are fine:

1. What kind of document is it (spec, design doc, decision doc, PRD, proposal, ADR, one-pager, something else)?
2. Who will read it first, and who else will it reach later?
3. What should a reader think, decide or do after reading?
4. Is there a template, an example you like, or a required format?
5. Constraints: length, deadline, sensitivity, review process, where it will live?

Then invite a context dump, without asking for organisation. What to ask for:

- background on the problem and how it was noticed
- earlier discussions, threads, meeting notes, related docs
- options already rejected, and why
- organisational context: owners, politics, past incidents, commitments made
- deadlines and what drives them
- technical architecture and dependencies
- stakeholder concerns, especially from people who will push back

Track what you have learned and what is still unclear as you go, and ask about unknown names, systems or acronyms immediately. Don't let gaps pile up.

**Exit test for context gathering:** you can ask about edge cases and trade-offs without needing basics explained. If your questions are still "what is X?", keep gathering.

## 2. Clarifying-question banks

Pick 5-10 that fit the gaps, number them, and make each answerable in a few words.

**Decision doc:** What exactly is being decided, and what is not? Who decides, and who must be consulted? What is the deadline, and what happens if it is missed? Which options are real, and is "do nothing" viable? What criteria matter most, in what order? What is the cost of each option in money, people and time? What would make you change the recommendation? Who loses something under the recommendation?

**Design doc / RFC / spec:** What are the hard requirements (scale, latency, compliance)? What exists today, and what must keep working? What are the interfaces and who consumes them? How does it fail, and what happens then? How is it rolled out and rolled back? How will you know it works (metrics, tests)? What is out of scope? Which alternatives were seriously considered?

**PRD:** Who exactly is the user, and what is their current workaround? What evidence shows the problem (data, quotes)? What is the success metric, its baseline and target? What must not get worse (guardrails)? What is the smallest version worth shipping? What are the dependencies on other teams? What is the launch audience and timing?

**Proposal / pitch:** What precisely is being asked for, from whom, by when? What does it cost? What is the expected return, and when will it show? What is the cheaper or smaller version? What happens if the answer is no? Who has already agreed?

**ADR:** What forced the decision now? What constraints are fixed? Which options were on the table? What becomes harder after this decision? What would trigger revisiting it?

**Postmortem / incident review** (or use internal-communications for the comms side): timeline with timestamps and zone, detection, impact (users, money, duration), root and contributing causes, what went well, action items with owners and dates.

## 3. Section order

Start with the section with the most unknowns, because it shapes the rest. Write summaries last.

| Type | Draft first | Then | Last |
|---|---|---|---|
| Decision doc | Options + Comparison | Decision to make, Risks, Ask | Recommendation |
| Design doc | Proposal | Context, Alternatives, Risks, Rollout | Summary, Open questions |
| PRD | Requirements | Problem, Users, Metrics, UX, Out of scope | Launch plan |
| Proposal | What we'll do + Costs | Why, Expected results, Alternatives | The ask |
| ADR | Decision | Context, Alternatives | Consequences |
| One-pager | Proposal | Problem, Impact, Cost | TL;DR, Ask |

If the user has no structure in mind, propose the template's sections for their doc type (`scaffold_doc.py --list`) and ask whether to adjust before scaffolding.

## 4. Brainstorm and curation conventions

- Number every option so the user can answer "keep 1, 4, 7; drop 3 (dup of 1); merge 5+6".
- 5 items for a small section, up to 20 for a complex one. Include things the user mentioned earlier and may have forgotten, angles nobody raised yet (risks, second-order effects, the sceptic's view), and things the audience will ask.
- One line per item, concrete ("Shadow-run both systems for a cycle"), not a topic ("Testing").
- Offer more options once; don't pad.
- Ask for brief reasons on removals ("audience knows this", "politically sensitive"). The reasons tell you what to leave out of later sections.
- If the user answers in prose ("most of it, but not the cost stuff"), translate it into the keep/drop list, say it back in one line, and proceed.
- Then ask the gap question: "Anything missing for this section?"
- Brainstorm lists live in the conversation, not in the document.

## 5. Drafting and editing rules

- Replace only the section's placeholder. Never regenerate the whole document for a section-level change.
- Every later change is a surgical edit: one sentence or bullet at a time, quoting the old text you replace. Don't silently rewrite neighbouring prose.
- When drafting the first section, ask the user to tell you what to change rather than editing the file themselves. Their instructions teach you their preferences faster. If they do edit directly, read the file again before your next edit, note what they changed (cut hedges? shorter bullets? different terms?), and apply that preference from then on.
- After 3 rounds on a section with only small changes, ask: "What can be cut without losing anything?" Removing text is usually the best last edit.
- Write for the stated reader. Define terms on first use, lead each section with its point, put numbers next to claims, and use the same name for a thing every time. Prose style rules: long-form-writing.
- Keep the user's facts. Mark anything you inferred with `[check: ...]`; `doc_status.py` counts these as placeholders, so nothing unverified slips into the shared version.

## 6. Whole-document review checklist

Run when about 80% of sections are drafted, and again at the end:

- **Flow:** does each section follow from the one before? Would a reader know why they are reading it?
- **Consistency:** same numbers, dates, names and scope everywhere. A number that appears twice must match.
- **Redundancy:** the same point made in two sections. Keep it where it does the most work.
- **Contradictions:** recommendation vs. risks vs. ask.
- **Filler:** sentences that would fit any document ("This is an important initiative", "leverage synergies"), throat-clearing openers, summary sentences that repeat the paragraph. Cut them.
- **Weight:** does every sentence change what the reader knows or does?
- **Skim path:** title + headings + first sentences should carry the argument.
- **Mechanics:** `doc_status.py doc.md --final` reports no placeholders, empty sections, images without alt text, or broken relative links. Expand the acronyms it lists, or confirm the audience knows them.

## 7. Reader testing details

**Why:** authors can't un-know context. A reader with only the document shows what it actually communicates, and many readers will in fact meet it through an assistant summarising or answering questions about it.

**Fresh reader:** a sub-agent started with no conversation history, given only the document text and one prompt. If you can't start sub-agents, the user opens a fresh chat session, pastes the document, and asks the prompts from `templates/reader-test-prompts.md`. Never use yourself as the reader, because you share the drafting context.

**Process:**

1. Predict 5-10 questions real readers would ask, and write the intended answer for each (`question || intended answer` in a text file).
2. `reader_test.py prepare doc.md --questions q.txt -o reader-test/` writes one prompt per question plus six whole-document checks.
3. Run each prompt in a fresh reader. Paste replies into `results.json`, score each `pass` / `partial` / `fail` against the intended answer, and name the section to fix.
4. `reader_test.py report reader-test/results.json`. "Ready" means no fail, at most a few partials, and no open check findings.
5. Fix the sections, then re-test only the failed questions plus the ambiguity check, with a new fresh reader.

Stop when replies are consistently correct and no new ambiguities come up. Two or three rounds is typical.

**Alt text:** images are invisible to a text-only reader. For any image without alt text, ask the user what it shows (or have them paste it) and write a one-sentence description of what the reader should learn from it, not just what it looks like.

## 8. Handling deviations

- **User wants to skip a stage:** confirm in one line, then skip. Offer the reader test once at the end anyway.
- **User wants freeform writing:** drop the stages and use the same quality bar (section-level edits, review checklist, `doc_status.py`).
- **Frustration or time pressure:** acknowledge it, and offer the fast path: draft all sections from what you have, mark gaps `[check: ...]`, and do one review pass plus a 3-question reader test.
- **Big new context mid-way:** pause, add it to your notes, and list the sections it affects before editing.
- **Disagreement between stakeholders:** don't resolve it in prose. Present it as an explicit open question or option with owners.

## 9. Using connected tools for context

If the environment has connectors (chat, mail, drive, wiki, tickets), offer to read the threads and documents the user names. Say what you will read before reading, and ask before searching broadly for unknown names. Quote what you used so the user can check it. If no connector is available, ask the user to paste the relevant parts. Never post, comment or share from the document workflow without an explicit request.
