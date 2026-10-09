---
name: delegate-to-subagents
description: "Delegate work to sub-agents with isolated context: parallel fixes or research, read-only codebase scouting, or executing a plan task by task with an implementer and reviewer per task and a ledger. Use when there are 2+ independent problems, a plan is ready to execute, or searching would flood the context. Not for tightly coupled changes (use implement-plan) or trivial work."
license: MIT
metadata:
  category: "agent-operations"
  version: "3.0.0"
---

# Delegate to Sub-agents

A sub-agent knows only what its brief says. Write briefs as files, keep results as files, and trust evidence over summaries.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `mode` | optional | inferred | `fan-out` (independent problems in parallel) · `scout` (read-only search) · `plan` (task-by-task execution) |
| `work` | required | — | 3 failing test files; `docs/plans/billing.md`; "where is rate limiting applied?" |
| `spec` | optional | the plan's linked spec | `docs/specs/billing.md` (the binding authority when the plan is ambiguous) |
| `workspace` | optional | git-ignored `.agent-work/<plan-slug>/` | briefs, reports, review packages, ledger |
| `max_parallel` | optional | 3–4 | 6 for read-only scouts |
| `fix_rounds` | optional | 5 per task | 3 |
| `models` | optional | cheapest tier that fits each role (see REFERENCE.md) | — |

## Output

- `fan-out` / `scout`: integrated changes or findings, each verified; a short summary with evidence (test output, `path:line` references).
- `plan`: every task committed and reviewed, a `ledger.md` recording completion, rulings, and deferred findings, a final whole-branch review, and a summary.

## Supporting files

- [REFERENCE.md](REFERENCE.md): independence test, model/tier selection, status handling, fix-loop rules, rulings, review package contents, waiting on agents, output contracts, ledger recovery. Read before `plan` mode.
- [templates/brief-implementer.md](templates/brief-implementer.md), [templates/brief-reviewer.md](templates/brief-reviewer.md), [templates/brief-investigator.md](templates/brief-investigator.md): dispatch briefs with return contracts.
- [templates/ledger.md](templates/ledger.md): progress ledger format.
- [scripts/task-brief.sh](scripts/task-brief.sh): extracts task N from a plan file into the workspace (code blocks kept intact; `.agent-work/` added to `.git/info/exclude`): `scripts/task-brief.sh PLAN N [WORKSPACE]`.
- [scripts/review-package.sh](scripts/review-package.sh): writes commit list, stat, and full diff for a range to one file for the reviewer: `scripts/review-package.sh BASE HEAD [WORKSPACE]`.

## Steps

### fan-out and scout

1. **Partition** by domain (one test file, one subsystem, one question). Independence test: no shared files, no shared mutable state, no ordering, and fixing one is unlikely to fix another. Related failures → investigate together first.
2. **Write one brief per agent** from the templates: one-line goal; the context it needs (error output, test names, paths, decisions); scope (what to touch, what not to); done-when (commands to run); return contract (format, length, `path:line` evidence). Never "fix all the tests".
3. **Dispatch together** (all calls in the same turn) up to `max_parallel`. Read-only scouts can take different angles: definitions, callers, tests, config.
4. **Keep working** while they run (prepare integration, read code). Wait in bounded stretches; check for agents that finished without reporting.
5. **Verify each result**: read the diff or cited lines, check the test output; a success summary alone is not evidence.
6. **Integrate one at a time**, run the full suite after each, resolve conflicts. Gaps get a new, narrower brief rather than a silent fix.

### plan

