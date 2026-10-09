---
name: write-agent-skill
description: "Create, improve, or test an agent skill (SKILL.md folder) or an agent instruction file like AGENTS.md so it triggers reliably and changes behaviour. Use when asked to \"write a skill\", a skill never triggers or is ignored, a description is too long, instruction files need tightening, or a skill needs evals. Not for end-user docs or one-off prompts."
license: MIT
metadata:
  category: "agent-operations"
  version: "3.0.0"
---

# Write an Agent Skill

A skill is a document an agent decides to read from one line (its description) and then follows under pressure. Write the trigger for the decision, the body for the run, and test both.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `goal` | required | — | "make agents run our DB migrations safely" or "fix: the pdf-files skill never triggers" |
| `mode` | optional | inferred | `create` · `improve` · `evaluate` · `instructions` (AGENTS.md or equivalent) |
| `skill_path` | optional | `skills/<name>/` (or the pack's layout) | `skills/engineering-workflows/safe-migration/` |
| `name` | optional | kebab-case from goal | `db-migrations` |
| `source_material` | optional | none | runbooks, past transcripts, docs, a conversation that worked well |
| `test_prompts` | optional | you write 3–5 positive and 2–3 near-miss negative | realistic user requests |
| `body_limit` | optional | ~400 lines for SKILL.md | 150 for always-loaded instruction files |

## Output

- The skill folder: `SKILL.md` (frontmatter + body) and only the siblings it needs (`REFERENCE.md`, `templates/`, `scripts/`, `examples/`), each linked from SKILL.md with when to read it.
- `evals/evals.json`: task prompts with assertions, and trigger queries (should / should not load).
- A short test report: with-skill vs baseline results, failures found, and changes made.

## Supporting files

- [REFERENCE.md](REFERENCE.md): writing levers (pointers, loads, information hierarchy, completion criteria, leading words, negation, pruning), matching guidance form to failure type, bulletproofing discipline skills, skill types, and the evaluation procedure in detail. Read before drafting and when a test fails.
- [templates/skill-template.md](templates/skill-template.md): skeleton with frontmatter, Inputs, Output, Steps, Checkpoints, Worked example, Pitfalls, Done when.
- [templates/evals.json](templates/evals.json): eval file format (task evals with assertions; trigger queries).
- [scripts/validate-skill.py](scripts/validate-skill.py): checks frontmatter (name matches folder, ≤ 64 chars, kebab-case; description with "Use when" (error over 1024 chars, warning outside 200–420), including YAML `>`/`|` block descriptions), required sections, body length, linked files exist, and unlinked `.md` siblings. Run after every edit: `python3 scripts/validate-skill.py <skill-dir> [--max-lines <body_limit>]`; exit 1 on errors, warnings do not fail.

## Steps

1. **Capture intent**: what should an agent do differently with this skill? In which situations should it load? What does a good result look like? Gather `source_material`; if a conversation already solved the task well, extract the steps, corrections, and formats from it.
2. **Run a baseline** (create/improve): give 2–3 realistic prompts to a fresh agent without the skill (or with the old version). Record what goes wrong: skipped steps, wrong output shape, missing elements, rationalisations. This tells you what the skill must fix, and which form of guidance works (REFERENCE.md "match the form to the failure").
3. **Write the description** (third person, one YAML double-quoted string, escape inner quotes as `\"`):
   - **Length: 200–380 chars, hard max 420.** The spec allows 1024, but agents list every installed skill's description inside a small shared budget (Claude Code: about 1% of the context window, roughly 8k chars on a 200k model). When the total overflows, descriptions are shortened or dropped silently, and the trigger words go with them. A 60-skill pack at 640 chars each already overflows.
   - **Shape:** "<The job, in one plain clause>. Use when <3–6 concrete triggers, including literal user phrases or file types>. Not for <nearest neighbour> (use <skill>)."
   - **Front-load:** the key use case and the strongest trigger words go in the first ~100 chars, because truncation cuts from the end.
   - No workflow summary (agents may follow it instead of reading the body) and no "Covers …" lists; put scope in a one-line note under the title.
   Done when the validator shows no description warning and every should-trigger query in step 7 contains a word or phrase from the description or an obvious synonym.
4. **Draft the body** from [templates/skill-template.md](templates/skill-template.md):
   - Inputs table (parameter, required, default, example) and Output (what exists when done)
   - numbered steps, each ending on a checkable completion criterion; if → then branches for real decisions
   - concrete commands, templates, and one worked example with real values
   - pitfalls drawn from the baseline failures
   - a Done-when checklist
   Explain *why* for non-obvious rules instead of shouting. Cut anything the model already does by default.
5. **Disclose, do not sprawl**: long reference, catalogues, and variants go to sibling files linked with "read when …". Fragile exact operations become scripts (tested, with `--help`). Keep SKILL.md under `body_limit`.
6. **Validate**: `python3 scripts/validate-skill.py <skill-dir> --max-lines <body_limit>` (for an instruction file, which has no frontmatter, just check its length against `body_limit` and its links by hand); fix every error, and every warning unless you can say why it does not apply.
7. **Evaluate** (REFERENCE.md has the full procedure):
   - task evals: run each prompt with the skill and with the baseline in fresh contexts, ideally in parallel; grade against assertions; compare pass rates, time, and tokens
   - trigger evals: 8–10 should-trigger (varied phrasings, indirect mentions) and 8–10 near-miss should-not-trigger queries; check the description routes them correctly
8. **Iterate**: for each failure, find the cause (trigger wording, missing step, vague criterion, wrong guidance form, prohibition that backfired) and change the skill, not the test. Re-run until results are stable. Keep the evals next to the skill.
9. **Instruction files** (`mode=instructions`): keep them short and high-signal: build/test/lint commands, conventions that differ from defaults, gotchas, where things live, and one-line pointers to deeper docs ("Before changing the schema, read docs/db.md"). Replace stale rules instead of appending; do not restate what `package.json`, config, or `--help` already say.

## Checkpoints

- After step 2: agree on the failures the skill must fix.
- After step 3: show the description and the trigger queries before writing a long body.
- Before calling it done: eval results shown to the user.

## Worked example

Goal: "agents keep writing migrations that lock big tables". Baseline: 3 prompts; agent adds a NOT NULL column with a default in one step twice out of three, never batches backfills.

Description:
```yaml
name: db-migrations
description: Plan and write database schema and data migrations that stay online (no long locks, reversible, batched backfills). Use when adding, renaming, or dropping columns, tables, or indexes, changing constraints, backfilling data, or reviewing a migration file. Not for query performance tuning or ORM model design.
```
Body essentials: Inputs (`table_rows`, `engine`, `deploy_model`); steps: check table size → choose expand/contract path → write migration with lock timeout → batched backfill script → verification query; Done-when includes "no statement takes an ACCESS EXCLUSIVE lock on a table > 1M rows".

Evals: 4 task prompts with assertions like `"uses CREATE INDEX CONCURRENTLY"`, `"backfill runs in batches ≤ 10k rows"`; 18 trigger queries including near-misses ("why is this query slow?" → should not trigger). With skill: 4/4 tasks pass, 17/18 triggers correct (fixed the miss by adding "index" to the description).

## Pitfalls

- Vague descriptions ("helps with databases"), descriptions that summarise the procedure, or long descriptions (over ~420 chars) that get truncated in the skill listing and lose their triggers.
- Bodies that restate general knowledge or the environment (scripts, config) instead of what changes behaviour.
- Steps ending in "understand X" (no checkable completion).
- Steering by long "never" lists for shaping problems; describe what the output *is* instead.
- Nuance clauses ("unless it matters") that reopen negotiation.
- Everything in one file, or so much disclosed that the needed step is hidden.
- Untested skills that read well but do not change behaviour.

## Done when

- [ ] `validate-skill.py` passes (name = folder, description 200–420 chars with triggers and a not-for cue, required sections, links resolve, body within limit).
- [ ] Every step ends on a checkable criterion; at least one worked example with real values.
- [ ] Siblings exist only where needed and each is linked with when to read it; scripts are tested.
- [ ] Task evals show improvement over baseline; trigger evals route correctly, including near-misses.
- [ ] Evals are saved beside the skill.
