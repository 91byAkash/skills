# Finish a Branch: reference

## Starting work in an isolated worktree

1. **Detect existing isolation.** Compare `git rev-parse --git-dir` with `--git-common-dir` (resolved to absolute paths). Different → already in a linked worktree (unless `git rev-parse --show-superproject-working-tree` prints a path, which means a submodule). Do not nest worktrees.
2. **Ask consent** if the user has not stated a preference: "Set up an isolated worktree so your current branch is untouched?" If declined, work in place.
3. **Prefer the host tool's native worktree feature** if one exists; manual `git worktree add` creates state the host cannot see.
4. **Choose the directory:** declared preference → existing `.worktrees/` → existing `worktrees/` → create `.worktrees/`.
5. **Make sure it is ignored:** `git check-ignore -q .worktrees/x || echo .worktrees/ >> "$(git rev-parse --git-path info/exclude)"`. This ignores it locally without committing to the user's branch; commit a `.gitignore` line only if the user wants it shared. Run from the repo root.
6. **Create:** `git worktree add .worktrees/<branch> -b <branch> && cd .worktrees/<branch>`. If the sandbox denies it, say so and work in place.
7. **Set up the project** by detected stack: `package.json` → `npm ci` (or pnpm/yarn per lockfile); `pyproject.toml`/`requirements.txt` → create venv and install; `Cargo.toml` → `cargo build`; `go.mod` → `go mod download`.
8. **Baseline tests** before any change. If they already fail, report it and ask whether to proceed; otherwise you cannot tell your breakage from existing breakage.

## Option summary

| Option | Merge | Push | Keep worktree | Delete branch |
|---|---|---|---|---|
| 1 Merge locally | yes | no | no | yes (`-d`) |
| 2 Pull request | no | yes | yes | no |
| 3 Keep as-is | no | no | yes | no |
| Discard (explicit request + typed `discard`) | no | no | no | yes (`-D`) |

## Rationalizations to reject

| Thought | Reality |
|---|---|
| "Tests passed earlier this session." | Only a run on this exact tree counts. |
| "They obviously want it merged." | Show the menu and wait. |
| "They seem done, I'll offer to discard." | Discard is never offered, only honoured on request. |
| "'Get rid of it' is confirmation enough." | Only the typed word authorizes deletion. |
| "PR is open, worktree is clutter." | Review fixes happen there; keep it until the work lands. |
| "That other worktree looks stale." | Only clean up worktrees this project created. |
| "Removal refused, `--force` finishes the job." | Refusal means files exist nowhere else; ask. |
| "Merged result failed, probably flaky." | Stop; branch and worktree stay while you investigate. |
| "Push rejected, force-push fixes it." | The remote moved; investigate first. |
