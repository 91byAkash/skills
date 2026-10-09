# Critic Review Loop: Reference

## Contents
- Score anchors
- Rubric starters by task type
- Writing good criteria
- Reviewer tier pairing
- Stalls and escalation
- Panel lenses
- Doubt pass
- Limits

## Score anchors

| Score | Meaning |
|---|---|
| 1–3 | broken, or major requirements missing |
| 4–6 | works, but with significant issues (correctness gaps, missing cases, unclear structure) |
| 7–8 | good; only minor issues |
| 9–10 | ready to ship; nothing material to change |

Ask the reviewer to justify the score against each criterion and to cite locations. A score without evidence is ignored.

## Rubric starters by task type

| Task | Criteria to adapt |
|---|---|
| Feature code | requirements met; edge cases and error paths handled; input validated at boundaries; readable names and small functions; tests would fail if behaviour broke |
| Bug fix | root cause fixed (not symptom); regression test reproduces the original bug; no side effects on callers |
| Refactor | behaviour unchanged (tests/golden outputs); simpler than before by a stated measure; no new coupling |
| REST/GraphQL API | correct status codes and error contract; auth on every route; pagination/limits; backward compatibility; no N+1 queries |
| Database migration | online (lock duration), reversible or explicitly one-way, batched backfill, index strategy, data-loss risk addressed |
| Data pipeline | idempotent reruns; schema drift handling; failure and retry behaviour documented; personal data handled |
| Infrastructure as code | least privilege; no hard-coded secrets; idempotent apply; safe destroy/rollback |
| Test suite | covers edge cases; tests independent; assertions meaningful (not just "no error") |
| Spec / design doc | problem unambiguous; alternatives with trade-offs; no hand-waving on hard parts; measurable success criteria; rollout and risks |
| Prose / docs | audience and purpose clear; structure scannable; claims accurate; no filler; steps runnable |

## Writing good criteria

- Observable in the output: "each public function has a docstring with an example" beats "well documented".
- One property each; 4–6 total.
- Include at least one criterion the first draft is likely to miss (the reason for running the loop).
- Add hard constraints from the user or spec verbatim.

## Reviewer tier pairing

The reviewer must be at least as capable as the worker, and the worker must be able to act on the feedback.

| Work | Worker | Reviewer |
|---|---|---|
| Mechanical (boilerplate, formatting, CRUD) | fast | standard |
| Standard (features, refactors, docs) | standard | standard |
| Complex (multi-file, integration, design) | standard | most capable |
| Very complex (security, concurrency, distributed, finance) | most capable | most capable |

## Stalls and escalation

Signal: no score improvement on the previous round with the same top issue, or two rounds in a row without improvement (the rules `scripts/loop-decide.py` applies). Options:
1. Split the work and run the loop on each part.
2. Use a stronger worker (the reviewer's fix may be beyond the current one).
3. Clarify the requirement with the user (the rubric may be contradictory).
4. With consent, accept a lower gate and record the gap in the report.

## Panel lenses

| Lens | Asks |
|---|---|
| Security | trust boundaries, injection, authz, secrets, data exposure |
| User experience | task success, error messages, empty/loading states, accessibility |
| Maintainability | naming, cohesion, coupling, test seams, dead code |
| Performance | complexity on hot paths, I/O counts, memory bounds |
| Operations | logging, metrics, failure modes, rollback |

Run lenses in parallel with short rubrics each; merge into one list sorted by severity; when lenses conflict, decide and state why.

## Doubt pass

1. State the decision, the context, the constraints, and the alternatives considered.
2. Ask a fresh reviewer for: the strongest argument against; the conditions under which an alternative wins; what evidence would settle it.
3. Check each argument against facts (code, data, docs). Change course only if one holds; record the outcome either way (e.g. an ADR via domain-glossary).

## Limits

- The reviewer has no memory between rounds; pass earlier findings each time.
- A loop is a strong first pass, not a replacement for human review on security- or compliance-critical work.
- Underspecified tasks do not converge; define acceptance criteria first.
- Cost: one reviewer call per round (per lens in panel mode); a 3-round loop is roughly 1–2× the time of a single pass.
