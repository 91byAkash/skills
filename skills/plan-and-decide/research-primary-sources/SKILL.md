---
name: research-primary-sources
description: "Answer a technical or factual question from primary sources (docs, specs, source code, changelogs) and write cited findings to one Markdown file. Use when asked to \"research\", \"verify how X behaves\", \"check the docs\", compare versions, or gather facts a decision needs. Not for market or opinion research (use customer-research) or a live failure (use diagnose-bug)."
license: MIT
metadata:
  category: "plan-and-decide"
  version: "3.0.0"
---

# Research from Primary Sources

Find out what is true from the party that owns the fact, and write it down so nobody has to redo the reading.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `question` | yes | – | "Does Postgres 16 logical replication support sequences?" |
| `decision_it_feeds` | optional | none | "choose replication strategy for the migration" |
| `scope` | optional | versions currently used in the repo | "Postgres 15 and 16 only" |
| `output_path` | optional | repo's existing notes folder (`docs/research/`, `notes/`), else `docs/research/YYYY-MM-DD-<slug>.md` | `docs/research/2026-10-08-pg-sequences.md` |
| `depth` | optional | `standard` (answer + evidence) | `quick` (≤15 min, 1-2 sources), `deep` (all versions, code-level confirmation) |
| `run_in_background` | optional | yes if a sub-agent is available | `no` |
| `deadline` | optional | none | "before the 3pm design review" |

## Output

One Markdown file at `output_path` using [templates/findings.md](templates/findings.md): a direct answer in the first lines, confidence level, numbered claims each with a citation (URL or `path:line`, version, date accessed), conflicts between sources, open questions, and what was not checked. A 3-line summary is posted in chat with the file path.

## Source hierarchy

| Rank | Source | Use for |
|---|---|---|
| 1 | Source code at the exact version in use, tests, schema/IDL files | what the software actually does |
| 2 | Official specification / RFC / standard | what conforming behaviour must be |
| 3 | Official docs for the matching version, API reference, man pages | intended behaviour and supported usage |
| 4 | Release notes, changelogs, migration guides, maintainers' issue comments | when behaviour changed and why |
| 5 | Original paper, dataset, or first-party announcement | research and statistical claims |
| 6 | Secondary write-ups (blogs, Q&A sites, tutorials, AI answers) | leads only; never cite as proof |

Rule: a claim is supported only when you have read rank 1-5 evidence yourself. If only rank 6 exists, label the claim "unverified".

## Steps

1. **Frame.** Rewrite the question as 1-3 checkable sub-questions. Note the version(s) in use (lock files, `--version`, Docker tags), narrowed to `scope` if given, and the decision it feeds. If the question is ambiguous, pick the interpretation that serves the decision and state it at the top.
2. **Delegate if possible.** If `run_in_background`, hand the framed question, scope, source hierarchy and output template to a sub-agent and keep working; only work that depends on the answer waits.
3. **Find the owner of each fact.** For each sub-question decide which rank-1-to-5 source owns it. Search official domains first; for libraries, open the repository at the tag matching your version, not the default branch.
4. **Read and extract.** For every claim record: the exact statement in your own words, the location (URL with anchor, or `file:line` at a commit/tag), the version it applies to, and the date accessed. Quote at most one short phrase when exact wording matters (e.g. normative MUST/SHOULD).
5. **Set the depth, then confirm behaviour when cheap.** `quick`: 1-2 rank-1-to-4 sources per sub-question, stop at ~15 minutes, executed checks only if they take under a minute. `standard`: one owning source per claim plus the executed checks below. `deep`: every version in `scope`, and each claim confirmed at code level (rank 1) or by execution. If `deadline` will arrive first, stop, write the file with what you have, and list unfinished sub-questions under *Open questions*.
   If a claim can be checked in under ~5 minutes (run a snippet, read the function, query a sandbox), do it and record the command and output. Executed evidence outranks documentation.
6. **Resolve conflicts.** If docs and code disagree, code wins for "what happens"; record both and flag the doc bug. If versions differ, give the answer per version.
7. **Assign confidence.** High: rank 1-2 evidence or executed check. Medium: rank 3-4 only. Low: indirect or partially relevant evidence. Unverified: rank 6 only.
8. **Write the file** at `output_path` (create folder if needed; follow existing naming). Answer first, evidence second, then gaps.
9. **Report** the path and the 3-line summary. If the answer changes a decision already made, say so explicitly.

## Checkpoints

- After step 1: each sub-question can be answered yes/no or with a value.
- After step 4: every claim has a location and a version; nothing cites a secondary source as proof.
- Before step 8: the first paragraph answers the question without the reader scrolling.

## Worked example

Question: "Can we rely on `fetch` keepalive requests surviving page unload in all browsers we support?"
- Sub-questions: Q1 What does the Fetch spec say about `keepalive` limits? Q2 Which of our supported browsers implement it? Q3 Is there a body size cap?
- Sources: Fetch Living Standard section on keepalive (rank 2); each browser's own compatibility notes / release notes (rank 4); a quick test page fired on `pagehide` (executed check).
- Findings file excerpt:
  ```
  Answer: Yes for our supported browsers, provided each request body stays under 64 KiB in total in-flight. Confidence: high.
  C1. The spec caps the total size of in-flight keepalive request bodies at 64 KiB (Fetch standard, "keepalive" section, accessed 2026-10-08).
  C2. Executed check: test page sent 3 beacons on pagehide in each supported browser; all arrived (command and log in appendix).
  Conflict: one tutorial claims a 32 KiB limit; no primary source supports it.
  Not checked: embedded webviews.
  ```

## Pitfalls

- Reading the docs for `latest` while the repo pins an older version.
- Citing a blog, Q&A answer, or AI summary as proof.
- Pasting long passages instead of extracting the claim.
- Burying the answer under the narrative of how you searched.
- Silently dropping a conflicting source; conflicts are findings.
- Unbounded reading: stop when each sub-question has rank 1-5 evidence or a clear "unknown", or when the `depth` budget is spent.

## Done when

- [ ] File exists at `output_path` and starts with a direct answer and confidence.
- [ ] Every claim cites a primary source with location, version and access date.
- [ ] Conflicts, gaps, and unchecked areas are listed.
- [ ] Executed checks include the exact command and observed output.
- [ ] Chat summary posted with the path and any impact on existing decisions.
