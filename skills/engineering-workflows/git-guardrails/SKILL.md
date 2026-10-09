---
name: git-guardrails
description: "Add pre-commit hooks that format and check staged files, plus a guard that blocks destructive git commands (push, force-push, reset --hard, clean -f, branch -D) from an agent. Use when the user wants pre-commit hooks or lint-staged, says \"stop the agent from pushing\", or a repo has no guardrails. Not for CI pipelines or server-side branch protection."
license: MIT
metadata:
  category: "engineering-workflows"
  version: "3.0.0"
---

# Git Guardrails

Scope: commit-time hooks (format staged files, lint, typecheck, tests in pre-push) and an agent command guard (push, force-push, reset --hard, clean -f, branch -D, whole-tree checkout/restore, stash drop, history rewrites). CI pipelines and hosting-side branch protection are configured in the hosting service, not here.

Two layers: hooks that keep bad commits out, and a guard that keeps destructive commands from running unattended.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `layers` | optional | both | `hooks`, `guard` |
| `stack` | optional | detected from lockfiles/manifests | `node`, `python`, `go`, `polyglot` |
| `hook_manager` | optional | Node: existing manager or a plain `.githooks/` dir; Python/polyglot: the `pre-commit` framework if already used, else `.githooks/` | `husky`, `pre-commit`, `plain` |
| `pre_commit_steps` | optional | format staged files → typecheck → tests (only steps that exist as scripts) | "lint only, tests in pre-push" |
| `guard_scope` | optional | project | `global` (all repos for this user) |
| `blocked_patterns` | optional | built-in list in the guard script (header) | add `git rebase` via `EXTRA_BLOCKED`; allow feature-branch pushes via `PUSH_POLICY=protect` |
| `formatter` | optional | the repo's existing formatter; else Prettier (JS/TS), Ruff format (Python), gofmt (Go) | `biome format` |

## Output

- Hook layer: an executable pre-commit hook (and optional pre-push) that runs the agreed steps, a staged-files formatter config, a `prepare`/setup step so hooks install for every clone, and a demonstration commit that ran through the hook.
- Guard layer: [scripts/guard-git-command.sh](scripts/guard-git-command.sh) installed where the agent tool's pre-command hook can call it, registered in that tool's settings, and a test showing a blocked command exits 2 with a `BLOCKED:` message.

## Supporting files

- [scripts/install-hooks.sh](scripts/install-hooks.sh) `[--with-pre-push] [--dry-run] [--force] [--help]`: writes a plain `.githooks/pre-commit` (and optional pre-push) for the detected stack, running linters only on staged files, prints every omitted step, and sets `core.hooksPath`. Refuses to run if another hook manager or `core.hooksPath` is already configured. Use when no hook manager is wanted.
- [scripts/guard-git-command.sh](scripts/guard-git-command.sh): blocks dangerous git commands; reads the command from arguments or from JSON on stdin (`.tool_input.command` or `.command`). Checks each `;`/`&&`/`|` segment (and `bash -c` strings) separately, ignores git words inside quoted arguments, and fails closed without python3. Customize in its header: `PUSH_POLICY` (`block-all` or `protect` + `PROTECTED_BRANCHES`, also settable as `GUARD_PUSH_POLICY` / `GUARD_PROTECTED_BRANCHES` env vars) and `EXTRA_BLOCKED` regexes. Exit 2 = blocked.
- [templates/hook-configs.md](templates/hook-configs.md): ready configs for Node (hook manager + staged-file runner), the `pre-commit` framework, and formatter defaults. Read when choosing a hook manager.

## Steps

1. **Inventory first.** Look for existing hooks (`.husky/`, `.pre-commit-config.yaml`, `.githooks/`, `git config core.hooksPath`, `.git/hooks/*` non-sample files), formatter and lint configs, `typecheck`/`test` scripts, and CI. Extend what exists; do not add a second hook manager.
2. **Detect the package manager** for Node: `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, `bun.lockb`/`bun.lock` → bun, else npm. Use it in every command.
3. **Choose steps.** Pre-commit must stay fast (target < 10-20 s): format and lint staged files only, then typecheck; move slow test suites to pre-push or CI if they exceed that. Omit steps whose scripts do not exist and tell the user.
4. **Install the hook layer** with the chosen manager (`hook_manager`; configs in templates/hook-configs.md), or for plain hooks run `scripts/install-hooks.sh --dry-run` to review, then `scripts/install-hooks.sh [--with-pre-push]`. Make sure fresh clones get hooks (`"prepare"` script for Node, `pre-commit install` in setup docs, or `git config core.hooksPath .githooks` in the setup script).
5. **Formatter config**: create one only if none exists, using conservative defaults.
6. **Verify hooks**: hook file exists and is executable; run the staged-file step manually; make a commit (the guardrail commit itself is a good smoke test: `chore: add pre-commit hooks`). If the hook fails on existing code, report it; do not bypass with `--no-verify`.
7. **Install the guard** (if `layers` includes it): use `guard_scope` (ask if unset: project or global); copy `scripts/guard-git-command.sh` into the agent tool's hooks folder for that scope, `chmod +x`, and register it as a pre-command hook for shell commands in the tool's settings, merging into existing settings without overwriting them.
8. **Customize patterns** with the user (`blocked_patterns`): e.g. allow `git push` to feature branches but block force-pushes and pushes to `main` with `PUSH_POLICY="protect"`, or add `'git rebase( |$)'` to `EXTRA_BLOCKED`.
9. **Test the guard**: `echo '{"tool_input":{"command":"git push origin main"}}' | <guard>` → exit 2 and `BLOCKED: ...` on stderr; `echo '{"tool_input":{"command":"git push --dry-run && git push -f origin main"}}' | <guard>` → exit 2 (chained commands are checked per segment); `echo '{"tool_input":{"command":"git status"}}' | <guard>` → exit 0. Repeat for every pattern the user added.

## Checkpoints

- Only one hook manager in the repo.
- Pre-commit time measured and acceptable.
- Hooks install automatically for new clones (or the setup doc says how).
- Guard blocks every agreed pattern and allows read-only git commands.

## Worked example

Node repo, pnpm, has `typecheck` and `test` scripts, no hooks.
- Install dev deps: hook manager + staged-file runner + Prettier (none present).
- `.husky/pre-commit`: `pnpm exec lint-staged`, `pnpm typecheck`; tests take 70 s → moved to `.husky/pre-push`.
- `.lintstagedrc`: `{"*.{ts,tsx,js,json,md,css}": "prettier --write"}`.
- Commit `chore: add pre-commit hooks (staged formatting + typecheck)`; hook ran in 6 s.
- Guard installed for the project; test: `git push --force origin main` → `BLOCKED`, exit 2; `git log` → allowed.

## Pitfalls

- Running the full test suite in pre-commit until people start using `--no-verify`.
- Formatting all files instead of staged ones (huge unrelated diffs).
- Adding a hook manager when one already exists, or forgetting the install step for new clones.
- Overwriting the agent tool's existing settings instead of merging.
- Guard patterns so broad they block `git push --dry-run` or read-only commands, or so narrow that `git push -f` slips through.
- Treating the guard as security: it stops accidents, not a determined user; use branch protection on the server for enforcement.

## Done when

- [ ] Hook layer committed and demonstrated by a real commit through the hook.
- [ ] New clones get hooks automatically or via one documented command.
- [ ] Guard installed in the chosen scope, registered without clobbering settings, and tested (blocked → exit 2, safe → exit 0).
- [ ] User told which steps were omitted and why.
