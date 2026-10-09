# Ledger - plan: <plan path>
Spec: <spec path | none reachable: rulings provisional>
Branch: <branch>  Workspace: <path>

## Pre-flight scan
| Tasks | Shared file/interface | Produces → consumes | Finding | Ruling |
|---|---|---|---|---|
| 2 ↔ 4 | src/api/types.ts | Task 2 adds `Invoice.total` → Task 4 reads `Invoice.amount` | name mismatch | use `total` (spec §3) |

| Task | Self-consistent? | Note |
|---|---|---|
| 1 | yes | |

## Log
Task 1: dispatched (BASE <sha>, model <tier>)
Task 1: complete (<sha>)
Task 2: fix round 1 (spec ❌: missing rounding rule)
Task 2: complete (<sha>)
Task 2: minor (deferred): helper name `calc` is vague
Ruling: rounding to 2 dp half-up - spec §4 says "standard rounding" - cheap to change if finance disagrees
