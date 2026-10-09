# Cancel flow spec: {product}

## Entry
Location of cancel control: {settings path} · Who can cancel: {owner/admin} · Online cancel available: yes

## Screen 1: survey
Question: "{Help us improve: what's the main reason you're cancelling?}"
Options (ordered by frequency): {…} · Free text: optional
Buttons: [Continue] [Keep my subscription]

## Reason → offer map
| Reason | Primary offer (copy) | Fallback | Eligibility rules |
|---|---|---|---|
| Too expensive | {25% off for 3 months: save ${x}/month} | {Starter at $y} | No discount in last 12 months |
| Not using enough | {Pause 1/2/3 months} | {Setup call} | 1 pause per 12 months |
| Missing feature | {roadmap status / workaround} | {feedback call} | |
| Switching | {which tool? + comparison} | {feedback call} | |
| Technical issues | {escalate to support} | {credit} | |
| Temporary | {pause} | {downgrade} | |
| Business closed | none | | |

## Routing by value
| MRR band | Handling |
|---|---|

## Screen 3: confirmation
"Your subscription is cancelled. Access continues until {date}. Data kept for {N} days. [Export data] [Reactivate]"

## Post-cancel
| Timing | Message | Trigger condition |
|---|---|---|

## Tracking events
cancel_started · reason_selected{reason} · offer_shown{type} · offer_accepted{type} · cancel_completed · reactivated · saved_customer_90d_active

## Compliance check
- [ ] Cancel as easy as signup; no forced call
- [ ] "Continue cancelling" visible on every screen
- [ ] Recurring terms and renewal reminders meet local rules
- [ ] Cancellation processes even if the flow errors
- [ ] Written confirmation sent

## Tests planned
{variable, metric, holdout size}
