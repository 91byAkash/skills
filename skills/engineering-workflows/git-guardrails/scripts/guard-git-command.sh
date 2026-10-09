#!/usr/bin/env bash
# guard-git-command.sh - block destructive git commands before an agent runs them.
#
# Input: the command either as arguments, or as JSON on stdin with the command in
# .tool_input.command or .command (common pre-command hook payload shapes).
# Exit codes: 0 = allowed, 2 = blocked (reason on stderr).
#
# Examples:
#   guard-git-command.sh git push origin main          -> exit 2
#   echo '{"tool_input":{"command":"git status"}}' | guard-git-command.sh   -> exit 0
#
# How it decides: the command line is split into segments on ; && || | & and
# newlines (bash -c / sh -c / eval strings are checked too). Each segment that
# runs git is normalised (global options such as -C, -c, --no-pager removed)
# and checked on its own, so "git push --dry-run && git push -f" is blocked
# and "git commit -m 'never reset --hard'" is allowed.
#
# Blocked by default: push (unless --dry-run/-n), reset --hard, clean -f
# (unless -n), branch -D / --delete --force, checkout -f, checkout or restore
# of the whole tree (. or :/), switch -f/--discard-changes, stash drop/clear,
# filter-branch, filter-repo, update-ref -d, reflog expire/delete.
# Needs python3; without it, any command mentioning git plus a risky word is
# blocked (fails closed).
#
# ---- Customize here -------------------------------------------------------
# PUSH_POLICY: block-all  = every real push is blocked (default)
#              protect    = pushes allowed except force-pushes, deletes, and
#                           pushes to PROTECTED_BRANCHES (implicit pushes from
#                           a protected current branch are blocked too)
PUSH_POLICY="${GUARD_PUSH_POLICY:-block-all}"
PROTECTED_BRANCHES="${GUARD_PROTECTED_BRANCHES:-main master}"
# EXTRA_BLOCKED: extended regexes matched against each normalised segment,
# e.g. 'git rebase( |$)' or 'git commit .*--amend'.
EXTRA_BLOCKED=()
# ---------------------------------------------------------------------------
set -uo pipefail

if [ $# -gt 0 ]; then
  cmd="$*"
else
  payload="$(cat)"
  if command -v jq >/dev/null 2>&1; then
    cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // .command // empty' 2>/dev/null)"
  else
    cmd="$(printf '%s' "$payload" | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print((d.get("tool_input") or {}).get("command") or d.get("command") or "")
except Exception: print("")' 2>/dev/null)"
  fi
  [ -n "$cmd" ] || cmd="$payload"
fi

case "$cmd" in *git*) ;; *) exit 0 ;; esac

block() { echo "BLOCKED: $1. Ask the user to run it themselves or to approve it explicitly." >&2; exit 2; }

if ! command -v python3 >/dev/null 2>&1; then
  if printf '%s' "$cmd" | grep -qE '(push|reset|clean|branch|checkout|restore|switch|stash|filter-|update-ref|reflog)'; then
    block "'$cmd' (python3 unavailable, guard failing closed)"
  fi
  exit 0
fi

current_branch="$(git branch --show-current 2>/dev/null || true)"
extra="$(printf '%s\n' "${EXTRA_BLOCKED[@]+"${EXTRA_BLOCKED[@]}"}")"
reason="$(GUARD_CMD="$cmd" PUSH_POLICY="$PUSH_POLICY" PROTECTED="$PROTECTED_BRANCHES" \
          CUR_BRANCH="$current_branch" EXTRA="$extra" python3 - <<'PY'
import os, re, shlex

cmd = os.environ["GUARD_CMD"]
policy = os.environ["PUSH_POLICY"]
protected = set(os.environ["PROTECTED"].split())
cur = os.environ["CUR_BRANCH"]
extra = [p for p in os.environ["EXTRA"].splitlines() if p.strip()]
SEPS = {";", "&&", "||", "|", "&", "|&", "(", ")", "{", "}"}
WRAPPERS = {"sudo", "env", "command", "nohup", "time", "exec", "xargs", "nice"}
GLOBAL_WITH_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}

