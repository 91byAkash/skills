---
name: session-retro
description: "Run a retrospective on an agent coding session and propose ranked, concrete environment fixes (lint rule, hook, CI job, navigation pointer, reviewer standard). Use when a long or bumpy session ends, or the user asks \"what should we change so this goes better next time?\" or \"why did that take so long?\". Not for a team sprint retro or incident postmortem (use internal-communications)."
license: MIT
metadata:
  category: "build-and-ship"
  version: "3.0.0"
---

# Session Retro

Improve the environment, not the agent's resolve. Prefer a deterministic check over a written rule, and a pointer over pasted instructions.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `session` | optional | current session | path to a session log/transcript, PR link, commit range |
| `repo` | optional | current working repo | `~/code/api` |
| `focus` | optional | all categories | `automated-checks`, `navigation` |
| `max_proposals` | optional | 7 | `3` |
| `apply` | optional | `no` (propose only) | `yes` to implement approved proposals |

## Output

A ranked list (most severe first) using [templates/retro-report.md](templates/retro-report.md): for each proposal, the evidence from the session (what happened, cost in time/tokens/errors), the category, the concrete change (file + content, or command), and the expected effect. If `apply: yes`, the approved changes are made and committed.

## Supporting files

- [templates/retro-report.md](templates/retro-report.md): report skeleton. Use for the final output.

## Where things belong

| Kind of guidance | Put it in | Why |
|---|---|---|
| Mechanical rule (banned API, import shape, file location, naming pattern) | a lint rule, pre-commit hook, or CI job | deterministic and free at review time |
| Judgment call (cross-file consistency, "match existing patterns") | the coding standards file read by the reviewer | the reviewer has the least context pressure |
| Where to find things | a one-line navigation pointer in the always-loaded agent instructions file (e.g. AGENTS.md) | always-loaded files must stay tiny |
| Reference knowledge | a doc in the docs folder, linked by a pointer | loaded only when needed |
| Repeatable procedure or user-invoked command | a skill | only its description costs context |

The implementer carries exploration, coding and debugging; the reviewer gets a diff. So standards are enforced at review, not front-loaded on the implementer.

## Steps

1. **Read the evidence.** Open the session log/transcript or the commit range. Note timestamps, tool calls, errors, retries, and user corrections. If no log is accessible, reconstruct from git history and the conversation and say so.
2. **Read the repo's guardrails** before proposing any: `package.json`/`Makefile` scripts, lint config, pre-commit config, CI workflows, the agent instructions file, the coding standards file. A check that exists but is unwired or broken is the finding; do not reinvent it. A repo with no pre-commit hook and no CI job running lint/typecheck/tests is itself a high-severity finding.
3. **Scan by category** (only the categories named in `focus`, if given) and collect candidates with evidence:
   - Navigation: long searches for a file or concept; hidden coupling between files → navigation pointer or co-location.
   - Automated checks: mistakes a linter/typechecker/test/filesystem rule would have caught → wire or add the check.
   - Coding standards: reviewer missed or over-enforced something → classify mechanical (build a check) vs judgment (add/clarify a standard; remove stale ones).
   - Instruction bloat: always-loaded instruction files that are large → move content to standards, checks, docs or skills.
   - No-ops: instructions that do not change behaviour ("write clean code") → delete.
   - Tool economy: expensive or repeated calls (huge outputs, full-repo greps, re-reading big files) → narrower commands, scripts, output redirection.
   - Information access: something crucial was invisible (server logs, DB schema, third-party sandbox) → tee logs to a file, read-only access, schema dump command.
4. **Rank** by severity = frequency × cost (time, tokens, wrong output reaching the user) × likelihood of recurrence. Label: **High** = wrong output reached the user, or it will recur in most sessions and cost 15+ minutes each time; **Medium** = recurs sometimes, or one-off but 15+ minutes; **Low** = minor friction or cleanup. Cap at `max_proposals`; list the rest under "Not proposed".
5. **Make each proposal concrete**: exact file and the text or config to add, or the command to wire. A proposal without a concrete change is a complaint.
6. **Present** to the user, most severe first. If `apply: yes`, implement only the approved ones (commit hooks and command guards: use `git-guardrails`), run the new check to show it catches the original mistake, and commit.

## Checkpoints

- Every proposal cites a specific moment in the session.
- Each mechanical rule became a check, not prose.
- The always-loaded instruction file did not grow by more than a few pointer lines.

## Worked example

Session: 2 hours adding a webhook endpoint.
1. **High - automated checks.** The agent imported from `src/internal/*` in a route file twice; the reviewer caught it late. Change: add an import-restriction lint rule for `src/routes/**` banning `src/internal/**`; wire `npm run lint` into the pre-commit hook (currently lint exists but no hook runs it). Effect: caught at commit, zero review cycles.
2. **High - information access.** 25 minutes guessing why the endpoint returned 401; the dev server logs were not visible. Change: `npm run dev 2>&1 | tee .logs/dev.log` script + pointer "server logs: .logs/dev.log" in AGENTS.md.
3. **Medium - navigation.** Three searches to find where webhooks are registered. Change: pointer line "Webhook registry: src/webhooks/registry.ts".
4. **Low - no-op.** AGENTS.md says "be careful with types"; delete.

## Pitfalls

- Proposing new rules for things an existing check already covers.
- Adding paragraphs to the always-loaded instructions file.
- Vague proposals ("improve docs") with no file or content.
- Blaming the model instead of changing the environment.
- Ranking by how interesting a fix is rather than its cost to future sessions.

## Done when

- [ ] Evidence read (log, transcript, or git history) and its source stated.
- [ ] Existing guardrails inventoried before proposing.
- [ ] Ranked proposals, each with evidence, category, concrete change, and effect.
- [ ] If applying: approved changes made, new checks demonstrated on the original mistake, committed.
