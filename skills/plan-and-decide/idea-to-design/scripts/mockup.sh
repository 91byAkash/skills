#!/usr/bin/env bash
# mockup.sh - wrap one or more HTML fragments into a standalone page for
# showing layout options side by side.
# Usage: scripts/mockup.sh OUT.html "Title" fragA.html [fragB.html ...]
# Each fragment becomes a labelled column (A, B, C... up to H). Open OUT.html
# in a browser and ask the user to answer in chat with a letter.
# Fragments are body-level HTML (no <html>/<head>); the class "box" gives a
# dashed placeholder block, e.g. <div class="box">Sidebar nav</div>.
set -euo pipefail
if [ $# -lt 3 ]; then
  echo "usage: $0 OUT.html \"Title\" fragment.html [fragment.html ...]" >&2
  exit 2
fi
out="$1"; title="$2"; shift 2
letters=(A B C D E F G H)
if [ $# -gt ${#letters[@]} ]; then
  echo "at most ${#letters[@]} fragments (got $#); more options than that is not a comparison" >&2
  exit 2
fi
for frag in "$@"; do
  [ -f "$frag" ] || { echo "missing fragment: $frag" >&2; exit 1; }
done
esc() { sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' -e 's/"/\&quot;/g' <<<"$1"; }
title_html="$(esc "$title")"
mkdir -p "$(dirname "$out")"
tmp="$(mktemp "${out}.XXXXXX")"
trap 'rm -f "$tmp"' EXIT
{
  cat <<HTML
<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${title_html}</title>
<style>
  body{margin:0;font:15px/1.5 system-ui,sans-serif;background:#f4f4f5;color:#18181b}
  header{padding:16px 24px;background:#fff;border-bottom:1px solid #e4e4e7}
  header h1{margin:0;font-size:18px} header p{margin:4px 0 0;color:#52525b}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px;padding:24px}
  .opt{background:#fff;border:1px solid #e4e4e7;border-radius:10px;overflow:hidden}
  .opt h2{margin:0;padding:8px 14px;font-size:13px;letter-spacing:.06em;text-transform:uppercase;background:#fafafa;border-bottom:1px solid #e4e4e7}
  .opt .body{padding:16px}
  .box{border:1px dashed #a1a1aa;border-radius:6px;padding:10px;margin:6px 0;color:#52525b}
</style></head><body>
<header><h1>${title_html}</h1><p>Reply in chat with the letter you prefer, or what to combine.</p></header>
<main class="grid">
HTML
  i=0
  for frag in "$@"; do
    printf '<section class="opt"><h2>Option %s</h2><div class="body">\n' "${letters[$i]}"
    cat "$frag"
    printf '\n</div></section>\n'
    i=$((i+1))
  done
  printf '</main></body></html>\n'
} > "$tmp"
mv "$tmp" "$out"
trap - EXIT
echo "wrote $out ($# options)"
