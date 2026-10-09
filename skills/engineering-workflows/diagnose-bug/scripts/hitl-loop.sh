#!/usr/bin/env bash
# hitl-loop.sh - scripted reproduction that a person performs in their own terminal.
#
# Make a copy, replace the SCRIPT table below, and have the person run it. Each row is
# one of:
#   "do|<instruction>"             the person performs an action, then presses Enter
#   "ask|<NAME>|<question>"        the person types an answer, saved under NAME
# When every row is done, all answers are printed as NAME=value lines so the agent can
# parse them. Never collect passwords or tokens: logging in belongs in a "do" row.
set -euo pipefail

SCRIPT=(
  "do|In a private window, open the staging site and log in with the shared test account."
  "ask|ROWS_IMPORTED|Import sample.csv on the Import page. How many rows does the summary report?"
  "ask|CONSOLE_ERROR|Open the browser console. First red error line, verbatim (or 'none'):"
  "ask|BROWSER|Browser name and version:"
)

answers=()
total=${#SCRIPT[@]}
for idx in "${!SCRIPT[@]}"; do
  IFS='|' read -r kind first rest <<< "${SCRIPT[$idx]}"
  printf '\n[%d/%d] ' "$((idx + 1))" "$total"
  case "$kind" in
    do)
      printf '%s\n' "$first"
      read -r -p "      (Enter when finished) " _ ;;
    ask)
      printf '%s\n' "$rest"
      reply=""
      read -r -p "      > " reply
      answers+=("$first=$reply") ;;
    *)
      printf 'unknown row type: %s\n' "$kind" >&2; exit 2 ;;
  esac
done

printf '\n=== answers ===\n'
[ ${#answers[@]} -eq 0 ] || printf '%s\n' "${answers[@]}"   # guard: bash 3.2 + set -u