1. **Set up**: isolated branch or worktree (never implement on the main branch without consent); create `workspace`; check for an existing ledger. If its first line names this plan, tasks marked complete are done; resume at the first incomplete task. After any context loss, trust the ledger and `git log` over memory.
2. **Pre-flight scan** of the plan: for each pair of tasks sharing a file or interface, what one produces vs what the other consumes; for each task, whether its tests match its code and files. Write the table to the ledger; rule on each conflict (spec wins) and record the ruling.
3. **Batch** tiny same-shape tasks (the same one-line change across files) into one dispatch.
4. **Per task**:
   1. Record `BASE=$(git rev-parse HEAD)`; run `scripts/task-brief.sh PLAN N <workspace>` and read the brief it prints: it must hold the whole task, code blocks included.
   2. Dispatch one implementer on the tier `models` gives for implementers (never two in parallel on the same branch) with: where the task fits, the brief path ("your requirements; exact values are here"), interfaces from earlier tasks, your resolution of ambiguities, the report path and return contract, and "do not dispatch sub-agents".
   3. Handle the status: `DONE` → review; `DONE_WITH_CONCERNS` → read concerns, address correctness/scope ones first; `NEEDS_CONTEXT` → supply and re-dispatch; `BLOCKED` → more context, a more capable model, a smaller task, or a recorded plan correction. Never re-run unchanged.
   4. Review: `scripts/review-package.sh $BASE HEAD <workspace>`; dispatch a reviewer with the brief, report, package, and the binding constraints copied verbatim. Require both verdicts: spec compliance and quality. Do not pre-judge findings for the reviewer.
   5. Fix loop for spec failures, Critical/Important findings, or confirmed gaps, up to `fix_rounds` rounds: the first three (or all, if `fix_rounds` ≤ 3) resume the same implementer with findings verbatim; any later rounds use a fresh implementer on a stronger model. Still failing after the last round → treat as `BLOCKED` (step 3). Each round: fix, rerun covering tests, append to the report, scoped re-review. Minor findings go to the ledger as deferred.
   6. Ledger: `Task N: complete (<commit>)`, plus any rulings.
5. **Do not pause between tasks** for check-ins. Stop only for: irreversible or destructive operations, security-sensitive actions, side effects outside the branch (merge, push to shared branches, publish), or a plan so broken every path is a guess. Everything else gets a ruling: `Ruling: <decision> - <why> - <cost if wrong>`.
6. **Final review** of the whole branch on the most capable model, pointing it at the deferred-findings list. One fix dispatch, one re-review, then adjudicate what remains.
7. **Finish**: full test suite green, summary with commits, rulings, and residual risks; hand off to `finish-branch`.

## Checkpoints

- Before dispatch: each brief stands alone (could a stranger do it with just this file?).
- Before marking a task complete: both review verdicts present and every "cannot verify from diff" item resolved by you.
- Before finishing: full suite run by you, not only by sub-agents.

## Worked example

Three failing files after a refactor: `abort.test.ts` (timing), `batch.test.ts` (wrong count), `approval.test.ts` (race). Independent subsystems → fan-out.

Brief for agent 1 (excerpt):
```
Goal: make the 3 failing tests in src/agents/abort.test.ts pass.
Failures: "captures partial output" expects 'interrupted at' in message; ...
Scope: src/agents/abort.ts and its test only. Do not raise timeouts; replace sleeps with event-based waits if timing is the cause.
Done when: `for i in $(seq 10); do pnpm vitest run src/agents/abort.test.ts || exit 1; done` passes (10 runs in a row).
Return: root cause (2 lines), files changed, test output tail.
```
Results: agent 1 fixed a missing await in abort cleanup; agent 2 changed a test expectation that encoded old behaviour (verified against spec); agent 3 fixed a shared counter race. Integrated one by one; full suite 412/412.

## Pitfalls

- Vague or context-free briefs; pasting the whole session history into briefs.
- Two agents editing the same files; parallel implementers on one branch.
- Accepting "done" without diff and test evidence.
- Implementers spawning their own reviewers (duplicate cost, no authority).
- Omitting the model choice, so every agent runs on the most expensive tier.
- Stopping after every task to ask "should I continue?".
- Losing progress after context compaction because no ledger was kept.

## Done when

- [ ] Every delegated unit had a standalone brief with done-when and a return contract.
- [ ] Every result was verified against its diff or cited evidence.
- [ ] (plan) Ledger lists every task complete with commit, plus rulings and deferred findings; final review done.
- [ ] Changes integrated and the full test suite passes in the main context.
