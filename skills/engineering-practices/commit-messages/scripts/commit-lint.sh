#!/usr/bin/env bash
# Lint a commit message.
#   commit-lint.sh FILE          (as a commit-msg hook: .git/hooks/commit-msg → this script)
#   commit-lint.sh -m "message"
#   echo "message" | commit-lint.sh
# Options: --plain   do not require Conventional Commits types (repo uses plain sentences)
# Exit 0 = ok (warnings allowed), 1 = errors.
set -euo pipefail
plain=0; msg=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --plain) plain=1; shift;;
    -m) [[ $# -ge 2 ]] || { echo "error: -m needs a message" >&2; exit 2; }; msg=$2; shift 2;;
    -h|--help) sed -n '2,7p' "$0"; exit 0;;
    *) msg=$(cat -- "$1"); shift;;
  esac
done
[[ -z $msg && ! -t 0 ]] && msg=$(cat)
# drop everything below the scissors line (`git commit -v` appends the diff there),
# then the comment lines git adds to the editor template
msg=$(sed -e '/^# -\{24\} >8 -\{24\}$/,$d' -e '/^#/d' <<<"$msg")
[[ -n ${msg//[[:space:]]/} ]] || { echo "error: empty message"; exit 1; }

errors=0; warns=0
err()  { echo "error: $*"; errors=$((errors + 1)); }
warn() { echo "warn:  $*"; warns=$((warns + 1)); }

subject=$(head -n1 <<<"$msg")
second=$(sed -n '2p' <<<"$msg")
body=$(tail -n +3 <<<"$msg")
types='feat|fix|refactor|perf|test|docs|build|ci|chore|style|revert'

case $subject in Merge\ *|Revert\ \"*|fixup!\ *|squash!\ *) echo "ok (generated subject)"; exit 0;; esac

if (( ! plain )); then
  if [[ ! $subject =~ ^($types)(\([A-Za-z0-9._/,-]+\))?(!)?:\ (.+)$ ]]; then
    err "subject must be '<type>(<scope>)!: <summary>' with type in: ${types//|/, }"
    summary=$subject
  else
    summary=${BASH_REMATCH[4]}
    breaking=${BASH_REMATCH[3]}
  fi
else
  summary=$subject
fi

len=${#subject}
(( len > 72 )) && err "subject is $len chars (max 72)"
(( len > 50 && len <= 72 )) && warn "subject is $len chars (aim for 50)"
[[ $subject =~ \.$ ]] && err "subject ends with a period"
first=$(awk '{print tolower($1)}' <<<"$summary")
if [[ $first =~ (ed|ing)$ && ! $first =~ ^(embed|feed|need|seed|speed|shed|bring|ping|string|ring|spring|thing|log-ing)$ ]] || \
   [[ $first =~ ^(adds|fixes|updates|removes|changes|creates|makes|implements|improves)$ ]]; then
  warn "summary should be imperative: use the base verb ('fix', 'add'), not '$first'"
fi
[[ $summary =~ ^(wip|fix|update|updates|changes|misc|stuff)$ ]] && err "summary '$summary' says nothing"
grep -Eqi '\b(this commit|this pr)\b' <<<"$msg" && warn "avoid 'this commit/PR'; state the change directly"

[[ -n $second ]] && err "line 2 must be blank (separates subject from body)"
long=$(awk 'NR > 2 && length > 72 && $0 !~ /^(BREAKING CHANGE|[A-Za-z-]+:) / && $0 !~ /https?:\/\// {print NR}' <<<"$msg" | paste -sd, -)
[[ -n $long ]] && warn "body lines over 72 chars: $long"

if [[ -n ${breaking:-} ]] && ! grep -q '^BREAKING CHANGE: ' <<<"$body"; then
  err "'!' in subject needs a 'BREAKING CHANGE: <what and how to migrate>' footer (house rule; the spec allows omitting it)"
fi
if grep -q '^BREAKING CHANGE' <<<"$body" && [[ -z ${breaking:-} ]] && (( ! plain )); then
  warn "BREAKING CHANGE footer present; add '!' after the type for visibility"
fi
if [[ ${subject%%[(:!]*} == revert && -z ${body//[[:space:]]/} ]]; then
  err "revert commits need a body saying why"
fi

if (( errors )); then echo "commit message: $errors error(s), $warns warning(s)"; exit 1; fi
if (( warns )); then echo "commit message: ok ($warns warning(s))"; else echo "commit message: ok"; fi
