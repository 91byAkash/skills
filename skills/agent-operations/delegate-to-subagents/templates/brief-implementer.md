# Implement Task <N>: <name>

Model: <tier, required>
Work in: <repo path / worktree>, branch <branch>

## Where this fits
<one line>

## Requirements
Read first: <workspace>/task-<N>-brief.md. It is your requirements; use its exact values verbatim.

## From earlier tasks
- <interface / decision the brief cannot know>

## Ambiguities resolved
- <your ruling on anything unclear>

## Scope
Touch: <files/areas>. Do not touch: <files/areas>. Follow existing patterns; do not restructure outside the task.

## Before you start
Ask now if requirements, approach, or dependencies are unclear. Escalate instead of guessing on architectural choices.

## Do
1. Implement exactly what the brief specifies (tests first if the brief says so).
2. While iterating, run the focused tests; before committing, run the full suite once.
3. Commit with a clear message.
4. Self-review your diff (read it; do not spawn reviewers or helpers; review is scheduled separately).

## Report
Write the full report to <workspace>/task-<N>-report.md: what changed, files, tests added, commands run with output tail, concerns.
Return only:
```
STATUS: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
COMMITS: <sha> <subject>
TESTS: <one-line summary>
CONCERNS: <none | one line each>
```
