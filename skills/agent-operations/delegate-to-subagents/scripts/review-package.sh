#!/usr/bin/env bash
# review-package.sh BASE [HEAD] [WORKSPACE]
#
# Bundles everything a reviewer needs for the range BASE..HEAD into a single text
# file and prints that file's path:
#   1. one line per commit   2. per-file change counts   3. the diff, 10 lines of context
# HEAD defaults to the current HEAD. WORKSPACE defaults to <repo root>/.agent-work, which
# is kept out of commits through .git/info/exclude; pass the per-plan workspace you
# also gave task-brief.sh. Take BASE from what you recorded before the implementer
# began (never HEAD~1), so a task made of several commits is reviewed as a whole.
set -euo pipefail

die() { printf 'review-package: %s\n' "$*" >&2; exit 1; }
case ${1:-} in -h|--help) sed -n '2,10p' "$0"; exit 0;; esac
[ $# -ge 1 ] || die "usage: review-package.sh BASE [HEAD] [WORKSPACE]"

from_rev=$1
to_rev=${2:-HEAD}
for rev in "$from_rev" "$to_rev"; do
  git cat-file -e "$rev^{commit}" 2>/dev/null || die "not a commit: $rev"
done

top=$(git rev-parse --show-toplevel)
workspace=${3:-$top/.agent-work}
mkdir -p "$workspace"

# Keep the scratch folder out of `git add -A` without touching tracked files.
exclude_file=$(git rev-parse --git-path info/exclude)
mkdir -p "${exclude_file%/*}"
if ! grep -qxF '.agent-work/' "$exclude_file" 2>/dev/null; then
  printf '.agent-work/\n' >> "$exclude_file"
fi

range="$from_rev..$to_rev"
short() { git rev-parse --short "$1"; }
package="$workspace/review-$(short "$from_rev")-$(short "$to_rev").txt"

section() { printf '\n## %s\n' "$1"; shift; "$@"; }
{
  printf '# Review package %s\n' "$range"
  section "Commits" git log --oneline "$range"
  section "Stat" git diff --stat "$range"
  section "Diff" git diff --unified=10 "$range"
} > "$package"

if [ "$(git rev-list --count "$range")" -eq 0 ]; then
  printf 'warning: no commits in range\n' >&2
fi
printf '%s\n' "$package"
