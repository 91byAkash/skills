# Sequence plan: [name]

- Trigger (entry):
- Goal (exit when achieved):
- Other exits / suppressions (e.g., in dunning, unsubscribed from marketing, became customer):
- Audience and segments:
- Branching rules (event → path):
- Sender (name, address, reply-to goes to):
- Success metric (sequence) and target:

| # | Send rule (delay or event) | Segment | Job | Subject (+2 alts) | Preview | Primary CTA → destination | Metric |
|---|---|---|---|---|---|---|---|

CSV for `scripts/email_tool.py plan`: email,day,goal,subject,preview,cta,type,body_words (type: transactional / educational / story / sales; one CTA per row)

## Measurement and tests
- Baseline:
- Test 1:
- Test 2:

## Pre-launch checks
- [ ] Mobile + dark mode test sends
- [ ] Links, UTMs and merge-field fallbacks
- [ ] Exit/suppression rules verified with test contacts
- [ ] Unsubscribe and address present (marketing mail)
