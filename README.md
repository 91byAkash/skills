# Akash Jha Agent Skills

64 practical skills for coding agents, covering the whole path from a rough idea to shipped, reviewed work, plus frontend design, growth marketing, writing and office documents, and how the agent itself operates.

Each skill is a folder with a `SKILL.md` that follows the open [Agent Skills format](https://agentskills.io/specification), so it works with any agent that loads skills from a `skills` folder. Skills are written to be used, not skimmed: every one states its inputs and defaults, gives numbered steps with checkable completion criteria, includes a worked example, and ends with a **Done when** checklist. Many ship tested helper scripts and templates.

## Install

```bash
# Pick skills interactively (the CLI detects which agents you use)
npx skills add 91byAkash/agent-skills

# See every skill without installing anything
npx skills add 91byAkash/agent-skills --list

# Install everything, non-interactively
npx skills add 91byAkash/agent-skills --skill '*' -y

# Install a single skill (or several)
npx skills add 91byAkash/agent-skills --skill diagnose-bug
npx skills add 91byAkash/agent-skills --skill test-driven-development --skill review-diff

# Install globally (user-wide) instead of into the current project
npx skills add 91byAkash/agent-skills --skill '*' -g
```

Skills install by name (`diagnose-bug`, `pdf-files`, ...); the category folders are only for browsing this repository. Manual install also works: copy any `skills/<category>/<skill>/` folder into your agent's skills directory.

> **Upgrading from 2.x?** 22 skills and 4 categories were renamed in 3.0.0 (for example `tdd` is now `test-driven-development` and `pdf` is now `pdf-files`). Remove the old folders and reinstall; the full old-to-new table is in [CHANGELOG.md](CHANGELOG.md).

## Install as a plugin

This repository is also a plugin marketplace (marketplace name `akash-skills`), so an agent with a `/plugin` command can install the pack as one plugin and update it later. Run these inside a session:

```text
/plugin marketplace add 91byAkash/agent-skills
/plugin install akash-agent-skills@akash-skills
```

The plugin loads all 64 skills. The agent picks them by description as usual, and you can also run one directly as `/akash-agent-skills:<skill>`, for example `/akash-agent-skills:diagnose-bug`.

To install only part of the pack, install category plugins instead of the full one. Pick either the full plugin or category plugins, not both, or the same skills load twice.

```text
/plugin install akash-skills-growth-marketing@akash-skills
/plugin install akash-skills-writing-documents@akash-skills
```

| Plugin | Category | Skills |
|---|---|---|
| `akash-skills-plan-and-decide` | Plan and decide | 5 |
| `akash-skills-build-and-ship` | Build and ship | 7 |
| `akash-skills-engineering-workflows` | Engineering workflows | 11 |
| `akash-skills-engineering-practices` | Engineering practices | 5 |
| `akash-skills-frontend-design` | Frontend and design | 6 |
| `akash-skills-growth-marketing` | Growth and marketing | 14 |
| `akash-skills-productivity` | Productivity | 4 |
| `akash-skills-writing-documents` | Writing and documents | 8 |
| `akash-skills-agent-operations` | Agent operations | 4 |

A category plugin's skills run as `/<plugin>:<skill>`, for example `/akash-skills-growth-marketing:seo-optimization`. To pick up a new release, run `/plugin marketplace update akash-skills`, then update the plugin from the **Installed** tab of `/plugin`. The plugin manifests only point at the nine category folders, so the `skills/<category>/<skill>/` layout and `npx skills add` work the same way.

## Keep the skill listing small

Agents only see each skill's name and description until they load it, and they cap that listing. Claude Code, for example, budgets about 1% of the context window for it and shortens or drops descriptions when the budget overflows, which strips the words the agent matches on. In 3.0.0 every description was cut to about 200–420 characters with the main use case first, but the whole pack is still more than a small-context agent can list in full. So:

- Install the category plugins (or `--skill` picks) you actually use rather than everything.
- In Claude Code, run `/doctor` to see whether the listing overflows. Raise the budget with the `skillListingBudgetFraction` setting (for example `0.02`) or list rarely used skills name-only through `skillOverrides`.

## How a skill is structured

```
skills/<category>/<skill>/
  SKILL.md        frontmatter + instructions (the only required file)
  REFERENCE.md    deeper reference, loaded only when the skill says so
  templates/      files to copy and fill in (reports, plans, configs)
  scripts/        tested helpers the agent runs instead of retyping logic
  examples/       runnable or copyable examples
```

`SKILL.md` frontmatter:

```yaml
name: diagnose-bug                # equals the folder name
description: "What it does. Use when <triggers>. Not for <neighbours>."   # 200-420 chars
license: MIT
metadata:
  category: "engineering-workflows"
  version: "3.0.0"
```

Body sections, in order:

| Section | What it gives the agent |
|---|---|
| **Inputs** | a table of parameters: required or optional, default, realistic example |
| **Output** | exactly what exists when the skill is finished |
| **Supporting files** | each sibling file and when to read or run it |
| **Steps** | numbered actions, each ending on a checkable condition, with branches for real decisions |
| **Checkpoints** | where to stop for confirmation or evidence |
| **Worked example** | a short run with real values |
| **Pitfalls** | the mistakes agents actually make, and the fix |
| **Done when** | a checklist that defines completion |

Skills refer to each other by name, never by file path, so each one installs and works on its own. When a skill hands off to another (for example, `implement-plan` ends with `verify-before-done`), install both to get the full flow.

## Catalog

The full table with required inputs and supporting files for every skill is in [INDEX.md](INDEX.md).

### Plan and decide

_Explore an open question and reach a decision before anything is built._

- [`idea-to-design`](skills/plan-and-decide/idea-to-design/SKILL.md): Turn a rough idea into an approved design before any code is written.
- [`multi-session-roadmap`](skills/plan-and-decide/multi-session-roadmap/SKILL.md): Chart an effort too big for one session as a map with decision tickets.
- [`prototype-to-decide`](skills/plan-and-decide/prototype-to-decide/SKILL.md): Build throwaway code (logic or UI variants) that answers one named design question.
- [`research-primary-sources`](skills/plan-and-decide/research-primary-sources/SKILL.md): Answer a technical or factual question from primary sources, with citations.
- [`stress-test-plan`](skills/plan-and-decide/stress-test-plan/SKILL.md): Stress-test a plan or decision through rounds of questions, each with a recommended answer.

### Build and ship

_The idea-to-ship spine, in order: spec, plan, build, verify, review, integrate, reflect._

- [`finish-branch`](skills/build-and-ship/finish-branch/SKILL.md): Close out a branch safely: verify, then merge, open a PR, keep, or discard.
- [`implement-plan`](skills/build-and-ship/implement-plan/SKILL.md): Execute a plan in small, test-first increments with a progress ledger.
- [`plan-tasks`](skills/build-and-ship/plan-tasks/SKILL.md): Break a spec into small, ordered, independently verifiable tasks.
- [`review-diff`](skills/build-and-ship/review-diff/SKILL.md): Review a diff on two axes: fidelity to the spec and code quality.
- [`session-retro`](skills/build-and-ship/session-retro/SKILL.md): Run a retrospective on an agent session to remove friction for future runs.
- [`verify-before-done`](skills/build-and-ship/verify-before-done/SKILL.md): Require fresh, concrete evidence before claiming work is done.
- [`write-spec`](skills/build-and-ship/write-spec/SKILL.md): Turn an agreed design or conversation into a testable feature spec.

### Engineering workflows

_Debug, refactor, migrate, secure, test, and keep a codebase healthy._

- [`browser-testing`](skills/engineering-workflows/browser-testing/SKILL.md): Verify web changes in a real browser and write reliable end-to-end tests.
- [`build-mcp-server`](skills/engineering-workflows/build-mcp-server/SKILL.md): Design, build, test, and evaluate an MCP server for agents.
- [`codebase-orientation`](skills/engineering-workflows/codebase-orientation/SKILL.md): Explore an unfamiliar repo read-only and map it, or locate code fast.
- [`diagnose-bug`](skills/engineering-workflows/diagnose-bug/SKILL.md): Find a bug's root cause with a tight feedback loop and falsifiable hypotheses.
- [`git-guardrails`](skills/engineering-workflows/git-guardrails/SKILL.md): Add commit-time checks and a guard against destructive git commands.
- [`improve-architecture`](skills/engineering-workflows/improve-architecture/SKILL.md): Find and plan the architecture changes that would most improve a codebase.
- [`safe-migration`](skills/engineering-workflows/safe-migration/SKILL.md): Run schema, API, or dependency migrations with expand/contract and rollback.
- [`safe-refactor`](skills/engineering-workflows/safe-refactor/SKILL.md): Restructure code without changing behaviour, one tested move at a time.
- [`security-hardening`](skills/engineering-workflows/security-hardening/SKILL.md): Harden code while building it, or audit a codebase for exploitable bugs.
- [`setup-wizard`](skills/engineering-workflows/setup-wizard/SKILL.md): Generate an interactive terminal wizard for a multi-step setup.
- [`triage-issues`](skills/engineering-workflows/triage-issues/SKILL.md): Move incoming issues through clear states and write agent-ready briefs.

### Engineering practices

_Rules and vocabulary other skills cite: test-first, module design, domain language, commits, PRs._

- [`commit-messages`](skills/engineering-practices/commit-messages/SKILL.md): Split work into atomic commits with Conventional Commits messages.
- [`domain-glossary`](skills/engineering-practices/domain-glossary/SKILL.md): Build the project's domain language and record decisions as ADRs.
- [`module-interface-design`](skills/engineering-practices/module-interface-design/SKILL.md): Design deep modules with small interfaces, and enforce their boundaries.
- [`pr-description`](skills/engineering-practices/pr-description/SKILL.md): Write pull request descriptions with the why, evidence, and merge risk.
- [`test-driven-development`](skills/engineering-practices/test-driven-development/SKILL.md): Red-green test-driven development rules, seams, and mocking discipline.

### Frontend and design

_Decide, build, and polish user interfaces._

- [`accessibility-audit`](skills/frontend-design/accessibility-audit/SKILL.md): Audit a web interface against WCAG 2.2 AA and fix the failures.
- [`design-system-tokens`](skills/frontend-design/design-system-tokens/SKILL.md): Create or extract design tokens and wire them into the codebase.
- [`frontend-visual-direction`](skills/frontend-design/frontend-visual-direction/SKILL.md): Choose and build a deliberate, subject-specific visual direction.
- [`motion-design`](skills/frontend-design/motion-design/SKILL.md): Decide whether to animate, then build or review fast, accessible motion.
- [`react-patterns`](skills/frontend-design/react-patterns/SKILL.md): Write and review React and React Native code for performance and clean APIs.
- [`ui-polish-review`](skills/frontend-design/ui-polish-review/SKILL.md): Review an interface for craft and usability issues and fix them.

### Growth and marketing

_Find, convert, and keep customers._

- [`ai-search-optimization`](skills/growth-marketing/ai-search-optimization/SKILL.md): Get a brand cited and recommended in AI-generated answers.
- [`analytics-and-experiments`](skills/growth-marketing/analytics-and-experiments/SKILL.md): Set up trustworthy tracking and run sound A/B experiments.
- [`content-strategy`](skills/growth-marketing/content-strategy/SKILL.md): Plan what content to make, why, and how it gets distributed.
- [`conversion-optimization`](skills/growth-marketing/conversion-optimization/SKILL.md): Diagnose and fix conversion leaks on pages, forms, and flows.
- [`customer-research`](skills/growth-marketing/customer-research/SKILL.md): Research customers and competitors into a reusable marketing context file.
- [`email-sequences`](skills/growth-marketing/email-sequences/SKILL.md): Design and write lifecycle and marketing email programs.
- [`launch-plan`](skills/growth-marketing/launch-plan/SKILL.md): Plan and run a product or feature launch, from readiness to post-launch follow-through.
- [`marketing-copy`](skills/growth-marketing/marketing-copy/SKILL.md): Write, edit, and refresh copy for web pages and short-form surfaces.
- [`marketing-plan`](skills/growth-marketing/marketing-plan/SKILL.md): Build a 90-day or 12-month marketing plan: market sizing, channel and idea selection, co-marketing.
- [`paid-ads`](skills/growth-marketing/paid-ads/SKILL.md): Plan, run, audit, and scale paid acquisition campaigns.
- [`pricing-and-offers`](skills/growth-marketing/pricing-and-offers/SKILL.md): Design and change pricing, packaging, and offers.
- [`retention-and-referrals`](skills/growth-marketing/retention-and-referrals/SKILL.md): Reduce churn and turn customers into an acquisition channel.
- [`sales-outreach`](skills/growth-marketing/sales-outreach/SKILL.md): Run outbound prospecting and create sales enablement material.
- [`seo-optimization`](skills/growth-marketing/seo-optimization/SKILL.md): Audit and improve a site's organic search visibility in priority order.

### Productivity

_Human-facing workflows: handoffs, learning, plain explanations, asking others._

- [`explain-plainly`](skills/productivity/explain-plainly/SKILL.md): Re-explain a message that did not land in short, plain language.
- [`session-handoff`](skills/productivity/session-handoff/SKILL.md): Compress the current session into a handoff document for the next agent.
- [`stakeholder-questionnaire`](skills/productivity/stakeholder-questionnaire/SKILL.md): Turn open questions into a short questionnaire for someone else to answer.
- [`teach-topic`](skills/productivity/teach-topic/SKILL.md): Teach a topic over several sessions with lessons, practice, and records.

### Writing and documents

_Prose, documentation, diagrams, and office file formats._

- [`cowrite-document`](skills/writing-documents/cowrite-document/SKILL.md): Co-write a substantial document (spec, RFC, PRD) in three stages.
- [`excel-spreadsheets`](skills/writing-documents/excel-spreadsheets/SKILL.md): Create, read, clean, and edit spreadsheets with live formulas and audits.
- [`internal-communications`](skills/writing-documents/internal-communications/SKILL.md): Write status updates, newsletters, FAQs, and incident reports.
- [`long-form-writing`](skills/writing-documents/long-form-writing/SKILL.md): Write and edit long-form prose: gather, shape, draft, and lint.
- [`pdf-files`](skills/writing-documents/pdf-files/SKILL.md): Read, extract, create, fill, and manipulate PDF files.
- [`powerpoint-decks`](skills/writing-documents/powerpoint-decks/SKILL.md): Create, read, and edit PowerPoint decks with visual QA.
- [`system-diagrams`](skills/writing-documents/system-diagrams/SKILL.md): Create accurate, validated diagrams of systems and processes.
- [`word-documents`](skills/writing-documents/word-documents/SKILL.md): Create, read, and edit Word documents, including tracked changes and comments.

### Agent operations

_How the agent itself works: writing skills, response style, delegation, self-review._

- [`critic-review-loop`](skills/agent-operations/critic-review-loop/SKILL.md): Improve work through rounds of independent critique against a rubric.
- [`delegate-to-subagents`](skills/agent-operations/delegate-to-subagents/SKILL.md): Delegate independent work or a whole plan to sub-agents with briefs and reviews.
- [`terse-mode`](skills/agent-operations/terse-mode/SKILL.md): Switch to terse, high-signal replies, minimal-change coding, or file compression.
- [`write-agent-skill`](skills/agent-operations/write-agent-skill/SKILL.md): Create, improve, and evaluate agent skills and instruction files.

## Requirements for the scripts

Skills are plain Markdown and need nothing to install. The helper scripts are optional; an agent runs them when a step calls for it.

- **bash** and **git** for the shell helpers (most of `engineering-workflows`, `build-and-ship`, `engineering-practices`).
- **Python 3.9+**. Most Python scripts use only the standard library. The document skills need third-party packages:

  ```bash
  pip install -r requirements.txt
  ```

  | Package | Used by |
  |---|---|
  | `pypdf`, `pdfplumber`, `reportlab` | `pdf-files` |
  | `python-docx` | `word-documents` |
  | `openpyxl` | `excel-spreadsheets` |
  | `python-pptx` | `powerpoint-decks` |
  | `lxml` | `word-documents`, `powerpoint-decks` (XML-level editing and validation) |
  | `pypdfium2`, `Pillow` | page rendering and thumbnails in `pdf-files`, `word-documents`, `excel-spreadsheets`, `powerpoint-decks` |
  | `playwright` (optional) | `browser-testing` example script; then `python -m playwright install chromium` |
  | `mcp`, `httpx`, `pydantic` (optional) | only for the server you build from the `build-mcp-server` Python template |

- **Node.js 18+** (optional): the TypeScript/JavaScript templates, and syntax checks in the pack check.
- **Optional system tools**, used when present: LibreOffice (`soffice`, for converting and recalculating office files), poppler-utils (`pdftoppm`, page images), Tesseract (OCR for scanned PDFs), mermaid-cli (`mmdc`, rendering diagrams), and a git hosting CLI for PR and issue steps.

## Check the pack

```bash
pip install pyyaml               # strict frontmatter parsing
bash scripts/check-pack.sh --expect 64
```

The check validates frontmatter against the Agent Skills rules (name format and uniqueness, name equals folder, description length, string-only metadata), required sections, every relative link (including links that would break once a skill is installed on its own), script syntax for Bash, Python, JavaScript and inline HTML scripts, and repository hygiene (no caches, no files over 100 KB), and the plugin manifests (valid JSON, required fields, and every skills path and plugin source exists and stays inside the repository, so all 64 skills are reachable). Pass `--denylist FILE` to also scan for a list of terms you never want published; keep that file outside the repository. CI runs the same check on every push and pull request.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the skill template and rules. Changes are listed in [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE) © 2026 Akash Jha
