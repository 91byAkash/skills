#!/usr/bin/env bash
# Extract one task from a markdown plan into its own brief file.
# Usage: task-brief.sh PLAN_FILE N [WORKSPACE]
#   WORKSPACE default: .agent-work/<plan-slug> at the repo root (added to .git/info/exclude
#   so briefs and reports are never committed by `git add -A`).
# A task starts at a heading like "## Task 3", "### Task 3: Title" or "## 3. Title" and runs
# until the next heading of the same or higher level. Lines inside ``` or ~~~ fences are
# never treated as headings (shell comments in code blocks stay in the brief).
# Prints the brief path. Exit 1 if the task is not found, 2 on bad usage.
set -euo pipefail
usage="usage: task-brief.sh PLAN_FILE N [WORKSPACE]"
case ${1:-} in -h|--help) sed -n '2,9p' "$0"; exit 0;; "") echo "$usage" >&2; exit 2;; esac
[[ $# -ge 2 ]] || { echo "$usage" >&2; exit 2; }
plan=${1:?$usage}; n=${2:?$usage}
[[ -f $plan ]] || { echo "no such plan: $plan" >&2; exit 2; }
[[ $n =~ ^[0-9]+$ ]] || { echo "N must be a task number: $n" >&2; exit 2; }
slug=$(basename "$plan" .md)
root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
ws=${3:-$root/.agent-work/$slug}
mkdir -p "$ws"
if git rev-parse --git-dir >/dev/null 2>&1; then
  ex="$(git rev-parse --git-path info/exclude)"; mkdir -p "$(dirname "$ex")"
  grep -qxF '.agent-work/' "$ex" 2>/dev/null || echo '.agent-work/' >> "$ex"
fi
out="$ws/task-$n-brief.md"
awk -v n="$n" '
  function level(s) { match(s, /^#+/); return RLENGTH }
  /^[ \t]*(```|~~~)/ { fence = !fence; if (found) print; next }
  !fence && /^#+[ \t]/ {
    if (found && level($0) <= lvl) { exit }
    if (!found && ($0 ~ "^#+[ \t]+(Task[ \t]+)?" n "([^0-9]|$)")) { found = 1; lvl = level($0) }
  }
  found { print }
  END { if (!found) exit 1 }
' "$plan" > "$out" || { rm -f "$out"; echo "task $n not found in $plan" >&2; exit 1; }
{ echo; echo "<!-- extracted from $plan, task $n -->"; } >> "$out"
echo "$out"
