---
name: commit-messages
description: "Write commit messages that state intent (Conventional Commits by default) and split a messy working tree into atomic commits. Use when committing, asked to \"write a commit message\", splitting changes into logical commits, or adding a commit-msg lint hook. Not for PR descriptions (use pr-description) or rewriting pushed history without approval."
license: MIT
metadata:
  category: "engineering-practices"
  version: "3.0.0"
---

# Commit Messages

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `changes` | optional | the working tree (`git status`, staged + unstaged diff) | a specific path set, or "only what's staged" |
| `convention` | optional | detected from `git log -30` | Conventional Commits; or plain imperative sentences |
| `scope_style` | optional | top-level module/package names seen in history | `api`, `billing`, `ui` |
| `mode` | optional | `message` (write message only) | `commit` (stage and commit), `split` (group a messy tree into several commits) |
| `issue` | optional | from branch name | `#482` |
| `trailers` | optional | none | `Co-authored-by: …`, or an AI-assistance trailer if the user's rules require one |

## Output

- `message` mode: the commit message in a code block, ready to paste.
- `commit`/`split` mode: one or more commits, each atomic, with the list of commits (hash + subject) reported.

## Supporting files

- [scripts/commit-lint.sh](scripts/commit-lint.sh): checks a message (file, stdin, or `-m`) against the format rules below; exits 1 on errors, 0 with warnings. Add `--plain` when `convention` is plain sentences. Run on every message you write: `scripts/commit-lint.sh -m "$msg"`. As a hook (when asked to add a commit-message check): `hook=$(git rev-parse --git-path hooks)/commit-msg && cp scripts/commit-lint.sh "$hook" && chmod +x "$hook"` (works in worktrees; if the repo sets `core.hooksPath` or uses husky/lefthook, add it there instead); it ignores the diff `git commit -v` appends.

## Format

```
<type>(<scope>)!: <summary>

<body: why, trade-offs, side effects; wrapped at 72>

<footers: BREAKING CHANGE: …, Refs #123, Closes #45, Co-authored-by: …>
```

| Type | Use for |
|---|---|
| `feat` | new user-visible capability |
| `fix` | bug fix |
| `refactor` | code change with no behaviour change |
| `perf` | performance improvement |
| `test` | adding/fixing tests only |
| `docs` | documentation only |
| `build` | build system, dependencies |
| `ci` | CI configuration |
| `chore` | maintenance that fits nothing else |
| `style` | formatting only |
| `revert` | reverting a previous commit |

Summary rules: imperative ("add", not "added"/"adds"), ≤ 50 chars preferred and 72 max, no trailing period, case after the colon per repo habit (lowercase by default), scope optional and never repeating what the summary says.

Body: skip when the subject says it all. **Always** include a body for breaking changes, security fixes, data migrations, and reverts (say why). Use `-` bullets. No "this commit", "I/we", "now/currently"; no emoji unless the repo uses them.

## Steps

1. **Read the convention**: `git log --format=%s -30`. If the repo does not use Conventional Commits, keep its style and apply only the summary/body rules.
2. **Review changes** (limited to `changes` if given): `git status`, `git diff`, `git diff --cached`. Spot anything that must not be committed (secrets, `.env`, build output, large binaries, editor files). Never commit those; suggest `.gitignore` entries.
3. **Group by intent** (`split`/`commit`): one logical change per commit. Separate formatting and pure refactors from behaviour changes; separate dependency bumps; keep a test with the code it tests.
4. **Stage each group precisely**: `git add -p <file>` for mixed files, `git add <paths>` otherwise. Check with `git diff --cached --stat`.
5. **Write the message**: pick type and scope (scope from `scope_style`, else the top-level folder or package the change lives in; omit it when the change spans several), write the summary as the change's intent, add body/footers when required. Footers: `Refs <issue>` (or `Closes <issue>` when this commit completes it), taking `issue` from the input or a branch name like `fix/482-empty-cart`; then each of `trailers`, one per line, after a blank line.
6. **Lint it**: `scripts/commit-lint.sh -m "<message>"` (add `--plain` for plain-sentence repos). Fix every error; fix warnings unless the repo's history does the same thing. In `message` mode, stop here and reply with the message.
7. **Commit** (if asked): `git commit -F <file>` (or `-m` with separate `-m` per paragraph). Each commit should build and pass tests on its own where practical.
8. **Never** amend, rebase, or force-push commits that are already pushed unless the user explicitly approves after you explain the effect.

## Checkpoints

- Before committing in `split` mode: show the proposed grouping (commit subjects + files) and get a yes.
- If a secret is found in the diff: stop and tell the user; if it was ever pushed, it must be rotated.

## Worked example

Working tree: new `GET /users/:id/profile` route + test, a Prettier reformat of three unrelated files, and a bumped lint dependency. Split into three:

```
style: apply formatter to billing helpers
```
```
build(deps): bump eslint to 9.12
```
```
feat(api): add GET /users/:id/profile

The mobile app needs profile fields without the full user payload,
which costs ~40 KB per cold start on slow networks.

Refs #128
```

Breaking change:
```
feat(api)!: rename /v1/orders to /v1/checkout

BREAKING CHANGE: clients calling /v1/orders must switch to
/v1/checkout before 2026-12-01; the old route then returns 410.
```

## Pitfalls

- "WIP", "fix", "updates", "misc changes".
- One commit mixing a feature, a refactor, and a reformat; review and revert become painful.
- Describing edits ("change x to y in file z") instead of intent.
- Subject-only messages for breaking changes, migrations, or security fixes.
- Committing generated files, lockfile churn from an unrelated install, or `.env`.
- Rewriting pushed history without approval.

## Done when

- [ ] Each commit holds one logical change and nothing that should not be versioned.
- [ ] Every message follows the repo convention and passes `scripts/commit-lint.sh`.
- [ ] Breaking changes, migrations, security fixes, and reverts have explanatory bodies.
- [ ] Issue references and required trailers are present.
- [ ] No pushed commits were rewritten without approval.
