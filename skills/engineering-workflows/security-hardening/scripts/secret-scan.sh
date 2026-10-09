#!/usr/bin/env bash
# Scan for likely secrets.
#   secret-scan.sh            scan lines added in the staged diff (default)
#   secret-scan.sh --path DIR scan files under DIR: tracked + untracked-but-not-ignored in a
#                             git repo, every file (minus .git/, node_modules/) otherwise
# Exit 0 = clean, 1 = possible secrets found, 2 = usage error.
set -euo pipefail

mode=staged; dir=.
case "${1:-}" in
  --path) mode=path; dir="${2:-.}"
          [[ -d $dir ]] || { echo "not a directory: $dir" >&2; exit 2; };;
  -h|--help) sed -n '2,6p' "$0"; exit 0;;
  "") ;;
  *) echo "unknown option: $1" >&2; exit 2;;
esac

patterns=(
  'AKIA[0-9A-Z]{16}'                                  # cloud access key id
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'
  'xox[baprs]-[0-9A-Za-z-]{10,}'                      # chat bot/user tokens
  'gh[pousr]_[0-9A-Za-z]{30,}'                        # code-host tokens
  'sk_(live|test)_[0-9A-Za-z]{16,}'                   # payment keys
  '(^|[^A-Za-z0-9_-])sk-[A-Za-z0-9_-]{20,}'          # generic API secret keys (not "task-...")
  'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'   # JWT
  '(postgres|mysql|mongodb(\+srv)?|redis)://[^:/ ]+:[^@ ]+@'         # creds in URLs
)
# keyword assignments are matched case-insensitively; token shapes above are case-sensitive
kw='(api[_-]?key|secret|passw(or)?d|token)[A-Za-z0-9_]*["'"'"']?[[:space:]]*[:=][[:space:]]*["'"'"'][^"'"'"'[:space:]]{8,}["'"'"']'
regex=$(IFS='|'; echo "${patterns[*]}")
match() { grep -Eq -e "$regex" <<<"$1" || grep -Eiq -e "$kw" <<<"$1"; }
skip='(\.example|\.sample|\.lock|lock\.json|\.min\.js|\.svg)$'

hits=0
report() { printf '%s\n' "$1"; hits=$((hits + 1)); }

if [[ $mode == staged ]]; then
  git rev-parse --git-dir >/dev/null 2>&1 || { echo "not a git repo; use --path" >&2; exit 2; }
  file=""
  while IFS= read -r line; do
    if [[ $line == "+++ b/"* ]]; then file=${line#+++ b/}; file=${file%$'\t'}; continue; fi
    [[ $line == +* && $line != "+++"* ]] || continue
    [[ $file =~ $skip ]] && continue
    if match "${line:1}"; then report "$file: ${line:1:160}"; fi
  done < <(git diff --cached -U0 --no-color)
else
  if git -C "$dir" rev-parse --git-dir >/dev/null 2>&1; then
    list=$(git -C "$dir" ls-files -z --cached --others --exclude-standard | tr '\0' '\n' | sort -u | sed "s|^|$dir/|")
  else
    list=$(find "$dir" -type f -not -path '*/.git/*' -not -path '*/node_modules/*')
  fi
  tmp="$(mktemp)"; trap 'rm -f "$tmp"' EXIT
  while IFS= read -r f; do
    [[ -z $f || $f =~ $skip || ! -f $f ]] && continue
    { grep -IEn -e "$regex" -- "$f"; grep -IEin -e "$kw" -- "$f"; } 2>/dev/null | sort -t: -k1,1n -u | cut -c1-200 | sed "s|^|$f:|" | while IFS= read -r l; do echo "$l"; done
  done <<<"$list" > "$tmp" || true
  while IFS= read -r l; do report "$l"; done < "$tmp"
fi

if (( hits > 0 )); then
  echo "possible secrets: $hits (rotate anything real that already left this machine)" >&2
  exit 1
fi
echo "secret scan: clean"
