#!/usr/bin/env bash
# hotspots.sh - rank files and directories by how often they changed recently,
# and list file pairs that change together. Read-only. Run from inside the repo.
# Usage: hotspots.sh [SINCE] [TOP] [MAX_COMMITS] [PATH]
#   SINCE        git date spec, default "6 months ago" ("--since=3.months" also accepted)
#   TOP          rows to show per section, default 15
#   MAX_COMMITS  only the newest N commits in the window, default 300
#   PATH         limit to a subtree (the skill's `direction`), default .
# Lock files, minified files and files that no longer exist are skipped.
# Commits touching more than 30 files (bulk renames, formatting) are ignored for co-change.
set -euo pipefail
since="${1:-6 months ago}"; since="${since#--since=}"
top="${2:-15}"; max="${3:-300}"; scope="${4:-.}"
git rev-parse --git-dir >/dev/null 2>&1 || { echo "not a git repository (cd into the repo first)" >&2; exit 1; }
top_dir="$(git rev-parse --show-toplevel)"
# PATH is relative to where you run it; convert to repo-root-relative (portable, no GNU realpath)
if [ -d "$scope" ]; then abs="$(cd "$scope" && pwd -P)"
elif [ -d "$(dirname "$scope")" ]; then abs="$(cd "$(dirname "$scope")" && pwd -P)/$(basename "$scope")"
else echo "PATH '$scope' not found" >&2; exit 2; fi
case "$abs" in "$top_dir") scope=. ;; "$top_dir"/*) scope="${abs#"$top_dir"/}" ;; *) echo "PATH '$scope' is outside the repo" >&2; exit 2 ;; esac
case "$top" in ''|*[!0-9]*) echo "TOP must be a number" >&2; exit 2 ;; esac
case "$max" in ''|*[!0-9]*) echo "MAX_COMMITS must be a number" >&2; exit 2 ;; esac
cd "$top_dir"
tmp="$(mktemp)"; trap 'rm -f "$tmp"' EXIT
# one block per commit: '@@' then the changed files that still exist
git log --since="$since" --max-count="$max" --no-merges --name-only --pretty=format:'@@' -- "$scope" \
  | grep -vE '(^$|package-lock\.json|yarn\.lock|pnpm-lock\.yaml|\.lock$|\.min\.)' \
  | while IFS= read -r line; do
      if [ "$line" = "@@" ] || [ -e "$line" ]; then printf '%s\n' "$line"; fi
    done > "$tmp" || true
commits="$(grep -c '^@@$' "$tmp" || true)"
echo "window: since $since, newest $max commits max, path $scope -> $commits commits"
[ "$commits" -gt 0 ] || { echo "no commits in window; widen SINCE or PATH"; exit 0; }

echo; echo "== Files by commits touching them =="
grep -v '^@@$' "$tmp" | sort | uniq -c | sort -rn | head -n "$top"

echo; echo "== Directories by file changes =="
grep -v '^@@$' "$tmp" | awk -F/ 'NF>1{NF--; print}' OFS=/ | sort | uniq -c | sort -rn | head -n "$top"

echo; echo "== Most frequent co-changing file pairs (2+ shared commits) =="
awk '
  function flush() { if (n>1 && n<=30) for(i=1;i<=n;i++) for(j=i+1;j<=n;j++) { a=f[i]; b=f[j]; if (a>b){t=a;a=b;b=t}; c[a" <-> "b]++ }; n=0 }
  /^@@$/ { flush(); next }
  { f[++n]=$0 }
  END { flush(); for (k in c) if (c[k]>1) print c[k], k }
' "$tmp" | sort -rn | head -n "$top"
