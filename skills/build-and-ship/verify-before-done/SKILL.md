---
name: verify-before-done
description: "Get fresh evidence (run the proving command now, read the full output) before claiming work is done, fixed, passing or ready, and report PASS/FAIL/UNAVAILABLE exactly. Use when about to send a \"done\" message, commit, PR or hand-off, after a sub-agent reports success, or when asked to \"check this meets the acceptance criteria\". Not for reviewing code quality (use review-diff)."
license: MIT
metadata:
  category: "build-and-ship"
  version: "3.0.0"
---

# Verify Before Done

Evidence before claims. If you have not run the proving command since the last change, you cannot say it passes.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `claim` | yes | – | "the login bug is fixed", "task 3 complete", "PR ready" |
| `acceptance` | optional | the plan/ticket/spec criteria for the work | ticket checklist, spec user stories |
| `commands` | optional | discovered from repo scripts/CI config | `npm test`, `cargo build --release`, `ruff check .` |
| `scope` | optional | `focused-then-wide` | `focused-only` for a one-file change, `full` before merge |
| `fix_allowed` | optional | `no` for validation-only requests; `yes` when checking your own in-progress work | `yes` |

## Output

A verification report in chat (and in the PR/ticket if relevant):

```
Claim: <claim>
| Check | Command | Result | Evidence |
|---|---|---|---|
| Unit tests | npm test | PASS | 128 passed, 0 failed (exit 0) |
| Typecheck | npx tsc --noEmit | PASS | exit 0, no output |
| Original symptom | curl -i localhost:3000/login ... | PASS | 302 → /dashboard (was 500) |
| E2E | npm run e2e | UNAVAILABLE | no browser in this environment |
Status: VERIFIED | NOT VERIFIED | PARTIAL (list what is unproven)
Risks: <anything unproven or flaky>
```

## The gate

1. **Identify** the command(s) that would prove the claim (table below).
2. **Run** them fresh and complete, after the last code change.
3. **Read** the whole output: exit code, failure count, warnings, skipped tests.
4. **Compare** with the claim. If the output does not confirm it, report the actual status with the evidence.
5. **Only then** state the claim, with the evidence attached.

## What proves what

| Claim | Proof required | Not enough |
|---|---|---|
| Tests pass | test command output with 0 failures and the count | an earlier run, "should pass" |
| Lint clean | linter output with 0 errors | a partial run, extrapolation |
| Build succeeds | build command exit 0 | lint passing, "logs look fine" |
| Types check | typecheck command exit 0 | tests passing (many runners skip type checks) |
| Bug fixed | reproduce the original symptom → now correct | code changed, assumed fixed |
| Regression test works | red-green: test fails with fix reverted, passes with fix | test passes once |
| Sub-agent finished | inspect the diff/files yourself and rerun its checks | the agent's success message |
| Requirements met | checklist of each criterion with evidence per line | "tests pass" |
| Performance improved | before/after measurements with the same method | "should be faster" |
| UI works | screenshot or browser test of the actual flow | component renders in a unit test |

## Steps

1. **List criteria.** Pull acceptance criteria from the ticket/plan/spec into a checklist. If none exist, write the 2-5 observable conditions implied by the claim and show them.
2. **Find commands.** Read `package.json` scripts, `Makefile`, `pyproject.toml`, CI workflow files; prefer the exact commands CI runs.
3. **Reuse only if current.** A previous result counts only if no file changed since (same commit, clean tree: `git status --porcelain` empty and `git rev-parse HEAD` unchanged).
4. **Run focused, then wide.** First the narrow check for the change (single test file, the reproduction), then the wider gate per `scope`: `focused-only` stops after the narrow check; `focused-then-wide` adds the full suite plus typecheck and lint; `full` also runs the build and any e2e/CI-only jobs you can run locally.
5. **Classify each result exactly:**
   - PASS: ran, exit 0, output confirms.
   - FAIL: ran and output contradicts the claim (quote the failing lines).
   - UNAVAILABLE: tool or environment missing (say what is missing).
   - BLOCKED: could not run because of a prior failure or missing access.
   - FLAKY: passed and failed across runs without code change (run up to 3 times; report counts).
6. **If FAIL and `fix_allowed` is no**, stop and report. If yes, fix, then restart from step 4.
7. **Check the regression test** for bug fixes: revert only the fix, never the test. Uncommitted fix: `git stash push -- <fixed source files>`, run the test, confirm it fails for the bug's reason, `git stash pop`. Committed fix: `git checkout <commit-before-fix> -- <fixed source files>`, run, confirm the failure, `git checkout HEAD -- <fixed source files>`. Then confirm it passes and `git status` shows no leftover change.
8. **Report** with the template. Stop once the proof is complete; do not add polish, cleanup, or extra tests after criteria pass.

## Checkpoints

- Every line in the report has a command and an observed result, not a paraphrase.
- Skipped or pending tests are counted and mentioned.
- The report's status matches the worst row (any FAIL → NOT VERIFIED; any UNAVAILABLE, BLOCKED or FLAKY on a required check → PARTIAL).

## Worked example

Claim: "Fixed the 500 on login with an email containing `+`."
- Criteria: (1) login with `a+b@x.com` succeeds; (2) existing auth tests pass; (3) regression test exists and fails without the fix.
- Run `npm test -- auth` → `23 passed, 0 failed`. Run reproduction `curl -s -o /dev/null -w '%{http_code}' -d 'email=a%2Bb@x.com&password=…' localhost:3000/login` → `302` (was `500`).
- Red-green: `git stash push src/auth/normalize.ts` → `npm test -- normalize` → `1 failed: expected "a+b@x.com" got "a b@x.com"`; `git stash pop` → `1 passed`.
- Typecheck `npx tsc --noEmit` → exit 0.
- Report: VERIFIED with the four rows.

## Red flags in your own wording

"should", "probably", "seems to", "looks good", "Done!", "Perfect!" before any command ran; about to commit or open a PR with no fresh run; trusting a sub-agent's summary; "just this once"; different wording to dodge the rule. Each means: run the gate first.

## Pitfalls

- Treating lint as a build or tests as a typecheck.
- Reading only the last line of output and missing "3 skipped" or a warning that is really an error.
- Verifying in a different environment or branch than the one being shipped.
- Expanding scope after the proof is complete.
- Reporting UNAVAILABLE as PASS.

## Done when

- [ ] Every acceptance criterion has a row with command and observed result.
- [ ] Commands were run after the last change (fresh evidence).
- [ ] Bug fixes have a red-green-verified regression test.
- [ ] Status is stated exactly (VERIFIED / NOT VERIFIED / PARTIAL) with risks listed.
