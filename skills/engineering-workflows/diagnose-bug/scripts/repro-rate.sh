#!/usr/bin/env bash
# repro-rate.sh - run a command many times and report how often it fails.
# Usage: repro-rate.sh [-n RUNS] [-j PARALLEL] [-q] -- COMMAND [ARGS...]
#   -n  number of runs (default 50)
#   -j  parallel workers (default 1)
#   -q  only print the summary
# Exit code: 0 if no run failed, 1 otherwise. Logs of failing runs are kept
# in a temp directory that is printed at the end.
set -uo pipefail
runs=50; par=1; quiet=0
while [ $# -gt 0 ]; do
  case "$1" in
    -n) runs="$2"; shift 2 ;;
    -j) par="$2"; shift 2 ;;
    -q) quiet=1; shift ;;
    --) shift; break ;;
    *) echo "usage: $0 [-n RUNS] [-j PARALLEL] [-q] -- COMMAND" >&2; exit 2 ;;
  esac
done
[ $# -gt 0 ] || { echo "no command given" >&2; exit 2; }
case "$runs" in ''|*[!0-9]*|0) echo "-n must be a positive integer" >&2; exit 2 ;; esac
case "$par" in ''|*[!0-9]*|0) echo "-j must be a positive integer" >&2; exit 2 ;; esac
logdir="$(mktemp -d)"
export logdir
run_one() {
  i="$1"; shift
  if "$@" > "$logdir/run-$i.log" 2>&1; then rm -f "$logdir/run-$i.log"; echo pass; else echo fail; fi
}
export -f run_one
start=$(date +%s)
results="$(seq 1 "$runs" | xargs -P "$par" -I{} bash -c 'run_one "$@"' _ {} "$@")"
fails=$(printf '%s\n' "$results" | grep -c '^fail$' || true)
secs=$(( $(date +%s) - start ))
pct=$(awk -v f="$fails" -v r="$runs" 'BEGIN{printf "%.1f", (f*100.0)/r}')
[ "$quiet" -eq 1 ] || ls "$logdir" | head -n 5 | sed "s|^|failing log: $logdir/|"
if [ "$fails" -eq 0 ]; then rmdir "$logdir" 2>/dev/null; logdir="(none, all passed)"; fi
echo "runs=$runs failures=$fails rate=${pct}% parallel=$par elapsed=${secs}s logs=$logdir"
[ "$fails" -eq 0 ]
