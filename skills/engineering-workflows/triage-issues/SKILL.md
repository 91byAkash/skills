---
name: triage-issues
description: "Triage issues and external PRs into one category and one state label, after verifying the claim and checking duplicates and prior rejections, then post the matching brief or notes. Use when asked \"what needs my attention?\", \"triage #42\", \"what's ready for agents?\", or to clean up a backlog. Not for fixing the issue (use diagnose-bug or implement-plan) or reviewing a PR diff in depth (use review-diff)."
license: MIT
metadata:
  category: "engineering-workflows"
  version: "3.0.0"
---

# Triage Issues

Scope: incoming issues and external pull requests (treated as issues with code attached).

Every triaged item ends with exactly one category and one state, and the comment that state requires. The maintainer decides; you gather evidence and recommend.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `request` | yes | – | "show what needs attention", "triage #42", "move #42 to ready-for-agent" |
| `tracker` | optional | the repo's configured tracker | GitHub Issues via CLI, Linear, local `.issues/` |
| `label_map` | optional | canonical names below used as-is | `{"ready-for-agent": "status: agent-ready"}` |
| `include_prs` | optional | `yes` for PRs from external contributors only | `no` |
| `disclosure_line` | optional | `> *Drafted with AI assistance during triage.*` at the top of every posted comment | custom text, or `none` if the maintainer says so |
| `out_of_scope_dir` | optional | `.out-of-scope/` | `docs/rejected/` |

## Output

- Attention view: three buckets (unlabelled; `needs-triage`; `needs-info` with reporter replies since the last notes), oldest first, each line `[issue|PR] #N title - one-line summary - age`.
- Per item: recommendation (category, state, reasoning, relevant code summary, verification result), then after the maintainer agrees: labels applied and one of: agent brief ([templates/agent-brief.md](templates/agent-brief.md)), needs-info notes ([templates/needs-info.md](templates/needs-info.md)), an out-of-scope record ([templates/out-of-scope.md](templates/out-of-scope.md)) plus close, or a close comment.

## Roles

| Kind | Role | Meaning |
|---|---|---|
| Category | `bug` | something is broken |
| Category | `enhancement` | new behaviour or improvement |
| State | `needs-triage` | maintainer has not evaluated yet |
| State | `needs-info` | waiting on the reporter |
| State | `ready-for-agent` | fully specified; an unattended agent can do it (PR: a brief says what is left to do on the diff) |
| State | `ready-for-human` | needs a person (judgment, external access, design decision, manual testing; PR: ready for a human to merge) |
| State | `wontfix` | will not be actioned (closed) |

Transitions: unlabelled → `needs-triage` → `needs-info` | `ready-for-agent` | `ready-for-human` | `wontfix`; `needs-info` → `needs-triage` when the reporter replies. Conflicting state labels on one item: flag and ask before doing anything else.

## Supporting files

- [templates/agent-brief.md](templates/agent-brief.md): the brief an unattended agent works from; rules for durable, behavioural briefs. Use for `ready-for-agent` and `ready-for-human`.
- [templates/needs-info.md](templates/needs-info.md): triage notes for `needs-info`.
- [templates/out-of-scope.md](templates/out-of-scope.md): one file per rejected concept. Use for rejected enhancements.

## Steps

