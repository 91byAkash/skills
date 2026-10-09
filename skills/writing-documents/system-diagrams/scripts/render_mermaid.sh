#!/usr/bin/env bash
# Render (and thereby validate) Mermaid diagrams with mermaid-cli in headless Chrome.
#
# Usage:
#   render_mermaid.sh diagram.mmd                       # -> diagram.svg next to it
#   render_mermaid.sh diagram.mmd out.png [--theme neutral|default|dark|forest] [--bg white|transparent] [--width 1600] [--scale 2]
#   render_mermaid.sh --check diagram.mmd               # validate only (renders to a temp file); exit 1 on a parse error
#   echo 'flowchart LR; A-->B' | render_mermaid.sh - out.svg
#
# Finds mmdc via $MMDC, PATH, or ./node_modules/.bin. Install once with:
#   npm install @mermaid-js/mermaid-cli     (set PUPPETEER_SKIP_DOWNLOAD=1 if Chrome is already installed)
# Finds Chrome via $PUPPETEER_EXECUTABLE_PATH or google-chrome / chromium on PATH.
# Exit codes: 0 ok, 1 Mermaid parse/render error (first lines printed), 2 setup problem.
set -euo pipefail

check=0; theme=neutral; bg=white; width=""; scale=""; args=()
while [ $# -gt 0 ]; do
  case "$1" in
    --check) check=1 ;;
    --theme) theme="$2"; shift ;;
    --bg) bg="$2"; shift ;;
    --width) width="$2"; shift ;;
    --scale) scale="$2"; shift ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) args+=("$1") ;;
  esac
  shift
done
[ ${#args[@]} -ge 1 ] || { sed -n '2,15p' "$0"; exit 2; }
in="${args[0]}"; out="${args[1]:-}"

mmdc="${MMDC:-}"
if [ -z "$mmdc" ]; then
  if command -v mmdc >/dev/null 2>&1; then mmdc=$(command -v mmdc)
  elif [ -x ./node_modules/.bin/mmdc ]; then mmdc=./node_modules/.bin/mmdc
  else echo "mmdc not found: npm install @mermaid-js/mermaid-cli, or set MMDC=/path/to/mmdc" >&2; exit 2; fi
fi
if [ -z "${PUPPETEER_EXECUTABLE_PATH:-}" ]; then
  for c in google-chrome google-chrome-stable chromium chromium-browser; do
    if command -v "$c" >/dev/null 2>&1; then export PUPPETEER_EXECUTABLE_PATH=$(command -v "$c"); break; fi
  done
fi

tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
printf '{"args":["--no-sandbox","--disable-gpu","--disable-dev-shm-usage"]}' > "$tmp/puppeteer.json"
if [ "$in" = "-" ]; then cat > "$tmp/stdin.mmd"; in="$tmp/stdin.mmd"; fi
[ -f "$in" ] || { echo "no such file: $in" >&2; exit 2; }
if [ "$check" = 1 ]; then out="$tmp/check.svg"; fi
[ -n "$out" ] || out="${in%.*}.svg"

extra=()
[ -n "$width" ] && extra+=(-w "$width")
[ -n "$scale" ] && extra+=(-s "$scale")
if ! "$mmdc" -i "$in" -o "$out" -t "$theme" -b "$bg" -p "$tmp/puppeteer.json" -q ${extra[@]+"${extra[@]}"} 2>"$tmp/err"; then
  # keep the useful part of the error: the parse message, not the stack trace
  grep -v '^\s*at \|Parser\.\|mermaid-cli-intercept' "$tmp/err" | sed '/^\s*$/d' | head -8 >&2
  echo "FAIL $in" >&2
  exit 1
fi
if [ "$check" = 1 ]; then echo "OK   $in"; else echo "$out"; fi
