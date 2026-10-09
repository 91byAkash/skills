---
name: session-handoff
description: "Write a handoff document (state, next steps, decisions, dead ends, checks) so a fresh agent or teammate can continue without rediscovering context. Use when the context window is filling up, when pausing work, when switching agents, machines or people, or when the user says \"hand this off\" or \"write a handoff\". Not for a lessons-learned review of the session (use session-retro)."
license: MIT
metadata:
  category: "productivity"
  version: "3.0.0"
---

# Session handoff

Write state, not story. The next reader needs to know where things are, what to do next, and what not to try again.

A handoff looks forward (how to continue). A retrospective looks back (what to change in the environment so the next session goes better); for that, use session-retro. Both can run at the end of a long session: retro first, then put its open fixes under "Parked" in the handoff.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `next_focus` | optional | continue the current task | "only finish the migration; leave UI for later" |
| `audience` | optional | a fresh agent | `teammate` (more context, less tool detail) |
| `location` | optional | OS temp dir (`$TMPDIR`, else `/tmp`; `%TEMP%` on Windows) | `docs/handoffs/` if the user wants it committed |
| `launch` | optional | `false` | `true`: start a fresh/background agent with the document as its first message, if your environment supports it |
| `name` | optional | based on the task | `fix-login-redirect` |

## Output

- `handoff-<name>-<YYYYMMDD-HHMM>.md` at `location`, following [templates/handoff.md](templates/handoff.md).
- The path reported to the user. If `launch=true`, the new agent's name/id.

## Supporting files

- [templates/handoff.md](templates/handoff.md): document structure with guidance per section.
- [scripts/handoff-skeleton.sh](scripts/handoff-skeleton.sh): prints a pre-filled skeleton with repo state (branch, upstream, uncommitted files, recent commits, stashes, worktrees) so you only add the judgment parts. Run: `scripts/handoff-skeleton.sh "<task>" [repo_dir] > "${TMPDIR:-/tmp}/handoff-<name>-$(date +%Y%m%d-%H%M).md"`. Handles detached HEAD and repos with no commits; prints a warning line when work is uncommitted, unpushed, or has no upstream.

## Steps

1. **Set the focus.** If `next_focus` is given, everything in the document serves it; drop unrelated threads (list them under "Parked").
2. **Capture repo state** with `scripts/handoff-skeleton.sh` (or by hand: branch, uncommitted changes, last commits, running processes, environment needed).
3. **Write the judgment parts** (for `audience=teammate`, add one line of background per decision and drop tool-level detail such as exact grep commands; for an agent, keep commands exact):
   - Goal in one or two sentences, with the definition of done.
   - Done / in progress / next steps (ordered, each one actionable: file, command, or decision).
   - Decisions and why (one line each).
   - Tried and rejected, with the reason (this is what saves the most time).
   - Open questions and risks; who can answer them.
   - How to verify: exact commands, tests, URLs, expected results.
4. **Reference, do not duplicate**: link specs, plans, tickets, ADRs, commits, PRs, and files by path or URL instead of pasting them.
5. **Suggested skills** for the next session (e.g. `implement-plan`, `diagnose-bug`, `verify-before-done`) with one line on why.
6. **Redact**: API keys, tokens, passwords, connection strings, personal data, customer names unless needed. Replace with `<redacted: where to get it>`.
7. **Save** to `location`; never into the repo unless asked. Report the path.
8. **Launch** (only if `launch=true` and the environment supports starting another agent): pass the document as the first message, give the job a descriptive name, and report how to find it. Otherwise tell the user how to start one with the file.

## Checkpoints

- Before saving: reread as the next agent. Could you start working within two minutes using only this file and its links?
- If anything uncommitted would be lost by switching machines, say so at the top.

## Worked example

```md
# Handoff: fix login redirect loop (2026-10-08 14:30 IST)

## Goal
Users with expired sessions loop between /login and /app. Done = expired session lands on /login once, then returns to the original page after sign-in; regression test passes.

## State
- Branch `fix/login-loop` (pushed), 2 commits ahead of main; uncommitted: `src/auth/middleware.ts` (WIP, see next step 1)
- Done: reproduced with `npm run test:e2e -- auth-expired` (fails); root cause found: middleware treats refresh-token 401 as "logged in".
- Next:
  1. Finish the `isExpired` branch in `src/auth/middleware.ts:48` to clear the cookie before redirect.
  2. Make `e2e/auth-expired.spec.ts` pass; run full `npm test`.
  3. Open PR with pr-description.

## Decisions
- Fix in middleware, not the client: the loop happens before any client code runs.

## Tried and rejected
- Clearing cookies in `/login` page load: loop persists because middleware redirects first.

## Verify
`npm run test:e2e -- auth-expired` → passes; manual: set cookie `session=expired` and open /app → single redirect.

## References
Issue #482 · ADR docs/adr/0007-session-cookies.md · commit a1b2c3d

## Suggested skills
diagnose-bug (if the test still fails) · verify-before-done · pr-description
```

## Pitfalls

- A chronological diary instead of current state.
- Next steps that are vague ("continue fixing auth").
- Omitting dead ends, so the next agent repeats them.
- Pasting whole specs or diffs that already live elsewhere.
- Secrets or personal data in the document (it may become another agent's prompt).
- Saving into the working tree and accidentally committing it.

## Done when

- [ ] Goal, state, ordered next steps, decisions, dead ends, open questions, and verification commands are present.
- [ ] Artifacts are referenced by path/URL, not duplicated.
- [ ] Suggested skills listed.
- [ ] No secrets or unnecessary personal data.
- [ ] Saved outside the repo (unless requested) and the path reported; launched if requested.
