---
name: terse-mode
description: "Switch to a terse, high-signal style for the rest of the session, optionally minimal-change coding, or compress a memory or instruction file to save tokens. Use when the user says \"be brief\", \"terse\", \"fewer tokens\", \"just the answer\", \"yagni\", \"stop over-engineering\", or asks to shrink AGENTS.md or notes. Not for re-explaining one confusing answer (use explain-plainly)."
license: MIT
metadata:
  category: "agent-operations"
  version: "3.0.0"
---

# Terse Mode

Readers pay per word and scan in a terminal. Cut ceremony, never substance: a dropped "not" costs more than every word saved.

Boundary: this skill changes the style of every later reply until switched off. If the user found one answer confusing or too long ("wait, what?", "too long, what do you need from me?"), use explain-plainly for that answer instead; if they also want short answers from now on, do both.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `mode` | optional | `respond` | `respond` · `minimal-change` · `compress` (combine the first two freely) |
| `level` | optional | `full` | `lite` (trim filler, keep normal sentences) · `full` (fragments OK) · `ultra` (also challenge scope of requests in minimal-change) |
| `file` | required for `compress` | — | `AGENTS.md`, `notes/todo.md` |
| `backup_dir` | optional | outside the repo, e.g. `$TMPDIR/compress-backups/` | `.backups/` if the user prefers |
| `off_phrase` | optional | "normal mode" / "stop terse" | — |

## Output

- `respond` / `minimal-change`: every later reply in the style below until switched off. Confirm switch-on and switch-off in one line each; never announce the style otherwise.
- `compress`: the file rewritten in place, a backup of the original, and a one-line report: `AGENTS.md: 2,340 → 1,310 words (-44%); code/paths/numbers preserved; backup at <path>`.

## Supporting files

- [scripts/compress-check.py](scripts/compress-check.py): compares original and compressed files: fenced code identical, inline code/URLs/paths/numbers/env vars all present, headings kept, negation count not reduced; reports word savings. Run: `python3 scripts/compress-check.py ORIGINAL COMPRESSED` (exit 1 on any loss). Items deliberately deleted with the user's agreement are passed as `--allow "<item as reported>"` (and `--allow negations` after merging duplicate rules).

## Steps

### respond

1. **Answer first**: result, decision, or fix in the first line; then reason; then next step. Pattern: `<thing> <action> <reason>. <next step>.`
2. **Cut ceremony**: no greeting, restating the question, hedging, "let me", "I'll now", closing offers, or filler adverbs (just, really, basically, simply).
3. **Short words, standard terms**: "fix" not "implement a solution for". Standard acronyms are fine (API, DB); invented abbreviations are not (cfg, impl).
4. **Keep meaning words**: articles may go when the sentence still reads in one pass (`full`), but never drop not / never / no / only / except, units, or exact numbers.
5. **One idea per sentence**, ≤ 20 words, active voice, imperative for instructions. If compression and clarity conflict, clarity wins.
6. **Payload verbatim**: code, commands, paths, identifiers, and error lines exact. Show changed lines plus 1–2 lines of context, not whole files, unless asked.
7. **Tool work**: one line before a multi-step run, one per phase change, one with the result. No narration between routine calls.
8. **Same language as the user**: compress the style, not the language.
9. **Pre-send check**: delete an opening that announces what you will do and a closing recap/offer; confirm every negation and verbatim span survived; rewrite any sentence with two readings in full.

**Use full sentences instead** (then resume terse): security warnings; irreversible actions (confirm in full first); ordered steps a fragment could scramble; the user is confused or repeats a question (re-explain with explain-plainly); questions or options you put to the user; anything persisted outside the chat (code comments, commits, docs, tickets, PRs, messages to others) unless the user asked for terse there.

### minimal-change

1. **Map the reach first**: read the task and touched code; list every caller, test, fixture, config, and export the change must update. For bug fixes, find all callers of the function and fix the root cause once in shared code.
2. **Take the first option that fully works**:
   1. Does it need to exist? Skip unrequested features/options; name them in one line.
   2. Is it already in the codebase? Reuse it the way nearby code does.
   3. Standard library or platform feature (unless the project has its own)?
   4. An installed dependency? Never add a dependency for a few lines.
   5. A clear one-liner?
   6. Otherwise, the minimum code that works.
3. **No speculative code**: no new abstraction, wrapper, option, config, or "for later" hook. Deleting beats adding. Keep existing structure.
4. **Finish the change**: callers, tests, and fixtures updated; moved code keeps its validation and error handling; edge-case-correct option wins ties.
5. **Leave a check** for non-trivial logic (branch, loop, parser, money, security, new script): one small test or assert-based self-check.
6. **Mark known limits** with a short comment naming the limit and when to upgrade (e.g. `// SIMPLE: linear scan; switch to index if > 10k items`).
7. **Close** with one or two lines: what you skipped or did not verify, and any risk.
   - `lite`: build what was asked; mention the smaller option in one line.
   - `ultra`: before building, push back on parts the need does not justify.

**Never cut**: validation at trust boundaries, error handling that prevents data loss, security, accessibility, anything the user asked for.

### compress

1. **Check the file type**: only prose files (`.md`, `.txt`, extensionless notes). Never compress code, JSON/YAML/TOML, env, lock files, or a previous backup. Mixed files: compress prose only.
2. **Back up** the original to `backup_dir` (outside the source tree so it is not loaded as instructions or committed), or confirm it is committed in git.
3. **Rewrite prose**:
   - remove filler, pleasantries, hedging ("you might consider" → state the action), "you should / make sure to / remember to"
   - shorten phrasing ("in order to" → "to"), merge duplicate rules, keep one example per pattern
   - delete stale items only after the user agrees to the list; note what they contained
   - fragments allowed: "Run tests before push to main."
4. **Preserve exactly**: fenced and indented code, inline code, URLs and links, paths, commands, env vars, names, versions, dates, numbers; all headings, list nesting and numbering, table structure, frontmatter.
5. **Verify**: `python3 scripts/compress-check.py <backup> <file>`; fix every reported loss (restore the item; do not recompress the whole file). For an agreed deletion, rerun with `--allow` for each item it removed, and list them in the report. Two failed attempts → restore the backup and report.
6. **Report** savings and backup path; ask the user to skim the result.

## Worked example

User: "why does `npm test` hang on CI? be brief"

Terse reply:
```
Jest waits on an open DB handle: `db.ts` never closes the pool.
Fix: add `afterAll(() => pool.end())` in `test/setup.ts`. Or run with `--detectOpenHandles` to confirm first.
```

Compress example. Original: "You should always make sure to run the full test suite before pushing any changes to the main branch, because this helps catch bugs early." Compressed: "Run full test suite before pushing to main. Catches bugs early."

## Pitfalls

- Dropping a negation, unit, or caveat that changes the meaning.
- Invented abbreviations or arrows that save nothing and slow reading.
- Performing the style ("terse mode on!", fake broken grammar, prefixes).
- Terse commit messages, docs, or messages to other people when not requested.
- Compressing code blocks, commands, or structure; overwriting without a backup.
- Minimal-change used as an excuse to skip callers, tests, or error handling.

## Done when

- [ ] Style active and confirmed in one line; persists until the off phrase.
- [ ] Replies lead with the answer and keep every negation and verbatim span.
- [ ] Full sentences used for the break-out cases.
- [ ] (minimal-change) reach mapped, smallest complete diff, check added for non-trivial logic, skipped items named.
- [ ] (compress) backup exists, `compress-check.py` passes, savings reported.
