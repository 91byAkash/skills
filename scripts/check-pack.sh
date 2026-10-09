#!/usr/bin/env bash
# check-pack.sh - lint this skills pack before publishing.
#
# Usage:  scripts/check-pack.sh [--denylist FILE] [--expect N] [REPO_ROOT]
#   REPO_ROOT   defaults to the parent of this script's directory.
#   --denylist  optional file of forbidden terms (one per line, '#' comments,
#               matched case-insensitively as whole words). Also read from the
#               PACK_DENYLIST env var. The file must live OUTSIDE the repo.
#   --expect N  fail unless exactly N skills are found.
#
# Checks:
#   1. every skills/**/SKILL.md has valid YAML frontmatter (spec rules: name is
#      lowercase-hyphenated, <= 64 chars, equals the folder name and is unique;
#      description is 1-1024 chars; metadata values are strings), says
#      "Use when", and has "## Inputs", "## Output" and "## Done when" sections.
#      Warns when a description exceeds 420 chars or all descriptions exceed 26k
#      chars (agents cut long skill listings), and fails when a "(use X)" or
#      "Related skills:" reference names a skill that does not exist.
#   2. every relative Markdown link resolves, and no link inside a skill points
#      outside that skill's folder (skills are installed one by one).
#   3. no code-hosting URLs and no denylist hits (if a denylist is given).
#   4. every script passes a syntax check (bash -n / py_compile / node --check),
#      including inline <script> blocks in HTML templates.
#   5. hygiene: no __pycache__/*.pyc/.DS_Store, no file over 100 KB.
#   6. plugin packaging (if the plugin manifest folder exists): plugin.json and
#      marketplace.json are valid JSON with the required fields, every skills
#      path and plugin source starts with ./, stays inside the repo and exists,
#      every SKILL.md is reachable from plugin.json, and every category plugin
#      finds at least one skill. When the agent CLI is on PATH, also runs its
#      `plugin validate --strict` on the marketplace and the plugin manifest.
# Requires: bash, python3 (PyYAML recommended for strict YAML parsing), node (optional).
# Exit code 0 = all checks pass, 1 = at least one failure.

set -u
DENY="${PACK_DENYLIST:-}"
ROOT=""
EXPECT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --denylist) DENY="$2"; shift 2 ;;
    --expect) EXPECT="$2"; shift 2 ;;
    -h|--help) sed -n '2,30p' "$0"; exit 0 ;;
    *) ROOT="$1"; shift ;;
  esac
done
if [ -n "$DENY" ] && [ -f "$DENY" ]; then DENY="$(cd "$(dirname "$DENY")" && pwd)/$(basename "$DENY")"; fi
[ -z "$ROOT" ] && ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || { echo "cannot cd to $ROOT"; exit 1; }
ROOT="$(pwd)"

fail=0; warn=0
err()  { echo "FAIL: $*"; fail=$((fail+1)); }
note() { echo "WARN: $*"; warn=$((warn+1)); }
PRUNE=(-not -path './.git/*' -not -path '*/node_modules/*')

# ---- 1. SKILL.md frontmatter and sections -----------------------------------
skills=$(find ./skills -name SKILL.md "${PRUNE[@]}" 2>/dev/null | wc -l | tr -d ' ')
[ "$skills" -gt 0 ] || err "no SKILL.md files found under $ROOT/skills"
[ -n "$EXPECT" ] && [ "$skills" != "$EXPECT" ] && err "expected $EXPECT skills, found $skills"
stray=$(find . -name SKILL.md "${PRUNE[@]}" -not -path './skills/*' | head -5)
[ -n "$stray" ] && err "SKILL.md outside skills/: $stray"

