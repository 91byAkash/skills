# Cancel flows and save offers

Contents: 1 structure · 2 exit survey · 3 reason → offer map · 4 offer types and rules · 5 flows by business type · 6 by billing interval · 7 segment flows · 8 UI rules · 9 post-cancel and win-back · 10 tests · 11 compliance · 12 rollout.

## 1. Structure

Trigger (cancel button in account settings, findable) → exit survey (one question) → one reason-matched offer + one fallback → confirmation (what happens, when access ends) → post-cancel (email, reactivation path, win-back triggers).

Keep it to 2-3 screens. "Continue cancelling" is visible on every screen. If the save flow errors, the cancellation still processes.

## 2. Exit survey

- One question, single-select, optional free text; 5-8 options; most common first (review quarterly).
- Neutral framing ("Help us improve: what's the main reason?"), no guilt.
- Options: too expensive · not using it enough · missing a feature · switching to another tool · technical issues · temporary/don't need it now · business closed/changed · other (text).
- Optional follow-up only where it changes the offer: "Which tool?" for switching (optional), "Which feature?" for missing feature.

## 3. Reason → offer map

| Reason | Primary offer | Fallback |
|---|---|---|
| Too expensive | Discount 20-30% for 2-3 months (show the dollar saving) | Downgrade to a cheaper plan; annual switch if engaged |
| Not using enough | Pause 1-3 months | Free setup/onboarding session |
| Missing feature | Roadmap status with honest timing, or the workaround | Feedback call; notify-when-shipped |
| Switching | Ask which tool; comparison on what matters to them | Price match for a limited period, or feedback call |
| Technical issues | Escalate to support now | Account credit + priority fix |
| Temporary/seasonal | Pause | Temporary downgrade |
| Business closed | No offer; thank them; data export | — |

A discount won't save someone who doesn't use the product; a roadmap won't save someone who can't afford it.

## 4. Offer types and rules

**Discount**: 20-30% for 2-3 months; never above ~30% (trains cancel-to-bargain); at most one discount offer per session, and one per customer per 12 months; full price resumes automatically (say so); if a discount-saved customer cancels again at full price, don't re-offer. Escalating ladders (15% then 25%) extract more saves short-term but teach bargaining; use sparingly.

**Pause**: options 1, 2, 3 months, default to 1; data kept, access off; one pause per 12 months; auto-resume with emails at −7 days (what's new), −1 day, and day 0 (welcome back). Pause usually beats discount because it doesn't devalue the product; a majority of pausers typically resume when pauses are short.

**Downgrade**: "right-size your plan"; show keep (✓) vs. lose (✗); keep their data; no upgrade prompts for 30 days after.

**Feature unlock / extension**: unlock a premium feature they never tried, or extend a higher tier briefly; for "not getting value".

**Personal outreach**: top 10-20% of accounts by MRR; CS call or founder email.

**Annual switch**: for engaged, price-sensitive monthly customers.

Economics: `retention_tool.py save` estimates expected value per cancel session including bargaining cost. Track offer LTV, not just acceptance.

## 5. Flows by business type

| Type | Flow | Notes | Typical save rate |
|---|---|---|---|
| B2C / self-serve | Survey → offer → confirm | Fully automated, mobile-friendly, 2-3 screens | 20-30% |
| B2B team plans | Survey → offer or route to CS → confirm | Admin/owner role required to cancel; show team impact ("8 people lose access"); allow "schedule a call" | 30-45% |
| Freemium | "Switch to Free?" first → survey → offer → confirm | Keeping them on free is the save; track for re-upgrade | — |

Routing by account value (example thresholds; adapt):

| MRR | Handling |
|---|---|
| < $100 | Automated flow |
| $100-500 | Automated + flag for CS follow-up |
| $500-2,000 | Offer a CS conversation before completing; online cancel still available |
| $2,000+ | Contract-governed; CS owns renewal/cancellation per contract terms |

Never require a call to cancel a consumer subscription that was bought online.

## 6. By billing interval

Monthly: more price-sensitive; discount (if price), pause (if not using/temporary), annual switch (if engaged but price-sensitive).

Annual: stronger reasons, more at stake; order: pause rest of term (if temporary) → plan adjustment + credit at renewal → CS outreach → partial refund + downgrade (beats full refund + cancel). Prorated refunds when significant time remains; "pause until renewal" when < 3 months left; be generous; bad refund experiences create loud detractors.

## 7. Segment flows

| Segment | Save approach | Save potential |
|---|---|---|
| New (< 30 days) | Onboarding help, setup call, extended trial; ask what they hoped to accomplish | Medium; learning is the main value |
| Engaged, cancelling on price | Discount, annual switch, downgrade | High |
| Dormant (no login 30+ days) | Pause or "what changed?"; no discount | Low |
| Power user switching | Feedback call, roadmap, competitive match | Medium |
| Repeat canceller | No repeat discount; pause or graceful exit | Low |
| Long tenure | More generous offers, personal note | Medium-high |

## 8. UI rules

One primary offer + one fallback, not a menu; dollar savings, not just percentages; use their name and account data (projects, team members) honestly; "No thanks, continue cancelling" as a clear button; mobile-first; no pre-checked boxes or confusing double negatives.

## 9. Post-cancel and win-back

Confirmation page: cancelled; access until [date]; data kept for [N] days; export available; reactivate button.

| Timing | Action |
|---|---|
| Immediately | Confirmation email with access end date and reactivation link |
| Day 1-6 | Nothing |
| Day 7 | Short experience survey |
| Day 30 | What's new (only if real changes) |
| Day 60 | Address their specific reason if fixed ("you asked for X; it shipped") |
| Day 90 | Final win-back with an offer |

Reactivation should restore data and settings in one click. Win-back copy lives in email-sequences.

## 10. Tests

One variable at a time, with save rate and 90-day survival as metrics: discount depth (20% vs. 30%); pause length options; survey before vs. after offer; modal vs. full page; empathetic vs. direct copy; offer order (pause first vs. discount first for price reasons). Keep a small no-offer holdout to measure true incremental saves.

## 11. Compliance (not legal advice; verify current rules)

- US: federal rules require clear disclosure of recurring terms, consent, and a simple cancellation method for online-sold subscriptions; the FTC's broader click-to-cancel rule was vacated in court in 2025, but state auto-renewal laws (e.g., California's, amended in 2025) require online cancellation where the customer signed up online and limit save-offer friction.
- EU/UK: consumer law requires clear cancellation routes; UK subscription-contract rules are being phased in; tell users about data retention after cancel, offer export, honor deletion requests, don't use post-cancel data for marketing without a lawful basis.
- Universal: cancellation as easy as signup; no hidden button; no forced call; save offers allowed but "continue cancelling" must be obvious; confirm cancellation in writing.

## 12. Rollout

Week 1: survey + one offer per reason + confirmation; tracking (cancel started, reason, offer shown, offer accepted, cancelled); card-expiry emails.
Weeks 2-4: fallback offers, pause, dunning sequence, decline-based retries, value-based routing.
Month 2+: health score and proactive triggers, offer tests, segment flows, win-back sequence, cohort analysis by reason and offer.

**Law check (not legal advice)**: many places require cancellation to be as easy as sign-up, online if sign-up was online. Examples: California's automatic renewal law (amended from July 2025), Germany's mandatory cancel button, the EU consumer rules on subscription traps. The US FTC's federal click-to-cancel rule was vacated in July 2025, but state laws and the FTC's general ROSCA enforcement still apply. Keep save offers to one screen that can be skipped.
