#!/usr/bin/env bash
# ledger.sh - keep a progress ledger for executing a plan so work survives
# context loss. Only records a task complete if its test command passes.
#
#   ledger.sh init PLAN_FILE [LEDGER_PATH]   create or resume a ledger
#   ledger.sh start N                        record BASE commit for task N
#   ledger.sh done N -- CMD [ARGS...]        run CMD; on exit 0 record completion
#   ledger.sh rule N "TEXT"                  record a ruling for task N ("Final" allowed)
#   ledger.sh note "TEXT"                    free-form line (pre-flight rows, minors)
#   ledger.sh status                         print ledger and next incomplete task
#
# State lives in <repo root>/.work/ (works from any subdirectory). On init the
# script adds .work/ to .git/info/exclude if it is not already ignored, so a
# broad `git add -A` never commits the ledger. CMD runs in the current directory.
set -euo pipefail
root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
root_p="$(cd "$root" && pwd -P)"
state_dir="$root/.work"; ptr="$state_dir/.current-ledger"
die() { echo "ledger: $*" >&2; exit 1; }
ledger() { [ -f "$ptr" ] || die "no active ledger; run: ledger.sh init PLAN_FILE"; cat "$ptr"; }
rel() {  # repo-relative, normalised; portable (no GNU realpath -m needed on macOS)
  local d f; f="$(basename "$1")"
  if d="$(cd "$(dirname "$1")" 2>/dev/null && pwd -P)"; then
    case "$d/" in "$root_p"/*) d="${d#"$root_p"}"; d="${d#/}"; echo "${d:+$d/}$f"; return ;; esac
    echo "$d/$f"
  else echo "$1"; fi
}
abs() { case "$1" in /*) echo "$1" ;; *) echo "$PWD/$1" ;; esac; }

cmd="${1:-}"; shift || true
case "$cmd" in
  init)
    plan="${1:-}"; [ -n "$plan" ] || die "usage: init PLAN_FILE [LEDGER_PATH]"
    [ -f "$plan" ] || echo "ledger: warning: plan file $plan not found (recording the name anyway)" >&2
    plan_id="$(rel "$(abs "$plan")")"
    base="$(basename "$plan")"; base="${base%.*}"
    if [ -n "${2:-}" ]; then path="$(abs "$2")"; else path="$state_dir/$base/progress.md"; fi
    mkdir -p "$(dirname "$path")" "$state_dir"
    if git -C "$root" rev-parse --git-dir >/dev/null 2>&1 && ! git -C "$root" check-ignore -q "$state_dir/x"; then
      excl="$(git -C "$root" rev-parse --git-path info/exclude)"
      case "$excl" in /*) ;; *) excl="$root/$excl" ;; esac   # --git-path is relative to $root
      mkdir -p "$(dirname "$excl")"; echo ".work/" >> "$excl"
      echo "ledger: added .work/ to .git/info/exclude (local only, not committed)"
    fi
    if [ -f "$path" ]; then
      first="$(head -n1 "$path")"
      if [ "$first" != "# ledger - plan: $plan_id" ]; then
        die "$path belongs to another plan ($first); pass a different LEDGER_PATH"
      fi
      echo "ledger: $(rel "$path") (resuming)"
    else
      printf '# ledger - plan: %s\n' "$plan_id" > "$path"
      echo "ledger: $(rel "$path") (new)"
    fi
    echo "$path" > "$ptr"
    ;;
  start)
    n="${1:-}"; [ -n "$n" ] || die "usage: start N"
    l="$(ledger)"
    if grep -q "^Task $n: complete" "$l"; then die "task $n already complete"; fi
    sha="$(git rev-parse HEAD 2>/dev/null || echo none)"
    echo "Task $n: start (base ${sha:0:7})" >> "$l"
    echo "base: $sha"
    ;;
  done)
    n="${1:-}"; shift || true
    [ "${1:-}" = "--" ] && shift
    [ -n "$n" ] && [ $# -gt 0 ] || die "usage: done N -- CMD [ARGS...]"
    l="$(ledger)"; out="$(dirname "$l")/task-$n-test.log"
    grep -q "^Task $n: complete" "$l" && die "task $n already complete"
    base="$(grep "^Task $n: start" "$l" | tail -n1 | sed -n "s/.*base \([0-9a-f]*\).*/\1/p" || true)"
    [ -n "$base" ] || echo "ledger: warning: no 'start $n' recorded; commit range unknown" >&2
    head_sha="$(git rev-parse --short=7 HEAD 2>/dev/null || echo none)"
    set +e; "$@" > "$out" 2>&1; rc=$?; set -e
    tail -n 15 "$out"
    if [ $rc -eq 0 ]; then
      echo "Task $n: complete (commits ${base:-?}..$head_sha, tests: $* -> exit 0)" | tee -a "$l"
    else
      echo "Task $n: NOT complete - tests exited $rc (full log: $(rel "$out"))" >&2
      exit $rc
    fi
    ;;
  rule)
    n="${1:-}"; txt="${2:-}"; [ -n "$n" ] && [ -n "$txt" ] || die "usage: rule N \"TEXT\""
    l="$(ledger)"
    if [ "$n" = "Final" ]; then echo "Final: Ruling: $txt" >> "$l"; else echo "Task $n: Ruling: $txt" >> "$l"; fi
    echo "recorded"
    ;;
  note)
    txt="${1:-}"; [ -n "$txt" ] || die "usage: note \"TEXT\""
    echo "$txt" >> "$(ledger)"; echo "recorded"
    ;;
  status)
    l="$(ledger)"; cat "$l"; echo "---"
    done_list="$(grep -o '^Task [0-9]*: complete' "$l" | awk '{print $2}' | tr -d ':' | sort -n | uniq | tr '\n' ' ')"
    echo "completed: ${done_list:-none}"
    plan="$root/$(head -n1 "$l" | sed 's/^# ledger - plan: //')"
    if [ -f "$plan" ]; then
      tasks="$(grep -oE '^#+ *(Task +)?[0-9]+([.:) ]|$)' "$plan" | grep -oE '[0-9]+' | sort -n | uniq)"
      next=""; for t in $tasks; do case " $done_list " in *" $t "*) ;; *) next="$t"; break ;; esac; done
      echo "plan tasks: $(echo $tasks | wc -w)  next incomplete: ${next:-none (all complete)}"
    else
      echo "plan file not found; cannot compute the next task"
    fi
    ;;
  *) sed -n '2,14p' "$0"; exit 2 ;;
esac
