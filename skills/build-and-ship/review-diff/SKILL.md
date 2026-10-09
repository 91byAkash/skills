---
name: review-diff
description: "Review a diff on two axes, Spec (built what was asked) and Standards (conventions, correctness, security, performance), with severity-labelled findings; also brief a fresh reviewer or act on review comments. Use when asked to \"review this PR/diff/branch\", before merging, or when review feedback arrives. Not for writing the PR text (use pr-description); security audits: use security-hardening."
license: MIT
metadata:
  category: "build-and-ship"
  version: "3.0.0"
---

# Review a Diff

Two axes, reported side by side: a change can follow every standard and build the wrong thing, or build the right thing and break every convention. Keep them separate so one cannot mask the other.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `base` | yes (ask if missing) | – | `main`, `origin/main`, a SHA, `HEAD~5` |
| `head` | optional | `HEAD` | `feat/scheduled-posts` |
| `spec` | optional | found from commit messages (`#123`, `Closes #45`), a passed path, or `docs/`/`specs/` matching the branch | `docs/specs/…-design.md` |
| `standards` | optional | every coding-standards doc found (CODING_STANDARDS.md, CONTRIBUTING.md, style guides, lint config) | `docs/standards.md` |
| `mode` | optional | `review` | `request` (brief a fresh reviewer), `receive` (act on feedback) |
| `review_focus` | optional | the plan's "Gaps the spec leaves open" list if any | "deleted post after scheduling" |
| `format` | optional | `full` | `terse` (one line per finding) |

## Output

```
## Spec
- Missing/partial: <requirement> - "<spec line>" - <where>
- Not asked for (scope creep): <behaviour> - <file:line>
- Implemented wrong: <requirement> - <why> - <file:line>
## Standards
<file>:L<line>: <severity> <problem>. <fix>.
...
## Verification story
Tests run / build / manual check / screenshots: <present | missing>
## Summary
Spec: N findings, worst = <...>. Standards: M findings, worst = <...>. Verdict: Approve | Request changes
```
Severity labels: `Critical:` (blocks merge: security hole, data loss, broken behaviour), no prefix = Required, `Consider:` (optional), `Nit:` (style, ignorable), `FYI` (no action), `Q:` (genuine question). A fresh reviewer briefed in `request` mode reports Critical / Important / Minor (the scale `implement-plan` grades by); Important = Required, Minor = Consider or Nit.

## Supporting files

- [REFERENCE.md](REFERENCE.md): five-axis checklist, smell baseline with fixes, structural remedies, change-size thresholds, dependency-upgrade review, disagreement hierarchy. Read before reviewing anything non-trivial.
- [templates/reviewer-brief.md](templates/reviewer-brief.md): the brief to hand a fresh reviewer (sub-agent or human) in `request` mode.

## Steps: review mode

1. **Pin the range.** `git rev-parse <base>` must succeed. Diff with three dots so it is against the merge-base: `git diff <base>...<head> --stat` then `git diff <base>...<head>`; commits: `git log <base>..<head> --oneline`. If the ref is bad or the diff is empty, then stop and say so.
2. **Find the spec** (order: commit references → passed path → spec file matching branch/feature → ask). If there is none, then the Spec axis reports "no spec available".
3. **Find the standards.** Collect every doc describing how code should be written. Add the smell baseline from REFERENCE.md: repo standards override it, and smells are always judgment calls. Skip anything tooling already enforces.
4. **Check size.** ~100 changed lines: fine. ~300: acceptable if one logical change. ~1000: ask to split (stack, by file group, horizontal stubs first, or vertical slices). Refactor + feature in one change → ask to separate. Also flag files pushed past ~1000 total lines with no decomposition.
5. **Read the tests first.** Do they test behaviour rather than internals? Edge cases? Would they catch a regression? Check by experiment when cheap: invert one condition the change adds, run the tests, restore. A mutation that stays green means a missing test; name it.
6. **Spec axis.** Missing or partial requirements, behaviour nobody asked for, and requirements implemented wrongly, each quoting the spec line. Where the spec is silent, judge by what a reasonable user would expect; silence is not permission to crash.
7. **Standards axis.** Walk each file for: correctness (edge cases, error paths, off-by-one, null, concurrency), readability (names, nesting, dead code), architecture (fits existing patterns, coupling, feature logic in shared modules, duplicates of canonical helpers), security (input validation at boundaries, injection, authz checks, secrets, untrusted external data), performance (N+1, unbounded loops or queries, missing pagination). Name a concrete remedy for every structural finding. Then take each `review_focus` item in turn and report it as a finding or as "covered by `<test name>`".
8. **Dead code.** List code the change made unused and ask before deleting it.
9. **Check the verification story**: tests run, build passed, manual check, screenshots for UI, before/after numbers for perf claims.
10. **Write the report** in the Output format (`format=terse`: one line per finding, rules in REFERENCE.md "Terse format"). Do not merge or re-rank across axes. Order within an axis by leverage: correctness and security first, nits last. Quantify where possible ("adds one query per row, ~50 ms per 100 rows").
11. **Declined to judge.** List anything you noticed but set aside as out of scope, one line each, so the author decides.

