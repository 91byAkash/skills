# Popup and Paywall Screen Specs

## Popup spec
| Field | Value |
|---|---|
| Type | email capture / lead magnet / discount / exit intent / announcement / slide-in |
| Trigger | click / exit intent (desktop) / scroll 50% / 45 s / page count ≥ 3 / behavior |
| Targeting | pages, source, new vs returning; exclude converted users, checkout, signup |
| Frequency | once per session; suppress [7-30] days after dismiss; never after conversion |
| Mobile | bottom sheet, ≤ 40% of screen, no entry interstitial |
| Headline | |
| Subhead | expectation or objection handler |
| Fields | email only (name optional) |
| CTA | first-person, specific |
| Decline | "No thanks" |
| Compliance | consent text + privacy link; boxes unticked |
| Accessibility | Esc closes, focus trap, labeled close button, contrast |
| Success state | what arrives, when |
| Metrics | views, submit rate, close rate, time to close |

## Upgrade screens
Fill one column per screen you need. Leave a cell blank only when the slot does not apply.

| Slot | Locked feature | Limit reached | Trial running out |
|---|---|---|---|
| When it appears | user taps the Pro feature, after they have reached the activation moment | the action that would exceed the free allowance | 7, 3 and 1 days before the trial ends |
| Top line | "[Feature] comes with Pro" | "Your workspace is full: [used] of [allowance] [units]" | "[N] days left on your Pro trial" |
| Visual | the feature rendered with their own data, or a preview | meter showing the allowance used up | summary of what they did during the trial |
| Value | "[Feature] lets you [outcome]" plus 2 bullets tied to what they were just doing | Free vs Pro allowance side by side, plus one extra Pro benefit | their own numbers (e.g. "38 invoices sent, 4 teammates added") and what changes on Free |
| Main button | "Get Pro, [$X]/mo" | "Upgrade for more [units]" | "Stay on Pro, [$X]/mo billed yearly" |
| Way out | "Not now" | a free alternative ("Clear out old [units]") | "Ask me tomorrow" and "Move to Free" |
| Never | hide the close button, block work they already started | delete or lock data they already created | fake countdowns, guilt-trip decline copy |

Example, limit reached:
```
Your workspace is full: 5 GB of 5 GB used
[storage meter, full]
Free 5 GB  ·  Pro 100 GB and version history
[Upgrade for more storage]    [Clear out old files]
```

## Post-purchase offer
Shown on the thank-you step, before the order confirmation email goes out.

| Slot | Rule |
|---|---|
| Heading | the next problem this buyer will hit, given what they just bought |
| Body | 3 to 5 short lines on a single benefit, referring to the item in their order |
| Proof | one concrete line (a number, a named customer) |
| Price | the real price; show a crossed-out price only if it is genuinely charged elsewhere |
| Accept | one tap, charged to the card they just used, added to the same order; say so beside the button |
| Decline | a plain link that lets them leave honestly, e.g. "Skip this, show my receipt" |