out=$(python3 - <<'PY'
import os, re, sys
try:
    import yaml
except ImportError:
    yaml = None
    print("WARN: PyYAML not installed; using a basic frontmatter parser (pip install pyyaml)")
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DESC_SOFT_MAX = 420      # per-skill description target
DESC_BUDGET = 26000      # whole-pack description target (chars)
seen = {}
bodies = {}
desc_total = 0
for root, dirs, files in os.walk("skills"):
    dirs[:] = [d for d in dirs if d not in (".git", "node_modules")]
    if "SKILL.md" not in files:
        continue
    path = os.path.join(root, "SKILL.md")
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        print(f"FAIL: {path}: missing frontmatter"); continue
    raw, body = m.group(1), m.group(2)
    if yaml:
        try:
            fm = yaml.safe_load(raw)
        except yaml.YAMLError as e:
            print(f"FAIL: {path}: invalid YAML frontmatter: {str(e).splitlines()[0]}"); continue
        if not isinstance(fm, dict):
            print(f"FAIL: {path}: frontmatter is not a mapping"); continue
    else:
        fm = dict(re.findall(r"^([A-Za-z_-]+):\s*(.*)$", raw, re.M))
        for k, v in list(fm.items()):
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                fm[k] = v[1:-1]
        for line in raw.splitlines():
            if re.match(r"^(name|description):[ \t]*[^\s\"'].*:\s", line):
                print(f"FAIL: {path}: unquoted ': ' in {line.split(':')[0]} (invalid YAML)")
    folder = os.path.basename(root)
    name = str(fm.get("name", "") or "")
    desc = str(fm.get("description", "") or "")
    if not name:
        print(f"FAIL: {path}: frontmatter has no name")
    else:
        if name != folder:
            print(f"FAIL: {path}: name '{name}' != folder '{folder}'")
        if len(name) > 64 or not NAME.match(name):
            print(f"FAIL: {path}: name '{name}' must be lowercase letters/digits/single hyphens, <= 64 chars")
        if name in seen:
            print(f"FAIL: {path}: duplicate name '{name}' (also {seen[name]})")
        seen[name] = path
    if not desc.strip():
        print(f"FAIL: {path}: frontmatter has no description")
    else:
        if len(desc) > 1024:
            print(f"FAIL: {path}: description is {len(desc)} chars (max 1024)")
        elif len(desc) > DESC_SOFT_MAX:
            print(f"WARN: {path}: description is {len(desc)} chars (pack target <= {DESC_SOFT_MAX}; long descriptions get cut from the agent's skill listing)")
        desc_total += len(desc)
        bodies[path] = (desc, body)
        if "use when" not in desc.lower():
            print(f"FAIL: {path}: description lacks a 'Use when' trigger")
    md = fm.get("metadata") if yaml else None  # the basic parser cannot read nested maps
    if md is not None:
        if not isinstance(md, dict) or not all(isinstance(v, str) for v in md.values()):
            print(f"FAIL: {path}: metadata must map string keys to string values")
        else:
            parts = root.split(os.sep)
            if "category" in md and len(parts) >= 3 and md["category"] != parts[1]:
                print(f"FAIL: {path}: metadata.category '{md['category']}' != folder '{parts[1]}'")
    for h in ("## Inputs", "## Output", "## Done when"):
        if not re.search(rf"^{re.escape(h)}", body, re.M):
            print(f"FAIL: {path}: missing section '{h}'")
    n = body.count("\n")
    if n > 500:
        print(f"WARN: {path}: body is {n} lines (spec recommends < 500)")
if desc_total > DESC_BUDGET:
    print(f"WARN: all descriptions total {desc_total} chars (pack target <= {DESC_BUDGET})")
# Cross-references: every skill named in "(use X)", "use X)" or a "Related skills:" line must exist.
REF = re.compile(r"\(use `?([a-z0-9]+(?:-[a-z0-9]+)+)`?|[(,]\s*`?([a-z0-9]+(?:-[a-z0-9]+)+)`?\)")
for path, (desc, body) in bodies.items():
    cands = set()
    for txt in (desc, body):
        for m in re.finditer(r"\(use ([^)]*)\)", txt):
            cands |= set(re.findall(r"`?\b([a-z0-9]+(?:-[a-z0-9]+)+)\b`?", m.group(1)))
    for line in body.splitlines():
        if line.startswith("Related skills:"):
            cands |= {re.sub(r"\s*\(.*", "", x).strip(" `.") for x in re.split(r",|\band\b|/", re.sub(r"\([^)]*\)", "", line.split(":", 1)[1]))}
    for c in sorted(x for x in cands if x and re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)+", x)):
        if c not in seen:
            print(f"FAIL: {path}: refers to unknown skill '{c}'")
PY
)
while IFS= read -r line; do
  case "$line" in FAIL:*) err "${line#FAIL: }" ;; WARN:*) note "${line#WARN: }" ;; esac
