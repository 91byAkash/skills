---
name: email-sequences
description: "Design and write opt-in lifecycle email sequences and the lead magnets that feed them. Use when the user asks for a welcome, nurture, onboarding, trial-to-paid, win-back or dunning sequence, a drip or newsletter plan, a lead magnet, or \"why are my emails underperforming\". Not for cold outbound to strangers (use sales-outreach)."
license: MIT
metadata:
  category: "growth-marketing"
  version: "3.0.0"
---

# Email Sequences

Every email has one job, arrives because of a trigger the reader caused, and moves them one step toward a defined outcome. Relevance beats volume.

Scope: welcome, lead nurture, onboarding, trial-to-paid, new customer, re-engagement, win-back, failed payment, upgrade, review/referral asks, usage reports, newsletters, promotions; lead magnets (format, buyer-stage fit, gating, landing and thank-you pages); triggers, timing, exit conditions, segmentation, subject lines, testing, metrics, deliverability and consent. In-app onboarding UX belongs to conversion-optimization.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `sequence_type` | required | ask | welcome, nurture, onboarding, trial-to-paid, re-engagement, win-back, dunning, newsletter, promo, lead-magnet |
| `trigger` | required | ask | downloaded checklist; signed up for trial; payment failed |
| `audience` | required | from context file | agency finance leads on a 14-day trial |
| `goal` | required | ask | activate (connect bank feed), book demo, convert to paid |
| `activation_event` | optional | ask for product sequences | first receipt matched |
| `segments` | optional | none | role, plan, engagement level, lead-magnet source |
| `assets` | optional | none | case studies, guides, videos, product screenshots |
| `platform` | optional | any ESP/CRM | needs branching on events |
| `brand_voice` | optional | from context file | plain, warm, first person from the founder |
| `metrics` | optional | none | current open/click/conversion by email |

Read `.agents/product-marketing.md` first. For product sequences, also find the activation event (see conversion-optimization onboarding).

## Output

1. **Sequence map** ([templates/sequence-plan.md](templates/sequence-plan.md)): name, trigger, goal, entry/exit conditions, suppression rules, branching, number and timing of emails, success metric.
2. **Per email**: purpose, send rule (delay or event), segment, subject + 2 alternatives, preview text, body, primary CTA (button text + destination), secondary link if any, and the metric it serves.
3. **Measurement and test plan**: KPIs per email and per sequence, first two tests.
4. For lead magnets: concept, format, outline, gate decision, form fields, landing + thank-you page copy, delivery method, promotion plan, target conversion rates.

## Supporting files

- [REFERENCE.md](REFERENCE.md): principles, sequence blueprints with timing, full email-type catalog (triggers, structure, copy approach), subject/preview patterns, copy structure and length, personalization and segmentation, testing, metrics and benchmarks, deliverability and compliance. Read for any sequence.
- [lead-magnets.md](lead-magnets.md): lead magnet principles, formats with build guidance, buyer-stage matching, gating, landing/thank-you/delivery, promotion, benchmarks, lead-quality signals, costs. Read for lead magnet work.
- [examples/trial-onboarding.md](examples/trial-onboarding.md): a fully written 6-email trial sequence with branching.
- [scripts/email_tool.py](scripts/email_tool.py): `plan` (checks a sequence CSV for subject/preview length, CTA count, gaps, weekend sends, length by type, bait), `subject` (lint subject lines), `health` (bounce, complaint, unsubscribe, click, conversion vs thresholds; complaint rate ≥ 0.3% is FAIL). Each exits 1 when anything is flagged. `python3 scripts/email_tool.py plan sequence.csv --start 2026-11-02 --b2b`.
- Templates: [sequence-plan](templates/sequence-plan.md), [email-brief](templates/email-brief.md).

## Steps

