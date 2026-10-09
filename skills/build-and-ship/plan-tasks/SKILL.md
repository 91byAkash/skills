---
name: plan-tasks
description: "Break a spec or agreed design into small, ordered, verifiable vertical slices with blocked-by edges, written as a plan file (files, signatures, tests, commands) or tracker tickets. Use when the user says \"break this down\", \"make tickets\", or \"write the implementation plan\" before coding starts. Not for open design questions (use idea-to-design) or executing the plan (use implement-plan)."
license: MIT
metadata:
  category: "build-and-ship"
  version: "3.0.0"
---

# Plan Tasks

A plan is the set of decisions an implementer cannot make alone: which files, which names and signatures, which values from the spec, which tests prove each task. Write those down; leave the obvious to the implementer.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `source` | yes | current conversation | `docs/specs/2026-10-08-scheduled-posts-design.md`, issue #88 |
| `format` | optional | `plan` | `plan` (one Markdown file), `tickets` (tracker issues), `local-tickets` (one file per ticket) |
| `plan_path` | optional | repo convention, else `docs/plans/YYYY-MM-DD-<feature>.md` | `plans/scheduling.md` |
| `tickets_dir` | optional (local-tickets) | `.scratch/<feature>/issues/` | `work/scheduling/` |
| `tracker_label` | optional | repo's "ready" label if used | `ready-for-agent` |
| `granularity` | optional | one task = one test cycle + one reviewable commit | "coarser: max 5 tasks" |
| `execution` | optional | ask the user after the plan is written | `self`, `subagents` |

## Output

- `plan`: one file per [templates/plan.md](templates/plan.md): a summary table (spec link, outcome, approach, stack), Rules for every task, Gaps the spec leaves open, Files touched, then numbered task blocks with the files touched, what each relies on and provides (exact signatures), and checkbox steps (red test → confirm it fails → implement → confirm it passes → commit).
- `tickets` / `local-tickets`: one ticket per slice per [templates/ticket.md](templates/ticket.md): the slice (end-to-end behaviour), what it waits on, and checkbox checks for done. Local files are numbered `01-<slug>.md` in dependency order.

## Supporting files

- [templates/plan.md](templates/plan.md): plan header and task block. Use for `format: plan`.
- [templates/ticket.md](templates/ticket.md): tracker issue and local-file ticket bodies. Use for ticket formats.

## Steps

1. **Gather.** Read the full source (body and comments for issues). Read glossary and ADRs in the area; use their vocabulary.
2. **Scope check.** If the source covers several independent subsystems, then propose one plan per subsystem and plan only the first.
3. **Map files and units** before tasks: which files are created or modified and what each is responsible for. One responsibility per file; files that change together live together; follow existing patterns. Note prefactoring that would make the change easy ("make the change easy, then make the easy change"); prefactor tasks go first.
4. **Draft vertical slices.** Each slice cuts a narrow but complete path through every layer it needs (schema, logic, API, UI, tests), is demoable or verifiable on its own, and fits one fresh session; size them to `granularity` (default: one test cycle plus one reviewable commit; if the user capped the count, merge adjacent slices that share a seam). Fold setup, config and docs into the slice that needs them. Split only where a reviewer could reasonably reject one piece and accept its neighbour.
5. **Handle wide refactors with expand-contract** (a mechanical change touching many call sites, e.g. renaming a column or retyping a shared symbol):
   - expand: add the new form beside the old; nothing breaks;
   - migrate: batches sized by blast radius (per package/directory), each its own task blocked by expand, CI green each time;
   - contract: delete the old form, blocked by every migrate batch;
   - if batches cannot be green alone, put them on a shared integration branch feeding one final integrate-and-verify task.
6. **Add blocked-by edges.** A task depends only on tasks that genuinely gate it. No cycles. Tasks with no blockers form the starting frontier.
7. **Review the breakdown with the user** as a numbered list: title, blocked by, what it delivers. Ask: granularity right? edges right? merge or split anything? Iterate until approved.
8. **Write the steps** (`plan` format). Each step is one action with a checkable result and lets the implementer write exactly one reasonable thing:
   - test step: test name + assertions as code, using the spec's exact values;
   - code step: file, exact signature (name, params, return type), pinned values; a body only for an algorithm the signature and test do not determine;
   - verification step: the command and the output that means pass (e.g. `pytest tests/test_x.py::test_y -v` → `1 passed`);
   - cross-task reference: point to the other task's Relies on / Provides lines; do not repeat its code.
