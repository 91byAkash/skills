---
name: idea-to-design
description: "Turn a rough idea into an approved design before any code: classify it (spike, bounded, architectural), clarify intent, compare 2-3 real approaches, get a yes. Use when the user says \"I want to build...\", \"how should we approach...\", \"can we...\", or starts a feature with an unclear approach. Not for grilling a chosen plan (use stress-test-plan)."
license: MIT
metadata:
  category: "plan-and-decide"
  version: "3.0.0"
---

# Idea to Design

Diverge, then converge, then get a yes. The output is an approved direction (and, for big work, a written spec), never code.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `idea` | yes | – | "Let users schedule posts for later" |
| `path` | optional | classified by you and announced | `spike`, `bounded`, `architectural` |
| `constraints` | optional | inferred from repo and conversation | "must ship in 2 weeks, Postgres only, no new vendors" |
| `num_approaches` | optional | 3 (2 if the space is narrow) | `2` |
| `spec_path` | optional (architectural only) | `docs/specs/YYYY-MM-DD-<topic>-design.md`, or the repo's existing convention | `design/2026-10-08-scheduling.md` |
| `visual` | optional | offered only when a question is truly visual | `yes` to render HTML mockups |

## Output

| Path | Artifact | Gate before implementation |
|---|---|---|
| Spike | 2-3 sentence probe plan, then a findings report with a recommendation; any code is labeled throwaway | User nods at the probe plan |
| Bounded | Short design in chat: approach, files touched, how it will be tested | Explicit "yes" to that design |
| Architectural | Written spec at `spec_path` (template in `templates/design-spec.md`), self-reviewed, committed | User approves the spec, then the plan made with `plan-tasks` |

## Supporting files

- [templates/design-spec.md](templates/design-spec.md): skeleton for the architectural spec. Read when writing the spec file.
- [REFERENCE.md](REFERENCE.md): red-flag table, spec reviewer checklist, approach comparison table, mockup guidance. Read when deciding a path is borderline or before the spec review.
- [scripts/mockup.sh](scripts/mockup.sh): wraps an HTML fragment in a neutral page so you can show layout options side by side. Run only after the user agrees to visuals.

## Steps

1. **Classify and announce.** Before the first question say which path and why, so the user can override:
   - `spike` if the question is feasibility ("can we...", "is it possible...", "quick and dirty is fine") and the deliverable is an answer.
   - `bounded` if the change modifies a flow that already exists in this repo (a flag, a small endpoint, a one-file fix). If there is no existing flow to read, it is not bounded.
   - `architectural` for new projects, new subsystems, or changes to interfaces other code depends on.
   - If torn between two, pick the heavier. Hidden complexity found later upgrades the path; nothing downgrades mid-task.
