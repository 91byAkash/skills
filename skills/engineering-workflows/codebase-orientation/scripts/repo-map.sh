#!/usr/bin/env bash
# repo-map.sh - read-only overview of a repository for orientation.
# Usage: repo-map.sh [REPO_DIR] [TREE_DEPTH]
#   REPO_DIR may be a subfolder (the `focus`): file lists and churn are then limited to it,
#   with paths relative to it. Prints sections to stdout; always exits 0 once it can cd.
set -uo pipefail
dir="${1:-.}"; depth="${2:-2}"
cd "$dir" || { echo "cannot cd to $dir" >&2; exit 1; }
prune='node_modules|.git|dist|build|out|target|vendor|.venv|venv|__pycache__|.next|.turbo|coverage|.cache'
list_files() {
  if git rev-parse --git-dir >/dev/null 2>&1; then git ls-files
  else find . -type f | sed 's|^\./||' | grep -vE "(^|/)($prune)(/|$)"; fi
}
section() { printf '\n== %s ==\n' "$1"; }

section "Tree (depth $depth, noise folders hidden)"
find . -maxdepth "$depth" -mindepth 1 \( -name node_modules -o -name .git -o -name dist -o -name build -o -name target -o -name vendor -o -name .venv -o -name venv -o -name __pycache__ -o -name .next -o -name coverage \) -prune -o -print \
  | sed 's|^\./||' | sort | head -n 120

section "Files by extension (top 15)"
list_files | awk -F. 'NF>1{print $NF}' | sort | uniq -c | sort -rn | head -n 15

section "Manifests and build files"
list_files | grep -E '(^|/)(package\.json|pnpm-workspace\.yaml|pyproject\.toml|requirements[^/]*\.txt|setup\.py|go\.mod|Cargo\.toml|pom\.xml|build\.gradle(\.kts)?|Gemfile|composer\.json|Makefile|Taskfile\.ya?ml|justfile|Dockerfile|docker-compose\.ya?ml|compose\.ya?ml)$' | head -n 40

section "Package scripts / make targets"
if [ -f package.json ] && command -v python3 >/dev/null; then
  python3 - <<'PY'
import json
try:
    s = json.load(open("package.json")).get("scripts", {})
    for k, v in s.items(): print(f"  npm run {k:<18} {v}")
except Exception as e: print("  (could not parse package.json)", e)
PY
fi
[ -f Makefile ] && grep -E '^[A-Za-z0-9_-][A-Za-z0-9_.-]*:([^=]|$)' Makefile | cut -d: -f1 | sed 's/^/  make /' | head -n 30
[ -f pyproject.toml ] && grep -A15 -E '^\[(project\.scripts|tool\.poetry\.scripts|tool\.taskipy\.tasks)\]' pyproject.toml | head -n 20

section "CI workflows"
list_files | grep -E '(^\.github/workflows/|^\.gitlab-ci\.yml$|^\.circleci/|^azure-pipelines\.yml$|^Jenkinsfile$|^\.buildkite/)' | head -n 20

section "Agent / contributor docs"
list_files | grep -iE '(^|/)(README|CONTRIBUTING|AGENTS|ARCHITECTURE|GLOSSARY|CONTEXT)[^/]*\.md$|(^|/)docs/(adr|decisions)/' | head -n 30

section "Test locations"
list_files | grep -E '(^|/)(tests?|__tests__|spec|e2e)/|\.(test|spec)\.[a-z]+$|_test\.(go|py)$|(^|/)test_[^/]*\.py$' \
  | awk -F/ '{print (NF>2 ? $1"/"$2"/" : (NF==2 ? $1"/" : "./"))}' | sort | uniq -c | sort -rn | head -n 10

section "Likely entry points"
list_files | grep -E '(^|/)(main\.(go|py|rs|ts|js)|index\.(ts|js)|server\.(ts|js|py)|app\.(py|ts|js)|manage\.py|cli\.(py|ts|js)|wsgi\.py|asgi\.py)$|(^|/)cmd/[^/]+/main\.go$|(^|/)bin/' | grep -vE "(^|/)($prune)/" | head -n 25

if git rev-parse --git-dir >/dev/null 2>&1; then
  section "Most changed files, last 6 months"
  # --relative limits to the current folder; lockfiles, minified and deleted files are skipped
  git log --since="6 months ago" --no-merges --name-only --relative --pretty=format: \
    | grep -v '^$' \
    | grep -vE '(^|/)([^/]*\.lock|package-lock\.json|pnpm-lock\.yaml|npm-shrinkwrap\.json|go\.sum)$|\.min\.(js|css)$' \
    | sort | uniq -c | sort -rn \
    | while read -r n f; do [ -e "$f" ] && printf '%7d %s\n' "$n" "$f"; done | head -n 12
  section "Recent commits"
  git log --oneline -n 10
fi

section "Largest source files (lines)"
list_files | grep -E '\.(ts|tsx|js|jsx|py|go|rs|java|kt|rb|php|cs|swift)$' | grep -vE '\.min\.js$' | head -n 5000 \
  | tr '\n' '\0' | xargs -0 -r wc -l 2>/dev/null | grep -v ' total$' | sort -rn | head -n 10
exit 0