1. **Define trigger, goal and exit.** Exit the moment the goal happens (converted, activated, booked) and suppress overlapping sequences (no nurture email to someone in dunning). If the goal is product activation → coordinate with in-app messages; email supports, doesn't duplicate.
2. **Pick the blueprint and length** (REFERENCE.md §2): welcome 3-7 over ~2 weeks; nurture 5-10 over 2-3 weeks; onboarding 5-7 over 14 days; re-engagement 3-4 over 2 weeks; win-back 2-4 over 30-90 days; dunning 3-4 over 7-14 days. Longer sales cycles and complex products → longer, more spaced sequences.
3. **Prefer behavior over time.** If the platform can branch on events → trigger on actions (didn't connect integration after 48h; hit 80% of plan limit; used premium feature) and skip steps already done. If not → time-based with exit conditions.
4. **Assign one job per email**, ordered value → proof → objection → offer. First email immediately, delivering what was promised plus one next step. Early emails 1-2 days apart; nurture 2-4 days; long-term weekly or biweekly. B2B: weekdays, recipient's local time; B2C: test weekends.
5. **Write subjects and previews.** Clear and specific beats clever; ~30-60 characters; preview 40-140 characters that extends (not repeats) the subject. Write 3 per email. No fake "Re:"/"Fwd:", no bait.
6. **Write bodies**: hook (the reason you're writing) → why it matters to them → the value → one CTA → human sign-off. Mobile-first, short paragraphs. Length: transactional 50-125 words, educational 150-300, story 300-500. Button text = action + outcome. Personalize with real data (usage, plan, inviter's name), with fallbacks.
7. **Segment** by behavior (active/inactive, clicked/not), stage (trial/paid, new/tenured, at-risk), and profile (role, use case, size, lead-magnet source). Branch content or cadence where segments need different help (e.g., low-engagement trials get setup help, high-engagement get the upgrade case).
8. **Lint and check**: `email_tool.py plan` on the sequence CSV; the `ai-tells.md` list in the `marketing-copy` skill (plus email tells: "I hope this finds you well", "just checking in", "feel free to reach out").
9. **Deliverability and compliance**: authenticated domain (SPF, DKIM, DMARC), one-click unsubscribe in marketing mail, physical address, consent recorded, complaint rate under 0.1% (never near 0.3%), sunset unengaged contacts, double opt-in where required or list quality is poor.
10. **Measure and test**: primary metric per email (click, activation, booking, conversion) and per sequence (goal completion rate, time to goal, revenue per recipient); treat opens as directional; test one variable at a time, subject lines first, then timing, CTA, length. Use analytics-and-experiments for sample sizes.

## Checkpoints

- After step 2: sequence map (trigger, goal, exits, timing) approved before writing copy.
- After step 6: review email 1 and the offer email first; they carry most of the result.
- Before launch: test sends on mobile and dark mode, links and merge-field fallbacks checked, suppression rules verified, `health` baseline recorded.

## Worked example

**Context**: expense tool, 14-day trial (no card), activation = first receipt matched to a card transaction; trial-to-paid 11%; activated users convert at 31%, non-activated at 3%.
- Goal: raise activation within 3 days; exit on activation (switch to the activated branch) or on purchase.
- Map: E1 immediate "Your cards are ready: match your first receipt in 2 minutes" → E2 day 1 if not activated (connect bank feed, 90-second video) → E3 day 3 if not activated (offer a 15-minute setup call; reply-to goes to a human) → activated branch: E4 day 4 case study "How a 30-person studio closed in 2 days" → E5 day 10 value summary from usage ("you matched 46 receipts, saved ~3 hours") + plan recommendation → E6 day 13 trial ends tomorrow, what changes, annual saving, one-click upgrade.
- Plan check: E3 subject first drafted "Re: your setup" → flagged as fake reply; changed to "Want us to set it up with you? (15 min)".
- Result after 4 weeks (A/B vs old time-based sequence, ~2,600 trials per arm): activation within 3 days 38% → 47%; trial-to-paid 11.0% → 13.4%; unsubscribe per send 0.3%.

## Pitfalls

- Several CTAs per email; long welcome emails that bury the promised asset.
- Time-only sequences that keep teaching setup to users who already activated.
- No exit or suppression rules: customers get "start your trial", dunning overlaps promotions.
- Clever subject lines that hide the point; fake "Re:"; preview text left as "View in browser".
- Judging success by open rates (inflated by privacy proxies) instead of clicks and goal completion.
- Discount-first win-back and trial emails that train people to wait.
- Mailing unengaged or purchased lists; ignoring authentication and complaint rates until inbox placement collapses.
- Gated lead magnets that are generic ebooks with no path to the product.

## Related skills

conversion-optimization (onboarding, popups, forms, landing pages), retention-and-referrals (churn, dunning, referral programs), marketing-copy (writing quality), content-strategy (newsletter content and distribution), sales-outreach (cold email and sales sequences), analytics-and-experiments (tests and attribution), pricing-and-offers (trial and upgrade offers).

## Done when

- [ ] Trigger, goal, entry/exit and suppression rules defined; branching specified where the platform allows.
- [ ] Every email has one job, one primary CTA, subject + alternatives, preview text, and a metric.
- [ ] Copy passes the plan check and the ai-tells self-check.
- [ ] Deliverability and consent requirements confirmed.
- [ ] KPIs per email and per sequence, and the first tests, are written down.
- [ ] Lead magnet work (if any) includes format, gate, form fields, landing + thank-you copy, delivery and promotion plan.
