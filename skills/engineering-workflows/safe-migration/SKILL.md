---
name: safe-migration
description: "Run a schema, data, API, event, config or dependency migration in reversible expand/backfill/switch/contract stages, each with rollback and proof. Use when renaming or retyping a column, splitting a table, changing an API or event shape, moving config formats, or doing a breaking dependency upgrade. Not for code-only restructuring (use safe-refactor)."
license: MIT
metadata:
  category: "engineering-workflows"
  version: "3.0.0"
---

# Safe Migration

Scope: schema, data, API, event, config and dependency changes that must stay compatible while old and new versions run side by side.


Every stage must be safe to run while old and new code coexist, and safe to undo. Destructive steps are separate and explicitly authorized.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `change` | yes | – | "rename `users.fullname` to `users.display_name`" |
| `kind` | optional | inferred | `schema`, `data`, `api`, `event`, `config`, `dependency` |
| `stage` | optional | next incomplete stage | `expand`, `backfill`, `switch-reads`, `contract` |
| `compat_window` | optional | until every reader/writer is deployed on the new version + one release | "2 weeks", "until mobile app v5 adoption > 98%" |
| `data_volume` | optional | measured (`SELECT count(*)`) | "40M rows" |
| `batch_size` | optional | 1,000-10,000 rows per batch, tuned so each batch < ~1 s | `5000` |
| `rollback_required` | optional | yes for every stage before contract | – |
| `destructive_ok` | optional | **no** (contract steps need explicit approval) | `yes` |

## Output

- A migration plan ([templates/migration-plan.md](templates/migration-plan.md)): inventory of readers/writers, stage table with forward step, rollback step, proof, and exit criteria.
- Code/migrations for the requested stage only, idempotent and observable (progress counts, error logs).
- Proof for the stage (queries, test results, dashboards) and the explicit list of what remains.

## Stage model (expand / contract)

| Stage | Forward | Rollback | Proof to exit |
|---|---|---|---|
| 0 Inventory | list every reader, writer, consumer, cache, export, report | – | inventory reviewed |
| 1 Expand | add the new column/table/field/endpoint/config key alongside the old; nullable or defaulted | drop the new, unused thing | deploy succeeds; old paths unchanged |
| 2 Dual-write | writers write old and new (or a trigger keeps them in sync) | stop writing new | new writes match old for fresh rows |
| 3 Backfill | copy existing data in idempotent batches | none needed (new is still unused) | count and checksum parity old vs new |
| 4 Verify | compare old vs new on reads (shadow reads, diff logs) | – | zero mismatches over the agreed window |
| 5 Switch reads | readers use new (behind a flag if possible) | flip the flag back | error rates and outputs unchanged |
| 6 Stop old writes | writers write only new | re-enable dual write, then back-fill old from new for rows changed since the stop | no reader touches old (logs/grep) |
| 7 Contract | drop old column/field/endpoint/key | restore from backup only | approved; compat window elapsed |

API/event variant: add the new field or version (v2) → producers send both → consumers accept both → consumers switch → producers stop sending old → remove old after the window. Never change the meaning of an existing field in place.

Dependency variant: read the changelog and migration guide → add compatibility shims or adapters → upgrade one package per change → run the full suite → remove shims after.

## Steps

1. **Inventory** readers and writers: grep the codebase for the old name/shape (including SQL strings, ORM mappings, templates, analytics queries, exports, other services, mobile clients, cron jobs, caches). Record owner and deployment cadence for each.
2. **Choose the compat window** from the slowest consumer (mobile apps and third parties are slow).
3. **Write the plan** from the template with the stage table, including rollback for every stage and the exit proof. A stage may lack a rollback only if `rollback_required` was set to `no` for it by the user; write "no rollback, accepted by <who>" in its row.
4. **Run only the requested `stage`** (default: the first row whose Status is not done). Make every step idempotent (`ADD COLUMN IF NOT EXISTS`, upserts, "where new is null" batches) so retries are safe, and make partial failure visible (log batch id, rows done, rows failed).
5. **Large tables** (measure `data_volume` first): avoid long locks: add new columns as nullable, or with a default only where the engine adds it without rewriting the table (check your engine and version); create indexes concurrently/online; backfill in `batch_size` batches with a pause between them, shrinking the batch if one takes over ~1 s; run outside peak hours, monitor replication lag.
6. **Prove the stage** with the exit proof (example parity query: `SELECT count(*) FROM users WHERE display_name IS DISTINCT FROM fullname;` must return 0).
7. **Stop.** Report what is done and what stage comes next. Never run contract implicitly; it requires `destructive_ok` and a fresh backup.

## Checkpoints

- Inventory covers non-code consumers (BI queries, exports, partner integrations).
- Each stage can be deployed independently and rolled back without data loss.
- Old and new code can run at the same time at every stage before contract.
- Parity proof is zero mismatches, not "looks right".

## Worked example

Change: rename `users.fullname` → `display_name` (40M rows, Postgres).
1. Inventory: API serializer, admin UI, nightly export job, BI dashboard query, search indexer.
2. Expand: `ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name text;` (no default, instant).
3. Dual-write: ORM writes both; DB trigger as a safety net for raw SQL writers.
4. Backfill: `UPDATE users SET display_name = fullname WHERE id BETWEEN $1 AND $2 AND display_name IS DISTINCT FROM fullname;` in 5,000-row batches with 100 ms sleeps; progress logged. (Using the parity predicate rather than `display_name IS NULL` keeps reruns idempotent and lets the remaining-rows count reach 0 even where `fullname` is NULL.)
5. Verify: parity query returns 0; shadow-read in the serializer logs mismatches for 3 days: none.
6. Switch reads behind flag `users.read_display_name`; stop writing `fullname` after BI query and export are updated.
7. Contract (after approval and backup, 2 weeks later): drop trigger, drop `fullname`.

## Pitfalls

- Renaming in place in one deploy, which breaks every running old instance.
- Forgetting non-code consumers (reports, exports, partners).
- Non-idempotent backfills that double-apply on retry.
- Long table locks from defaults, rewrites, or non-concurrent index creation.
- Removing the old path before the slowest consumer has upgraded.
- Treating contract as part of the same change as expand.

## Done when

- [ ] Inventory and plan written with rollback for every stage.
- [ ] Requested stage executed idempotently with progress visible.
- [ ] Stage exit proof shown (parity counts, flags, error rates).
- [ ] Next stage named; contract not run without explicit approval.
