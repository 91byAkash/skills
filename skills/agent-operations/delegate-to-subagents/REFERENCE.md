# Parallel Sub-agents: Reference

## Contents
- When to delegate
- Model and tier selection
- Brief rules
- Status handling
- Review package and reviewer inputs
- Fix loop
- Rulings and stop conditions
- Waiting on agents
- Output contracts
- Ledger and recovery

## When to delegate

| Situation | Choice |
|---|---|
| 2+ failures in different subsystems, no shared state | fan-out, one agent per domain |
| "Where is X / who calls Y / list uses of Z" across a big repo | scout(s), read-only, terse contract |
| Plan with mostly independent tasks, sub-agents available | plan mode |
| Tightly coupled tasks, or no sub-agent tool | execute inline (implement-plan) |
| Edit of 1–2 known files | do it yourself or one builder with exact `path:line` |
| Answer you already know | no sub-agent |

Delegation pays when the work is large or noisy relative to the brief. Everything a sub-agent returns lands in your context and is re-read every turn, so ask for compact returns and put long material in files.

## Model and tier selection

Always name the model/tier when dispatching; an omitted one usually inherits the session's most expensive model.

| Role | Tier |
|---|---|
| Implementer, plan text contains the complete code (transcription + tests), or single-file mechanical fix | cheapest |
| Implementer from prose, multi-file integration, debugging | standard |
| Design or architecture judgment; final whole-branch review | most capable |
| Task reviewer | standard as floor; scale up for subtle/concurrent/security diffs |
| Scoped re-review of a small fix | cheap to standard |
| Fix rounds 4–5 | at least one tier above the stuck implementer |

Turn count matters more than per-token price: the cheapest tiers often take 2–3× the turns on multi-step work.

## Brief rules

- One task, not the session history. Include: where it fits (one line), requirements (the brief file), interfaces and decisions from earlier tasks, ambiguity resolutions, scope limits, done-when commands, return contract, report-file path.
- Exact values (numbers, strings, signatures, test cases) live only in the brief file.
- Never make a sub-agent read the whole plan.
- Carry pointers to ledger entries (deferred findings) that touch the same area.
- Implementers: ask questions before starting; run focused tests while iterating and the full suite once before committing; never spawn sub-agents; escalate rather than guess on architecture decisions.

## Status handling

| Status | Action |
|---|---|
| `DONE` | build review package, dispatch reviewer |
| `DONE_WITH_CONCERNS` | read concerns; correctness/scope ones get resolved before review; observations get noted |
| `NEEDS_CONTEXT` | supply what is missing, re-dispatch |
| `BLOCKED` | context problem → more context, same model; reasoning problem → stronger model; too big → split; plan wrong → ruling, then re-dispatch with the ruling |

Never re-dispatch unchanged after an escalation.

## Review package and reviewer inputs

Package = `git log --oneline BASE..HEAD`, `git diff --stat BASE..HEAD`, `git diff -U10 BASE..HEAD` in one file (`scripts/review-package.sh`). Use the BASE recorded before dispatch, never `HEAD~1` (multi-commit tasks get truncated).

Reviewer receives: brief path, report path, package path, and the binding constraints copied verbatim (exact values, formats, "same layout as X"). Do not ask it to rerun tests already evidenced in the report. Do not include "do not flag…" or caps on severity; adjudicate findings afterwards instead. Items marked "cannot verify from diff" are yours to resolve with cross-task knowledge before marking complete.

Required verdicts: **spec compliance** (all requirements met, nothing extra) and **quality** (correctness, tests meaningful, naming, structure, no dead code), with findings tagged Critical / Important / Minor and `path:line`.

## Fix loop

- Triggers: spec ❌, any Critical/Important finding, a confirmed gap.
- Minor findings: `Task N: minor (deferred): …` in the ledger; the final review triages them.
- Findings that conflict with plan text: rule (spec is binding), record, then act.
- Rounds 1–3: resume the original implementer (or a fresh one with brief + report + findings if resuming is impossible).
- Rounds 4–5: fresh implementer, stronger model: "A prior implementer attempted this N times; you own it now. Read the report for what was tried."
- Each round: fix, rerun covering tests, append fix report (tests, command, output) to the report file; then scoped re-review of the fix diff.
- After the last round: adjudicate each open finding. Load-bearing ones → rule and continue (or stop if every path is a guess); others → park in the ledger with rulings.

## Rulings and stop conditions

Continue without asking for conflicts, ambiguities, plan defects, and caps you would have liked to exceed. Record: `Ruling: <decision> - <why> - <cost if wrong>`. A plan without a reachable spec makes rulings provisional; note it in the ledger.

Stop and ask only for: irreversible/destructive operations; security-sensitive actions; side effects outside the branch that norms require asking about (merge, push to shared branch, publish, sending messages); a plan so broken every path is a guess.

## Waiting on agents

- Do local work while agents run (ledger, next brief, reading reports).
- When idle, wait in bounded stretches (5–10 minutes where possible); between stretches post one status line and reconcile: list live agents, chase any that finished silently.
- Avoid short polling loops and open-ended silent waits.

## Output contracts

Ask for returns you can parse at a glance:

**Investigator**
```
<question>:
- path:line - `symbol` - note
totals: <n> sites
```
or `No match.` (and what was searched).

**Builder**
```
<path:line-range> - <change, ≤10 words>
verified: <tests run + result>
```
or one terminal word: `too-big` · `needs-confirm` · `ambiguous` · `regressed`, with one line of why.

**Reviewer**
```
path:line: <Critical|Important|Minor>: <problem>. <fix>.
spec: ✅|❌  quality: approved|changes
totals: C=<n> I=<n> M=<n>
```
or `No issues.`

Paraphrase terse contracts before showing them to the user.

## Ledger and recovery

- First line: `# Ledger - plan: <plan path>`. A ledger naming another plan belongs to that plan; leave it.
- Append-only lines: pre-flight table, `Task N: dispatched (BASE <sha>)`, `Task N: fix round R`, `Task N: complete (<sha>)`, `Ruling: …`, `Task N: minor (deferred): …`.
- Resume rule: tasks with `complete` are done; a task whose last line is a fix round resumes at the next round.
- The workspace is git-ignored scratch; `git clean -fdx` deletes it. Recover from `git log` if that happens. Delete the workspace after the final review is clean.
