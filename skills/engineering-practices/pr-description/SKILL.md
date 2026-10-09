---
name: pr-description
description: "Write a pull request (or merge request) title and body with a visual summary, before/after evidence, and merge risk (reversibility, blast radius). Use when opening or updating a PR, asked to \"write the PR description\", or a reviewer asks what a change does. Not for commit messages (use commit-messages) or reviewing code (use review-diff)."
license: MIT
metadata:
  category: "engineering-practices"
  version: "3.0.0"
---

# Pull Request Description

The diff shows *what*. The body supplies the *why*, the shape of the change, evidence it works, and how dangerous it is to merge.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `base` | optional | repo default branch (`main`/`master`) | `release/2.4` |
| `head` | optional | current branch | `feat/webhook-retries` |
| `motivation` | optional | from linked issue, spec, or commits; ask if absent | "Partners miss events when their endpoint blips" |
| `links` | optional | issue refs found in branch name/commits | `#482`, spec `docs/specs/webhooks.md` |
| `evidence` | optional | gathered by you (test runs, screenshots) | `before.png`, `after.png`, failing→passing test output |
| `title_style` | optional | repo convention from recent merged PRs | Conventional prefix `feat(webhooks): …` |
| `sections` | optional | Summary, Evidence, Risk, Reviewer notes | add "Rollout" for flagged features |

## Output

- A title (imperative, specific, ≤ 70 characters).
- A Markdown body from [templates/pr-body.md](templates/pr-body.md) with irrelevant sections deleted.
- Returned as text for the user to paste, or applied to the PR only if the user asked you to update it.

## Supporting files

- [templates/pr-body.md](templates/pr-body.md): body skeleton.
- [REFERENCE.md](REFERENCE.md): visual summary forms (pseudocode, call tree, component tree, file tree, sequence diagram, shape diffs), evidence tiers, risk vocabulary, and large-PR tactics. Read when choosing the summary visual or judging risk.
- [scripts/pr-context.sh](scripts/pr-context.sh): prints commits, diff size (with a lockfile/generated-free line count for the large-PR rule), lines by top-level area, risk signals (migrations, dependencies, env/config, CI, public API, tests), referenced issues, and a warning if uncommitted changes exist (they are not in the PR). Run first: `scripts/pr-context.sh [base] [head]`; exits 2 on an unknown ref.

## Steps

1. **Gather context**: `scripts/pr-context.sh <base> <head>`; read the full diff (`git diff <base>...<head>`) and commit log. Read `GLOSSARY.md` if present and use its terms. If the script warns about uncommitted changes, ask whether they belong in the PR before describing them.
2. **Find the motivation**: `motivation` if given, else the linked issue/spec (`links`, or the issues the script lists), commit bodies, or ask. One or two sentences: the problem, for whom.
3. **Write the title**: imperative verb + specific object, ≤ 70 chars, in `title_style` or the convention of recent merged PRs (`gh pr list --state merged --limit 10`, or `git log --merges --format=%s -20` on the base). `Retry failed webhook deliveries with backoff`, not `Webhook fixes`.
4. **Summary**: one short paragraph plus the *smallest* visual that makes the change obvious (REFERENCE.md lists forms). Pick by change type:
   - logic → pseudocode or a state diff
   - control flow → call tree (diffed if the tree existed)
   - UI → component tree or screenshots
   - refactor/moves → shallow file tree diff
   - cross-service interaction → sequence diagram
5. **Evidence**: before/after, starting from any `evidence` the user supplied. Best: screenshots or recordings for visual changes. Next: the specific test that failed before and passes now, or command output. Run things yourself; never claim a result you did not see.
6. **Risk**:
   - *Reversibility*: a two-way door (cheap to revert) or a one-way door (data migration, deleted data, published API/event change, external side effects).
   - *Blast radius*: who/what could break (one page, all API consumers, mobile layout, billing).
   - For one-way doors: rollout and rollback plan (flags, backfills, ordering of deploys).
7. **Reviewer notes**: where to start reading, what you are unsure about, what is intentionally out of scope, follow-ups.
8. **Tidy**: keep the `sections` asked for (default: the four in the template), bullets over paragraphs, identifiers in backticks, delete empty sections, no file-by-file list, no secrets, internal hostnames, or personal data.
9. **Large PR** (> ~400 changed lines excluding lockfiles and generated files, as the script's size line counts, or several concerns): propose a reading order or a split into stacked PRs.

## Checkpoints

- If motivation is unknown after step 2 → ask before writing.
- Before including evidence → you ran it in this session (or label it as from CI with a link).

## Worked example

Title: `Retry failed webhook deliveries with exponential backoff`

```markdown
## Summary
Partners lost events when their endpoint returned 5xx once. Deliveries now retry up to 6 times over ~1 hour, then land in a dead-letter table visible in the admin UI. Refs #482.

    deliver(event)
    -  post once; log on failure
    +  post; on 5xx/timeout schedule retry at 1m, 2m, 4m, 8m, 16m, 32m
    +  after 6 failures → dead_letters + alert

## Evidence
- Before: `webhook.test.ts › retries on 503` failed (1 attempt made).
- After: passes; 6 attempts at the expected delays with a fake clock.
- Staging: forced 503 on a test endpoint; event delivered on attempt 3.

## Risk
- **Reversibility:** two-way door (flag `webhook_retries`, default off).
- **Blast radius:** outbound webhooks only; retry traffic to partner endpoints rises at most 6×.

## Reviewer notes
Start at `delivery/scheduler.ts`. Unsure whether 1 h total is long enough for enterprise partners; follow-up #490 makes it configurable.
```

## Pitfalls

- Restating commit messages or listing every file.
- Vague titles ("Fix stuff", "Updates").
- Diagrams bigger than the change; keep only the calls, files, states that matter.
- "Tests pass" without saying which tests or showing output.
- Hiding a one-way door (migration, API removal) in a long body. Put it under Risk.
- Pasting screenshots containing real customer data.

## Done when

- [ ] Title is imperative, specific, ≤ 70 chars, and follows repo convention.
- [ ] Summary states the why and includes one fitting visual (or none if the change is tiny).
- [ ] Evidence shows before and after, all of it observed.
- [ ] Reversibility and blast radius are stated; one-way doors have rollout/rollback notes.
- [ ] Reviewer notes give a starting point and any uncertainty.
- [ ] No secrets, internal URLs, or personal data; empty sections removed.
