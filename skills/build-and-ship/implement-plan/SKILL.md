---
name: implement-plan
description: "Execute a written plan or ticket set task by task, test-first, with a progress ledger that survives context loss and recorded rulings instead of stalling, ending in a whole-branch review. Use when the user says \"implement this\", \"build ticket #42\", or \"execute the plan\". Not for work with no agreed plan (use plan-tasks) or fanning tasks out to sub-agents (use delegate-to-subagents)."
license: MIT
metadata:
  category: "build-and-ship"
  version: "3.0.0"
---

# Implement a Plan

The plan already did the thinking. Execute it exactly, prove each step with a test you watched fail and then pass, and leave a record that survives your own forgetting.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `plan` | yes | – | `docs/plans/2026-10-08-scheduled-posts.md`, ticket URL, list of local ticket files |
| `spec` | optional | the spec the plan links to | `docs/specs/…-design.md` |
| `branch` | optional | a new feature branch / worktree; never main without consent | `feat/scheduled-posts` |
| `ledger` | optional | `.work/<plan-basename>/progress.md` (git-ignored) | `.scratch/sched/progress.md` |
| `test_cmd` | optional | the plan's per-task commands; full suite from repo config | `npm test`, `pytest -q` |
| `typecheck_cmd` | optional | repo's typecheck/lint script if any | `npx tsc --noEmit` |
| `check_in` | optional | `none` between tasks; stop only for the four stop conditions | `per-task` |

## Output

- Commits on `branch`, one or more per task, following the plan's commit steps.
- `ledger` file: identity line, pre-flight rows, one `Task N: complete (...)` line per task, every `Ruling:` and deferred minor.
- Final message with: tasks completed, test evidence (command → result), **Rulings I made** (each with cost if wrong), **Deferred minors**, review outcome, next step (`finish-branch`).

## Supporting files

- [scripts/ledger.sh](scripts/ledger.sh): `init`, `start`, `done`, `rule`, `note`, `status` subcommands that maintain the ledger and only record a task complete if its test command passes. `init` git-ignores `.work/` locally (via `.git/info/exclude`); `status` prints the next incomplete task by reading the plan's task headings (`### 3. Name` from `plan-tasks`, or `### Task 3`). Works from any subdirectory. Use it from the first task.

## Stop conditions (the only reasons to pause and ask)

1. An irreversible or destructive operation (data deletion, force push, dropping tables).
2. A security-sensitive action (secrets, permissions, auth changes beyond the plan).
3. A side effect outside the workspace that needs permission (merge, push to a shared branch, publish, deploy).
4. A plan so broken that every way forward is a guess.

Everything else (ambiguity, small conflicts, plan typos) is a **ruling**: decide using the spec as the authority, record `Ruling: <decision> - <why> - <cost if wrong>`, and continue.

## Steps

1. **Set up.** Create or check out `branch` (default: a new feature branch or worktree named after the plan; never main without consent). Run `scripts/ledger.sh init <plan> [ledger]`.
   - If the ledger exists and its first line names this plan, then tasks with `Task N: complete` are done: trust the ledger and `git log` over memory, run `scripts/ledger.sh status`, and resume at the task it names as next incomplete.
   - If it names a different plan, leave it alone and start a fresh ledger path.
