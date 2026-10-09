# Example: RSA output for an agency expense tool

Fictional product "Ledgerline" (expense cards and receipt matching for agencies). Every claim must be true for the real product before use; 400+ agencies and "2 days" come from the context file and a case study.

Ad group structure:
- AG1 [Agency expense software]: "expense software for agencies" (phrase), [agency expense software] (exact), "expense management for agencies" (phrase) → RSA1
- AG2 [Client rebilling]: "rebill client expenses" (phrase), [client expense tracking] (exact) → RSA2 (not shown)
- AG3 [Receipt automation]: "receipt matching software" (phrase) → RSA3 (not shown)

Negative keywords:
  Campaign-level: free · template · jobs · salary · course · personal · reimbursement form · ledgerline (brand runs in its own campaign)
  Ad-group level: AG1: "expense report template", "per diem"; AG2: "invoice generator", "freelance"; AG3: "receipt printer", "receipt scanner app"

Sitelinks:
  - Pricing | Plans from $39 a month | 14-day free trial | /pricing
  - Agency Case Study | Close books in 2 days | How one studio did it | /customers/northgate
  - Client Rebilling | Tag spend to projects | Export to your ledger | /features/rebilling
  - Product Tour | 2-minute walkthrough | No signup needed | /tour

Callouts: No Credit Card Needed · Slack Approvals · Per-Client Card Limits · Setup in One Afternoon

RSA1 — AG1 Agency expense software
  Final URL: https://example.com/agencies
  Path1: expenses   Path2: agencies
  Pinning: none

Lint (`python3 scripts/ads_tool.py limits rsa.txt --keyword "expense software"`):

```
headline      1 ( 29) Expense Software for Agencies
headline      2 ( 25) Close Month-End in 2 Days
headline      3 ( 30) Receipts Matched Automatically
headline      4 ( 28) Rebill Clients Without Excel
headline      5 ( 30) Built for Agency Finance Teams
headline      6 ( 28) Cards With Per-Client Limits
headline      7 ( 24) Approve Spend From Slack
headline      8 ( 24) Trusted by 400+ Agencies
headline      9 ( 28) Start Your Free 14-Day Trial
headline     10 ( 27) See a 2-Minute Product Tour
headline     11 ( 28) Tag Costs to Client Projects
headline     12 ( 23) Set Up in One Afternoon
headline     13 ( 27) Export Books to Your Ledger
headline     14 ( 22) Plans From $39 a Month
headline     15 ( 27) Ledgerline Expense Software
description   1 ( 88) Cards, receipts and approvals in one place. Agencies close books in 2 days. Try it free.
description   2 ( 88) Every expense tagged to a client and project, so rebilling takes minutes, not a weekend.
description   3 ( 87) 400+ agencies use Ledgerline to stop chasing receipts. Start a free 14-day trial today.
description   4 ( 87) Per-client card limits and Slack approvals keep spend in budget. No credit card needed.
path          1 (  8) expenses
path          2 (  8) agencies

ok
```

Why this passes the RSA rules: 15 distinct headlines (keyword ×3, benefit ×4, proof ×1, CTA ×2, differentiator ×3, price ×1, brand ×1), each readable alone; 4 descriptions covering benefit + proof, feature + outcome, proof + CTA, offer + objection; no em dashes, superlatives or all caps. An earlier draft failed lint because of a duplicate headline, "Best Expense Tool EVER!!" (superlative, stacked exclamation marks, all caps) and an em dash in a description.
