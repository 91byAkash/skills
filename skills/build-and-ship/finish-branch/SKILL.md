---
name: finish-branch
description: "Close out a finished branch safely: run the full suite, detect the workspace (checkout, worktree, detached HEAD), confirm the base, offer merge / PR / keep, and clean up only what this work created. Use when work is done and reviewed (\"merge this\", \"wrap up the branch\", \"open the PR\"), or to set up an isolated worktree first. Not for writing the PR text (use pr-description)."
license: MIT
metadata:
  category: "build-and-ship"
  version: "3.0.0"
---

# Finish a Branch

Verify, detect, ask, execute, clean up. The integration decision belongs to the user; destructive steps need explicit confirmation.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `branch` | optional | current branch | `feat/scheduled-posts` |
| `base` | optional | from plan/conversation/upstream, then confirmed with the user | `main`, `develop` |
| `test_cmd` | optional | detected (`npm test`, `pytest`, `cargo test`, `go test ./...`) | `make test` |
| `remote` | optional | `origin` | `upstream` |
| `choice` | optional | ask with the menu | `1` merge, `2` PR, `3` keep |
| `worktree_dir` | optional (setup) | user preference → existing `.worktrees/` → `worktrees/` → create `.worktrees/` | `../wt` |

## Output

- A green test run on the tree being integrated (command + counts).
- The executed choice: merge commit on `base` with tests green on the merged result, or a pushed branch + PR URL, or a "kept" note with branch and worktree path.
- Cleanup report: what was removed (worktree, branch) and what was preserved and why.

## Supporting files

- [scripts/branch-state.sh](scripts/branch-state.sh) `[BASE] [REMOTE]`: read-only report of workspace type, branch, upstream, ahead/behind, dirty files, cleanup owner, and a base-branch guess (the candidate HEAD forked from most recently, with the commit counts behind the guess). Run first.
- [REFERENCE.md](REFERENCE.md): starting work in an isolated worktree (detection, directory choice, ignore check, setup and baseline tests), and the rationalizations table. Read when setting up, or when cleanup is refused.

## Steps

1. **Verify.** Run the full `test_cmd` on the current tree. If anything fails, then report `Tests failing (N). Must fix before completing:` with the failures and stop; the menu comes only after green.
2. **Detect.** Run `scripts/branch-state.sh [<base>] [<remote>]` (pass `base` if known). Act on any `warning:` line first (on a base branch, nothing ahead, base not found). It reports:
   - `normal` (git dir == common dir) → 3-option menu, no worktree cleanup;
   - `worktree` on a named branch → 3-option menu, cleanup only if this work created it;
   - `detached worktree` → 2-option menu (no local merge); usually created by a host tool, so clean up only if `cleanup owner` says this project;
   - `detached (normal checkout)` → 2-option menu; nothing to clean up;
   - `submodule` → treat as normal.
   Capture the worktree path now; later steps change directory.
3. **Confirm the base.** If not stated in the plan or conversation, ask "This branch split from `<guess>`, correct?" (quote the candidate counts if more than one was close). Merging into the wrong base is expensive to undo.
4. **Present the menu exactly**, then wait:
   ```
   All tests pass on <branch>. How should I finish it?
   1. Merge into <base> here
   2. Push it and open a pull request
   3. Leave it as it is for now
   ```
   Detached HEAD: `1. Push to a new branch and open a pull request  2. Leave it as it is`. Never add "discard" to the menu.
5. **Execute.**
   - **1 Merge:** from the main checkout (`cd "$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)"`): `git checkout <base>`, then `git pull --ff-only` if `<base>` has an upstream (skip it for a local-only base), then `git merge --no-ff <branch>`, then run `test_cmd` on the merged result. If it fails, stop, leave branch and worktree intact, investigate (nothing is pushed yet). If green: cleanup (step 6), then `git branch -d <branch>`.
   - **2 PR:** `git push -u <remote> <branch>` (detached: `git push <remote> HEAD:refs/heads/<new-branch>`). Create the PR against `base` with the forge CLI or the URL printed on push, following the repo PR template (see `pr-description`). Report the URL. Keep the worktree for review fixes.
   - **3 Leave:** report `Left <name> untouched; its worktree is still at <path>.`
   - If a push is rejected, the remote moved: fetch and inspect; force-push only on explicit request.
6. **Clean up** (after option 1 or a confirmed discard only), from outside the worktree:
   - normal checkout → nothing to remove;
   - worktree under `.worktrees/` or `worktrees/` that this work created → `git worktree remove <path> && git worktree prune`;
   - any other worktree → owned by the host tool; leave it.
   - If removal is refused for modified/untracked files, never use `--force` yourself. Show `git -C <path> status --porcelain -uall` and ask: commit them to the branch, move them to the main checkout, or delete them.
7. **Discard (only if the user explicitly asks to throw the work away).** List what will be deleted (branch, commits from `git log <base>..<branch> --oneline`, worktree path) and require the user to type `discard`. Then clean up as in step 6 and `git branch -D <branch>`.

## Checkpoints

- Green suite output read before the menu.
- Base branch confirmed, not assumed.
- Option 1: tests re-run on the merged result before anything is deleted.
- No `--force`, `-D`, or force-push without the explicit confirmation described.

## Worked example

```
$ npm test            → 142 passed, 0 failed
$ scripts/branch-state.sh
type: worktree
branch: feat/scheduled-posts
worktree: /repo/.worktrees/feat-scheduled-posts
upstream: (none)
ahead/behind main: 6 / 2
dirty: 0 files
base guess: main  [commits ahead of each candidate: main(6)]
cleanup owner: this project (.worktrees/ or worktrees/)
```
"This branch split from `main`, correct?" → yes. Menu shown → user picks 1.
Merge in `/repo`, `npm test` on merged result → 142 passed. `git worktree remove /repo/.worktrees/feat-scheduled-posts`, `git worktree prune`, `git branch -d feat/scheduled-posts`. Report: merged into main at `9c1e2ab`, worktree and branch removed.

## Pitfalls

- "Tests passed earlier": run them on the tree you are integrating.
- Assuming the user wants a merge, or offering to discard unprompted.
- Accepting a casual "sure, delete it" as consent to discard; only the typed word `discard` counts.
- Removing the worktree right after opening a PR; review fixes happen there.
- Cleaning up worktrees you did not create.
- Running `git worktree remove` from inside the worktree being removed.

## Done when

- [ ] Suite green on the integrated tree (and on the merged result for option 1).
- [ ] Base confirmed; menu presented; user's choice executed.
- [ ] PR URL or merge commit reported, or kept branch/worktree path reported.
- [ ] Cleanup done only for owned workspaces, with nothing forced without confirmation.
