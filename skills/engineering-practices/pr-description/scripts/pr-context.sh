#!/usr/bin/env bash
# Summarise a branch for writing a PR description.
# Usage: pr-context.sh [BASE] [HEAD]
#   BASE default: origin/HEAD, else main, else master.  HEAD default: HEAD (committed work only;
#   uncommitted changes are reported separately because they are not in the PR).
# Exit: 0 ok, 2 not a repo / unknown ref.
set -euo pipefail
git rev-parse --git-dir >/dev/null 2>&1 || { echo "not a git repository" >&2; exit 2; }

base=${1:-}; head=${2:-HEAD}
if [[ -z $base ]]; then
  base=$(git symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null || true)
  for b in main master; do [[ -z $base ]] && git rev-parse -q --verify "$b^{commit}" >/dev/null && base=$b; done
fi
[[ -n $base ]] || { echo "cannot find base branch; pass one" >&2; exit 2; }
for r in "$base" "$head"; do
  git rev-parse -q --verify "$r^{commit}" >/dev/null || { echo "unknown ref: $r (try origin/$r, or git fetch)" >&2; exit 2; }
done
mb=$(git merge-base "$base" "$head") || { echo "no common ancestor between $base and $head" >&2; exit 2; }
range=("$mb" "$head")
name=$head; [[ $head == HEAD ]] && name=$(git rev-parse --abbrev-ref HEAD)
lockfiles='(^|/)(package-lock\.json|npm-shrinkwrap\.json|pnpm-lock\.yaml|yarn\.lock|bun\.lockb?|Cargo\.lock|poetry\.lock|uv\.lock|Pipfile\.lock|Gemfile\.lock|composer\.lock|go\.sum)$'

echo "== branch $name vs $base (merge-base ${mb:0:8})"
echo
echo "== commits"
git log --reverse --format='- %s%n%w(0,2,2)%b' "$mb..$head" | sed '/^ *$/d'
echo
echo "== size"
git diff --shortstat "${range[@]}"
git diff --numstat "${range[@]}" | awk -F'\t' -v lf="$lockfiles" \
  '$3 !~ lf && $3 !~ /(\.min\.(js|css)|\.snap|\.svg)$|(^|\/)(dist|build|generated|__generated__)\// { n += ($1 == "-" ? 0 : $1) + ($2 == "-" ? 0 : $2) }
   END { printf "  %d changed lines excluding lockfiles and generated files%s\n", n, (n > 400 ? " (large: propose a reading order or a split)" : "") }'
if [[ $head == HEAD ]] && ! git diff --quiet HEAD 2>/dev/null; then
  echo "  note: uncommitted changes exist and are NOT part of this PR: $(git diff --shortstat HEAD)"
fi
echo
echo "== changed lines by top-level area"
git diff --numstat "${range[@]}" | awk -F'\t' '{ n = split($3, p, "/"); a = (n == 1 ? "." : p[1]);
    add[a] += ($1 == "-" ? 0 : $1); del[a] += ($2 == "-" ? 0 : $2) }
  END { for (k in add) printf "  %-30s +%-6d -%d\n", k, add[k], del[k] }' | sort
echo
echo "== risk signals"
files=$(git diff --name-only "${range[@]}")
flag() { local label=$1 pattern=$2; local hits; hits=$(grep -Ei -- "$pattern" <<<"$files" || true)
  [[ -n $hits ]] && { echo "  $label:"; sed 's/^/    /' <<<"$hits"; } || true; }
test_re='(^|/)(tests?|__tests__|spec|e2e)/|[._-](test|spec)\.[a-z]+$|_test\.(go|py)$|(^|/)test_[^/]*\.py$'
flag "migrations / schema (one-way door?)" '(^|/)(migrations?|alembic|prisma)/|schema\.|\.sql$'
flag "dependencies"                       "(^|/)(package\.json|requirements[^/]*\.txt|pyproject\.toml|go\.mod|Cargo\.toml|Gemfile|composer\.json)$|$lockfiles"
flag "config / env"                       '(^|/)\.env|(^|/)(config|settings)|\.ya?ml$|\.toml$'
flag "CI / build"                         '(^|/)\.github/|\.gitlab-ci|Jenkinsfile|Dockerfile|Makefile|\.circleci/'
flag "public API / contracts"             '(openapi|swagger)|\.proto$|\.graphqls?$|(^|/)(routes?|api)/'
flag "tests"                              "$test_re"
if ! grep -Eqi -- "$test_re" <<<"$files"; then echo "  no test files changed: say why in the PR, or add tests"; fi
issues=$(git log --format='%s %b' "$mb..$head" | grep -oE '#[0-9]+' | sort -u | paste -sd' ' - || true)
branch_issue=$(grep -oE '[0-9]{2,}' <<<"$name" | head -1 || true)
echo
echo "== referenced issues: ${issues:-none}${branch_issue:+ (branch mentions $branch_issue)}"
