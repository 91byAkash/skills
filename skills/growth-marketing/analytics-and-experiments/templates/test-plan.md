# Experiment: [short name]

| Surface (page / flow) | Owner | ID in testing tool | Runs from | Ends on (fixed now, not later) |
|---|---|---|---|---|
| | | | | |

## 1. What we will do with the result
Agree these before anything ships; nobody re-argues them once data arrives.

| If the data shows… | We will… |
|---|---|
| Primary metric up with significance, no guardrail significantly worse | roll the change out to everyone |
| Primary metric down with significance | keep the current version and record what we learned |
| No significant difference | [ship the simpler version if the interval rules out harm / keep the current version / design a bolder follow-up] |
| A guardrail clearly harmed, or the split is broken (SRM p < 0.001) | stop early; these are the only reasons to stop early |

## 2. The bet
- **What we saw:** [observation, and where it came from: analytics, session recordings, research]
- **The change:** [exactly one change]
- **Who sees it:** [audience or traffic segment]
- **Expected effect:** [primary metric] moves [up / down] by at least [MDE]
- **Proof we will accept:** [metric definition] crosses [threshold] at 95% confidence

## 3. Arms
| Arm | What the visitor gets | Screenshot | Why it might win |
|---|---|---|---|
| Current (control) | | | n/a |
| Challenger | | | |

## 4. Mechanics
- Format: A/B, A/B/n or split URL
- Randomised on: user (logged-in ID or first-party cookie)
- Traffic split: 50/50, or the ramp schedule [ ]
- Who is eligible: [new visitors only? device? country?]
- Where the split happens: in the browser, on the server, or at the edge
- Cannot overlap with: [other running experiments]

## 5. What we measure
| Metric | Role (primary / secondary / guardrail) | How it is calculated (numerator ÷ denominator) | Current value |
|---|---|---|---|

A guardrail exists to stop the test if it gets significantly worse.

## 6. How long it runs
Paste the calculator output:
```
python3 scripts/abtest.py duration --baseline [ ] --mde [ ] --daily [ ] --exposed [ ] --variants [ ]
```
Visitors needed per arm: [ ] · whole weeks: [ ] · smallest segment we intend to read: [ ]

## 7. Before launch
- [ ] Someone other than the author has read sections 1 and 2.
- [ ] Each arm checked on phone and desktop in the main browsers.
- [ ] Primary and guardrail events confirmed firing in each arm.
- [ ] No visible flicker (anti-flicker snippet capped at 1 s if used).
- [ ] The analysis date is in the calendar, and stakeholders know there will be no early verdicts.