2. **Explore context (read-only).** Files, docs, recent commits, existing patterns that could be reused. If the request is really several independent subsystems ("chat, billing and analytics"), then stop and propose a decomposition with an order; brainstorm only the first piece.
3. **Write back your understanding.** 3-6 lines: intended outcome, who it is for, success criteria, constraints (the `constraints` input verbatim if given, plus any you inferred, marked as inferred). Separate "you said" from "I am assuming". Ask the user to correct it.
4. **Clarify.** Ask one focused question at a time, multiple-choice when possible, about purpose, constraints, and success. Stop asking when you could defend a design. Spike: skip to step 7.
   - Visual questions: if a question is about layout, looks, or spatial relationships and `visual` is not `no`, offer a mockup once in its own short message. On yes (or `visual=yes`), write one HTML fragment per option and run `scripts/mockup.sh .scratch/mockups/<topic>.html "<question>" a.html b.html` (rules in [REFERENCE.md](REFERENCE.md#visual-mockups)). If declined, stay in text for the rest of the session.
5. **Diverge (architectural; optional for bounded).** Produce `num_approaches` approaches that differ in structure, not wording. For each, fill the same rows of the comparison table in REFERENCE.md: one-line summary, how it works, main benefit, main cost/risk, rough effort (S/M/L), reversibility, what it rules out. Lead with your recommendation and say why. Strip features nobody asked for from every option (YAGNI).
6. **Present the design in sections** (architectural): architecture, components and their interfaces, data flow, error handling, testing. Scale each from a few sentences to ~250 words. After each section ask "does this look right so far?" and revise before moving on. Design units with one clear purpose each: for every unit you can say what it does, how it is used, and what it depends on.
7. **Gate.**
   - Spike: present the question and the probe in 2-3 sentences, get a nod, investigate as cheaply as correctness allows, report a recommendation.
   - Bounded: present the short design and STOP. Do not start in the same message.
   - Architectural: write the spec to `spec_path`, run the self-review (step 8), commit it, then ask the user to review the file.
8. **Spec self-review** (architectural): fix inline, no second pass needed:
   - Placeholders: any TBD, TODO, empty section, vague requirement.
   - Consistency: sections that contradict each other or the architecture.
   - Scope: still one implementation plan, or does it need splitting?
   - Ambiguity: any requirement two engineers could read differently; pick one meaning and state it.
9. **Hand off.** Architectural: once the spec is approved, the next step is `plan-tasks`, nothing else. Bounded: implement via the normal workflow (test-first where practical). Spike: the recommendation is the end; keeping the spike code is a new request that gets its own classification.

## Checkpoints

- Path announced before the first question.
- Understanding note acknowledged or corrected by the user.
- Every approach differs on at least one structural axis (data model, ownership, sync vs async, build vs buy).
- For bounded and architectural: no implementation action (scaffolding, installs, product code) before the gate is passed. Read-only exploration is always fine.

## Worked example

Idea: "Let users schedule posts for later" in an app that already has a `publishPost()` service.

- Step 1: "This touches publishing, which exists, but needs a new time-based trigger and a new post state, so I am treating it as architectural."
- Step 3 note: Outcome: authors pick a future time and the post goes live then. Assumed: minute precision is enough; timezone is the author's profile timezone.
- Step 5 approaches:

| | A. DB column + polling worker | B. Delayed job per post in the queue | C. External scheduler service |
|---|---|---|---|
| How | `publish_at` column; worker every minute publishes due posts | enqueue job with delay at schedule time; cancel on edit | cron service calls an endpoint |
| Benefit | simple, survives restarts, easy to list scheduled posts | precise, no polling | no infra to run |
| Cost | up to 60 s late; polling load | edits/cancels must track job ids; queue retention limits | vendor dependency, auth on endpoint |
| Effort | S | M | M |
| Rules out | sub-minute precision | cheap "list all scheduled" queries | running fully offline / self-hosted |

  Recommendation: A, because listing and editing scheduled posts is a core need and one-minute lateness is acceptable.
- Step 8 catches "notify followers?" left as TBD; resolved to "same as immediate publish".
- Spec committed at `docs/specs/2026-10-08-scheduled-posts-design.md`; user approves; next step `plan-tasks`.

## Pitfalls

- "Too simple to need approval": every path ends with an approval, scaled to its size.
- Calling something bounded to skip the spec; reaching for the lighter label is the sign you should take the heavier one.
- Options that differ only cosmetically, or a default lean toward the most complex one.
- A wall of questions before offering anything concrete; one question at a time.
- Writing code, scaffolding, or installing dependencies during brainstorming.
- Treating approval of the idea as approval of artifacts that do not exist yet (spec, plan).
- Proposing unrelated refactors; include only improvements the new work needs.

## Done when

- [ ] Path stated and not overridden (or updated after the user overrode it).
- [ ] Understanding note confirmed by the user.
- [ ] Spike: findings reported with a recommendation. Bounded: user said yes to the chat design. Architectural: spec written, self-reviewed, committed, and approved.
- [ ] Recommended approach and the trade-off being accepted are written down.
- [ ] The next skill or action is named.
