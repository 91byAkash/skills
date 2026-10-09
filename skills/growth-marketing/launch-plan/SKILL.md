---
name: launch-plan
description: "Plan a product, feature or relaunch launch: tier, readiness gate, dated timeline, channels, launch day, follow-up. Use when the user says \"we are launching\", needs a launch checklist or calendar, a Product Hunt day, site go-live QA, directory or review-site submissions, or a changelog digest. Not for 90-day or 12-month marketing plans (use marketing-plan)."
license: MIT
metadata:
  category: "growth-marketing"
  version: "3.0.0"
---

# Launch Plan

A launch is a campaign of several moments, not a day. Anchor it in the team, budget and evidence that actually exist.

Scope: launch tiers and readiness, owned/rented/borrowed channels, the five launch phases, launch-platform days, launch-day operations, post-launch follow-through, shipped-work announcements, site go-live QA, directory and review-site submissions, partner scoring for a launch. The 90-day/12-month plan, market sizing, idea selection and the full co-marketing playbook live in the marketing-plan skill.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `scope` | required | launch | launch (major/medium/minor), directories, shipped digest |
| `what` | required | ask | v2 with client approvals and payments; new integration |
| `launch_date` | required | propose next Tue-Thu with enough lead time | 2026-11-17 |
| `audience` | required | from `.agents/product-marketing.md` | freelance designers and 2-10 person studios |
| `goal` | required | ask | 400 trials in 14 days |
| `team_and_budget` | required | ask | founder + 1 marketer; $1.5k launch budget |
| `channels_now` | optional | ask | newsletter 6,200 subs; blog; no paid |
| `assets_and_proof` | optional | none | beta quotes, demo video, 60 beta users |
| `constraints` | optional | none | brand avoids hype |

Read `.agents/product-marketing.md` first and ask only for what it does not answer. Mark unconfirmed numbers `[TBD: confirm]`.

## Output

Depending on `scope`, one or more of:
- **Launch brief** ([templates/launch-brief.md](templates/launch-brief.md)): goal and kill trigger, "you can now" statements, messages with proof, readiness gate, channel table with owners and dates, dated timeline from `timeline`, asset list, pages that become wrong, post-launch plan, risks; plus a **launch-day runbook** ([templates/launch-day-runbook.md](templates/launch-day-runbook.md)).
- **Directory plan**: readiness verdict, tiers chosen and skipped, week-by-week batches, destination pages to build, per-tier copy variants, review drive, tracker ([templates/directory-tracker.csv](templates/directory-tracker.csv)).
- **Partner shortlist** for the launch: scored candidates and the ask for each.
- **Shipped digest** ([templates/shipped-digest.md](templates/shipped-digest.md)) for continuous release announcements.

## Supporting files

- [launch.md](launch.md): campaign mindset, readiness gate, owned/rented/borrowed, five phases, launch-platform day, launch-day ops, post-launch, tiers, shipped-work workflow, measurement. Read for any launch.
- [site-launch-qa.md](site-launch-qa.md): before/at/after go-live checks for sites, redesigns, migrations and launch pages. Read before any page or site switch.
- [directories.md](directories.md): rules, readiness, tiers, per-tier positioning, submission safety and workflow, link verification, review drives, community distribution, targets. Read for directory or review-site work.
- [scripts/launch_tool.py](scripts/launch_tool.py) (standard library only): `timeline --date D --tier major|medium|minor [--today D]`, `partners --csv partners.csv` (columns as in [examples/partners.csv](examples/partners.csv), each 1-5), `tracker --csv tracker.csv` (exit 1 on issues; columns of [templates/directory-tracker.csv](templates/directory-tracker.csv)), `links --file page.html|--url U --domain D`.

## Steps