9. **Fill Rules for every task** (version floors, dependency limits, naming/copy rules, platform requirements, exact values copied from the spec) and **Gaps the spec leaves open** (up to five inputs or failure modes the spec implies but no test covers yet, most likely first; then add a test for each to the owning task).
10. **Self-review** and fix inline:
    - coverage: every spec requirement maps to a task;
    - step scan: no step that decides nothing ("handle edge cases", "add validation", "TBD"), no full bodies the tests already determine;
    - type consistency: names and signatures match across tasks (`clearLayers()` vs `clearAllLayers()` is a bug);
    - gaps: each line under Gaps the spec leaves open names the task whose test pins it;
    - proportion: if the plan is several times longer than the spec, or mostly code, cut bodies back to signatures and assertions.
11. **Publish.** `plan`: save to `plan_path`. `local-tickets`: write `tickets_dir/NN-<slug>.md` files numbered in dependency order (blockers get lower numbers). Tickets: create in dependency order (blockers first) so edges reference real ids; use native blocking links where the tracker has them; make them sub-issues of the source issue if there was one; never close or edit the parent.
12. **Hand off.** Link the plan and ask the user to review it and, unless `execution` was given, choose execution: `self` (one session implements all tasks, one review at the end; cheaper) or `subagents` (fresh implementer + reviewer per task; more thorough). Recommend one in a sentence (task coupling, count, cost of a shipped mistake). Next skill: `implement-plan` or `delegate-to-subagents`.

## Checkpoints

- After step 4: every slice touches every layer it needs; no "backend only" slice unless it is a prefactor or wide-refactor batch.
- After step 7: user approved the breakdown.
- After step 10: zero placeholder lines; each task ends with a runnable verification command.

## Worked example

Spec: scheduled posts (DB column + polling worker).

Breakdown shown to the user:
1. Prefactor: extract `publishPost(postId)` from the controller into the posts service. Blocked by: none. Delivers: same behaviour, callable from a worker.
2. Schedule a post via API. Blocked by: 1. Delivers: `POST /posts/:id/schedule {publishAt}` stores `publish_at`, post shows as "Scheduled".
3. Worker publishes due posts. Blocked by: 2. Delivers: a post scheduled one minute ahead goes live within 60 s.
4. Edit/cancel schedule in UI. Blocked by: 2. Delivers: author changes or clears the time from the editor.

Task 3 in the plan:
```markdown
### 3. Publish due posts
Touches: new `src/workers/publishDue.ts` · test `tests/workers/publishDue.test.ts`
Relies on: `publishPost(postId: string): Promise<void>` (task 1). Provides: `publishDue(now: Date): Promise<number>` (count published).
- [ ] Write failing test `publishes posts whose publish_at <= now and skips future ones` (two posts, now = 2026-10-08T10:00Z, expect 1 published)
- [ ] Run `npm test -- publishDue` → expect FAIL "publishDue is not a function"
- [ ] Implement `publishDue(now)`; select with `FOR UPDATE SKIP LOCKED` so two workers never publish the same post
- [ ] Run `npm test -- publishDue` → expect PASS
- [ ] Commit `feat(posts): publish scheduled posts from worker`
```
Gaps line: "Post deleted after scheduling → worker skips it without error" → test added to Task 3.

## Pitfalls

- Horizontal slices ("all the schema", "all the API") that cannot be verified alone.
- Steps that decide nothing, or that paste the whole implementation.
- Edges that encode preference rather than real dependency, serializing work needlessly.
- Forcing a wide refactor into one green slice instead of expand-contract.
- File paths and snippets in tracker tickets (they go stale); keep those for the plan file.
- Publishing tickets before the user approves the breakdown.

## Done when

- [ ] Breakdown approved by the user.
- [ ] Every spec requirement maps to a task; Gaps the spec leaves open filled (or "Checked: none found").
- [ ] Every task lists files touched, what it relies on and provides, and steps ending in a verification command with expected output (plan), or checks for done and what it waits on (tickets).
- [ ] Self-review passed with no placeholders and consistent names.
- [ ] Plan saved / tickets created in dependency order; location reported; execution method requested.
