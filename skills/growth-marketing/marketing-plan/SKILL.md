---
name: marketing-plan
description: "Build a funded 90-day or 12-month marketing plan tied to the funnel stage that limits growth. Use when the user asks for a marketing, growth or go-to-market plan, \"how big is this market\", TAM/SAM/SOM, marketing ideas, a marketing budget, or co-marketing partners. Not for planning a single launch (use launch-plan) or an editorial calendar (use content-strategy)."
license: MIT
metadata:
  category: "growth-marketing"
  version: "3.0.0"
---

# Marketing Plan

A marketing plan is a sequenced portfolio of moves tied to the AARRR stage that limits growth, funded by real money and staffed by real people.

Scope: market-quality gate, intake, 17-area current-state scoring, AARRR and binding constraint, budget math, funding-stage tiers, 70/20/10 allocation, operating model, market sizing (TAM/SAM/SOM), idea selection, partnerships and co-marketing, measurement.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `scope` | required | ask | plan (90-day/12-month), sizing, ideas, co-marketing |
| `what` | required | ask | whole company; one product line |
| `audience` | required | from `.agents/product-marketing.md` | freelance designers and 2-10 person studios |
| `goal` | required | ask | +$240k new ARR in 12 months |
| `stage_and_funding` | required for plans | ask | $180k ARR, bootstrapped, no raise planned |
| `economics` | required for plans | ask; CAC = all acquisition cost ÷ new customers | ARPC $40/mo, blended CAC $320, annual retention 70% |
| `team_and_budget` | required | ask | founder + 1 marketer; $4.5k/month all-in |
| `channels_now` | optional | ask | newsletter 6,200 subs; blog; no paid |
| `constraints` | optional | none | no paid until profitable; brand avoids hype |

Read `.agents/product-marketing.md` first and ask only for what it does not answer. Mark unconfirmed numbers `[TBD: confirm]`.

## Output

Depending on `scope`, one or more of:
- **Marketing plan** ([templates/marketing-plan.md](templates/marketing-plan.md)): Parts A-H: leadership brief, one-page positioning, scored baseline, AARRR moves per stage, a 90-day timeline in 30-day blocks plus a quarterly year view with budget arithmetic and funding tiers, operating model with ownership matrix, ideas backlog with skip reasons, measurement and open decisions.
- **Market sizing**: TAM/SAM/SOM range from at least two methods, confidence, and a go / go narrow / test first / park call.
- **Idea shortlist**: 3-5 ideas, each with fit, first steps, success metric and resources, ranked by `ice`.
- **Co-marketing plan**: scored partner list, chosen format, pitch, agreement points ([templates/co-marketing-proposal.md](templates/co-marketing-proposal.md)).

## Supporting files

- [marketing-plan.md](marketing-plan.md): principles, market-quality gate, intake, 17-area scoring, AARRR and binding constraint, business-model variations, budget methods, funding tiers, growth shape and 70/20/10, team and agencies, measurement, drafting and verification. Read for plans.
- [market-sizing.md](market-sizing.md): market definition, TAM/SAM/SOM, four methods, triangulation, confidence, go/no-go score. Read when market size or a revenue ceiling is in question.
- [ideas.md](ideas.md): selection by stage, budget, time and goal; the idea library by category; stunts and direct mail. Read when asked for ideas or building an ideas backlog.
- [co-marketing.md](co-marketing.md): partnership types, finding and scoring partners, formats, pitch, agreement, measurement. Read when borrowing audiences.
- [scripts/plan_tool.py](scripts/plan_tool.py) (standard library only): `ice --csv ideas.csv [--budget N]`, `budget goal|revenue …`, `sizing …`, `partners --csv partners.csv`, `rubric --csv rubric.csv [--exempt …]`. CSV columns are the headers of the samples in [examples/ideas.csv](examples/ideas.csv), [examples/partners.csv](examples/partners.csv) and [examples/rubric.csv](examples/rubric.csv).

## Steps