def tokenize(s):
    lex = shlex.shlex(s.replace("\n", " ; "), posix=True, punctuation_chars=";&|(){}")
    lex.whitespace_split = True
    try:
        return list(lex)
    except ValueError:            # unbalanced quotes: fall back to a crude split
        return s.replace("\n", " ; ").split()

def segments(s, depth=0):
    seg = []
    for t in tokenize(s) + [";"]:
        if t in SEPS:
            if seg:
                yield from expand(seg, depth)
            seg = []
        else:
            seg.append(t)

def expand(seg, depth):
    i = 0
    while i < len(seg) and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", seg[i]) or seg[i] in WRAPPERS):
        i += 1
    seg = seg[i:]
    if not seg:
        return
    head = os.path.basename(seg[0])
    if head in ("bash", "sh", "zsh") and "-c" in seg and depth < 3:
        j = seg.index("-c")
        if j + 1 < len(seg):
            yield from segments(seg[j + 1], depth + 1)
        return
    if head == "eval" and depth < 3:
        yield from segments(" ".join(seg[1:]), depth + 1)
        return
    yield seg

def git_parts(seg):
    if os.path.basename(seg[0]) != "git":
        return None
    i = 1
    while i < len(seg) and seg[i].startswith("-"):
        opt = seg[i].split("=", 1)[0]
        i += 2 if (opt in GLOBAL_WITH_ARG and "=" not in seg[i]) else 1
    if i >= len(seg):
        return None
    return seg[i], seg[i + 1:]

def short_flags(args):
    out = set()
    for a in args:
        if a == "--":
            break
        if a.startswith("-") and not a.startswith("--"):
            out.update(a[1:])
    return out

def whole_tree(args):
    return any(a in (".", ":/", "*", "./") for a in args)

def check(sub, args):
    flags, longs = short_flags(args), {a.split("=")[0] for a in args if a.startswith("--")}
    if sub == "push":
        if "--dry-run" in longs or "n" in flags:
            return None
        force = "f" in flags or longs & {"--force", "--force-with-lease", "--force-if-includes", "--mirror"} or any(a.startswith("+") for a in args)
        delete = "d" in flags or "--delete" in longs or any(a.startswith(":") for a in args)
        if policy != "protect":
            return "push (PUSH_POLICY=block-all)"
        if force:
            return "force push"
        if delete:
            return "remote branch deletion"
        positional = [a for a in args if not a.startswith("-")]
        refspecs = positional[1:]
        targets = {r.split(":")[-1].replace("refs/heads/", "") for r in refspecs}
        targets = {cur if t in ("HEAD", "@") else t for t in targets}
        if not refspecs and cur in protected:
            return f"implicit push from protected branch '{cur}'"
        if targets & protected or "--all" in longs:
            return "push to a protected branch"
        return None
    if sub == "reset" and "--hard" in longs:
        return "reset --hard"
    if sub == "clean" and ("f" in flags or "--force" in longs) and not ("n" in flags or "--dry-run" in longs):
        return "clean -f"
    if sub == "branch" and ("D" in flags or (("d" in flags or "--delete" in longs) and ("f" in flags or "--force" in longs))):
        return "forced branch delete"
    if sub == "checkout" and ("f" in flags or "--force" in longs or whole_tree(args)):
        return "checkout that discards working-tree changes"
    if sub == "restore" and whole_tree(args):
        return "restore of the whole tree"
    if sub == "switch" and ("f" in flags or longs & {"--force", "--discard-changes"}):
        return "switch that discards local changes"
    if sub == "stash" and args[:1] and args[0] in ("drop", "clear"):
        return "stash " + args[0]
    if sub in ("filter-branch", "filter-repo"):
        return "history rewrite (" + sub + ")"
    if sub == "update-ref" and "d" in flags:
        return "update-ref -d"
    if sub == "reflog" and args[:1] and args[0] in ("expire", "delete"):
        return "reflog " + args[0]
    return None

for seg in segments(cmd):
    parts = git_parts(seg)
    if not parts:
        continue
    sub, args = parts
    why = check(sub, args)
    norm = " ".join(["git", sub] + args)
    if not why:
        for p in extra:
            if re.search(p, norm):
                why = f"matches custom pattern '{p}'"
                break
    if why:
        print(f"'{norm}' is a protected git operation: {why}")
        break
PY
)"
[ -n "$reason" ] && block "$reason"
exit 0
