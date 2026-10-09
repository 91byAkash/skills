# Changelog

All notable changes to this pack are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the pack uses [semantic versioning](https://semver.org/).

## [3.0.0] - 2026-10-09

A review of every skill: real bugs fixed, outdated facts corrected, descriptions rewritten so agents can actually see them, and clearer, collision-free names. **Breaking:** 22 skills and 4 categories are renamed, so reinstall (old installed folders are not removed automatically).

### Changed
- **Descriptions cut from ~40,500 to ~23,600 characters in total** (from an average of 640 to 370 per skill; all now between 320 and 420). Claude Code lists skills within about 1% of the context window and silently shortens or drops descriptions that overflow. Each description now leads with the job, then `Use when` with literal trigger phrases, then `Not for` with the nearest neighbour skill. The old "Covers ..." lists moved into a `Scope:` line in each body.
- **Renamed skills** (clearer intent, and no clashes with other popular packs that also ship `pdf`, `docx`, `xlsx`, `pptx`, `tdd`, `code-review`, `handoff`, `doc-coauthoring` or `internal-comms`):

| 2.x name | 3.0 name |
|---|---|
| `grill-the-plan` | `stress-test-plan` |
| `brainstorm-ideas` | `idea-to-design` |
| `map-a-large-effort` | `multi-session-roadmap` |
| `code-review` | `review-diff` |
| `retro` | `session-retro` |
| `compatible-migration` | `safe-migration` |
| `tdd` | `test-driven-development` |
| `deep-modules` | `module-interface-design` |
| `seo-audit` | `seo-optimization` |
| `handoff` | `session-handoff` |
| `teach` | `teach-topic` |
| `plain-restate` | `explain-plainly` |
| `questionnaire` | `stakeholder-questionnaire` |
| `writing-process` | `long-form-writing` |
| `doc-coauthoring` | `cowrite-document` |
| `internal-comms` | `internal-communications` |
| `architecture-diagrams` | `system-diagrams` |
| `pdf` | `pdf-files` |
| `docx` | `word-documents` |
| `xlsx` | `excel-spreadsheets` |
| `pptx` | `powerpoint-decks` |
| `parallel-subagents` | `delegate-to-subagents` |

- **Renamed categories and category plugins:**

| 2.x | 3.0 |
|---|---|
| `shaping` (`akash-skills-shaping`) | `plan-and-decide` (`akash-skills-plan-and-decide`) |
| `main-flow` (`akash-skills-main-flow`) | `build-and-ship` (`akash-skills-build-and-ship`) |
| `engineering-upkeep` (`akash-skills-engineering-upkeep`) | `engineering-workflows` (`akash-skills-engineering-workflows`) |
| `reference` (`akash-skills-reference`) | `engineering-practices` (`akash-skills-engineering-practices`) |

- `launch-plan` is split in two. `launch-plan` now covers a single launch (readiness, timeline, launch day, directories, site QA, follow-up). The new **`marketing-plan`** covers 90-day and 12-month plans, market sizing, idea selection, budgets and co-marketing, with its own `plan_tool.py`.
- Cross-references between skills are consistent in both directions (for example cowrite-document ↔ write-spec, terse-mode ↔ explain-plainly, safe-refactor ↔ safe-migration, session-handoff ↔ session-retro, long-form-writing ↔ marketing-copy).
- `write-agent-skill` now teaches the description budget, and `validate-skill.py` warns about descriptions under 200 or over 420 characters, or with `Use when` late in the text.

### Fixed
- **Scripts.** Each was run on fixtures and on bad input. Highlights:
  - `implement-plan/ledger.sh` never found `### 3. Name` task headings, crashed when run from a subdirectory, and used GNU-only `realpath -m`.
  - `improve-architecture/hotspots.sh` used GNU-only `realpath`.
  - `diagnose-bug/find-polluter.sh` mangled test commands that had quoted arguments and missed real polluters. `repro-rate.sh -n abc` reported `-nan%` and exited 0.
  - `security-hardening/secret-scan.sh` false-positived on `sk-` inside ordinary words.
  - `pdf_tool.py tables` imported pandas, which is not a dependency.
  - `html_to_pdf.sh` did not work on macOS.
  - `recalc.py`, `css-audit.py`, `funnel.py`, `email_tool.py`, the `sales-outreach` lint and the `analytics` `srm` check all exited 0 when they found problems.
  - `lint_mermaid.py` rejected valid Mermaid 11+ diagram types and state notes.
  - `render_mermaid.sh` broke on macOS bash 3.2.
  - `frontier.py` treated `1` and `001` as different tickets.
  - `fragments.py add` silently dropped positional text.
  - `reader_test.py` could print READY with failing checks.
  - `docx_to_markdown.py` produced broken bold and italic markup.
  - `--help` and missing-file handling were fixed across about 20 scripts, which now print a clean error and exit 2 instead of a traceback.
- **Facts brought up to date.**
  - MCP: spec 2026-07-28 (stateless core, `server/discover`) and TypeScript SDK v2 packages. The smoke test probes both protocol eras.
  - OWASP Top 10:2025 with CWE tagging.
  - DTCG 2025.10 token value format.
  - React 19.2 and Next.js 16 APIs.
  - Anthropic crawler tokens (ClaudeBot, Claude-SearchBot, Claude-User).
  - Google's 2025 rich-result removals.
  - PMax limits (3-15 headlines).
  - Gmail, Yahoo and Outlook bulk-sender enforcement.
  - Consent Mode v2, the GA4 Measurement Protocol status, and Meta CAPI dedup.
  - LibreOffice support for XLOOKUP, FILTER and similar functions.
  - Cancellation-law status after the FTC rule was vacated.
- **Workflow bugs.**
  - `verify-before-done`'s red-green check did nothing once the fix was committed.
  - `finish-branch` ran `git pull` on bases with no upstream, and committed a `.gitignore` change without asking.
  - `plan-tasks`, `implement-plan` and `review-diff` referred to plan sections that the template does not have.
  - `critic-review-loop` said "three rounds" where the script uses two.
  - The `retention-and-referrals` worked example was missing an argument.
- Regional notes where they matter: GDPR, India's DPDP Act 2023, RBI e-mandate rules for recurring payments, EAA, ADA and RPwD for accessibility.

### Added
- `check-pack.sh`:
  - warns on descriptions over 420 characters and on a whole-pack total over 26,000;
  - fails when a `(use X)` or `Related skills:` reference names a skill that does not exist, which catches stale names after a rename.
- README section on keeping the skill listing small (category plugins, `/doctor`, `skillListingBudgetFraction`, `skillOverrides`).

## [2.0.0] - 2026-10-08

A full rework of all 63 skills. Version 1 had been trimmed so far that many skills lost the parameters, defaults, rules, and templates needed to use them.

### Added
- A consistent structure for every skill: frontmatter, **Inputs** table (parameter, required, default, example), **Output**, numbered steps with checkable completion criteria, checkpoints, a worked example with real values, pitfalls, and a **Done when** checklist.
- Sibling files where they earn their place: `REFERENCE.md` deep dives, `templates/`, `examples/`, and tested `scripts/` (92 helpers in 44 skills, for example secret scanning, contrast checks, CSS and accessibility static audits, MCP smoke tests, commit linting, PR context, review packages, PDF/DOCX/XLSX/PPTX tooling, and a skill validator).
- `metadata.category` and `metadata.version` in every frontmatter, plus `license: MIT`.
- `scripts/check-pack.sh`: validates frontmatter against the Agent Skills spec (name rules, uniqueness, description length, string metadata), required sections, links (including links that would break once a skill is installed on its own), script syntax, and file hygiene. A CI workflow runs it on every push and pull request.
- `README.md`, `INDEX.md`, `CONTRIBUTING.md`, `requirements.txt`, and this changelog.
- Plugin packaging: `plugin.json` and `marketplace.json` let the repository install as a plugin and serve as its own plugin marketplace (`akash-skills`). `akash-agent-skills` installs all 63 skills; nine category plugins (`akash-skills-<category>`) install a subset. The manifests list the category folders, so the `skills/<category>/<skill>/` layout and `npx skills add` are unchanged. `check-pack.sh` validates both files and that every skills path and plugin source exists.

### Changed
- Restored working detail in every skill (inputs, defaults, rules, commands, templates, examples), written fresh in plain language.
- Layout is now `skills/<category>/<skill>/SKILL.md`, which the `skills` CLI discovers directly.
- Descriptions are quoted YAML strings that state what the skill is for, when to use it, and what it is not for.

### Fixed
- `check-pack.sh` without PyYAML no longer flags quoted descriptions or nested `metadata` as errors.
- Review pass across all nine categories: wording, cross-references between skills, script bugs found by running each script on real input, and frontmatter that some YAML parsers rejected.

### Removed
- The separate JSON manifest file; `INDEX.md` and each skill's frontmatter metadata replace it.
- Fluff, duplicated general knowledge, and project-specific references.
