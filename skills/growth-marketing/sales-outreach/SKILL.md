---
name: sales-outreach
description: "Run outbound and support sales: prospect lists, cold email sequences, deliverability, reply handling, sales collateral and RevOps. Use when the user asks to build a lead list, write cold emails or a cadence, set up outbound, handle objections, make a battle card or deck, or fix lead scoring or routing. Not for opt-in lifecycle email (use email-sequences)."
license: MIT
metadata:
  category: "growth-marketing"
  version: "3.0.0"
---

# Sales Outreach

Relevance beats volume: a short, specific message to the right person at the right moment outperforms a clever template sent to thousands. Outbound only works on top of clean targeting, a healthy sending setup, and fast, honest follow-through.

Scope: list building by motion (SaaS, non-SaaS B2B, local SMB, first customers), account research, cold email and follow-ups, deliverability and stop-loss rules, multichannel cadences, reply handling, enablement (deck, one-pager, objection library, battle cards, call scripts, ROI case, proposals, win-loss) and RevOps (lifecycle stages, MQL, lead scoring, routing, speed-to-lead, pipeline, data hygiene).

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `mode` | required | inferred | `prospect-list`, `cold-sequence`, `cadence`, `reply-handling`, `enablement-asset`, `revops` |
| `branch` | for lists | inferred | `saas`, `b2b`, `local-smb`, `demand-signal` (first customers) |
| `icp` | required | from context file | agencies 10-80 staff in UK/US with a finance hire |
| `offer` | required | ask | 15-minute teardown of their month-end process; pilot |
| `proof` | required | ask | Northgate Studio: close 5 → 2 days |
| `signals` | optional | infer | hiring finance ops, new CFO, pricing-page visits |
| `target_count` | optional | 25 (SMB 15) | 100 accounts |
| `tools` | optional | browser + public sources | CRM, licensed data provider, sending tool |
| `asset_type` | for enablement | ask | deck, one-pager, battle card (competitor name), objection doc, demo script |
| `gtm_motion` | for revops | ask | product-led, sales-led, hybrid; ACV; cycle length |
| `constraints` | optional | none | EU recipients, no LinkedIn automation |

Read `.agents/product-marketing.md` first (ICP, pains, proof, competitors).

## Output

- **prospect-list**: ICP statement + pass/fail checklist; lead table or CSV (score, company, contact, signal, why, sources, confidence, verified date); top 3-5 outreach targets with one-line reasons. Demand-signal branch: evidence report with quotes and links instead.
- **cold-sequence**: 3-5 emails (subject, body, CTA, day), personalization fields with sources, opt-out line, and lint results ([templates/cold-sequence.md](templates/cold-sequence.md)).
- **cadence**: day-by-day multichannel plan by tier with stop rules.
- **reply-handling**: classified replies with drafted responses and actions.
- **enablement-asset**: the asset in its standard structure (enablement.md), every claim with a source.
- **revops**: lifecycle definitions, scoring model, routing rules, SLAs, pipeline stages, deal desk tiers, automation list.

## Supporting files

- [prospecting.md](prospecting.md): branches, ICP, five phases, signals ranked with freshness windows, signal → play, tiers, account research rules, demand-signal and local SMB branches, compliance. Read for lists and research.
- [cold-email.md](cold-email.md): principles, frameworks, personalization levels, subject lines, follow-ups and breakups, deliverability setup and stop-loss, benchmarks and funnel math, multichannel cadence, LinkedIn, calls, reply handling and booking. Read for any outreach.
- [enablement.md](enablement.md): deck, one-pager, objection library, live objections, battle cards, win-loss, ROI, discovery/demo/call scripts, case study briefs, proposals, playbooks, persona cards. Read for collateral.
- [revops.md](revops.md): lifecycle stages, MQL and SLAs, scoring models with points, routing, speed-to-lead, pipeline stages and metrics, automations, deal desk, data hygiene. Read for revops.
- [scripts/outreach.py](scripts/outreach.py): `lint` (cold email checks), `score` (points-based lead grading), `capacity` (mailboxes/domains for a volume), `funnel` (contacts needed for meetings or deals). `python3 scripts/outreach.py lint draft.txt --touch 1`.
- Templates: [cold-sequence](templates/cold-sequence.md), [account-brief](templates/account-brief.md), [battle-card](templates/battle-card.md).

## Steps

