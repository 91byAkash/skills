#!/usr/bin/env bash
# branch-state.sh - read-only summary of the current git workspace, used before
# integrating a branch. Prints: type, branch, worktree path, upstream,
# ahead/behind vs a base, dirty file count, and a base-branch guess.
# Usage: branch-state.sh [BASE] [REMOTE]
#   BASE    skip guessing and report against this branch
#   REMOTE  remote to consult for branches and its default HEAD (default origin)
# Base guess: among the remote's default branch, main, master, develop, trunk
# (local or remote, excluding the current branch), the one HEAD forked from
# most recently (fewest commits in BASE..HEAD). Always confirm it with the user.
set -uo pipefail
git rev-parse --git-dir >/dev/null 2>&1 || { echo "not a git repository" >&2; exit 1; }

abs() { (cd "$1" 2>/dev/null && pwd -P); }
gd="$(abs "$(git rev-parse --git-dir)")"
gc="$(abs "$(git rev-parse --git-common-dir)")"
top="$(git rev-parse --show-toplevel)"
branch="$(git branch --show-current)"
super="$(git rev-parse --show-superproject-working-tree 2>/dev/null)"
remote="${2:-origin}"

if [ -n "$super" ]; then type="submodule (treat as normal)"
elif [ "$gd" = "$gc" ]; then
  if [ -z "$branch" ]; then type="detached (normal checkout; 2-option menu)"; else type="normal"; fi
elif [ -z "$branch" ]; then type="detached worktree (2-option menu)"
else type="worktree"; fi

upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || echo '(none)')"

resolve() {  # print a usable ref for branch name $1, or nothing
  if git show-ref --verify --quiet "refs/heads/$1"; then echo "$1"
  elif git show-ref --verify --quiet "refs/remotes/$remote/$1"; then echo "$remote/$1"; fi
}

guess="${1:-}"; alts=""
if [ -z "$guess" ]; then
  default="$(git symbolic-ref --quiet --short "refs/remotes/$remote/HEAD" 2>/dev/null | sed "s|^$remote/||")"
  best=""; best_n=""
  seen=" "
  for b in $default main master develop trunk; do
    case "$seen" in *" $b "*) continue ;; esac; seen="$seen$b "
    [ "$b" = "$branch" ] && continue
    ref="$(resolve "$b")"; [ -n "$ref" ] || continue
    n="$(git rev-list --count "$ref..HEAD" 2>/dev/null)" || continue
    alts="$alts $b($n)"
    if [ -z "$best_n" ] || [ "$n" -lt "$best_n" ]; then best="$b"; best_n="$n"; fi
  done
  guess="$best"
fi

echo "type: $type"
echo "branch: ${branch:-(detached HEAD at $(git rev-parse --short HEAD))}"
echo "worktree: $top"
echo "upstream: $upstream"
if [ -n "$guess" ]; then
  ref="$(resolve "$guess")"
  if [ -n "$ref" ] && counts="$(git rev-list --left-right --count "$ref...HEAD" 2>/dev/null)"; then
    behind="${counts%%[[:space:]]*}"; ahead="${counts##*[[:space:]]}"
    echo "ahead/behind $guess: $ahead / $behind"
    [ "$ahead" = "0" ] && echo "warning: no commits ahead of $guess; nothing to integrate"
  else
    echo "warning: base '$guess' not found locally or on $remote"
  fi
fi
dirty="$(git status --porcelain | wc -l | tr -d ' ')"
echo "dirty: $dirty files"
echo "base guess: ${guess:-(unknown, ask the user)}${alts:+  [commits ahead of each candidate:$alts]}"
[ -n "$branch" ] && case " main master develop trunk " in *" $branch "*)
  echo "warning: you are on '$branch', which is usually a base branch, not a feature branch";; esac
case "$type" in
  worktree*|detached\ worktree*)
    case "$top" in
      */.worktrees/*|*/worktrees/*) echo "cleanup owner: this project (.worktrees/ or worktrees/)";;
      *) echo "cleanup owner: host tool (leave in place)";;
    esac;;
esac
exit 0