2. **Read once.** Read the plan and the spec. Note the plan's "Rules for every task" and "Gaps the spec leaves open" sections. If no spec is reachable, record that rulings are provisional.
3. **Pre-flight scan.** For every task that consumes what an earlier task produces, compare the Interfaces blocks. Record one row per pair with `scripts/ledger.sh note "..."` (`Pre-flight: T2 consumes install_hook, T1 produces installHook -> ruling: use installHook`), or `Pre-flight: no shared interfaces`.
4. **Per task:**
   1. `scripts/ledger.sh start <N>` (records BASE commit). Re-read this task's text; memory is a summary, the plan has exact values.
   2. Work the steps in order. Write the test first, run it, and confirm it fails for the expected reason. A test that passes before the code exists is a finding about the test.
   3. For every command with an expected output, compare real output:
      - matches → next step;
      - code is wrong → debug the cause (see `diagnose-bug`), never bend the code to the expected string;
      - plan is wrong → smallest change that satisfies the spec, `scripts/ledger.sh rule <N> "<ruling>"`, continue.
   4. Run single test files often and `typecheck_cmd` after each step that changes types. Redirect long output to a file and read the tail.
   5. Commit as the plan says.
   6. `scripts/ledger.sh done <N> -- <task test command>`: records completion only if the command exits 0.
   7. If `check_in=per-task`, post the ledger line and wait for the user before the next task; with the default `none`, continue.
5. **Completion contract per task** (all true, with evidence from this session): every named test exists and ran; the final run passed; every expected output was compared; every deviation has a ruling.
6. **Full suite** once after the last task (`test_cmd`), plus build/lint if the repo has them.
7. **Whole-branch review.** Use `review-diff` on `merge-base..HEAD`, by a fresh reviewer (sub-agent) if available, giving it the plan, spec, the plan's Gaps list as `review_focus`, and the ledger's rulings. If you can only self-review, say so in the final message.
8. **Grade findings by effect** (what a user would experience if it shipped), not by the reviewer's label:
   - Critical/Important → one fix pass; each fix starts with a failing test reproducing the finding, then the fix, then the whole suite green. Ledger `Final: fixed <finding> - <test> RED->GREEN, suite N/N`.
   - Minor → ledger `Final: minor (deferred): <one line>`; do not fix unasked.
   - Declining a finding → a ruling with cost if wrong.
9. **Report** using the Output format and hand off to `finish-branch`.

## Checkpoints

- Before task 1: on a non-main branch, ledger identity line written, pre-flight recorded.
- After each task: ledger line exists with commit range and test result.
- After step 6: full suite output read, not assumed.
- Before reporting: every ruling and deferred minor copied into the final message.

## Worked example

Plan: 4 tasks for scheduled posts.
```
$ scripts/ledger.sh init docs/plans/2026-10-08-scheduled-posts.md
ledger: .work/2026-10-08-scheduled-posts/progress.md (new)
$ scripts/ledger.sh start 1          # base 3f2a9c1
... write test, run: FAIL "publishPost is not exported" (expected) ...
... implement, run: PASS ...
$ git commit -m "refactor(posts): extract publishPost into service"
$ scripts/ledger.sh done 1 -- npm test -- posts
Task 1: complete (commits 3f2a9c1..8b41d07, tests: npm test -- posts -> exit 0)
```
Task 3's plan says `publishDue(now: string)` but Task 1 produced Date-based helpers:
`scripts/ledger.sh rule 3 "publishDue takes Date not string - matches Task 1 helpers - cost if wrong: one signature change"`.
Final review: one Important (worker swallows DB errors silently) → test `logs and rethrows on query failure` RED → fix → GREEN, suite 41/41. One Minor (naming) deferred.

## Pitfalls

- "I remember what task N says": re-read it; exact values live in the plan.
- Skipping the watch-it-fail step because the plan's code "is right".
- Deviating silently; an unrecorded deviation is a decision made in secret.
- Asking "should I continue?" after every task when the user chose continuous execution.
- Ledger updates batched "for later"; context loss does not wait.
- Fixing minors nobody asked for, or replacing the fresh review with re-reading your own diff.
- Working on main without consent.

## Done when

- [ ] Every task has a `complete` ledger line backed by a passing test command.
- [ ] Full suite (and build/typecheck if present) passed after the last task, output read.
- [ ] Whole-branch review done; Critical/Important fixed test-first; minors deferred in the ledger.
- [ ] Final message lists rulings (with cost if wrong), deferred minors, and evidence.
- [ ] Next step `finish-branch` named; scratch workspace removed only after the record is in git or the final message.