1. **Classify the request.** Full plan → steps 2-6. Sizing only → step 3 sizing part. Ideas only → step 5. Partners only → co-marketing.md with `partners`. If the request is one release moment → use the launch-plan skill instead.
2. **Intake.** Read materials and connected data; ask the ten intake topics (marketing-plan.md) only where unanswered; list every gap as an open decision. If blended CAC is unknown → it is open decision #1.
3. **Score and diagnose.** Score the 17 areas with notes (`rubric`), read the shape, rate market quality (size × frequency) and size the market if in doubt (`sizing`). Pick the binding AARRR stage with the decision rules (marketing-plan.md §5).
4. **Fund it honestly.** Compute the budget with `budget goal` or `budget revenue`; add 10-20% experiments. If the goal needs more than ~40% of ARR or money not yet raised → lower the goal, improve CAC or retention, or label moves "post-round". Map moves to the current funding tier and show what the next tier unlocks.
5. **Select moves and ideas.** Generate candidates per stage from ideas.md; score with `ice`; fund in rank order; confidence ≤ 3 → small test with kill rule. Record skipped ideas with reasons. Allocate roughly 70/20/10 across current, next and experimental. Score partners with `partners` where moves borrow audiences.
6. **Write the plan and verify.** Draft the parts in order (positioning → baseline → funnel plan → timeline → operating model → ideas backlog → measurement → leadership brief last), review each with the owner, then run the verification pass (references real, tools connected or flagged, no internal paths, voice, all TBDs in open decisions, past work acknowledged).

## Checkpoints

- After step 3: owner agrees the binding stage before moves are chosen.
- After step 4: owner agrees the goal is funded (or accepts the reset) before moves are detailed.
- Before delivery: verification pass done; open decisions ranked.

## Worked example

**Context** (fictional): proposal software for freelance designers and small studios; $180k ARR, ARPC $40/month, blended CAC $320, annual retention 70%, bootstrapped; founder plus one marketer; newsletter 6,200 subscribers. Wants a 12-month plan with "+$240k new ARR". A v2 launch in November is planned with the launch-plan skill and appears in the plan as one move.
- **Budget**: `budget goal --new-arr 240000 --arr 180000 --arpc 40 --cac 320 --retention 0.7` → 500 customers, $263k with a 15% experimental layer, 146% of ARR → flagged unfunded. Reset with `budget revenue --arr 180000 --pct 0.3 --arpc 40 --cac 240 --retention 0.7`: $54k/year, 225 customers, +$75.6k net new ARR, year-end ~$256k, payback 7.5 months; the $240 CAC target depends on partner, template and directory channels (open decision #1: measure CAC by channel in Q1).
- **Sizing**: `sizing --buyers 40000 --spend 480 --capture 0.01 0.02 --channel partners:8 --channel directories-seo:10 --channel outbound:6` → SAM $19.2M, SOM $192k-384k, channel-led $138k; 2.1× gap = reach constraint, not demand. The +$75.6k goal sits inside channel-led reach.
- **Current state**: `rubric --csv examples/rubric.csv` → 27/80 across 16 scored areas; strongest positioning and messaging; weakest competitor comparison (0), conversion pages (1), email lifecycle (1); paid and international low but stage-appropriate → binding constraint is acquisition destination pages plus activation lifecycle.
- **Ideas**: `ice --csv examples/ideas.csv --budget 6000` funds annual-plan default, newsletter swaps, a 40-template gallery, a pricing calculator, the launch-platform day, an integration launch and referral credit ($5.1k); import tool and paid retargeting wait; the mailed sketchbook kit (confidence 3) becomes a 10-studio test.
- **Partners**: `partners --csv examples/partners.csv` → design-business newsletter 4.55 and invoicing app 4.27 pursue; portfolio builder 3.50 maybe; co-working chain rejected (brand), stock-photo marketplace rejected (fit 2).

## Pitfalls

- Plans that list tactics without sequence, owners or funding.
- Paid spend before money exists; promising exponential growth; hiding unknown CAC or bad churn.
- One impressive TAM figure instead of a range from two methods.
- Fifteen shallow ideas instead of 3-5 deep ones; no skip list, so rejected ideas come back every quarter.
- Partner campaigns without written commitments or consent for shared leads (GDPR, India's DPDP Act 2023 and similar laws need a lawful basis to pass leads between companies).

## Related skills

launch-plan (single launches, directories, site go-live), customer-research (positioning inputs), content-strategy (editorial calendar), paid-ads (paid channel builds once funded), pricing-and-offers (ARPC and packaging levers), retention-and-referrals (retention, referral and affiliate mechanics), sales-outreach (partner-facing collateral, outbound), analytics-and-experiments (KPI targets, measurement plan).

## Done when

- [ ] Scope classified; goal and primary metric written.
- [ ] 17-area score with notes, market-quality quadrant and binding AARRR stage stated.
- [ ] Budget arithmetic shown with `plan_tool.py`, funding check passed or goal reset.
- [ ] 90-day timeline in 30-day blocks with owners, plus a quarterly year view.
- [ ] Ideas backlog with ICE scores and skip reasons; 70/20/10 split shown.
- [ ] Measurement plan and ranked open decisions; every number sourced, computed or marked TBD.
