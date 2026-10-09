---
name: stakeholder-questionnaire
description: "Write a short, ordered questionnaire for one stakeholder, client or expert, then fold the answers into decisions. Use when a decision is blocked on someone else's knowledge, before a discovery or requirements call, or when the user says \"write questions for X\" or \"what should I ask them?\". Not for surveys at scale (use customer-research) or grilling the user (use stress-test-plan)."
license: MIT
metadata:
  category: "productivity"
  version: "3.0.0"
---

# Stakeholder questionnaire

Interview the user only about the *send* (who it goes to and what they need back); aim the document's questions at the gap between what the user knows and what the recipient knows.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `recipient` | required | ask | "Priya, finance controller, knows the invoicing rules, not technical" |
| `needs` | required | ask | "which invoices need GST e-invoicing; who approves credit notes; deadline for go-live" |
| `topic` | optional | from `needs` | "billing migration" |
| `context_docs` | optional | none | spec, ticket, meeting notes to mine for what is already known |
| `deadline` | optional | none | "Friday 17 Oct" |
| `medium` | optional | Markdown document | form, email body, meeting agenda |
| `max_questions` | optional | 12 | 6 for a busy executive |
| `out_path` | optional | `questionnaire-<slug>.md` in the current directory | `docs/discovery/finance-questions.md` |

## Output

- The questionnaire file at `out_path`, using [templates/questionnaire.md](templates/questionnaire.md).
- A short note to the user: path, number of questions, estimated time to answer, and anything you removed because you could answer it from available material.
- After answers arrive (if asked): decisions recorded in the right place and follow-up questions listed.

## Supporting files

- [templates/questionnaire.md](templates/questionnaire.md): document skeleton with question formats (multiple choice, range, ranking, open, confirm-our-guess).

## Steps

1. **Ask about the recipient** (one exchange): role, expertise, relationship to the user, how much time they will give. This sets tone and how much context to include.
2. **Ask what the user needs back** (one exchange): the decisions or facts they must walk away with. Done when you have a concrete list.
3. **Remove what you can answer**: check `context_docs`, the codebase, data, or public docs. Do not ask the recipient for anything findable.
4. **Draft questions aimed at the gap**, each:
   - one idea, never compound ("and/or" → split it)
   - plain language in the recipient's vocabulary; no internal jargon
   - a one-line *this decides* note only when the purpose is not obvious
   - the easiest answerable format: options with "Other / not sure", a range, yes/no with "it depends on…", or "Our best guess is X; correct?"
   - neutral wording (no leading questions); real alternatives listed
5. **Order and group**: most important first (async may get one pass), grouped under themed headings, dependent questions after the ones they depend on. Trim to `max_questions`.
6. **Frame the document**: a header table (sender, recipient, reply-by date, time needed, what the answers feed into); a short background paragraph naming the decision at stake; a line on how to answer (partial answers welcome); and a closing catch-all question ("What should we have asked but did not?").
7. **Format for the medium**: answer stubs under each question in a document; numbered list for email (options inline, "reply under each number"); time-boxed agenda for a meeting (minutes per theme, most important first); for a form, a field list (question, type: single choice / multiple choice / short text / long text / number, options, required yes/no) the user can paste into their form tool.
   Estimate answer time for the header and the note: about 0.5 min per choice or confirm question, 1 min per range or ranking, 3 min per open question. Over 15 minutes for an executive or 30 for anyone else → cut to `max_questions` again or split into two rounds.
8. **Write the file** and report. Do not send it yourself unless the user explicitly asks and names the channel.
9. **When answers come back**: record each decision where the project keeps them (spec, ADR, ticket), note contradictions or new unknowns, and propose follow-ups.

## Checkpoints

- After steps 1–2: recipient and needed outcomes confirmed.
- Before writing: share the cut list if you removed many questions, so nothing important was dropped.

## Worked example

Recipient: finance controller (non-technical, 15 minutes). Needs: e-invoicing scope, credit-note approval, go-live date.

```md
## E-invoicing scope

### Which invoices must be registered for e-invoicing?
_This decides: whether we build registration for all customers or only business customers._
- [ ] All invoices
- [ ] Only invoices to GST-registered businesses
- [ ] Not sure, depends on: ___
>

### Our understanding is that export invoices are exempt. Is that right?
- [ ] Yes  - [ ] No  - [ ] Partly: ___
>
```
Removed: "What is our GSTIN?" (found in the billing settings).

## Pitfalls

- Long questionnaires padded with nice-to-know items.
- Compound or leading questions.
- Asking for information that is already documented.
- No background paragraph, so the recipient cannot answer well.
- Open-ended questions where options would take seconds to answer.
- Sending it on the user's behalf without being asked.

## Done when

- [ ] Recipient and needed outcomes were confirmed with the user.
- [ ] Every question maps to a needed decision or fact and cannot be answered from available material.
- [ ] Questions are single-idea, neutral, in the recipient's language, ordered by importance, within `max_questions`.
- [ ] Header table gives the decision the answers feed, deadline and effort; closing catch-all present.
- [ ] File written and path reported; nothing sent without explicit instruction.
