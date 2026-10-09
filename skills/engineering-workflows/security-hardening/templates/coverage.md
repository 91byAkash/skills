# Coverage: <target>

- Source ref: <git rev-parse HEAD>
- Profile / scope: <quick|standard|deep> / <paths or "whole target">
- Execution policy: local code, local fixtures, dummy data only
- Prior run: <none | findings.json ref; N carried, N revalidated, N suppressed>
- Status: complete | incomplete: <exact reason, e.g. "time budget; rows 14-22 not hunted">

## Recon inventory
- Entry points: <routes, handlers, CLI, consumers, cron, parsers, webhooks, admin tools>
- Identity model: <principals; how tenant/owner is determined>
- Data stores / outbound calls / build path: <...>
- Secret scan: `scripts/secret-scan.sh --path .` -> <clean | N hits, each explained>
- Dependency audit: `<command>` -> <summary>

## Ledger
<!-- quick: one row per surface; standard: surface x attack class; deep: subsystem x class x lifecycle -->
| # | Surface | Boundary | Attack class | Status | Result |
|---|---|---|---|---|---|
| 1 | `GET /invoices/:id` | tenant isolation | object-level authorization | hunted | F-001 confirmed |
| 2 | `POST /import-url` | outbound fetch | SSRF | hunted | no candidate (scheme + IP allowlist present) |
| 3 | admin CLI | operator only | command injection | not examined | out of scope this run |

Status values: hunted | not examined (with reason).

## Not examined
- <surface or class>: <reason>
