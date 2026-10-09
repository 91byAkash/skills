# Diagnose a Bug: reference

## Loop catalog

| Loop | Build it like this | Best for |
|---|---|---|
| Failing test | test at the closest seam that reaches the bug | logic bugs with a known entry point |
| HTTP script | `curl -s -w '%{http_code} %{time_total}\n' ...` against a dev server, assert status/body | API bugs |
| CLI + snapshot | run with a fixture, `diff <(cmd fixture) expected.txt` | tools, data transforms |
| Headless browser | script that drives the page and asserts DOM, console errors, network responses | UI bugs |
| Replay | save the real request/payload/event to a file and feed it to the handler in isolation | bugs seen only with production data |
| Harness | tiny script importing the module with stubbed dependencies and calling one function | deep logic far from any entry point |
| Property/fuzz | loop 1000 random inputs, print the first failing one | "sometimes wrong" output |
| Bisection | `git bisect start BAD GOOD && git bisect run ./loop.sh` (exit 0 good, 1 bad, 125 skip) | regressions between known states |
| Differential | same input through two versions/configs, diff outputs | upgrades, config changes |
| Human-in-the-loop | `scripts/hitl-loop.sh` prompts the person and prints captured answers | hardware, third-party UIs, physical steps |

## Raising the reproduction rate (intermittent bugs)

The goal is a debuggable rate, not a perfect repro. Loop the trigger 100×, run in parallel (`scripts/repro-rate.sh -j 8 -n 200 -- cmd`), add CPU/IO stress, shrink timing windows, inject small sleeps at suspected race points. ~50% is easy to debug; ~1% is not.

## Root-cause tracing (error deep in a call chain)

1. Write down the symptom exactly (message, value, location).
2. Find the line that directly produces it.
3. Ask what called it and with which values; log or break there.
4. Keep walking up until you find where the bad value is created.
5. Fix at the origin; add a guard at the symptom site only as an extra layer.
Tip: temporarily capture a stack trace where the bad value first appears (`console.trace`, `traceback.print_stack()`, `debug.PrintStack()`).

## Multi-component systems

For pipelines like CI → build script → signing, or API → service → database: add one log at every boundary showing what came in, what went out, and the relevant environment/config (print `SET`/`UNSET` for secrets, never values). Run once. The first boundary where reality diverges from expectation is the failing component; investigate only that.

## Condition-based waiting (flaky tests)

Replace guessed delays with a wait for the actual condition:
```ts
async function waitFor<T>(check: () => T | false | null | undefined, what: string, timeoutMs = 5000, everyMs = 20): Promise<T> {
  const start = Date.now();
  for (;;) {
    const v = check();
    if (v) return v;
    if (Date.now() - start > timeoutMs) throw new Error(`timed out after ${timeoutMs}ms waiting for ${what}`);
    await new Promise(r => setTimeout(r, everyMs));
  }
}
// await waitFor(() => events.find(e => e.type === "DONE"), "DONE event");
```
Patterns: event arrived, state equals X, count ≥ N, file exists, compound condition. Keep a fixed delay only when timing itself is under test (debounce, throttle) and comment why.

## Defense in depth (after the root-cause fix)

| Layer | Purpose | Example |
|---|---|---|
| Entry validation | reject bad input at the boundary | empty project path rejected by `create()` |
| Business validation | operation-specific sanity checks | workspace manager refuses empty directory |
| Environment guard | block dangerous actions in the wrong context | tests may not run `git init` outside a temp dir |
| Forensics | capture context if it still happens | log stack trace before the dangerous call |

## Performance regressions

1. Baseline: measure the slow path with a fixed method (timer around the call, profiler, `EXPLAIN ANALYZE`, browser performance panel). Record median of ≥5 runs.
2. Bisect between fast and slow states using the measurement as the loop (fail if > threshold).
3. Profile the slow version; look for N+1 queries, missing indexes, accidental O(n²), synchronous IO, cache misses, large payloads.
4. Fix, re-measure with the same method, report before/after medians.

## Red-flag thoughts (stop and return to the loop)

- "Quick fix now, investigate later." / "Let me just try X."
- "I'll change a few things and run the tests."
- "I'll skip the test and check manually."
- "It's probably X." without a prediction to test.
- "One more attempt" after two failures.
- Each fix reveals a new problem somewhere else (architecture problem; discuss).

## Signals from the user that the process is off

"Is that actually happening?" (you assumed without evidence), "Stop guessing", "Did you check the logs?", "We already ruled that out", frustration after repeated fixes. Each means: go back to evidence.
