---
name: stress-test-plan
description: "Stress-test a plan or decision by interviewing the user in numbered rounds, each question with a recommended answer, until nothing is left assumed. Use when the user says \"grill me\", \"poke holes in this\", \"interview me\", wants to pressure-test before building, or a request is too vague to act on; also to spec a recurring workflow. Not for choosing between approaches (use idea-to-design)."
license: MIT
metadata:
  category: "plan-and-decide"
  version: "3.0.0"
---

# Stress-Test a Plan

Turn a fuzzy plan into an explicit, shared understanding before anything is built. You ask, the user decides, and you look up facts yourself.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `topic` | yes | – | "Move billing from monthly cron to event-driven invoicing" |
| `mode` | optional | `plan` | `plan` (decision tree) or `workflow` (spec a recurring workflow, see REFERENCE.md) |
| `capture_docs` | optional | `auto` (only if the repo already has a glossary/ADR folder) | `yes`, `no` |
| `glossary_path` | optional | existing `GLOSSARY.md` (or `CONTEXT.md` / `docs/glossary.md`), else none | `docs/domain/GLOSSARY.md` |
| `adr_dir` | optional | existing `docs/adr/`, else none | `docs/decisions/` |
| `max_questions_per_round` | optional | whole frontier (soft cap 7) | `5` |
| `stop_condition` | optional | frontier empty + user confirms | "stop after 3 rounds, list the rest as open" |

## Output

1. A sequence of question rounds in the chat (format below).
2. A final **Decision summary** block the user confirms:

```markdown
## Decision summary: <topic>
Decided
- D1 <decision> (why: <one line>)
Assumptions the user accepted
- A1 ...
Open risks / deferred
- R1 ... (owner, revisit when)
Out of scope
- ...
Next step: write-spec | plan-tasks | prototype-to-decide | multi-session-roadmap
```

3. Optional files when `capture_docs` applies: glossary entries in `glossary_path` and one ADR per hard-to-reverse decision in `adr_dir` (entry and ADR formats come from `domain-glossary`; do not invent a second format).
4. In `workflow` mode, items 2-3 are replaced by `workflows/<name>.md` (from [templates/workflow-spec.md](templates/workflow-spec.md), with an empty *Open questions* section) plus `NOTES.md` holding the user's tools, channels and canonical terms.

## Supporting files

- [REFERENCE.md](REFERENCE.md): question bank by area (scope, data, failure, rollout, security, ops) and the workflow-mode vocabulary. Read when the frontier feels thin or you are in `workflow` mode.
- [templates/workflow-spec.md](templates/workflow-spec.md): the spec skeleton for `workflow` mode.

## Concepts

- **Decision tree**: every decision opens the decisions that hang off it.
- **Frontier**: open decisions whose prerequisites are all settled, i.e. the questions you can ask now without guessing at answers you have not heard.
- **Fact vs decision**: facts (what the code does, what the API supports, what a library costs) are yours to find. Decisions (what we want, what we accept) belong to the user.

## Steps

0. **Workflow mode** (`mode=workflow`): run the same loop, but the tree is the workflow's trigger, inputs, steps, checkpoints, output and failure handling (vocabulary and rules in [REFERENCE.md](REFERENCE.md#workflow-mode)). If `NOTES.md` is missing or thin, the first rounds are about the user's tools and channels. Write the spec from the template as decisions settle.
1. **Orient (read-only).** Read the relevant code, docs, glossary, ADRs, open issues. Write down facts you found with file paths. If a fact is needed and slow to get, start a sub-agent or background search and keep going; only questions downstream of that fact wait.
2. **Build the tree.** List the decisions you can see. Mark each as `settled` (stated by user or fixed by the code), `frontier`, or `blocked-by <D#>`.
   - If the tree has fewer than 3 real decisions, then say so and skip the interview: propose the plan directly.
   - If the topic is really several independent efforts, then say so and suggest `multi-session-roadmap`.
3. **Ask a round.** Put the frontier in one message, numbered, using this format. If it holds more than `max_questions_per_round` (default soft cap 7), ask the ones with the most dependents first and hold the rest for the next round:

```
Q1 - <short title>: <question; list options A/B/C when there are real alternatives>
Recommended: <your answer + one-line reason>
---
Q2 - <short title>: ...
Recommended: ...
```

   Rules: phrase each so "yes" accepts the recommendation; one decision per question; no question whose answer depends on another question in the same round; never ask for a fact you can look up.
4. **Wait.** Do not act on assumptions. Accept partial answers; unanswered items stay on the frontier. "Yes to all" accepts all recommendations; record them as decided.
5. **Recompute.** Apply answers, unlock dependent questions, drop questions made moot. If an answer contradicts an earlier decision, then raise the conflict as the first question of the next round.
6. **Capture as you go** (if `capture_docs` is `yes`, or `auto` and `glossary_path`/`adr_dir` already exist): add a glossary entry to `glossary_path` when a term gets a sharpened meaning; write an ADR into `adr_dir` only when the decision is hard to reverse, surprising without context, and the result of a real trade-off (all three).
7. **Repeat** steps 3-6 until the frontier is empty or the `stop_condition` hits.
8. **Confirm.** Post the Decision summary (in `workflow` mode: the path of the finished spec file and its trigger/checkpoint/output lines). Ask: "Is this our shared understanding?" Do not start building until the user says yes.

## Checkpoints

- After step 2: every frontier question has a recommended answer you could defend.
- After each round: count settled / frontier / blocked. The frontier should shrink or move outward; if the same question survives two rounds unanswered, ask whether to defer it as a risk.
- Before step 8: no decision in the summary rests on an assumption the user never saw.

## Worked example

Topic: "Add team accounts to our single-user notes app."

Round 1 (frontier after reading `models/user.ts`, `billing/`):
```
Q1 - Ownership: Does a note belong to a team or to a person who can share it with a team?
  A) team-owned  B) person-owned + shared
Recommended: A, because billing is per team and offboarding is simpler.
---
Q2 - Billing unit: Charge per seat or flat per team?
Recommended: per seat; the payment provider price is already per user.
---
Q3 - Migration: Should every existing user become a team of one on launch day?
Recommended: yes, so there is one code path.
```
User: "1 yes, 2 flat for teams under 5 then per seat, 3 yes."
Round 2 now unlocks: roles (owner/admin/member?), what happens to notes when a member leaves (follows from Q1 = team-owned), invite flow. Q about "sharing outside the team" waits until roles are settled.

Final summary lists D1 team-owned notes, D2 hybrid pricing, D3 auto-migrate, D4 three roles, R1 "pricing threshold needs finance sign-off", next step `write-spec`. An ADR is written for D1 (hard to reverse).

## Pitfalls

- Asking one question per message when several are independent: slow and tiring.
- Bundling dependent questions in one round, which forces the user to guess.
- Asking the user what the code does.
- Recommending nothing ("what do you think?"); every question needs a stance.
- Treating silence as consent; unanswered means still open.
- Writing ADRs for trivial or easily reversed choices.
- Starting implementation before the confirmation in step 8.

## Done when

- [ ] Frontier is empty (or stop condition reached with remaining items listed as open risks).
- [ ] Every decision in the summary was answered or explicitly accepted by the user.
- [ ] Facts used in the summary cite where they came from (file, doc, command).
- [ ] Glossary/ADR files written only where warranted, and linked in the summary.
- [ ] User confirmed shared understanding and the next step is named.