1. **Interpret the request.** "What needs attention" → step 2. A named item → step 3. "Move #N to X" → quick override (step 9). "What's ready for agents" → list `ready-for-agent` items with brief summaries.
2. **Attention view.** Query the tracker (e.g. `gh issue list --state open --json number,title,labels,createdAt,author --limit 200`; local tracker: one Markdown file per issue under `.issues/` with `labels:` and `created:` front matter, closed ones moved to `.issues/closed/`), bucket as above, include external PRs if `include_prs`, show counts, let the maintainer pick.
3. **Gather.** Read the full body, comments, labels, author, dates (PR: the diff). Parse prior triage notes and do not re-ask answered questions. Read the glossary and ADRs for the area.
4. **Three checks:**
   - duplicate: search open and closed issues by concept, not just the title words (`gh issue list --state all --search "<concept> in:title,body" --limit 50`, or the tracker's equivalent). Found → candidate close as duplicate, linking the original, and carry any new evidence over to it as a comment;
   - redundancy: search for the requested behaviour by domain concept, not just the reporter's words; report where you looked. Found → candidate `wontfix (already implemented)` with a pointer to where it lives.
   - prior rejection: read `out_of_scope_dir/*.md`; surface any match.
5. **Recommend** category + state with reasons, a short relevant code summary, and wait for the maintainer.
6. **Verify the claim** before any deeper discussion. Bug: reproduce from the reporter's steps (see `diagnose-bug` for building a loop). PR: check it out, run its tests/commands, confirm it does what it claims. Report: confirmed (with code path), failed, or insufficient detail (strong `needs-info` signal).
7. **Shape it if needed.** If the request is under-specified, run `stress-test-plan` with the maintainer one round at a time; update the glossary/ADRs as terms and decisions settle.
8. **Apply the outcome** (show the maintainer the exact labels and comment text before posting):
   - `ready-for-agent`: post an agent brief.
   - `ready-for-human`: same brief plus why it cannot be delegated.
   - `needs-info`: post triage notes with specific questions.
   - `wontfix`: already implemented → point to the code, close (no out-of-scope record); rejected bug → polite explanation, close; rejected enhancement → write or extend `out_of_scope_dir/<concept>.md`, link it in the comment, close.
   - `needs-triage`: apply; optional progress comment.
   - duplicate: comment linking the original, close (no state label beyond the tracker's own duplicate marker, if it has one).
   Translate every canonical label through `label_map` before applying it. Every posted comment starts with `disclosure_line` (replace the line in the templates; delete it only if the maintainer set it to `none`).
9. **Quick override.** "Move #42 to ready-for-agent": trust the maintainer, state the exact changes (labels, comment, close), then apply. Skip shaping; if moving to `ready-for-agent` with no brief, ask whether to write one.
10. **Resume.** If triage notes exist, check which questions the reporter answered and present the updated picture first.

## Checkpoints

- Exactly one category and one state per triaged item.
- Claim verified (or explicitly impossible) before a `ready-*` state.
- Duplicate, already-implemented and prior-rejection checks reported with where you looked.
- Briefs contain no file paths or line numbers and have testable acceptance criteria.

## Worked example

Item #212 "CSV export drops rows with emoji".
- Gather: reporter attached a sample file; no prior notes.
- Checks: no existing fix (searched export encoder and CSV writer by concept "encoding"); no out-of-scope match.
- Verify: export of the sample yields 97 of 100 rows; rows with emoji missing. Code path: CSV writer encodes as Latin-1 and skips rows that fail.
- Recommend: `bug` + `ready-for-agent`; maintainer agrees.
- Brief: summary "CSV export silently drops rows containing characters outside Latin-1"; current vs desired behaviour (UTF-8 with BOM option, no rows dropped, encoding errors surfaced); key interfaces (`ExportOptions.encoding`, the CSV writer's row-encoding step); acceptance: 100/100 rows for the sample, an emoji round-trip test, an error is reported instead of skipping; out of scope: XLSX export.

## Pitfalls

- Recommending `ready-for-agent` without reproducing the bug.
- Briefs that say "open file X, line 42" (stale within weeks) or describe implementation steps instead of behaviour.
- "Please provide more info" instead of specific questions.
- Writing an out-of-scope record for something that already exists, or one file per issue instead of per concept.
- Posting comments or closing issues before the maintainer agreed.
- Triaging collaborators' in-progress PRs (discovery covers external PRs only; a named PR is always fair game).

## Done when

- [ ] The requested view or item handled; maintainer agreed to the outcome.
- [ ] Labels: one category + one state; no conflicts.
- [ ] The state's artifact posted (brief, notes, out-of-scope record + link, or close comment) with the disclosure line.
- [ ] Verification result and duplicate/rejection checks recorded in the comment or summary.
