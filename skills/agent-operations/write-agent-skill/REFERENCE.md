# Writing for Agents: Reference

## Contents
- Pointers and the two loads
- Information hierarchy and disclosure
- Completion criteria
- Leading words
- Negation
- Pruning
- Match the form to the failure
- Bulletproofing discipline skills
- Skill types and how to test each
- Evaluation procedure
- Trigger (description) evaluation
- Folder layouts

## Pointers and the two loads

A **pointer** is a line in the agent's context that names out-of-context material and the condition for reaching it: a skill description, an AGENTS.md line linking a doc, a "read REFERENCE.md when…" line in a skill.
- Put the most distinctive word first.
- One trigger per distinct case; synonyms of one case are one case.
- Do not repeat in the pointer what the body says about identity.

Every line costs one of two budgets:
- **Context load**: always-loaded text (descriptions, AGENTS.md) costs tokens and attention every turn whether used or not.
- **Cognitive load**: the human must remember which documents exist. Spend it where human judgment matters.
Material behind a pointer pays only for the pointer line until it is needed.

## Information hierarchy and disclosure

Content is **steps** (ordered actions) or **reference** (rules, definitions, catalogues consulted on demand). Tiers:
1. in-file steps (primary)
2. in-file reference
3. disclosed reference in sibling or external files, reached by a pointer
Push down too little and the top sprawls; push down too much and the needed piece is hidden. Branches (cases different runs take) are the cleanest things to disclose. Keep a concept's definition, rules, and caveats together under one heading.

## Completion criteria

Every step ends on a condition that tells the agent it is done.
- **Clear**: done vs not-done is observable ("tests pass", "every changed model listed"). Vague bounds ("understanding reached") cause premature completion.
- **Demanding**: "every modified file accounted for" drives more digging than "produce a change list".
Best criteria are checkable and exhaustive. If later steps tempt the agent to rush the current one, consider splitting the sequence across files.

## Leading words

A compact concept the model already knows (e.g. *tracer bullet*, *red/green*, *tight loop*, *deletion test*) used as a token repeatedly. It anchors behaviour each time it appears and makes pointers sharper. Hunt for triads and sentences that keep gesturing at one idea and collapse them into one well-chosen word, defined once.

## Negation

Prohibitions bring the forbidden behaviour into context. For shaping problems, describe the target form ("The summary is three bullets: result, risk, next step") rather than listing what not to do. Keep prohibitions for discipline problems (below), paired with the reasoning.

## Pruning

- One source of truth per meaning; duplicates drift.
- The environment (scripts in package.json, config, directory layout, `--help`) is a source of truth; restating it creates a stale cache. Point to it instead.
- Check every line for relevance to the task; remove exposition and stale rules.
- Remove no-ops: instructions the model already follows by default. Test: does removing the line change behaviour?

## Match the form to the failure

Classify the baseline failure first; the wrong form can make things worse.

| Baseline failure | Use | Avoid |
|---|---|---|
| Knows the rule, skips it under pressure | explicit rule + reasons + rationalisation table + red flags | soft "prefer/consider" wording |
| Complies but output has the wrong shape | a positive recipe/contract: the parts of the output, in order | lists of "don't" |
| Omits a required element | a required slot or field in the template | prose reminders near the template |
| Behaviour should depend on a condition | a conditional on an observable predicate ("if a spec file exists, link it") | unconditional rule + exemptions |

Rules for any form: no nuance clauses ("unless it matters"); express real exceptions as separate observable conditions. Exemption clauses do not scope well ("this limit does not apply to code blocks" still suppresses code blocks); restructure instead.

## Bulletproofing discipline skills

For rules agents break under time pressure (always write a failing test first; never claim done without running the check):
- State the rule plainly and why it exists.
- Close loopholes you saw in baseline runs explicitly ("a passing run of your new test alone is not a passing suite").
- Address "spirit vs letter" arguments head-on.
- Add a rationalisation table: thought → reality.
- Add a short red-flags list that means "stop and restart the step".
- Re-test with pressure scenarios (deadline, sunk cost, "it's simple"), and add each new rationalisation you see.

## Skill types and how to test each

| Type | Example | Test with |
|---|---|---|
| Discipline (rules) | verify-before-done, test-driven-development | pressure scenarios; check compliance and the rationalisations used |
| Technique (how-to) | diagnose-bug, build-mcp-server | realistic tasks; check steps followed and quality of result |
| Pattern (mental model) | module-interface-design | design/review tasks; check the vocabulary and judgments appear |
| Reference (facts, APIs) | accessibility patterns | lookup tasks; check correct, specific answers |

## Evaluation procedure

1. **Write 3–5 task evals**: realistic prompts with any input files, plus 3–6 objective assertions each (`"output has a Done-when checklist"`, `"migration uses batched backfill"`). Descriptive names.
2. **Run pairs in fresh contexts**: with skill vs baseline (no skill when creating; snapshot of the old version when improving). Start all runs together when parallel helpers are available so conditions match.
3. **Record** outputs, time, and tokens per run in a workspace beside the skill: `<name>-workspace/iteration-N/<eval-name>/{with_skill,baseline}/`.
4. **Grade** each assertion pass/fail with evidence (quote the output). Have a separate grader (another agent or the user) for subjective checks; for blind comparison, hide which output came from which version.
5. **Aggregate**: pass rate per configuration, mean time/tokens, and per-assertion differences. Look for assertions that never fail (too easy) or always fail (broken test or missing capability).
6. **Review qualitatively** with the user: show side-by-side outputs, collect feedback.
7. **Improve**: generalise from failures (do not overfit to one prompt), remove what did not help, keep the skill lean. New iteration directory; repeat until improvements plateau.

Assertion tips: objective and checkable by reading the output or running a command; avoid assertions that restate the prompt; include at least one that the baseline likely fails.

## Trigger (description) evaluation

- 16–20 realistic queries with detail (file names, context, casual phrasing), half should-trigger, half should-not.
- Should-trigger: different phrasings, indirect needs where the user does not name the skill, edge cases.
- Should-not-trigger: near-misses sharing keywords with the skill but needing another skill. Obvious irrelevancies test nothing.
- For each query, ask a fresh agent which skills it would load given only the descriptions in the pack (or run the real router if available). Record precision and recall.
- Rewrite the description to fix misses: add the missing distinct trigger, sharpen the not-for cue. Keep a held-out subset to avoid overfitting.
- Agents tend to skip skills for tasks they think are trivial; triggers matter most for multi-step or specialised work.

## Folder layouts

```
small/                       with-tool/                   heavy-reference/
  SKILL.md                     SKILL.md                     SKILL.md
                               scripts/check.py             REFERENCE.md
                               templates/report.md          references/<topic>.md
                                                            examples/
                                                            evals/evals.json
```
- Frontmatter `name` equals the folder name (kebab-case, no spaces).
- Scripts: deterministic, `--help`, non-zero exit on failure, tested; prefer running them over reading their source.
- Keep references one level deep from SKILL.md; deeper chains get skipped.
- Long reference files start with a contents list.
