# Funnel Spec: [offer]

## 1. Inputs
| Input | Value | Implication |
|---|---|---|
| Offer + price | | |
| Traffic source + temperature | | |
| Awareness level | | |
| Fulfilment (digital/physical/service) | | |
| Existing assets (list, store, pixels, domain) | | |
Conflicts flagged: [e.g., high price on cold traffic with instant checkout]

## 2. Shape
[Chosen shape] because [one line].

## 3. Pages (one block per page; no blank fields — write the assumption if unknown)
```
### [Page name] — type: LANDING | CHECKOUT | UPSELL | DOWNSELL | THANKYOU | OPT-IN | BOOKING
Goal (one action):
Traffic in (from where, mindset):
Above the fold: headline / subhead / hero / primary CTA text
Body sections in order (job of each):
Proof required (specific):
Objections handled (objection → line that handles it):
Fields collected (justify each):
Price shown (yes/no, framing):
Exit path if no conversion (retargeting, email capture, none):
Success metric + starting target:
```

## 4. Price ladder
| Step | Offer | Price | Expected take | Notes |
|---|---|---|---|---|
| Entry | | | | |
| Upsell 1 | | | 10-30% | complementary, one-click |
| Downsell (on decline) | | | | smaller commitment |
| Back end | | | | sold by email/call later |

## 5. Instrumentation (launch blockers)
- [ ] Event per step: [names]
- [ ] Click ids captured on landing and stored on the order
- [ ] Server-side purchase event with value + currency (updated after upsells)
- [ ] Test slot: [page, variable, metric]

## 6. Build order
1. Checkout  2. Upsell/downsell  3. Thank-you  4. Landing  5. Emails

## 7. Open assumptions to confirm
- …