1. **Pick the mode and branch.** Selling to software/digital companies → SaaS; other businesses → B2B; local shops/clinics/services → local SMB; looking for first customers or design partners → demand-signal (start from the problem, not firmographics). Hybrid → dominant branch plus the other's signals.
2. **Define the ICP** as one paragraph plus pass/fail criteria: firmographics, technographics (SaaS), buying signal (why now), decision-maker profile, disqualifiers. Don't source before this exists.
3. **Source 2-3× the target** from 2-3 cross-checked sources; public business contacts and licensed data only; no scraping of platforms that forbid it, no CAPTCHA/login bypass, no sensitive-trait targeting (prospecting.md §8). Record source URL and date for every contact.
4. **Qualify with evidence**: each criterion backed by a source; confidence High (2+ independent sources or official page) / Medium / Low; verify email deliverability before use (and again if the list sits > 7 days). Score Hot/Warm/Cold/Skip (`outreach.py score`); assign tiers (Tier 1 = top 25-50 accounts 1:1; Tier 2 = segments of 20-200 sharing a pain; Tier 3 = 1:many).
5. **Research by tier**: Tier 1 brief (10-20 min) from job posts, their pages, leaders' public statements, news, reviews; Tier 2 one sourced hook per contact + segment brief; Tier 3 segment brief only. Facts first with source and date, then the angle; "no hook found" falls back to the segment message.
6. **Check sending setup** before any copy goes out: secondary domains, SPF/DKIM/DMARC, 2-3 mailboxes per domain, 3-4 weeks warmup, list verified, tracking off, opt-out line + postal address (cold-email.md §6). Size it with `outreach.py capacity`.
7. **Write the sequence**: first email 25-75 words, peer tone, their world first, personalization that leads into the problem, one proof point, one low-friction interest question ("Worth a look?"), no link, no meeting ask. Subject 2-4 lowercase internal-looking words. Follow-ups (3-5 total, days 3, 7-8, 14, 21-28) each add a new angle, proof or resource and stand alone; end with an honored breakup. Run `outreach.py lint` on each.
8. **Cadence** (Tier 1-2): weave email, LinkedIn, calls and short video; a reply on any channel stops all channels; an opt-out anywhere is an opt-out everywhere; one sender per account.
9. **Handle replies within minutes**: classify (positive, info request, objection, not now, referral, wrong person, out of office, unsubscribe/hostile, bounce); propose two times + a link; confirm the day before with something useful. Agents may auto-handle OOO, unsubscribes, bounces and not-now reminders; humans send positive, objection and referral replies until accuracy is proven.
10. **Enablement assets** (enablement.md): pick the structure; tailor by buyer (technical, economic, champion); every claim defensible with a source; battle cards need a named competitor, last-verified date, and "when to walk away".
11. **RevOps** (revops.md): define lifecycle stages with entry/exit/owner, MQL = fit + engagement, SLA (contact within 4 business hours, ideally minutes for demo requests; qualify within 48h), routing, pipeline stage exit criteria, deal desk approvals; recalibrate scoring quarterly against closed-won.
12. **Measure**: reply rate, positive reply rate, meetings per 100 contacts, opportunities, win rate by source and signal; stop campaigns per stop-loss rules (bounce > 2%, complaints near 0.1%, reply < ~1% after 300+ sends).

## Checkpoints

- After step 2: ICP and disqualifiers approved.
- After step 4: sample of 10 qualified leads reviewed before scaling the list.
- Before first send: deliverability checklist passed; sequence linted; opt-out present. Sending itself is the user's action.
- Weekly: stop-loss metrics reviewed; signals refreshed (freshness windows).

## Worked example

**Context**: expense tool selling to agencies (10-80 staff); offer: free 15-minute teardown of their month-end process; proof: studio cut close from 5 to 2 days.
- ICP: agencies 10-80 staff, UK/US, first or second finance hire in the last 90 days or open finance-ops role; disqualifiers: already on a spend-management platform with cards (from job post tech mentions), < 10 staff.
- Sourcing: job boards for "finance operations" roles at agencies + company pages; 140 candidates → 61 qualified (High 34, Medium 27); 18 Hot (open finance-ops role + VP/Head of Finance reachable + verified email).
- Capacity: 60 new contacts/week × 4 touches ≈ 48 emails/day → 2 mailboxes at 25/day; 1 domain plus a spare, warmed 4 weeks.
- Email 1 (56 words): subject "finance ops hire"; opens with the open role; names the month-end receipt chase that hire usually inherits; proof line; "Worth a look before they start?"; opt-out line. Lint: ok.
- Follow-ups: day 3 two-line policy tip; day 8 case study; day 14 offer the teardown; day 24 breakup with 1-2-3 reply options.
- Results after 6 weeks (240 contacts): 7.9% reply, 9 positive, 7 meetings, 2 opportunities. Funnel check: `outreach.py funnel --reply 0.079 --positive 0.47 --meeting 0.78` → ~35 contacts per meeting, versus ~120 on the earlier static list.

## Pitfalls

- Sourcing before defining the ICP; huge unverified lists; bounce rates above 2%.
- Fake personalization ("loved your post") or personalization unrelated to the problem.
- Long, self-focused emails; feature dumps; asking for 30 minutes in the first touch; links and tracking pixels in cold mail.
- "Just checking in" follow-ups; ignoring a breakup you sent; touching people on another channel after they replied or opted out.
- Sending from the primary domain; skipping warmup; buying resold mailboxes or broker lists without provenance.
- Scraping platforms against their terms; targeting sensitive traits; no lawful basis records for EU/UK contacts.
- Collateral with claims reps can't defend; battle cards that are stale or trash competitors.
- Scoring that rewards content downloads over buying intent; no negative scoring; MQLs with no SLA.

## Related skills

customer-research (ICP, pains, competitor profiles), email-sequences (opt-in nurture after a reply), marketing-copy (copy quality), pricing-and-offers (offers, deal desk discounts), content-strategy (LinkedIn presence), analytics-and-experiments (attribution, tests), launch-plan (outbound as a launch channel).

## Done when

- [ ] ICP paragraph + pass/fail checklist exist; every lead has source URLs, confidence and verified date.
- [ ] Leads scored and tiered; top targets explained.
- [ ] Deliverability checklist passed and capacity sized before sending.
- [ ] Every email linted; one ask; opt-out line; follow-ups add new value; breakup honored.
- [ ] Cadence stop rules and reply classification defined.
- [ ] Enablement/revops deliverables follow their structures with sources, owners and SLAs.
