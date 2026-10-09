---
name: safe-refactor
description: "Restructure code without changing behaviour: pin the boundary with characterization tests, then make one green, committed move at a time. Use when asked to clean up, extract, split a large file, consolidate duplicates, move ownership, or \"make the change easy\" before a feature. Not for bug fixes (use diagnose-bug) or data, schema or API contract changes (use safe-migration)."
license: MIT
metadata:
  category: "engineering-workflows"
  version: "3.0.0"
---

# Safe Refactor

Scope: rename, extract, inline, move, split, consolidate, prepare code for a feature. If stored data, a wire format or a public contract must change, use `safe-migration` instead.

Behaviour stays identical; only structure changes. Verification brackets every structural edit: same proof before, same proof after.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `target` | yes | – | `src/billing/invoice.ts` (900 lines), "duplicate date helpers" |
| `goal_structure` | yes | – | "split into calculate / render / persist modules", "one canonical formatDate" |
| `boundary` | optional | public interface of `target` (exports, HTTP routes, CLI flags, events, DB writes) | "invoice PDF bytes and DB rows must be identical" |
| `proof_cmd` | optional | narrowest tests covering the boundary + typecheck | `npm test -- invoice && npx tsc --noEmit` |
| `commit_per_step` | optional | yes | `no` (squash at end) |
| `allowed_changes` | optional | none beyond structure | "may rename private functions" |

## Output

- A series of small commits, each a single named move (`refactor(billing): extract calculateTotals from invoice.ts`), each passing `proof_cmd`.
- Characterization tests added (if coverage was missing) and kept.
- A short summary: moves made, proof command and result before/after, anything deliberately left (with reason).

## Behaviour boundary checklist

Everything observable from outside the boundary must stay identical: return values and types, thrown errors and messages callers match on, side effects and their order (DB writes, events, logs others parse), performance class (no O(n) → O(n²)), concurrency/transaction semantics, serialization formats, public names (unless scoped), default values, and configuration keys.

## Refactoring moves

| Move | When | Safety notes |
|---|---|---|
| Rename | name hides intent | use the language server/IDE rename; grep string usages (reflection, templates, configs) |
| Extract function/module | long function, mixed responsibilities | pass data in explicitly; keep the old entry point delegating until callers move |
| Inline | wrapper adds nothing (pass-through) | check every caller first |
| Move | logic lives far from the data it uses | re-export from the old location temporarily if many callers |
| Split file | file > ~500-1000 lines with several reasons to change | split by responsibility, not by type of code |
| Consolidate duplicates | near-identical helpers | write tests for each variant first; differences are often intentional |
| Replace conditional with dispatch | same switch in several places | table or polymorphism; keep the default branch behaviour |
| Introduce parameter object | same 3+ params travel together | keep old signature as a shim until callers migrate |

## Steps

1. **Define the boundary** (checklist above) and write it down in 3-5 lines. Anything listed in `allowed_changes` may differ; everything else on the list may not. If the requested change alters any other observable behaviour, then it is not a refactor: split the behaviour change into a separate task.
2. **Establish proof before touching structure.** Run `proof_cmd` and record the result. If coverage of the boundary is thin, add characterization tests that pin current behaviour, including odd outputs (do not "fix" them now). For complex outputs, use snapshot/golden files (`expected/*.json`, PDF hash) generated from the current code. Run the golden test twice before any edit: if it differs between two runs of unchanged code (timestamps, random ids, PDF creation dates, map ordering), pin the clock and seeds or normalise those fields first, or every later comparison is noise.
3. **Check the baseline is green.** If tests already fail, then stop and report; you cannot tell your breakage from existing breakage.
4. **Plan the sequence** of moves so every intermediate state builds and passes. Move one ownership boundary at a time. For changes touching many call sites, use expand → migrate callers in batches → contract (old path deleted last).
5. **Execute one move**, then run `proof_cmd`. Green → commit with the move named (with `commit_per_step=no`, still commit each move locally and squash at the end, so a revert stays one command). Red → revert that move (`git restore --staged --worktree <files>` and delete files the move created, until `git status` is clean) and take a smaller step; do not debug a half-done refactor.
6. **Repeat** until `goal_structure` is reached. No new dependencies, config, or features unless correctness requires them; if tempted, write a note for later.
7. **Final proof**: full test suite, typecheck, lint, build; compare golden outputs; if performance-sensitive, compare a benchmark before/after.
8. **Clean up** temporary shims and re-exports only if every caller has moved (grep proves it); otherwise list them as follow-ups.

## Checkpoints

- Baseline green and recorded before the first edit.
- Every commit contains exactly one named move and passes the proof.
- No diff in golden outputs.
- Public interface diff is empty unless renames were in scope.

## Worked example

Target: `invoice.ts` (930 lines): totals, PDF rendering and persistence mixed.
- Boundary: `createInvoice(orderId)` return value, the PDF bytes, rows written to `invoices` and `invoice_lines`, and the `invoice.created` event payload.
- Proof: existing tests cover totals only, so add a characterization test that runs `createInvoice` on 3 fixture orders with a frozen clock (the PDF embeds its creation date) and compares PDF SHA-256, DB rows, and event payload to golden files; two runs on unchanged code give identical hashes.
- Moves: (1) extract `calculateTotals` → proof green → commit; (2) move PDF code to `invoicePdf.ts`, old module imports it → green → commit; (3) extract `persistInvoice` → green → commit; (4) `invoice.ts` is now a 60-line orchestrator.
- Final: suite 214/214, `tsc` clean, golden files unchanged.

## Pitfalls

- Sneaking in a bug fix or feature "while I'm here"; behaviour changes hide inside refactor diffs.
- Big-bang rewrites where nothing builds for hours.
- Consolidating "duplicates" that differ on purpose (time zones, rounding).
- Trusting tests that do not cover the boundary; add characterization tests first.
- Leaving shims forever, or removing them while callers remain.
- Reformatting whole files, which buries the real moves in noise.

## Done when

- [ ] Boundary written down and unchanged (tests, golden outputs, interface diff prove it).
- [ ] Goal structure reached through small commits, each green.
- [ ] Full suite, typecheck, lint and build pass.
- [ ] Temporary shims removed or listed as follow-ups; no new dependencies or behaviour.
