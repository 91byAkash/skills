---
name: diagnose-bug
description: "Find the root cause of a bug, failing test, crash, flaky test or performance regression with a red feedback loop, ranked hypotheses and a regression test. Use when something is broken, throwing, slow or intermittent, the user says \"debug this\" or \"why is this failing\", or a fix did not work. Not for new features (use implement-plan) or planned restructuring (use safe-refactor)."
license: MIT
metadata:
  category: "engineering-workflows"
  version: "3.0.0"
---

# Diagnose a Bug

Scope: bugs, failing or flaky tests, crashes, performance regressions.

No fix without a root cause, and no root cause without a loop that goes red on this exact bug. Build the loop first; everything after it is mechanical.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `symptom` | yes | – | "Export button returns 500 for accounts with >1000 rows" |
| `expected` | optional | inferred from spec/tests | "CSV downloads within 5 s" |
| `environment` | optional | local dev | staging URL, CI job link, OS/browser versions |
| `artifacts` | optional | none | stack trace, HAR file, log excerpt, core dump, screen recording |
| `known_good` | optional | none | last good commit/tag/version, for bisection |
| `fix_allowed` | optional | `yes` | `no` = investigate and report only |
| `debug_tag` | optional | `[DEBUG-<4 random hex>]` | `[DEBUG-a4f2]` |

## Output

- **Loop command** (already run, output shown, secrets redacted) that is red on the bug.
- **Root-cause statement**: "X happens because Y, introduced by Z", with the evidence that proved it.
- **Fix** at the narrowest responsible layer plus a regression test at a correct seam (or a note that no correct seam exists and why).
- **Cleanup confirmation**: debug logs removed (grep for the tag returns nothing), throwaway harnesses deleted.
- Commit/PR message stating the confirmed hypothesis.

## Supporting files

- [REFERENCE.md](REFERENCE.md): loop-construction catalog, root-cause tracing, multi-component boundary logging, condition-based waiting for flaky tests, defense-in-depth, performance branch, red-flag thoughts. Read when you cannot build a loop, the bug is intermittent, or the error is deep in a call chain.
- [scripts/repro-rate.sh](scripts/repro-rate.sh): run a command N times (optionally in parallel) and report the failure rate. Use for flaky bugs and to prove a fix.
- [scripts/find-polluter.sh](scripts/find-polluter.sh): run test files one by one to find which one leaves a given file or state behind.
- [scripts/hitl-loop.sh](scripts/hitl-loop.sh): template that drives a human through reproduction steps and prints captured answers as KEY=VALUE. Last resort when a human must click.

## Steps

0. **Redact.** Before showing any output, replace secrets with `<REDACTED>`; keep credentials in env vars used by the loop.

