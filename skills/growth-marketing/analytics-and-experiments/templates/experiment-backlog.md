# Experiment Backlog and Playbook

## Hypothesis sources (refill monthly)
Analytics drop-offs · session recordings/heatmaps · support tickets and sales call notes · customer interviews/surveys · competitor patterns · losers and inconclusives from past tests.

## Backlog (ICE: each 1-10, score = average)
| ID | Surface | Observation (evidence) | Hypothesis | Primary metric | I | C | E | ICE | Est. weeks (from calculator) | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| H01 | Pricing | 38% toggle billing then exit | Default annual, show monthly beside it | trial start rate | 7 | 6 | 8 | 7.0 | 3 | queued |

Scoring guide: **Impact**: share of revenue flowing through the surface × plausible lift. **Confidence**: 8+ only with direct evidence (data, research, prior win elsewhere). **Ease**: 8+ if shippable in under 2 days without engineering review.

Alternative weighted scorecard when stakeholders want risk explicit (score 1-5): impact 30%, confidence 25%, ease 20%, risk if wrong 15% (5 = low risk), strategic fit 10%.

## Program health (review monthly)
| Metric | Target | This month |
|---|---|---|
| Tests launched | 4-8 | |
| Win rate | 20-30% | |
| Median duration | 2-4 weeks | |
| Backlog depth | 20+ | |
| Cumulative shipped lift on key metric | — | |

Cadence: weekly 30-min health check (breakage, SRM, guardrails only) · biweekly readouts and launches · monthly velocity review and re-score · quarterly playbook audit (which winning patterns are not yet rolled out elsewhere? which funnel stages are untested?).

## Results log
| ID | Name | Surface | Dates | Primary | Result | Lift (CI) | Link |
|---|---|---|---|---|---|---|---|

## Playbook entry (one per concluded test)
```
### [Test name]  ·  [date]
Hypothesis: …
Sample: [n]/arm  ·  Result: win/loss/inconclusive, [metric] [+x%] (95% CI [a, b]), p = [ ]
Guardrails: …  ·  Segment notes: …
Why: …
Pattern: [reusable rule, e.g. "proof next to the pricing CTA lifts plan selection"]
Apply to: …  ·  Status: implemented / parked / follow-up
```