## Steps: request mode

1. Get `BASE=$(git merge-base <base> <head>)` (or the task's start commit) and `HEAD=$(git rev-parse <head>)`, using the `base`/`head` inputs.
2. Fill [templates/reviewer-brief.md](templates/reviewer-brief.md): what was built, the requirements/plan path, base/head, review focus. Give the reviewer the brief, never your session history.
3. Act on findings: Critical now, Important before proceeding, Minor noted (then follow receive mode for each item). Push back with evidence where the reviewer is wrong.

## Steps: receive mode

1. Read all feedback before reacting. Restate each item as a technical requirement.
2. If any item is unclear, ask about those items before implementing any of them (items are often related).
3. For each item verify against the codebase: correct for this stack? breaks existing behaviour? is there a reason for the current code? does the reviewer have full context?
4. "Implement it properly" for a feature: check actual usage first; if unused, propose removing it instead.
5. Implement in order: blocking (breakage, security) → simple fixes → complex refactors; test each; run the suite at the end.
6. Respond with the technical change ("Fixed: null guard added in `loadUser`, test `returns 404 for unknown id`") or reasoned pushback. No "You're absolutely right!", no "Great point!".

## Checkpoints

- Range resolves and the diff is non-empty before reviewing.
- Every finding has location, problem, fix, and severity.
- Spec findings quote the spec; standards findings cite the rule or name the smell.
- No finding contradicts a documented repo standard.

## Worked example

Range `main...feat/scheduled-posts`, spec `docs/specs/2026-10-08-scheduled-posts-design.md`, 240 lines changed.
```
## Spec
- Missing: "author can cancel a scheduled post" - no endpoint or UI found.
- Not asked for: `src/posts/schedule.ts:88` adds recurring schedules.
## Standards
src/workers/publishDue.ts:L31: Critical: two workers can publish the same post; select is not locked. Use `FOR UPDATE SKIP LOCKED` or an atomic status update.
src/workers/publishDue.ts:L47: errors from publishPost are caught and dropped. Log with post id and rethrow so the job retries.
src/posts/routes.ts:L12: Consider: `publishAt` is a string throughout (possible Primitive Obsession). Parse once into a Date at the boundary.
tests/workers/publishDue.test.ts: inverting `<=` to `<` in the due check stays green; add a test for publish_at == now.
## Verification story
Unit tests listed; no manual run of the worker against a DB.
## Summary
Spec: 2 findings, worst = cancel missing. Standards: 4, worst = double publish. Verdict: Request changes.
```

## Pitfalls

- "LGTM" with no evidence of reading; or softening a real bug as "minor concern".
- Reviewing only whether tests pass.
- Burying one critical issue under twenty nits.
- Merging the two axes into one ranked list.
- Flagging style that a formatter or linter already enforces.
- Accepting "I'll clean it up later"; require it now or a filed issue.
- In receive mode: implementing half the items while others are unclear, or agreeing performatively.

## Done when

- [ ] Range, spec source, and standards sources stated.
- [ ] Both axes reported (or Spec marked "no spec available").
- [ ] Every finding is located, labelled, and has a fix; structural ones name a remedy.
- [ ] Verification story checked; declined-to-judge list included.
- [ ] Verdict and the worst finding per axis given.
