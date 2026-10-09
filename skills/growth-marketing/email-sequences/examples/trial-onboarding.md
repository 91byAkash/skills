# Example: 14-day trial onboarding (expense tool)

**Trigger**: trial starts. **Goal**: activation (first receipt matched) within 3 days, then paid conversion. **Exits**: purchase (move to new-customer series); unsubscribe. **Branch**: activated vs not, checked before each send. **Sender**: Maya from the customer team, replies go to a shared inbox answered within 4 business hours.

---

**E1 · immediately · all**
Subject: Your cards are ready: match your first receipt in 2 minutes
Preview: One photo, one tap, and your first transaction is reconciled.

Hi {first_name|there},

Your workspace is live. The fastest way to see how this works: make one small purchase with your virtual card, then snap the receipt from the notification on your phone. It matches automatically.

[Match my first receipt]

Over the next two weeks I'll send a few short emails, each with one thing that saves your team time at month-end.

Maya, customer team

(~75 words · transactional · metric: activation within 24h)

---

**E2 · day 1 · not activated**
Subject: The 90-second setup most teams do first
Preview: Connect your bank feed and existing card transactions show up ready to match.

Hi {first_name|there},

If you'd rather not issue a new card yet, connect the bank feed for the cards you already use. Last month's transactions appear in about a minute, and you can match receipts to them straight away.

Here's a 90-second walkthrough: [Connect my bank feed]

Maya

(~65 words · metric: bank feed connected)

---

**E3 · day 3 · not activated**
Subject: Want us to set it up with you? (15 minutes)
Preview: Bring your card list and accounting login; we'll do the setup together on a call.

Hi {first_name|there},

Most teams that stall at this point are juggling month-end themselves. If that's you, book 15 minutes and we'll connect your cards, import last month's receipts and set your approval rules together.

[Pick a time]

Or reply with what's blocking you and I'll send the exact steps.

Maya

(~65 words · metric: call booked or activation)

---

**E4 · day 4 · activated**
Subject: How a 30-person studio closes the month in 2 days
Preview: They used to lose the last three days of every month to receipt chasing.

Story email (~320 words): the studio's finance lead, the old process (spreadsheet + Slack reminders), the change (cards + receipt-at-purchase + approval rules), the result (close went from 5 days to 2, 46 missing receipts per month to 3), and the one setting they'd turn on first. CTA: [Turn on approval rules].

(metric: approval rules enabled)

---

**E5 · day 10 · activated**
Subject: Your first 10 days: 46 receipts matched
Preview: About 3 hours saved so far. Here's the plan that fits your team size.

Usage summary block (receipts matched, hours saved estimate, cards issued) → plan recommendation based on spender count → annual saving shown in currency → [Choose my plan]. Secondary link: "Need more time? Reply and we'll extend your trial by 7 days."

(metric: plan page visits, upgrades)

---

**E6 · day 13 · all not purchased**
Subject: Your trial ends tomorrow
Preview: What changes, what you keep, and a one-click way to continue.

Plain facts: trial ends {date}; cards pause, data stays for 30 days; continuing takes one click on the plan we recommended; annual saves {annual_saving}. [Continue on {plan}]. Low-activation readers see an alternative CTA: "Book a 15-minute walkthrough before deciding."

(metric: trial-to-paid)

---

**Expected impact check**: compare against the previous time-based sequence with a 50/50 split; primary metric trial-to-paid, secondary activation within 3 days and unsubscribes.