1. **Classify the request.** One release or product moment → steps 2-8. Directory work alone → step 6. If the request spans quarters, budget or the whole funnel → hand that part to the marketing-plan skill and keep only the launch here.
2. **Set goal and tier.** Tier by customer impact (launch.md §8): major = new product, big capability, pricing change, new segment; medium = meaningful feature or integration; minor = polish and fixes (changelog and digest only). Write one primary metric, a target and a kill or rethink trigger.
3. **Run the readiness gate** (simple, lovable, complete, plus operations). If any core property fails → narrow the claim or delay; never fill the gap with launch volume. If the claim depends on anything behind a flag → it is not launchable yet.
4. **Date it.** Run `timeline --date D --tier T`. If lead time is shorter than the tier plans for → compress: merge tasks, cut the launch-platform day or partner asks first, never the QA and support items. If a major launch falls outside Tue-Thu and uses a launch platform → move it.
5. **Choose channels** with the owned/rented/borrowed map: every launch needs at least one owned channel, one or two rented channels where the buyer already is, and one borrowed audience. If the audience is not on launch platforms (non-technical niche, regulated, local) → skip that day and put the effort into partners and owned channels.
6. **Plan directories** only after destination pages exist (directories.md rules 1-2). If readiness questions 1-7 have any "no" → build that first. Batch by tier; get human approval before every account or submission; verify each live link's `rel` with `links`; track with `tracker`.
7. **Plan borrowed reach.** List partner candidates from customer tool usage and audience overlap; score with `partners`; pursue ≥ 3.8 and reject on fit or brand below 3. For formats, pitch and agreement, use the marketing-plan skill (co-marketing).
8. **Produce assets, run the day, follow through.** Asset list with owners; site QA checks (T-, T0, T+); runbook with roles and hourly report; post-launch recap, roundup email, comparison pages, customer stories, review drive, retrospective at T+14 and launch-cohort review at T+30. For continuous shipping, run the shipped-work loop weekly (launch.md §9).

## Checkpoints

- After step 3: owner confirms readiness verdict and the launch claim.
- After step 4: dated timeline and channel owners approved before asset work starts.
- Before any directory account, form or submission: explicit human approval per batch.
- Before launch day: site QA "before" list passed and rollback owner named.

## Worked example

**Context** (fictional): proposal software for freelance designers and small studios; founder plus one marketer; newsletter 6,200 subscribers. Launching v2 (client approvals and payments). Today is 2026-10-08.
- **Tier and date**: major. `timeline --date 2026-11-17 --tier major --today 2026-10-08` warns only 40 of 56 planned days remain; the goal, positioning and readiness tasks (T-56 to T-42) are merged into one week, the beta stays live, everything from T-35 on runs as dated. Tuesday launch is kept.
- **Readiness**: "complete" failed for payments in two currencies → claim narrowed to approvals plus card payments; multi-currency becomes a medium launch in January.
- **Channels**: owned = newsletter, in-app, blog; rented = LinkedIn, one design community the founder is active in; borrowed = partners below; launch-platform day kept because beta users are active there.
- **Partners**: `partners --csv examples/partners.csv` → design-business newsletter 4.55 and invoicing app 4.27 pursue; portfolio builder 3.50 maybe; stock-photo marketplace rejected (fit 2).
- **Directories**: comparison and alternative pages built first; 38 listings in three weekly batches, each approved; `links` shows 9 followed, 29 nofollow/ugc.
- **Result at T+30**: 612 trials in 14 days vs. 400 target; launch-cohort trial-to-paid 9% vs. 12% normal (curiosity traffic, as expected); 11 reviews from 22 asks; two alternative pages ranking on page one.

## Pitfalls

- One-day launches with nothing before or after; launching to an audience that was never built.
- Delaying for "one more feature", or launching something that fails simple/lovable/complete.
- Announcing features still behind flags; screenshots that do not match the product; leaving pricing and comparison pages stale.
- Fifteen shallow channels instead of four deep ones; no owned channel capturing the spike.
- Asking for votes, messaging strangers, or posting promos into communities you never joined.
- Directory blasts before destination pages exist; identical descriptions; paid bulk submissions; review listings with no reviews; checking link status from response headers instead of the HTML.
- Partner campaigns without written commitments or consent for shared leads.

## Related skills

marketing-plan (12-month plan, budget, ideas, co-marketing), marketing-copy (launch page, announcement and listing copy), email-sequences (pre-launch, launch, onboarding and roundup emails), content-strategy (post-launch content, social cadence), seo-optimization (site migrations, technical go-live checks), ai-search-optimization (entity profiles), paid-ads (paid launch support), conversion-optimization (launch landing page), pricing-and-offers (launch pricing, early-access offers), analytics-and-experiments (launch tracking, cohort comparison).

## Done when

- [ ] Goal, metric, target and kill trigger written; tier chosen.
- [ ] Readiness gate run and the launch claim limited to what is live and complete.
- [ ] Timeline dated from the launch day, with owners for every channel and asset.
- [ ] Owned, rented and borrowed channels each covered or explicitly skipped with a reason.
- [ ] Site QA, launch-day roles and post-launch follow-ups (T+14 retro, T+30 cohort review) scheduled.
- [ ] Directory work (if in scope) has destination pages, per-tier copy, approvals and a tracker that passes `tracker`.
- [ ] Every number either sourced, computed with `launch_tool.py`, or marked TBD.