1. **Build the feedback loop.** Try, in roughly this order: failing test at the closest seam → HTTP/curl script against a dev server → CLI run with fixture diffed against a known-good snapshot → headless browser script → replay a captured request/event → throwaway harness around one function → property/fuzz loop → bisection harness (`git bisect run <loop>`) → differential run (old vs new version/config) → human-in-the-loop script.
   Tighten it: faster (skip unrelated setup), sharper (assert the exact symptom, not "no crash"), deterministic (pin time, seed randomness, isolate filesystem and network).
   **Gate**: one command you have run that is red-capable (asserts the user's symptom), deterministic (or a pinned high reproduction rate), fast (seconds), and agent-runnable. If you are reading code to build a theory before this exists, stop.
   If you genuinely cannot build one: say so, list what you tried, and ask for access to the failing environment, a redacted artifact, or permission for temporary instrumentation. Do not guess-fix.
2. **Reproduce and minimise.** Confirm the loop shows the user's failure, not a neighbouring one, and that it repeats. Capture the exact symptom. Then remove inputs, callers, config, data and steps one at a time, re-running after each cut, until every remaining element is load-bearing.
3. **Read the evidence you already have.** Everything in `artifacts`; full error message and stack trace (file, line, code); the `environment` it fails in versus where your loop runs; recent changes (`git log -p --since=…`, dependency and config diffs); a similar working path in the codebase and every difference between it and the broken one. If `known_good` is given and the loop exits non-zero on the bug, bisect before hypothesising: `git bisect start HEAD <known_good> && git bisect run <loop command>` (exit 125 = skip an unbuildable commit), then `git bisect reset`.
4. **Hypothesise.** Write 3-5 ranked, falsifiable hypotheses: "If X is the cause, then changing Y makes the bug disappear (or Z makes it worse)." Show the list to the user before testing (they may re-rank instantly); continue if they are away.
5. **Instrument.** Each probe tests one prediction; change one variable at a time. Prefer a debugger/REPL breakpoint, then targeted logs at the boundaries that distinguish hypotheses, tagged with `debug_tag`. Never log everything and grep. For multi-component systems, log what enters and leaves each boundary once to find the failing layer. For deep stack errors, trace the bad value backward to where it originated. For performance, measure a baseline first (timer, profiler, query plan) and bisect; logs mislead.
6. **Confirm the mechanism.** Do not edit product code until one mechanism explains all the evidence. If `fix_allowed` is no, then report cause and proof and stop.
7. **Regression test first**, only at a correct seam (one that exercises the real bug pattern as it happens at the call site). Turn the minimised repro into a failing test; watch it fail; if you forced red by mutating code or fixtures, diff against a pristine copy to prove it. If no correct seam exists, record that as a finding (architecture is preventing lock-down; see `improve-architecture`).
8. **Fix narrowly.** Change the layer that owns the wrong behaviour; preserve unrelated behaviour and the user's uncommitted changes; no renames, cleanup, or abstractions outside the fix. Add validation at other layers only where the bug could re-enter (defense-in-depth).
9. **Verify.** Test passes; original un-minimised loop is green; nearby tests and the affected gate pass; for flaky bugs, `scripts/repro-rate.sh` shows 0 failures over at least as many runs as it took to see the failure 5 times.
10. **If the fix did not work:** count attempts. Under 3: return to step 3 with the new evidence. At 3 or more failed fixes, or if each fix reveals a new problem elsewhere, stop and discuss the architecture with the user before trying again.
11. **Clean up.** `git grep -n "<debug_tag>"` (or `grep -rn --exclude-dir=node_modules`) returns nothing, including untracked files you added (`git status`); throwaway harnesses deleted or moved to a marked debug folder; commit message states the confirmed hypothesis.

## Checkpoints

- After step 1: the loop command and its red output are shown.
- After step 2: a minimal repro where every element is load-bearing.
- After step 4: ranked hypotheses, each with a prediction.
- After step 9: green loop, passing regression test, failure rate 0 for flaky cases.

## Worked example

Symptom: "Export returns 500 for big accounts."
- Loop: `curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $TOKEN" localhost:3000/api/export?account=big-fixture` → `500` (redacted token in env). Small fixture → `200`.
- Minimise: 1001 rows fails, 1000 passes; filters, date range and user role are not load-bearing.
- Hypotheses: (1) query builder hits a 1000-item `IN (...)` limit → batching ids makes it pass; (2) response streaming times out → raising the timeout makes it pass; (3) memory limit → a smaller row payload passes at 1001.
- Probe: log `[DEBUG-7c1e] ids.length` and the DB error → `too many terms in IN clause (max 1000)`. Hypothesis 1 confirmed.
- Regression test at the export service seam with 1001 ids → fails; fix: chunk ids in 1000s inside the repository function → passes; curl → `200`; full suite green; `grep -rn "DEBUG-7c1e"` empty. Commit: `fix(export): chunk id lookups to stay under the DB IN-clause limit`.

## Pitfalls

- Reading code and theorising before a red loop exists.
- Fixing a nearby bug the loop happened to catch instead of the user's symptom.
- One hypothesis at a time, anchored on the first idea.
- Changing several things at once, or stacking fixes on a failed fix.
- Sleeps in tests to "fix" flakiness instead of waiting for the condition.
- Leaving untagged debug logs behind.
- A regression test at a seam too shallow to reproduce the real pattern (false confidence).

## Done when

- [ ] Red-capable loop shown, then green after the fix (original scenario).
- [ ] Root cause stated with the evidence that confirmed it.
- [ ] Regression test fails without the fix and passes with it, or missing seam documented.
- [ ] Nearby tests and affected gates pass; flaky cases show a 0 failure rate over enough runs.
- [ ] Debug instrumentation and throwaway harnesses removed; hypothesis recorded in the commit/PR.
