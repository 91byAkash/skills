#!/usr/bin/env bash
# Report how often each glossary term and each of its avoided synonyms appears.
# Usage: term-usage.sh GLOSSARY.md [PATH...]   (paths default to .)
# Reads entries of the form "**Term**:" followed by an "_Avoid_: a, b, c" line.
# Output: one block per term; avoided words with hits are marked "DRIFT". Exit 0 either way.
# Matching is case-insensitive and whole-word; multi-word terms also match identifier forms
# (subscription_cancellation, subscriptionCancellation, subscription-cancellation).
# Parenthetical notes in an Avoid list ("churn (a metric, not an event)") are ignored.
set -euo pipefail
[[ ${1:-} == -h || ${1:-} == --help ]] && { sed -n '2,8p' "$0"; exit 0; }
[[ $# -ge 1 && -f $1 ]] || { echo "usage: $0 GLOSSARY.md [PATH...]" >&2; exit 2; }
glossary=$1; shift
paths=("$@"); [[ ${#paths[@]} -eq 0 ]] && paths=(.)

pattern() {  # escape ERE metacharacters, then let spaces match space, _, - or nothing
  sed -E 's/[][\.^$*+?(){}|/]/\\&/g; s/[[:space:]]+/[[:space:]_-]?/g' <<<"$1"
}
count() {  # case-insensitive whole-word count, skipping vendored/build dirs and the glossary itself
  grep -rIiowE --exclude-dir={.git,node_modules,dist,build,vendor,.venv} \
       --exclude="$(basename "$glossary")" -e "$(pattern "$1")" "${paths[@]}" 2>/dev/null | wc -l | tr -d ' ' || true
}
where() {
  grep -rIilwE --exclude-dir={.git,node_modules,dist,build,vendor,.venv} \
       --exclude="$(basename "$glossary")" -e "$(pattern "$1")" "${paths[@]}" 2>/dev/null | head -5 | paste -sd' ' - || true
}

term=""; drift=0
while IFS= read -r line; do
  if [[ $line =~ ^\*\*([^*]+)\*\*: ]]; then
    term=${BASH_REMATCH[1]}
    printf '%-28s %5s uses\n' "$term" "$(count "$term")"
  elif [[ -n $term && $line =~ ^_Avoid_:[[:space:]]*(.*)$ ]]; then
    avoid=$(sed -E 's/\([^)]*\)//g' <<<"${BASH_REMATCH[1]}")
    IFS=',' read -ra words <<<"$avoid"
    for w in "${words[@]}"; do
      w=$(sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//' <<<"$w")
      [[ -z $w ]] && continue
      n=$(count "$w")
      if (( n > 0 )); then
        printf '  DRIFT avoid %-18s %5s uses  e.g. %s\n' "\"$w\"" "$n" "$(where "$w")"
        drift=$((drift + 1))
      else
        printf '  ok    avoid %-18s %5s\n' "\"$w\"" 0
      fi
    done
  fi
done < "$glossary"
echo "avoided words still in use: $drift"
