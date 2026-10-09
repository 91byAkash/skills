---
name: explain-plainly
description: "Re-explain your previous message in short, plain language: the one point that matters, no jargon, a concrete example, and exactly what the user must decide or do. Use when the user says \"wait, what?\", \"I don't follow\", \"ELI5\", \"too long\" or \"what do you need from me?\". Not for switching to short answers for the whole session (use terse-mode)."
license: MIT
metadata:
  category: "productivity"
  version: "3.0.0"
---

# Explain plainly

The last message failed. Re-pitch it; do not repeat it louder.

This is a one-off rewrite of one message. If the user wants every answer shorter from now on, use terse-mode instead.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `message` | optional | your previous message | a specific earlier explanation the user points to |
| `confusion` | optional | inferred from the user's reply | "what's a migration?", "do I need to do anything?" |
| `audience` | optional | the user as they come across | non-engineer stakeholder; new team member |
| `max_words` | optional | 100 | 50 for "just tell me what to do" |
| `glossary` | optional | `GLOSSARY.md` if the project has one | use project terms consistently |

## Output

A reply in this shape (drop lines that do not apply):

```
Short version: <one or two sentences with the core point>
What you need to do: <the decision or action, numbered if more than one>
Example: <one concrete example or analogy, only if the idea is abstract>
```
Then offer more detail on request instead of including it.

## Steps

1. **Find the core**: the single thing the user must know or decide. If the original message had several, pick the one blocking progress; mention the rest as "Also, later: …" in one line.
2. **Find what broke**: too long, unknown terms, missing context (they were not following the earlier steps), or no clear ask. Fix that specific failure.
3. **Lead with the core** in one or two sentences, in the user's words where possible.
4. **Write in plain, controlled language**:
   - short sentences (aim for 15–20 words); one idea each
   - active voice; concrete subjects ("The build fails", not "Failures are being observed")
   - common words; if a technical term is needed, use one term consistently and define it in a few words the first time
   - project terms from the glossary, not synonyms
5. **Add a little context** only if they lacked it: one sentence on where we are ("We are on step 2 of 3: moving the data").
6. **Make the ask explicit**: what to decide, with the options and your recommendation, or what to do, as numbered steps.
7. **Use an example** when the idea is abstract: real values, a small before/after, or a familiar analogy (labelled as an analogy).
8. **Stop** at `max_words`. Offer: "Want the details on X?"
9. **Correct, do not hide**: if the earlier message was wrong, say so plainly ("Correction: …").

## Worked example

Original (landed badly): three paragraphs about "the expand-contract migration requiring a dual-write window and backfill before the column drop, which affects the deploy ordering".

Restated:
```
Short version: We can't delete the old "phone" column in this release. We have to copy the data to the new column first, which takes one extra release.
What you need to do: Approve shipping this in two releases (this week and next) instead of one. I recommend yes.
Example: Like moving house: you move the boxes before you give back the old keys.
```

## Pitfalls

- Same structure, different words; still too long.
- Burying the decision under background.
- Apologising at length or explaining why the first message was long.
- Introducing new information or new options while "simplifying".
- Over-simplifying into something false; keep it accurate, just shorter.
- Condescending tone ("Simply put, it's easy…").

## Done when

- [ ] The core point is in the first one or two sentences.
- [ ] Every remaining technical term is necessary and defined.
- [ ] The user's decision or action is explicit, with a recommendation if it is a choice.
- [ ] The reply is within `max_words` (unless the user asked for more).
- [ ] Nothing new was introduced, and any earlier error was corrected openly.
