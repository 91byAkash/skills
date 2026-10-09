# Decision: Move invoicing to the new ledger

| | |
|---|---|
| Decision owner | Priya Rao |
| Deciders | Finance lead, Head of Platform |
| Decide by | 2026-10-20 |
| Status | Proposed |
| Created | 2026-10-08 |

## Recommendation

Move invoice generation to the new ledger service in Q4, behind a flag, starting with the 40 largest accounts. It removes the nightly reconciliation that failed 6 times last quarter, and it costs two engineers for six weeks. We give up the custom rounding rules that three legacy customers use; finance has agreed to honour them by credit note for 12 months.

## The decision to make

Should invoicing move to the new ledger this quarter, or stay on the legacy billing database until the ERP migration in Q2? We need an answer by 20 October because the Q4 roadmap locks then and the platform team is the only team that can do the work.

## Options

1. **Move now (recommended).** Two engineers, six weeks, flag-gated rollout by account tier.
2. **Wait for the ERP migration.** No engineering cost this quarter; reconciliation stays manual for about 7 more months.
3. **Patch reconciliation only.** One engineer, two weeks; fixes the timeout that caused 4 of the 6 failures, not the other 2.

## Comparison

| Criterion (ranked) | Move now | Wait | Patch |
|---|---|---|---|
| Removes reconciliation failures | yes | no | partly |
| Engineering cost this quarter | 12 eng-weeks | 0 | 2 eng-weeks |
| Risk to month-end close | medium during rollout | high (manual) | medium |
| Rework when ERP lands | none, ledger stays | n/a | patch is thrown away |

## Risks of the recommendation

- A rounding difference shows on migrated invoices. Mitigation: for one billing cycle, generate every invoice in both systems (a shadow run) and diff them before anything is sent. If a migrated account's invoices are wrong, turning its flag off sends the next run through legacy billing again; no data migration is needed to go back.
- The work slips past the December close. Mitigation: if shadow diffs are not clean by 1 December, we pause and stay on legacy until January.
- The Ledger & Reconciliation Services (LRS) team owns the ledger and has not yet committed review capacity. We need one LRS reviewer for about 4 hours a week during weeks 43-48; their lead is asked to confirm this by 20 October.

## What we need from you

- **Finance lead:** confirm the credit-note approach for the three customers on custom rounding.
- **Head of Platform:** approve two engineers from the payments squad for weeks 43-48.
