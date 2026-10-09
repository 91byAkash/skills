# Dunning emails: {product}

Plain text · from {name/product} · reply-to support · update link = magic link (no login)

## Card expiring (−30 / −15 / −7 days)
Subject: Your card ending {last4} expires soon
Hi {first_name}, the card on your {product} subscription expires on {date}. Update it here so nothing gets interrupted: {link}. Takes about 30 seconds.

## 1 · Day 0
Subject: Your payment didn't go through
Hi {first_name}, we couldn't charge your {card_brand} ending {last4} for {product} (${amount}). This usually just needs a quick card update: {link}. Your access isn't affected and we'll retry automatically, but updating is the fastest fix. Reply if you need help.

## 2 · Day 3
Subject: Reminder: update your payment for {product}
Hi {first_name}, we still haven't been able to process ${amount}. {link}. Your {projects/data} are safe; we just need a working payment method to keep the account active.

## 3 · Day 7
Subject: Your {product} account pauses on {date}
Hi {first_name}, a few retries on your card ending {last4} have been declined. If we can't collect payment by {date}, the account pauses and you'll lose access to:
- {their key workspace/data}
- {team access for N people}
Update here: {link}. Nothing gets deleted; you can reactivate anytime.

## 4 · Day 10
Subject: Last reminder: your account pauses tomorrow
Hi {first_name}, ${amount} is past due and the account pauses tomorrow ({date}). {link}. After pausing, your data is kept for {N} days and one card update restores everything. If you meant to cancel, you don't need to do anything.

## In-app banner
"Your payment of ${amount} didn't go through. Update your card to keep access. [Update payment]"

## Paused account
Day 1: "Your account is paused; your data is safe for {N} days. {link}"
Day 7: "Everything you built is still here. {link}"
