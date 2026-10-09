#!/usr/bin/env bash
# html_to_pdf.sh - print an HTML file to PDF with headless Chrome/Chromium.
# Use for rich layouts, CSS print styles, and scripts ReportLab cannot shape
# (Devanagari, Arabic, Thai...). Page size/margins come from CSS @page.
#
# Usage: html_to_pdf.sh page.html out.pdf
#   Chrome's own date/URL header and footer are always suppressed; put running
#   footers in the HTML (position: fixed; bottom: 0).
#   <style>@page { size: A4; margin: 18mm } .break { break-before: page }</style>
#   Set CHROME=/path/to/chrome to pick a browser; macOS app bundles are found too.
set -euo pipefail
[ $# -ge 2 ] || { sed -n '2,9p' "$0"; exit 1; }
in="$1"; out="$2"; shift 2
[ -f "$in" ] || { echo "error: $in not found" >&2; exit 1; }
browser="${CHROME:-}"
if [ -z "$browser" ]; then
  for b in google-chrome google-chrome-stable chromium chromium-browser chrome; do
    if command -v "$b" >/dev/null 2>&1; then browser="$b"; break; fi
  done
fi
if [ -z "$browser" ]; then
  for b in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium"; do
    if [ -x "$b" ]; then browser="$b"; break; fi
  done
fi
[ -n "$browser" ] || { echo "error: no Chrome/Chromium found (alternatives: weasyprint, wkhtmltopdf)" >&2; exit 1; }
abs_in="$(cd "$(dirname "$in")" && pwd)/$(basename "$in")"
abs_out="$(cd "$(dirname "$out")" && pwd)/$(basename "$out")"
profile="$(mktemp -d)"; trap 'rm -rf "$profile"' EXIT
flags=(--headless=new --disable-gpu --no-sandbox --user-data-dir="$profile" --no-pdf-header-footer --run-all-compositor-stages-before-draw --virtual-time-budget=5000)
rm -f "$abs_out"
# GNU timeout is not on stock macOS; fall back to gtimeout or no limit
tmo=""
if command -v timeout >/dev/null 2>&1; then tmo="timeout 90"
elif command -v gtimeout >/dev/null 2>&1; then tmo="gtimeout 90"; fi
$tmo "$browser" "${flags[@]}" --print-to-pdf="$abs_out" "file://$abs_in" >/dev/null 2>&1 || true
[ -s "$abs_out" ] || { echo "error: no PDF produced" >&2; exit 1; }
echo "$abs_out"
