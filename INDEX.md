# Index

All 64 skills, by category. Each links to its `SKILL.md`. **Required inputs** are the parameters the skill needs from you; everything else has a default (see the skill's Inputs table). Renamed in 3.0.0? See the rename table in [CHANGELOG.md](CHANGELOG.md).

## 1. Plan and decide (`skills/plan-and-decide/`)

_Explore an open question and reach a decision before anything is built._

| Skill | Purpose | Required inputs | Supporting files |
|---|---|---|---|
| [`idea-to-design`](skills/plan-and-decide/idea-to-design/SKILL.md) | Turn a rough idea into an approved design before any code is written. | `idea` | 1 script, 1 template, 1 reference doc |
| [`multi-session-roadmap`](skills/plan-and-decide/multi-session-roadmap/SKILL.md) | Chart an effort too big for one session as a map with decision tickets. | `idea` or `map` | 1 script, 2 templates, 1 reference doc |
| [`prototype-to-decide`](skills/plan-and-decide/prototype-to-decide/SKILL.md) | Build throwaway code (logic or UI variants) that answers one named design question. | `question` | 2 templates |
| [`research-primary-sources`](skills/plan-and-decide/research-primary-sources/SKILL.md) | Answer a technical or factual question from primary sources, with citations. | `question` | 1 template |
| [`stress-test-plan`](skills/plan-and-decide/stress-test-plan/SKILL.md) | Stress-test a plan or decision through rounds of questions, each with a recommended answer. | `topic` | 1 template, 1 reference doc |

## 2. Build and ship (`skills/build-and-ship/`)

_The idea-to-ship spine, in order: spec, plan, build, verify, review, integrate, reflect._

| Skill | Purpose | Required inputs | Supporting files |
|---|---|---|---|
| [`finish-branch`](skills/build-and-ship/finish-branch/SKILL.md) | Close out a branch safely: verify, then merge, open a PR, keep, or discard. | none (all optional) | 1 script, 1 reference doc |
| [`implement-plan`](skills/build-and-ship/implement-plan/SKILL.md) | Execute a plan in small, test-first increments with a progress ledger. | `plan` | 1 script |
| [`plan-tasks`](skills/build-and-ship/plan-tasks/SKILL.md) | Break a spec into small, ordered, independently verifiable tasks. | `source` | 2 templates |
| [`review-diff`](skills/build-and-ship/review-diff/SKILL.md) | Review a diff on two axes: fidelity to the spec and code quality. | `base` | 1 template, 1 reference doc |
| [`session-retro`](skills/build-and-ship/session-retro/SKILL.md) | Run a retrospective on an agent session to remove friction for future runs. | none (all optional) | 1 template |
| [`verify-before-done`](skills/build-and-ship/verify-before-done/SKILL.md) | Require fresh, concrete evidence before claiming work is done. | `claim` | — |
| [`write-spec`](skills/build-and-ship/write-spec/SKILL.md) | Turn an agreed design or conversation into a testable feature spec. | `source` | 1 template |

## 3. Engineering workflows (`skills/engineering-workflows/`)

_Debug, refactor, migrate, secure, test, and keep a codebase healthy._

| Skill | Purpose | Required inputs | Supporting files |
|---|---|---|---|
| [`browser-testing`](skills/engineering-workflows/browser-testing/SKILL.md) | Verify web changes in a real browser and write reliable end-to-end tests. | `task` | 1 script, 1 template, 1 example, 1 reference doc |
| [`build-mcp-server`](skills/engineering-workflows/build-mcp-server/SKILL.md) | Design, build, test, and evaluate an MCP server for agents. | `service`, `workflows` | 1 script, 3 templates, 1 reference doc |
| [`codebase-orientation`](skills/engineering-workflows/codebase-orientation/SKILL.md) | Explore an unfamiliar repo read-only and map it, or locate code fast. | `question` | 1 script, 1 template |
| [`diagnose-bug`](skills/engineering-workflows/diagnose-bug/SKILL.md) | Find a bug's root cause with a tight feedback loop and falsifiable hypotheses. | `symptom` | 3 scripts, 1 reference doc |
| [`git-guardrails`](skills/engineering-workflows/git-guardrails/SKILL.md) | Add commit-time checks and a guard against destructive git commands. | none (all optional) | 2 scripts, 1 template |
| [`improve-architecture`](skills/engineering-workflows/improve-architecture/SKILL.md) | Find and plan the architecture changes that would most improve a codebase. | none (all optional) | 1 script, 1 template |
| [`safe-migration`](skills/engineering-workflows/safe-migration/SKILL.md) | Run schema, API, or dependency migrations with expand/contract and rollback. | `change` | 1 template |
| [`safe-refactor`](skills/engineering-workflows/safe-refactor/SKILL.md) | Restructure code without changing behaviour, one tested move at a time. | `target`, `goal_structure` | — |
| [`security-hardening`](skills/engineering-workflows/security-hardening/SKILL.md) | Harden code while building it, or audit a codebase for exploitable bugs. | `target` | 1 script, 3 templates, 2 reference docs |
| [`setup-wizard`](skills/engineering-workflows/setup-wizard/SKILL.md) | Generate an interactive terminal wizard for a multi-step setup. | `procedure` | 1 script |
| [`triage-issues`](skills/engineering-workflows/triage-issues/SKILL.md) | Move incoming issues through clear states and write agent-ready briefs. | `request` | 3 templates |

## 4. Engineering practices (`skills/engineering-practices/`)

_Rules and vocabulary other skills cite: test-first, module design, domain language, commits, PRs._

| Skill | Purpose | Required inputs | Supporting files |
|---|---|---|---|
| [`commit-messages`](skills/engineering-practices/commit-messages/SKILL.md) | Split work into atomic commits with Conventional Commits messages. | none (all optional) | 1 script |
| [`domain-glossary`](skills/engineering-practices/domain-glossary/SKILL.md) | Build the project's domain language and record decisions as ADRs. | `topic` | 1 script, 3 templates, 1 reference doc |
| [`module-interface-design`](skills/engineering-practices/module-interface-design/SKILL.md) | Design deep modules with small interfaces, and enforce their boundaries. | `target` | 2 templates, 1 reference doc |
| [`pr-description`](skills/engineering-practices/pr-description/SKILL.md) | Write pull request descriptions with the why, evidence, and merge risk. | none (all optional) | 1 script, 1 template, 1 reference doc |
| [`test-driven-development`](skills/engineering-practices/test-driven-development/SKILL.md) | Red-green test-driven development rules, seams, and mocking discipline. | `behavior` | 1 reference doc |

## 5. Frontend and design (`skills/frontend-design/`)

_Decide, build, and polish user interfaces._

| Skill | Purpose | Required inputs | Supporting files |
|---|---|---|---|
| [`accessibility-audit`](skills/frontend-design/accessibility-audit/SKILL.md) | Audit a web interface against WCAG 2.2 AA and fix the failures. | `target` | 1 script, 1 template, 1 reference doc |
| [`design-system-tokens`](skills/frontend-design/design-system-tokens/SKILL.md) | Create or extract design tokens and wire them into the codebase. | `mode` | 3 scripts, 2 templates, 1 reference doc |
| [`frontend-visual-direction`](skills/frontend-design/frontend-visual-direction/SKILL.md) | Choose and build a deliberate, subject-specific visual direction. | `brief` | 2 templates, 1 reference doc |
| [`motion-design`](skills/frontend-design/motion-design/SKILL.md) | Decide whether to animate, then build or review fast, accessible motion. | `target` | 1 template, 1 example, 1 reference doc |
| [`react-patterns`](skills/frontend-design/react-patterns/SKILL.md) | Write and review React and React Native code for performance and clean APIs. | `target` | 3 reference docs |
| [`ui-polish-review`](skills/frontend-design/ui-polish-review/SKILL.md) | Review an interface for craft and usability issues and fix them. | `target` | 1 script, 1 template, 1 reference doc |

## 6. Growth and marketing (`skills/growth-marketing/`)

_Find, convert, and keep customers._

| Skill | Purpose | Required inputs | Supporting files |
|---|---|---|---|
| [`ai-search-optimization`](skills/growth-marketing/ai-search-optimization/SKILL.md) | Get a brand cited and recommended in AI-generated answers. | `domain`, `category` | 1 script, 5 templates, 1 reference doc |
| [`analytics-and-experiments`](skills/growth-marketing/analytics-and-experiments/SKILL.md) | Set up trustworthy tracking and run sound A/B experiments. | `mode`, `business_model` | 1 script, 4 templates, 2 reference docs |
| [`content-strategy`](skills/growth-marketing/content-strategy/SKILL.md) | Plan what content to make, why, and how it gets distributed. | `goal`, `audience` | 1 script, 4 templates, 3 reference docs |
| [`conversion-optimization`](skills/growth-marketing/conversion-optimization/SKILL.md) | Diagnose and fix conversion leaks on pages, forms, and flows. | `surface`, `url_or_mockup`, `goal` | 1 script, 4 templates, 2 reference docs |
| [`customer-research`](skills/growth-marketing/customer-research/SKILL.md) | Research customers and competitors into a reusable marketing context file. | `goal`, `product` | 1 script, 4 templates, 1 reference doc |
| [`email-sequences`](skills/growth-marketing/email-sequences/SKILL.md) | Design and write lifecycle and marketing email programs. | `sequence_type`, `trigger`, `audience`, `goal` | 1 script, 2 templates, 1 example, 2 reference docs |
| [`launch-plan`](skills/growth-marketing/launch-plan/SKILL.md) | Plan and run a product or feature launch, from readiness to post-launch follow-through. | `scope`, `what`, `launch_date`, `audience`, `goal`, `team_and_budget` | 1 script, 4 templates, 1 example, 3 reference docs |
| [`marketing-copy`](skills/growth-marketing/marketing-copy/SKILL.md) | Write, edit, and refresh copy for web pages and short-form surfaces. | `mode`, `primary_action`, `audience` | 1 script, 2 templates, 1 example, 4 reference docs |
| [`marketing-plan`](skills/growth-marketing/marketing-plan/SKILL.md) | Build a 90-day or 12-month marketing plan: market sizing, channel and idea selection, co-marketing. | `scope`, `what`, `audience`, `goal`, `team_and_budget` | 1 script, 2 templates, 3 examples, 4 reference docs |
| [`paid-ads`](skills/growth-marketing/paid-ads/SKILL.md) | Plan, run, audit, and scale paid acquisition campaigns. | `mode`, `objective`, `economics`, `budget`, `offer_and_page`, `audience` | 1 script, 5 templates, 1 example, 4 reference docs |
| [`pricing-and-offers`](skills/growth-marketing/pricing-and-offers/SKILL.md) | Design and change pricing, packaging, and offers. | `mode`, `business_type` | 1 script, 3 templates, 2 reference docs |
| [`retention-and-referrals`](skills/growth-marketing/retention-and-referrals/SKILL.md) | Reduce churn and turn customers into an acquisition channel. | `goal`, `business_type` | 1 script, 4 templates, 4 reference docs |
| [`sales-outreach`](skills/growth-marketing/sales-outreach/SKILL.md) | Run outbound prospecting and create sales enablement material. | `mode`, `icp`, `offer`, `proof` | 1 script, 3 templates, 4 reference docs |
| [`seo-optimization`](skills/growth-marketing/seo-optimization/SKILL.md) | Audit and improve a site's organic search visibility in priority order. | `site` | 1 script, 3 templates, 4 reference docs |

## 7. Productivity (`skills/productivity/`)

_Human-facing workflows: handoffs, learning, plain explanations, asking others._

| Skill | Purpose | Required inputs | Supporting files |
|---|---|---|---|
| [`explain-plainly`](skills/productivity/explain-plainly/SKILL.md) | Re-explain a message that did not land in short, plain language. | none (all optional) | — |
| [`session-handoff`](skills/productivity/session-handoff/SKILL.md) | Compress the current session into a handoff document for the next agent. | none (all optional) | 1 script, 1 template |
| [`stakeholder-questionnaire`](skills/productivity/stakeholder-questionnaire/SKILL.md) | Turn open questions into a short questionnaire for someone else to answer. | `recipient`, `needs` | 1 template |
| [`teach-topic`](skills/productivity/teach-topic/SKILL.md) | Teach a topic over several sessions with lessons, practice, and records. | `topic` | 3 templates, 1 reference doc |

## 8. Writing and documents (`skills/writing-documents/`)

_Prose, documentation, diagrams, and office file formats._

| Skill | Purpose | Required inputs | Supporting files |
|---|---|---|---|
| [`cowrite-document`](skills/writing-documents/cowrite-document/SKILL.md) | Co-write a substantial document (spec, RFC, PRD) in three stages. | `doc_type`, `audience`, `desired_impact`, `context` | 3 scripts, 7 templates, 2 examples, 1 reference doc |
| [`excel-spreadsheets`](skills/writing-documents/excel-spreadsheets/SKILL.md) | Create, read, clean, and edit spreadsheets with live formulas and audits. | `task` | 7 scripts, 1 template, 1 example, 1 reference doc |
| [`internal-communications`](skills/writing-documents/internal-communications/SKILL.md) | Write status updates, newsletters, FAQs, and incident reports. | `type`, `team_or_scope`, `audience` | 2 scripts, 8 templates, 1 example, 1 reference doc |
| [`long-form-writing`](skills/writing-documents/long-form-writing/SKILL.md) | Write and edit long-form prose: gather, shape, draft, and lint. | `mode`, `topic` / request, `pile`, `article_path`, `reader`, `prerequisites`, `files` | 3 scripts, 5 templates, 1 example, 1 reference doc |
| [`pdf-files`](skills/writing-documents/pdf-files/SKILL.md) | Read, extract, create, fill, and manipulate PDF files. | `task` | 4 scripts, 2 templates, 1 example, 2 reference docs |
| [`powerpoint-decks`](skills/writing-documents/powerpoint-decks/SKILL.md) | Create, read, and edit PowerPoint decks with visual QA. | `task` | 11 scripts, 1 template, 1 example, 2 reference docs |
| [`system-diagrams`](skills/writing-documents/system-diagrams/SKILL.md) | Create accurate, validated diagrams of systems and processes. | `question`, `source` | 4 scripts, 10 templates, 2 examples, 1 reference doc |
| [`word-documents`](skills/writing-documents/word-documents/SKILL.md) | Create, read, and edit Word documents, including tracked changes and comments. | `task` | 11 scripts, 3 templates, 1 example, 1 reference doc |

## 9. Agent operations (`skills/agent-operations/`)

_How the agent itself works: writing skills, response style, delegation, self-review._

| Skill | Purpose | Required inputs | Supporting files |
|---|---|---|---|
| [`critic-review-loop`](skills/agent-operations/critic-review-loop/SKILL.md) | Improve work through rounds of independent critique against a rubric. | `work` | 1 script, 2 templates, 1 reference doc |
| [`delegate-to-subagents`](skills/agent-operations/delegate-to-subagents/SKILL.md) | Delegate independent work or a whole plan to sub-agents with briefs and reviews. | `work` | 2 scripts, 4 templates, 1 reference doc |
| [`terse-mode`](skills/agent-operations/terse-mode/SKILL.md) | Switch to terse, high-signal replies, minimal-change coding, or file compression. | none (all optional) | 1 script |
| [`write-agent-skill`](skills/agent-operations/write-agent-skill/SKILL.md) | Create, improve, and evaluate agent skills and instruction files. | `goal` | 1 script, 2 templates, 1 reference doc |
