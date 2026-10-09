#!/usr/bin/env bash
# find-polluter.sh - find which test file leaves a file or directory behind.
# Runs each matching test file on its own and checks whether TARGET appeared.
# Usage: find-polluter.sh TARGET "TEST_RUNNER_CMD" FILE...
#   TARGET           path that should not exist after a clean test run (e.g. .git, tmp/out.db)
#   TEST_RUNNER_CMD  command that runs one test file; the file path is appended
#   FILE...          test files to check (use your shell's globbing)
# Example: find-polluter.sh .git "npx vitest run" src/**/*.test.ts   (bash: shopt -s globstar first)
# Exit code: 1 when a polluter is found (it is printed), 0 when none is, 2 on usage errors.
set -uo pipefail
if [ $# -lt 3 ]; then
  sed -n '2,10p' "$0"; exit 2
fi
target="$1"; runner="$2"; shift 2
if [ -e "$target" ]; then
  echo "TARGET '$target' already exists; remove it first so results are meaningful." >&2
  exit 2
fi
total=$#; n=0
for f in "$@"; do
  n=$((n+1))
  printf '[%d/%d] %s\n' "$n" "$total" "$f"
  # run through bash so quoted arguments inside TEST_RUNNER_CMD survive
  bash -c "$runner \"\$1\"" _ "$f" >/dev/null 2>&1 || true
  if [ -e "$target" ]; then
    echo "FOUND: '$f' creates '$target'"
    ls -la "$target" 2>/dev/null | head -n 5
    exit 1
  fi
done
echo "No single test file created '$target'. It may need two tests in sequence; try running pairs."
exit 0
