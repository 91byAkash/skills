# Failed-payment recovery (dunning)

Involuntary churn is customers who meant to stay. It's usually the cheapest churn to fix: no product changes, no persuasion, mostly plumbing and clear emails.

Contents: 1 timeline · 2 pre-dunning · 3 decline types and retries · 4 email sequence · 5 grace period · 6 in-app notices · 7 setup checklist · 8 metrics and value.

## 1. Timeline

| Day | Action |
|---|---|
| −30 to −7 | Card-expiry reminders; pre-billing notice for annual plans |
| 0 | Payment fails → classify decline → retry plan + email 1 + in-app banner |
| 1-3 | Retry; email 2 |
| 5-7 | Retry; email 3 (consequence and date) |
| 7-10 | Final retry; email 4 (final notice) |
| 10-14 | Grace period ends → pause (not delete) |
| 14+ | Paused-account emails, then win-back |

## 2. Pre-dunning

- **Card expiry**: email at 30, 15 and 7 days before expiry; in-app banner at 3 days. Subject like "Your card ending 4242 expires soon"; one button to update; "takes 30 seconds".
- **Network card updaters**: card networks run account-updater programs that refresh replaced or expired card numbers; most billing providers support them (some by default, some via gateway settings). Typically cuts expired/replaced-card declines substantially.
- **Backup payment method**: ask after a recovered failure (best timing: they felt the pain), or after the first successful payment; asking at signup converts poorly.
- **Pre-billing notice**: 7 days before annual renewals with amount, date, what's included and an update link; some jurisdictions require renewal reminders.
- **Payment method mix**: offer bank debit or invoicing for B2B; fewer card failures.

## 3. Decline types and retries

| Decline | Type | Retry? |
|---|---|---|
| Insufficient funds | Soft | Yes, in 2-3 days and after typical paydays |
| Generic decline | Soft | Yes, 3-4 times |
| Processing/network error | Soft | Yes, within 24h |
| Expired card | Hard | No; request a new card (updater may fix) |
| Lost/stolen card | Hard | No; request a new card |
| "Do not honor" | Ambiguous | Once more, then ask for a new card |
| Authentication required (strong customer authentication) | Auth | No retry; send the customer to authenticate |

Schedule without provider optimization: day 1 (24h, morning), day 3 (different time of day), day 5 (after the 1st/15th payday), day 7 (next business-day morning), day 10 (final). Retry on the day of month the payment previously succeeded; avoid weekends. Provider "smart retry" features that time attempts by model typically beat fixed schedules; turn them on when available. Stop retrying hard declines: repeated attempts on dead cards hurt your standing with processors.

Regional rules: in India, card and UPI recurring payments run on RBI e-mandates (customer registers the mandate; pre-debit notice at least 24 hours before each charge; additional authentication above ₹15,000 per charge, or ₹1 lakh for some categories such as insurance and mutual funds), so a failed mandate usually needs re-registration, not a blind retry. In the EU/UK, merchant-initiated renewals are generally exempt from SCA, but a soft decline asking for authentication must go to the customer.

## 4. Email sequence

Plain text, from a person or the product, direct update link that works without login (magic link), no blame ("your payment didn't go through", not "you failed to pay"), support reply-to.

1. **Day 0, friendly**: subject "Your payment didn't go through". Card ending, amount, it happens, update link, access not affected yet, we'll retry.
2. **Day 3, reminder**: "Quick reminder: update your payment for [Product]". Still unpaid, update link, data safe.
3. **Day 7, consequence**: "Your account will be paused on [date]". What they'll lose (their projects, team access for N people), update link, data won't be deleted.
4. **Day 10, final**: "Last reminder: account pauses tomorrow". Update link; after pausing data is kept for N days and reactivation is one click; "If you meant to cancel, no action needed."

Templates with placeholders: [templates/dunning-emails.md](templates/dunning-emails.md). SMS can supplement for consumer products with consent.

## 5. Grace period

| Setting | Recommendation |
|---|---|
| Length | 7-14 days after the final retry |
| Access | B2B: full access (higher recovery, respectful); B2C: read-only (urgency without data-loss fear); immediate lockout only for very cheap plans |
| Banner | "Payment past due: update to continue" on every page |
| Retries | Continue in background |

After grace: pause, don't delete. Day 1 "paused" email; day 7 "your data is still here"; day 30 win-back; day 60 final win-back; day 90 deletion warning if your retention policy deletes.

## 6. In-app notices

- Banner on every page load during dunning; dismissible per session; one click to the update form; never block the product during the grace period.
- Final-warning modal before pause: date, what they keep access to (projects, team members), "Update payment method" and "Remind me later".
- Admin-only for team accounts (members see "contact your admin").

## 7. Setup checklist (provider-neutral)

- [ ] Smart retries or the manual schedule above enabled.
- [ ] Card updater enabled.
- [ ] Webhooks/events handled: payment failed (start dunning), invoice paid (stop dunning, restore access), subscription status changed, subscription deleted.
- [ ] Dunning emails replaced with your own copy (or the provider's customized).
- [ ] Magic-link update page tested on mobile.
- [ ] Grace period and post-grace action (pause vs. cancel) configured per plan.
- [ ] Recovery tracked by decline type.

## 8. Metrics and value

| Metric | Target (directional) |
|---|---|
| Overall recovery rate | 50-60%+ |
| Soft-decline recovery | 70%+ |
| Hard-decline recovery | 40%+ |
| Time to recovery | < 5 days |
| Pre-dunning prevention | 20-30% of expected failures |
| Dunning email click rate | 30%+ of opens (treat opens as unreliable) |
| Involuntary churn | Trending toward 0.5-1.5% of MRR/month |

Value: `retention_tool.py dunning --failed-mrr 6000 --current 0.32 --target 0.6 --monthly-churn 0.055` → +$1,680 MRR recovered per month, ~$30.5k lifetime value per month of improvement, ~$108k first-year cash if sustained.
