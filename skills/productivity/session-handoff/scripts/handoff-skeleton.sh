#!/usr/bin/env bash
# Print a handoff skeleton pre-filled with repository state.
# Usage: handoff-skeleton.sh "<task title>" [REPO_DIR]
# Fill in the sections marked TODO; nothing here is sent anywhere.
set -euo pipefail
case "${1:-}" in -h|--help) sed -n '2,4p' "$0"; exit 0 ;; esac
task=${1:-"<task>"}; dir=${2:-.}
cd "$dir" 2>/dev/null || { echo "handoff-skeleton.sh: no such directory: $dir" >&2; exit 2; }
now=$(date '+%Y-%m-%d %H:%M %Z')
echo "# Handoff: $task ($now)"
echo
if git rev-parse --git-dir >/dev/null 2>&1; then
  if ! git rev-parse --verify -q HEAD >/dev/null; then
    branch="$(git symbolic-ref --short HEAD 2>/dev/null || echo '?') (no commits yet)"
  elif ! branch=$(git symbolic-ref --short -q HEAD); then
    branch="detached HEAD at $(git rev-parse --short HEAD)"
  fi
  upstream=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || echo "none")
  ab=""
  if [[ $upstream != none ]]; then
    read -r behind ahead < <(git rev-list --left-right --count "$upstream...HEAD")
    ab=" (ahead $ahead, behind $behind)"
  fi
  dirty=$(git status --porcelain | wc -l | tr -d ' ')
  unpushed=""
  [[ $upstream == none ]] && unpushed="branch has no upstream; "
  [[ -n ${ahead:-} && ${ahead:-0} -gt 0 ]] && unpushed+="$ahead unpushed commit(s); "
  if (( dirty > 0 )) || [[ -n $unpushed ]]; then
    echo "> WARNING: ${unpushed}${dirty} uncommitted file(s). Commit, push, or note them before switching machines."
    echo
  fi
  echo "## Goal"
  echo "TODO: 1-2 sentences + definition of done"
  echo
  echo "## State"
  echo "- Branch: \`$branch\`, upstream \`$upstream\`$ab"
  if (( dirty == 0 )); then echo "- Uncommitted: none"; else
    echo "- Uncommitted:"
    git status --porcelain | sed 's/^/  - /' | head -30
  fi
  (( dirty > 30 )) && echo "  - … $((dirty - 30)) more"
  echo "- Recent commits:"
  git log -8 --format='  - %h %s (%cr)' 2>/dev/null || echo "  - none"
  stashes=$(git stash list | head -5)
  [[ -n $stashes ]] && { echo "- Stashes:"; sed 's/^/  - /' <<<"$stashes"; }
  wts=$(git worktree list 2>/dev/null | wc -l | tr -d ' ')
  (( wts > 1 )) && { echo "- Worktrees:"; git worktree list | sed 's/^/  - /'; }
else
  echo "## Goal"
  echo "TODO"
  echo
  echo "## State"
  echo "- Not a git repository: $(pwd)"
fi
cat <<'MD'
- Done: TODO (with evidence)
- In progress: TODO (file:line)
- Next (ordered):
  1. TODO
  2. TODO

## Decisions (and why)
- TODO

## Tried and rejected
- TODO

## Open questions / risks
- TODO

## How to verify
```
TODO commands
```

## Environment
- TODO services to run, env var names (no values), seed data, accounts: <redacted: where to get it>

## References
- TODO

## Parked (out of scope for the next session)
- TODO or delete

## Suggested skills
- TODO
MD
