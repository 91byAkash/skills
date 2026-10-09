#!/usr/bin/env bash
# Setup wizard - walks a person through manual steps and records the results.
# Library functions first; author stages at the bottom (after "STAGES").
#   stage "Name"                 new screen + progress "Stage i/N"
#   say / step / note / warn     instruction lines
#   open_url URL                 open in the default browser (Linux, macOS, WSL); WIZARD_NO_OPEN=1 only prints it
#   ask VAR "prompt" [regex]     visible input, default = existing .env value
#   ask_secret VAR "prompt" [regex]  hidden input, default = existing .env value
#   write_env KEY VALUE          idempotent upsert into $ENV_FILE
#   set_ci_secret NAME VALUE     pipe value to $CI_SECRET_CMD NAME (stdin, never argv)
#   confirm "question"           y/N gate, returns 0 on yes
#   pause ["message"]            wait for Enter
# Env: ENV_FILE (default .env), CI_SECRET_CMD (e.g. "gh secret set"; empty = skip CI; dry-run = record only).
# Smoke test without a person: printf 'answers\n...' | WIZARD_NO_OPEN=1 ENV_FILE=/tmp/t.env CI_SECRET_CMD=dry-run ./setup-x.sh
# Closed input stops the wizard (exit 1) instead of looping.
set -euo pipefail

ENV_FILE="${ENV_FILE:-.env}"
CI_SECRET_CMD="${CI_SECRET_CMD:-}"   # e.g. "gh secret set"; empty = skip CI writes
TOTAL_STAGES=0; _i=0
WROTE_ENV=(); WROTE_CI=(); SKIPPED=()

# Styling: escape codes only when stdout is a terminal, so piped logs stay plain.
_tty=0; [ -t 1 ] && _tty=1
_style() { [ "$_tty" = 1 ] && printf '\e[%sm' "$1" || true; }
B=$(_style 1); D=$(_style 2); C=$(_style 36); Y=$(_style 33); G=$(_style 32); R=$(_style 0)

_clear() { [ -t 1 ] && printf '\e[2J\e[H' || true; }
# Output lines are indented two spaces; colour codes are already baked into the argument.
_emit() { printf '  %s\n' "$1"; }
say()  { _emit "$1"; }
step() { _emit "$C->$R $1"; }
note() { _emit "$D$1$R"; }
warn() { _emit "$Y! $1$R"; }

# _readline VAR [silent]: read one line into VAR; closed input ends the wizard cleanly.
_readline() {
  local __into=$1 __line=""
  if [ "${2:-}" = silent ]; then IFS= read -r -s __line || _eof; echo; else IFS= read -r __line || _eof; fi
  printf -v "$__into" '%s' "$__line"
}
_eof() { printf '\n'; warn "input closed; stopping. Values saved so far stay in $ENV_FILE; re-run to continue."; exit 1; }

banner() {
  _clear
  printf '\n%s%s%s\n' "$B" "$1" "$R"
  printf '%s%s stages. Ctrl-C any time; re-running keeps saved values.%s\n\n' "$D" "$TOTAL_STAGES" "$R"
  pause "Press Enter to start"
}
stage() { _clear; _i=$((_i+1)); printf '\n%s%s[%s/%s] %s%s\n\n' "$B" "$C" "$_i" "$TOTAL_STAGES" "$1" "$R"; }

pause() {
  local msg=${1:-"Press Enter to continue"} ignored
  printf '  %s ' "$D$msg$R"
  _readline ignored
}
confirm() {
  local answer
  printf '  %s? %s [y/N] %s' "$Y" "$1" "$R"
  _readline answer
  case "$answer" in [Yy]*) return 0 ;; *) return 1 ;; esac
}

# Try the platform openers in turn; with WIZARD_NO_OPEN=1 just show the address.
open_url() {
  local url=$1 opener
  printf '  %sopening%s %s\n' "$G" "$R" "$url"
  [ "${WIZARD_NO_OPEN:-0}" = 1 ] && return 0
  for opener in wslview xdg-open open; do
    if command -v "$opener" >/dev/null 2>&1; then
      "$opener" "$url" >/dev/null 2>&1 && return 0
      break
    fi
  done
  warn "could not open a browser; visit the URL manually"
}