done <<< "$out"

# ---- 2. relative links resolve and stay inside their skill -------------------
# Files under templates/ are copied into other projects, so their links point at
# the destination's layout and are not checked here.
links=0
while IFS= read -r md; do
  d="$(dirname "$md")"
  skill=""
  case "$md" in ./skills/*) skill="$(cd "$(dirname "$md")" && while [ ! -f SKILL.md ] && [ "$(pwd)" != "$ROOT" ]; do cd ..; done; pwd)";; esac
  while IFS= read -r t; do
    t="${t%%#*}"; t="${t%% *}"
    [ -z "$t" ] && continue
    case "$t" in http://*|https://*|mailto:*|/*|'<'*|'') continue ;; esac
    links=$((links+1))
    if [ ! -e "$d/$t" ]; then err "$md: broken link -> $t"; continue; fi
    if [ -n "$skill" ] && [ "$skill" != "$ROOT" ]; then
      target="$(cd "$(dirname "$d/$t")" && pwd)"
      case "$target/" in "$skill"/*) ;; *) err "$md: link leaves the skill folder -> $t" ;; esac
    fi
  done < <(awk '/^[[:space:]]*```/{f=!f; next} !f' "$md" | sed 's/`[^`]*`//g' | grep -o '](\([^)]*\))' | sed 's/^](//; s/)$//')
done < <(find . -name '*.md' "${PRUNE[@]}" -not -path '*/templates/*' | sort)

# ---- 3. denylist + code-hosting URLs -----------------------------------------
host="git""hub"   # split so this file does not match its own scan
if grep -rIniE "${host}\\.com|${host}usercontent|gitlab\\.com|bitbucket\\.org" --exclude-dir=.git --exclude-dir=node_modules . ; then
  err "code-hosting URLs found (see above)"
fi
if [ -n "$DENY" ]; then
  if [ ! -f "$DENY" ]; then
    err "denylist file not found: $DENY"
  else
    case "$DENY" in "$ROOT"/*) err "denylist lives inside the repo ($DENY); move it outside so it is never published" ;; esac
    pat="$(mktemp)"; grep -v '^[[:space:]]*#' "$DENY" | sed '/^[[:space:]]*$/d' > "$pat"
    if grep -rIniwF -f "$pat" --exclude-dir=.git --exclude-dir=node_modules . ; then
      err "denylist terms found (see above)"
    fi
    rm -f "$pat"
  fi
fi

# ---- 4. script syntax ----------------------------------------------------------
scripts=0
pyc="$(mktemp -d)"
while IFS= read -r s; do
  scripts=$((scripts+1))
  case "$s" in
    *.sh)  bash -n "$s" 2>&1 || err "$s: bash syntax error" ;;
    *.py)  PYTHONPYCACHEPREFIX="$pyc" python3 -m py_compile "$s" 2>&1 || err "$s: python syntax error" ;;
    *.js|*.mjs|*.cjs)
      if command -v node >/dev/null 2>&1; then node --check "$s" 2>&1 || err "$s: node syntax error"
      else note "node not installed; skipped $s"; fi ;;
  esac
done < <(find . -type f \( -name '*.sh' -o -name '*.py' -o -name '*.js' -o -name '*.mjs' -o -name '*.cjs' \) "${PRUNE[@]}" | sort)
if command -v node >/dev/null 2>&1; then
  while IFS= read -r h; do
    scripts=$((scripts+1))
    tmpjs="$(mktemp --suffix=.js 2>/dev/null || mktemp)"
    python3 - "$h" "$tmpjs" <<'PY'
import re, sys
src = open(sys.argv[1], encoding="utf-8").read()
blocks = re.findall(r"<script(?![^>]*\bsrc=)(?![^>]*type=[\"'](?:application/json|text/template)[\"'])[^>]*>(.*?)</script>", src, re.S | re.I)
open(sys.argv[2], "w").write("\n;\n".join(blocks))
PY
    node --check "$tmpjs" 2>&1 || err "$h: inline script syntax error"
    rm -f "$tmpjs"
  done < <(find . -type f -name '*.html' "${PRUNE[@]}" | sort)
fi
rm -rf "$pyc"

# ---- 5. hygiene ------------------------------------------------------------------
junk=$(find . \( -name __pycache__ -o -name '*.pyc' -o -name .DS_Store \) "${PRUNE[@]}" | head -5)
[ -n "$junk" ] && err "build/OS junk present: $junk"
big=$(find . -type f -size +100k "${PRUNE[@]}" | head -5)
[ -n "$big" ] && err "files over 100 KB: $big"

# ---- 6. plugin packaging ---------------------------------------------------------
# Names are split so this file does not match its own denylist scan.
PLUGDIR=".clau""de-plugin"; AGENT_CLI="clau""de"
if [ -d "$PLUGDIR" ]; then
  out=$(PLUGDIR="$PLUGDIR" python3 - <<'PY'
import json, os, re
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ROOT = os.path.realpath(".")
PD = os.environ["PLUGDIR"]
def load(path):
    if not os.path.isfile(path):
        print(f"FAIL: {path} is missing"); return None
    try:
        return json.load(open(path, encoding="utf-8"))
    except ValueError as e:
        print(f"FAIL: {path}: invalid JSON: {e}"); return None
def rel_dir(where, base, p):
    """Resolve a ./ component path against base; return the real path or None."""
    if not isinstance(p, str) or not (p in (".", "./") or p.startswith("./")):
        print(f"FAIL: {where}: path '{p}' must start with ./"); return None
    if ".." in p.split("/"):
        print(f"FAIL: {where}: path '{p}' contains '..'"); return None
    full = os.path.realpath(os.path.join(base, p))
    if full != ROOT and not full.startswith(ROOT + os.sep):
        print(f"FAIL: {where}: path '{p}' leaves the repository"); return None
    if not os.path.isdir(full):
        print(f"FAIL: {where}: path '{p}' does not exist"); return None
    return full
def skills_in(d):
    """Skills the plugin loader finds in one skills path: d itself or its direct children."""
    if os.path.isfile(os.path.join(d, "SKILL.md")):
        return {d}
    return {os.path.join(d, c) for c in os.listdir(d) if os.path.isfile(os.path.join(d, c, "SKILL.md"))}
def as_list(v):
    return v if isinstance(v, list) else [v]

all_skills = set()
for root, dirs, files in os.walk("skills"):
    dirs[:] = [x for x in dirs if x not in (".git", "node_modules")]
    if "SKILL.md" in files:
        all_skills.add(os.path.realpath(root))

pj = load(os.path.join(PD, "plugin.json"))
plugin_name = version = None
if isinstance(pj, dict):
    plugin_name, version = pj.get("name"), pj.get("version")
    if not isinstance(plugin_name, str) or not KEBAB.match(plugin_name):
        print(f"FAIL: plugin.json: name '{plugin_name}' must be kebab-case")
    for k in ("version", "description", "license"):
        if not isinstance(pj.get(k), str) or not pj.get(k).strip():
            print(f"FAIL: plugin.json: '{k}' must be a non-empty string")
    if not isinstance(pj.get("author"), dict) or not pj["author"].get("name"):
        print("FAIL: plugin.json: author.name is required")
    found = set()
    for p in as_list(pj.get("skills", [])):
        d = rel_dir("plugin.json skills", ".", p)
        if d:
            s = skills_in(d)
            if not s:
                print(f"FAIL: plugin.json skills: '{p}' holds no <skill>/SKILL.md folders")
            found |= s
    if os.path.isdir("skills"):
        found |= skills_in(os.path.realpath("skills"))  # default scan, always on
    for miss in sorted(all_skills - found):
        print(f"FAIL: plugin.json: {os.path.relpath(miss, ROOT)} is not reachable from any skills path")
    print(f"INFO: plugin {plugin_name}: {len(found)} skills")
elif pj is not None:
    print("FAIL: plugin.json must be a JSON object")

mj = load(os.path.join(PD, "marketplace.json"))
if isinstance(mj, dict):
    if not isinstance(mj.get("name"), str) or not KEBAB.match(mj["name"]):
        print(f"FAIL: marketplace.json: name '{mj.get('name')}' must be kebab-case")
    if not isinstance(mj.get("owner"), dict) or not mj["owner"].get("name"):
        print("FAIL: marketplace.json: owner.name is required")
    entries = mj.get("plugins")
    if not isinstance(entries, list) or not entries:
        print("FAIL: marketplace.json: plugins must be a non-empty array"); entries = []
    names = set()
    for i, e in enumerate(entries):
        where = f"marketplace.json plugins[{i}]"
        if not isinstance(e, dict):
            print(f"FAIL: {where}: must be an object"); continue
        n = e.get("name")
        if not isinstance(n, str) or not KEBAB.match(n):
            print(f"FAIL: {where}: name '{n}' must be kebab-case")
        if n in names:
            print(f"FAIL: {where}: duplicate plugin name '{n}'")
        names.add(n)
        src = e.get("source")
        if not isinstance(src, str):
            continue  # remote sources are not checked here
        base = rel_dir(f"{where} source", ".", src)
        if not base:
            continue
        has_manifest = os.path.isfile(os.path.join(base, PD, "plugin.json"))
        if has_manifest and base == ROOT and n != plugin_name:
            print(f"FAIL: {where}: entry name '{n}' must equal plugin.json name '{plugin_name}'")
        if "version" in e and version and e["version"] != version:
            print(f"FAIL: {where}: version '{e['version']}' != plugin.json version '{version}'")
        if not has_manifest:
            found = set()
            for p in as_list(e.get("skills", [])):
                d = rel_dir(f"{where} skills", base, p)
                if d:
                    found |= skills_in(d)
            if os.path.isdir(os.path.join(base, "skills")):
                found |= skills_in(os.path.join(base, "skills"))
            if not found:
                print(f"FAIL: {where}: plugin '{n}' finds no skills")
            else:
                print(f"INFO: plugin {n}: {len(found)} skills")
    if plugin_name and plugin_name not in names:
        print(f"FAIL: marketplace.json: no entry for plugin '{plugin_name}'")
elif mj is not None:
    print("FAIL: marketplace.json must be a JSON object")
PY
)
  while IFS= read -r line; do
    case "$line" in FAIL:*) err "${line#FAIL: }" ;; WARN:*) note "${line#WARN: }" ;; INFO:*) echo "${line#INFO: }" ;; esac
  done <<< "$out"
  if command -v "$AGENT_CLI" >/dev/null 2>&1; then
    for target in . "$PLUGDIR/plugin.json"; do
      "$AGENT_CLI" plugin validate --strict "$target" >/dev/null 2>&1 || err "$AGENT_CLI plugin validate --strict $target failed (run it to see why)"
    done
  fi
fi

echo "----"
echo "skills=$skills links=$links scripts=$scripts failures=$fail warnings=$warn"
[ "$fail" -eq 0 ] && echo "PASS" || echo "FAILED"
[ "$fail" -eq 0 ]
