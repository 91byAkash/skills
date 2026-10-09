---
name: improve-architecture
description: "Find where a codebase is hard to change and rank 3-6 deepening candidates in an offline HTML report, then explore the one the user picks. Use when asked for an architecture review, \"where is this codebase hurting?\", refactoring targets, or code agents struggle to navigate. Not for executing a known refactor (use safe-refactor) or reviewing a diff (use review-diff)."
license: MIT
metadata:
  category: "engineering-workflows"
  version: "3.0.0"
---

# Improve Architecture

Scope: shallow modules, leaky seams, scattered logic, weighted toward recent git hot spots.

Find where complexity leaks and propose turning shallow modules into deep ones: small interfaces hiding substantial behaviour. Use the vocabulary from `module-interface-design` (module, interface, depth, seam, adapter, leverage, locality) exactly.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `repo` | optional | current working directory | `~/code/shop` |
| `direction` | optional | inferred from git hot spots | "order intake", `src/billing/` |
| `history_window` | optional | last 300 commits or 6 months, whichever is smaller | `3 months ago` |
| `max_candidates` | optional | 5 | `3` |
| `report_path` | optional | `${TMPDIR:-/tmp}/architecture-review-<timestamp>.html` (outside the repo) | `/tmp/arch.html` |
| `glossary` / `adr_dir` | optional | `GLOSSARY.md`, `docs/adr/` if present | `docs/domain/GLOSSARY.md`, `docs/decisions/` |

## Output

1. An HTML report at `report_path` (from [templates/architecture-report.html](templates/architecture-report.html)): header with legend, one card per candidate, and a Top recommendation section. Its absolute path is given to the user and opened if possible (`xdg-open`, `open`, `start`).
2. After the user picks: decisions captured in the conversation, glossary updates, an ADR when a candidate is rejected for a lasting reason, and a hand-off (`write-spec`, `plan-tasks`, or `safe-refactor`).

Each card contains: title naming the deepening, an evidence line (churn and co-change numbers, deletion-test result), strength badge (`Strong` / `Worth exploring` / `Speculative`), dependency category (`in-process`, `local-substitutable`, `ports & adapters`, `true external/mock`), files, before/after diagram, one-sentence problem, one-sentence solution, wins (≤6 words each, phrased as locality/leverage/test gains), ADR callout if it conflicts with one.

## Supporting files

- [scripts/hotspots.sh](scripts/hotspots.sh) `[SINCE] [TOP] [MAX_COMMITS] [PATH]`: ranks still-existing files and directories by recent change frequency and lists co-changing pairs. Run at step 1.
- [templates/architecture-report.html](templates/architecture-report.html): offline report scaffold with card markup and simple box-and-arrow diagrams. Copy and fill at step 4.
- `module-interface-design` skill: vocabulary, deletion test, dependency categories. Read first if the terms are unfamiliar.

## Steps

1. **Scope before scanning (YAGNI).** From inside `repo`, run `scripts/hotspots.sh "<history_window>" 15 300 [<direction path>]` (defaults: `"6 months ago" 15 300 .`). If `direction` is a path, pass it as PATH; if it is a concept, find its folder first. Otherwise focus on the top churned areas; deepening pays off where change keeps happening. If churn is scattered, widen.
2. **Read context**: glossary (use its domain names for modules), ADRs in the area (do not re-litigate them), existing tests.
3. **Explore for friction** (a sub-agent can walk the code while you read). Note evidence, with file paths:
   - understanding one concept requires bouncing between many small modules;
   - shallow modules: interface nearly as complex as the implementation (pass-through wrappers, one-call helpers, config objects mirroring internals);
   - pure functions extracted only for tests while bugs live in how they are called (lost locality);
   - coupled modules leaking across seams (shared mutable state, reaching into internals, the same change touching 4+ files: see co-change output);
   - untested areas, or areas only testable by mocking internals.
   Apply the **deletion test** to each suspect: if deleting the module concentrates complexity in one place, it was shallow (good candidate); if complexity just moves elsewhere, it is earning its keep.
4. **Write the report** with `max_candidates` cards ranked by expected leverage. Diagrams carry the weight: before = many boxes and red leak arrows; after = one thick box with a small interface. If a diagram needs a paragraph to explain, redraw it. Do not propose concrete interfaces yet.
5. **Handle ADR conflicts**: include a candidate that contradicts an ADR only if the friction is serious; mark it "contradicts ADR-NNNN, worth reopening because ...".
6. **Ask**: "Which of these would you like to explore?" Stop until the user picks.
7. **Work the chosen candidate** with `stress-test-plan`: constraints, dependents, what moves behind the seam, the shape of the deep module, which tests survive and which get replaced by tests at the new interface. For interface options, use the design-it-twice step in `module-interface-design`.
8. **Capture as decisions land**: new concept names go into the glossary (create lazily); fuzzy terms sharpened there; if the user rejects a candidate for a reason a future reviewer would need, offer an ADR so it is not suggested again (skip "not now" reasons).
9. **Hand off** with a summary of the decided shape and the next skill.

## Checkpoints

- Every candidate cites concrete files and evidence (churn numbers, co-change, call chain), not taste.
- Every candidate passed the deletion test in the "concentrates" direction.
- Report is outside the repo and opens offline.
- No interface design before the user picks.

## Worked example

Hot spots (last 6 months): `src/orders/handler.ts` 41 commits, `validator.ts` 38, `repo.ts` 35, `pricingClient.ts` 30; these four co-change in 27 commits.

Card 1 (Strong, in-process): "Collapse the order intake pipeline into one Order Intake module"
- Problem: placing an order touches four shallow modules that each pass the same `OrderDraft` along; pricing calls leak into the repo layer.
- Solution: one module with a single place-an-order entry point hiding validation, pricing, and persistence (its signature is designed in step 7, after the pick).
- Wins: "Tests hit one interface", "Pricing stops leaking", "Delete 3 pass-through wrappers".
- Deletion test: deleting `validator.ts` concentrates rules into intake (good).

User picks card 1 → interview settles that pricing stays an adapter (two real implementations: live and quote preview, so the seam is real), glossary gains "Order Intake", hand-off to `plan-tasks`.

## Pitfalls

- Scanning the whole repo evenly instead of where change happens.
- Calling every small file shallow; small modules with simple interfaces and real behaviour are fine.
- Drifting into vague words ("service", "component", "boundary") instead of the shared vocabulary.
- Proposing an interface before the user chooses, or re-litigating settled ADRs.
- Report files written into the repo, or depending on network-only assets.

## Done when

- [ ] Report written outside the repo, path shared, ranked candidates with diagrams and evidence.
- [ ] User picked a candidate (or declined all) and the decision was explored.
- [ ] Glossary/ADR updated where warranted.
- [ ] Next step named with a short summary of the agreed shape.