_env_get() {
  [ -f "$ENV_FILE" ] || return 1
  local line; line="$(grep -E "^$1=" "$ENV_FILE" | tail -n1)" || return 1
  line="${line#*=}"
  case "$line" in
    \"*\") line="${line:1:${#line}-2}"; line="${line//\\\"/\"}"; line="${line//\\\\/\\}" ;;   # undo write_env escaping
    \'*\') line="${line:1:${#line}-2}" ;;
  esac
  printf '%s' "$line"
}

_ask() { # _ask hidden VAR prompt regex
  local hidden="$1" var="$2" prompt="$3" re="${4:-}" cur="" val=""
  cur="$(_env_get "$var" || true)"
  while :; do
    if [ -n "$cur" ]; then
      if [ "$hidden" = 1 ]; then printf '  %s (Enter keeps saved value ****%s): ' "$prompt" "${cur: -4}"; else printf '  %s [%s]: ' "$prompt" "$cur"; fi
    else printf '  %s: ' "$prompt"; fi
    if [ "$hidden" = 1 ]; then _readline val silent; else _readline val; fi
    [ -z "$val" ] && val="$cur"
    if [ -z "$val" ]; then warn "a value is required"; continue; fi
    if [ -n "$re" ] && ! [[ "$val" =~ $re ]]; then warn "that does not look right (expected pattern $re)"; continue; fi
    break
  done
  printf -v "$var" '%s' "$val"
}
ask()        { _ask 0 "$@"; }
ask_secret() { _ask 1 "$@"; }

write_env() {
  local key="$1" val="$2" tmp
  touch "$ENV_FILE"; tmp="$(mktemp)"
  grep -vE "^$key=" "$ENV_FILE" > "$tmp" || true
  val="${val//\\/\\\\}"; val="${val//\"/\\\"}"      # escape \ and " for a double-quoted dotenv value
  printf '%s="%s"\n' "$key" "$val" >> "$tmp"
  mv "$tmp" "$ENV_FILE"; chmod 600 "$ENV_FILE" 2>/dev/null || true
  WROTE_ENV+=("$key"); note "saved $key to $ENV_FILE"
}

set_ci_secret() {
  local name="$1" val="$2"
  if [ -z "$CI_SECRET_CMD" ]; then SKIPPED+=("CI secret $name (CI_SECRET_CMD not set)"); return 0; fi
  if [ "$CI_SECRET_CMD" = dry-run ]; then WROTE_CI+=("$name (dry-run)"); note "would set CI secret $name"; return 0; fi
  local err; err="$(mktemp)"
  if printf '%s' "$val" | $CI_SECRET_CMD "$name" >/dev/null 2>"$err"; then WROTE_CI+=("$name"); note "set CI secret $name"
  else SKIPPED+=("CI secret $name (command failed: $(head -n1 "$err"))"); warn "could not set CI secret $name: $(head -n1 "$err")"; fi
  rm -f "$err"
}

summary() {
  _clear
  printf '\n%sDone.%s\n' "$B$G" "$R"
  [ ${#WROTE_ENV[@]} -gt 0 ] && printf '  wrote to %s: %s\n' "$ENV_FILE" "${WROTE_ENV[*]}"
  [ ${#WROTE_CI[@]} -gt 0 ] && printf '  CI secrets: %s\n' "${WROTE_CI[*]}"
  if [ ${#SKIPPED[@]} -gt 0 ]; then printf '  skipped:\n'; printf '   - %s\n' "${SKIPPED[@]}"; fi
  local ig=0; git check-ignore -q -- "$ENV_FILE" 2>/dev/null || ig=$?
  [ "$ig" = 1 ] && warn "$ENV_FILE is NOT git-ignored: add it to .gitignore before committing anything"
  printf '\n'
}

# =============================== STAGES ===============================
TOTAL_STAGES=2
banner "Example service setup"

stage "API key"
open_url "https://dashboard.example.com/settings/api-keys"
step "Settings -> API keys -> Create key -> name it 'local-dev' -> copy."
ask_secret EXAMPLE_API_KEY "Paste the API key" '^[A-Za-z0-9_-]{16,}$'
write_env EXAMPLE_API_KEY "$EXAMPLE_API_KEY"
set_ci_secret EXAMPLE_API_KEY "$EXAMPLE_API_KEY"

stage "Delete the old key (irreversible)"
step "Settings -> API keys -> old 'local-dev' key -> Revoke."
if confirm "Revoked the old key?"; then note "noted"; else SKIPPED+=("old key not revoked"); fi

summary
