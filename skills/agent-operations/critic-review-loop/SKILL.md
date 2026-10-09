---
name: critic-review-loop
description: "Improve a piece of work (code, spec, doc, migration, prose) through rounds where a fresh critic scores it 1-10 against a rubric, then targeted revision, until a quality gate or round limit. Use when the user says \"polish this\", \"review loop\", \"critique and improve\", or correctness matters more than speed. Not for one-line fixes or work gated by tests (use verify-before-done)."
license: MIT
metadata:
  category: "agent-operations"
  version: "3.0.0"
---

# Critic Review Loop

First drafts are rarely final. A reviewer with fresh context catches what the author's reasoning hides; the rubric keeps both honest.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `work` | required | — | "implement the caching layer" (do + review) or `src/auth/` (review existing) |
| `mode` | optional | inferred | `do-and-review` · `review-existing` · `doubt` (argue against one decision) · `panel` (several lenses) |
| `rubric` | optional | built from the task type (REFERENCE.md) | 4–6 measurable criteria |
| `gate` | optional | 8/10 | 9 for security-critical work |
| `min_rounds` | optional | 2 | 1 for "quick" |
| `max_rounds` | optional | 4 | 2 for "quick"; never exceed without user consent |
| `reviewer_tier` | optional | equal to or stronger than the worker | most capable for concurrency, security, finance |

Phrases map to settings: "quick/fast" → min 1, max 2, gate 6; "strict/thorough" → min 2, gate 8+; "gate 9", "max 5 loops", "reasoning reviewer" set the obvious fields.

## Output

- The revised work.
- A loop report ([templates/loop-report.md](templates/loop-report.md)): score per round, key issues and actions, critiques rejected with evidence, final score, and anything knowingly left unresolved.

## Supporting files

- [REFERENCE.md](REFERENCE.md): rubric starters per task type, score anchors, reviewer tier pairing, stall handling, panel lenses, doubt-pass procedure. Read when building the rubric.
- [templates/critic-brief.md](templates/critic-brief.md): the brief for the reviewer (task, rubric, anchors, prior findings, return format).
- [templates/loop-report.md](templates/loop-report.md): report format.
- [scripts/loop-decide.py](scripts/loop-decide.py): reads the scores so far and prints `continue`, `stop: gate met`, `stop: max rounds`, or `escalate: stalled` (exit 10 / 0 / 0 / 20). Run: `python3 scripts/loop-decide.py --gate 8 --min 2 --max 4 6 7 7`, adding `--same-top-issue` when the latest critique's top issue matches the previous one; or pass saved critiques with `--from-file critic-round-*.md`.

## Steps

1. **Check fit**: clear acceptance criteria exist (if not, define them first, or use `write-spec`). Tiny or exploratory tasks: skip the loop.
2. **Build the rubric** before working: 4–6 criteria specific to *this* task and checkable from the output ("every endpoint returns 401 without a token", not "secure"). Start from REFERENCE.md's table for the task type. Fix `gate`, `min_rounds`, `max_rounds`.
3. **Produce the work** (`do-and-review`) as a genuine best attempt, or read the existing work (`review-existing`).
4. **Dispatch a fresh reviewer** with [templates/critic-brief.md](templates/critic-brief.md): task summary, rubric, score anchors, the work itself (files, diff, or document), and from round 2 on, the list of earlier findings with their status so it does not re-raise fixed items. Never include your reasoning or intent. No sub-agent available → open a fresh context and paste only the brief and work.
5. **Parse the result**: `Score: N/10`, issues tagged Critical / Important / Minor with locations and fixes. Post one line to the user: `Round 2/4: 7/10 - missing TTL eviction; N+1 in list endpoint`.
6. **Decide** with `scripts/loop-decide.py` (or by hand, in this order): fewer than `min_rounds` → continue; score ≥ `gate` → stop; rounds = `max_rounds` → stop; no improvement on the previous round with the same top issue → escalate; two rounds in a row without improvement (last three scores flat or falling) → escalate; otherwise continue.
7. **Revise in a targeted way**: fix Critical and Important issues; Minor ones if cheap. Do not rewrite wholesale; keep a list of every earlier finding to avoid regressions. If a critique is wrong, show the evidence (test, code, source) in the next brief and in the report; do not apply it and do not lower the gate to compensate.
8. **Escalate on a stall**: split the task and loop on the parts, use a stronger worker, or (with the user's agreement) accept a lower gate and record the gap.
9. **Final pass** after stopping: trivial Minor fixes, remove revision leftovers, check coherence; run tests if code.
10. **Report** with the template.

### Variants

- **doubt**: before committing to a non-trivial decision (library choice, schema, architecture), give a fresh reviewer the decision, context, and alternatives, and ask for the strongest case against it plus what evidence would change the decision. Adopt changes only if the argument survives your check.
- **panel**: 2–3 reviewers in parallel, each with a different lens (security, user experience, maintainability, performance) and its own short rubric; merge findings, dedupe, and resolve conflicts explicitly.

## Checkpoints

- Rubric shown to the user before round 1 when stakes are high.
- Never run past `max_rounds` without the user's consent.

## Worked example

Task: "add caching to `getPrices()`; use a review loop, gate 8". Rubric: correct invalidation on price update; TTL configurable with sane default; bounded memory (eviction); no stale reads after write in the same request; tests cover hit, miss, expiry, invalidation.

```
Round 1/4: 5/10 - no eviction (unbounded Map); no invalidation on update; tests miss expiry
Round 2/4: 7/10 - LRU added; invalidation added; Important: cache key ignores currency
Round 3/4: 9/10 - Minor: magic number 300 for TTL → named constant
Result: 9/10 in 3 rounds. Rejected: "use Redis" (out of scope: single-instance service, noted in brief).
```

## Pitfalls

- Reviewing your own work in the same context (anchoring) and calling it a critique.
- Vague rubrics ("good quality") that produce vague, inflated scores.
- Reviewer weaker than the worker, so subtle issues pass.
- Re-raising fixed issues because prior findings were not passed in.
- Applying every critique blindly, or dismissing inconvenient ones without evidence.
- Chasing a 10: the gate is the goal; extra rounds cost time.

## Done when

- [ ] Rubric with task-specific, checkable criteria was set before the first review.
- [ ] Each round used a fresh reviewer that saw only the brief and the work.
- [ ] The loop stopped on the gate, the round limit, or an escalation decision.
- [ ] Critical and Important findings are fixed or rejected with evidence.
- [ ] The loop report lists scores per round, actions, rejections, and open items.
