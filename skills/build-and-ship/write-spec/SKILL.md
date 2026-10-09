---
name: write-spec
description: "Write agreed decisions into a feature spec (problem, user stories, technical decisions, test seams, out of scope) by synthesis, not interview; save as a file or tracker issue. Use when the user says \"write this up\", \"turn this into a spec/PRD\", or \"file this as an issue\" after decisions are made. Not for open options (use idea-to-design) or task breakdown (use plan-tasks)."
license: MIT
metadata:
  category: "build-and-ship"
  version: "3.0.0"
---

# Write a Spec

Synthesize what has already been agreed into a spec an implementer can build from. Do not re-interview the user; if a decision is genuinely missing, list it under Open questions instead of inventing it.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `source` | yes | current conversation | conversation, `docs/specs/…-design.md`, issue #123, prototype verdict |
| `destination` | optional | repo's spec folder if one exists, else `docs/specs/<slug>.md` | `tracker` (publish as an issue), `docs/prd/teams.md` |
| `tracker_label` | optional (tracker) | the repo's "ready for implementation" label, if any | `ready-for-agent` |
| `glossary` | optional | the project glossary if present (`GLOSSARY.md`, see `domain-glossary`) | `docs/domain/GLOSSARY.md` |
| `adr_dir` | optional | `docs/adr/` if present | `docs/decisions/` |
| `story_depth` | optional | `exhaustive` | `core` for small features (5-10 stories) |

## Output

A Markdown spec following [templates/spec.md](templates/spec.md): What is wrong today, What we will build, Stories by actor (numbered, "As a <actor>, I want <capability>, so that <benefit>"), Technical decisions, How it will be tested (seams + prior art), Not in this release, Open questions, Notes and links. Saved to `destination` (file path or issue URL reported back).

## Supporting files

- [templates/spec.md](templates/spec.md): the spec skeleton with guidance comments. Use every time.

## Steps

1. **Gather.** If `source` is an approved design spec from `idea-to-design` that already has stories-level detail and test seams, do not write a second document: hand it straight to `plan-tasks` (or publish it as-is when `destination=tracker`). Otherwise re-read the conversation, linked design docs, prototype verdicts, and relevant issues. Read the glossary and ADRs in the touched area; use glossary terms exactly and do not contradict an ADR (if the plan does, flag it as an open question).
2. **Explore the code** enough to name the modules involved and existing patterns. Do not put file paths in the spec; they go stale.
3. **Choose test seams.** A seam is the interface at which tests observe behaviour (public API, HTTP endpoint, CLI, UI route, message handler).
   - Prefer existing seams over new ones.
   - Prefer the highest seam that can observe the behaviour; fewer seams is better, one is ideal.
   - If a new seam is needed, propose it as high as possible.
   Share the proposed seams with the user in two or three lines and adjust if they disagree. This is the only check-in.
4. **Write user stories.** Cover every actor (end user, admin, support, API client, system job) and every lifecycle moment (first use, normal use, error, empty state, permission denied, deletion, migration of existing data). For `exhaustive`, expect 15-40 stories on a medium feature. For `core`, write 5-10 stories: the happy path per actor plus the error, empty and permission-denied moments; list the skipped lifecycle moments under Notes and links.
5. **Write technical decisions** as a list: modules built or changed, interface changes, schema changes, API contracts (request/response shapes in prose or a small type), state transitions, important interactions, technical clarifications. No file paths, no code, except a short decision-rich snippet that came from a prototype (state machine, schema, type shape), labeled as such.
6. **Write how it will be tested**: what a good test looks like here (observe external behaviour, not internals), which modules are tested at which seam, prior art (similar existing tests to copy).
7. **Write "Not in this release"** explicitly, including tempting adjacent work.
8. **Self-check** against the checkpoints below; fix inline.
9. **Save or publish.** File: write to `destination`. Tracker: create one issue with the spec as body and apply `tracker_label` if the repo uses one. Report the path/URL.

## Checkpoints

- Problem and Solution are written from the user's perspective, not the code's.
- Every implementation decision traces to something agreed (conversation, doc, prototype); anything else is an open question.
- No `TBD`, no file paths, no code beyond prototype excerpts.
- Each user story is testable at one of the chosen seams.

## Worked example

Source: a conversation that settled "team accounts, team-owned notes, hybrid pricing, auto-migrate existing users".

Excerpt of the result:
```markdown
## What is wrong today
Small companies share one login today because notes belong to a single person; when someone leaves, their notes leave with them.

## Stories by actor
1. As a team owner, I want to invite a colleague by email, so that they can see our notes.
2. As an invited colleague, I want to accept with my existing account, so that I keep my personal notes.
3. As a team owner, I want notes to stay with the team when a member is removed, so that knowledge is not lost.
...
14. As an existing single user, I want my account to become a team of one automatically, so that nothing changes for me on launch day.

## Technical decisions
- Notes gain an owning team; personal notes belong to the user's personal team.
- Roles: owner, admin, member. Only owners manage billing.
- Billing: flat price under 5 seats, per seat from 5.

## How it will be tested
- Seam: the HTTP API. Tests create teams and notes through endpoints and assert visibility per role; prior art: the existing sharing API tests.

## Not in this release
- Cross-team sharing; SSO.
```

## Pitfalls

- Interviewing again instead of synthesizing; missing decisions become Open questions.
- A short story list that only covers the happy path.
- File paths and code snippets that will be stale next week.
- Many low-level seams (testing internals) instead of one high seam.
- Silently contradicting an ADR or glossary term.

## Done when

- [ ] Every template section is filled or explicitly "None".
- [ ] Stories cover all actors and error/empty/permission states.
- [ ] Test seams were shown to the user and agreed.
- [ ] Open questions listed (or "None").
- [ ] Spec saved/published; path or URL reported; next step (`plan-tasks`) named.
