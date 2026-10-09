# Migration plan: <change>

- Kind: schema | data | api | event | config | dependency
- Owner:
- Compat window: <until when / which condition>
- Data volume: <rows/bytes>

## Inventory
| Reader/Writer | Where (repo/service/file) | Reads or writes | Owner | Deploy cadence | Updated in stage |
|---|---|---|---|---|---|

## Stages
| # | Stage | Forward step | Rollback step | Exit proof | Status |
|---|---|---|---|---|---|
| 1 | Expand | | | | |
| 2 | Dual-write | | | | |
| 3 | Backfill | | (not needed) | parity query = 0 | |
| 4 | Verify | | | | |
| 5 | Switch reads | | flip flag | | |
| 6 | Stop old writes | | re-enable dual write + back-fill old from new | | |
| 7 | Contract (needs approval + backup) | | restore from backup | | |

## Backfill details
- Batch size / pause:
- Idempotency key / predicate:
- Progress logging:
- Abort criteria (error rate, replication lag):

## Monitoring during rollout
- Metrics/dashboards:
- Alerts:

## Open risks
- 
