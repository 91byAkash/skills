# 3P update (Progress, Plans, Problems)

A weekly pulse for executives and neighbouring teams who know a little about your work, but not much. It should take 30-60 seconds to read. Check it with `comms_check.py --type 3p`.

## Format (strict: nothing else, no bullets, no extra headings)

```
<emoji> <Team name> (<dates covered>)
Progress: <1-3 sentences>
Plans: <1-3 sentences>
Problems: <1-3 sentences>
```

- **Emoji**: one that fits the team or the week's mood (a rocket for a launch week, a construction sign for a migration). Use the `:shortcode:` form in Slack and the real character in email.
- **Team name**: confirm it with the user. Don't guess from the channel name.
- **Dates**: write them out, e.g. `(Oct 2-8)`. Progress and Problems cover the last 7 days; Plans cover the next 7.
- **Progress**: what shipped, which milestones you hit, numbers moved. Outcomes, not activity.
- **Plans**: the 1-3 things that matter most next week, with dates where they exist.
- **Problems**: what is slowing the team down (people, blockers, a lost deal, a bug). Name the help you need and from whom. If nothing is wrong, write `None this week.` Don't drop the line.

## Granularity scales with team size

| Team covered | Progress reads like |
|---|---|
| Squad (5 people) | "Shipped CSV export to 100% of users; 212 exports on day one." |
| Department (60) | "Mobile and web both hit the Q4 crash-rate target (<0.3%)." |
| Whole company | "Closed 10 new enterprise deals ($2.1M ARR); hired 20 people." |

## Filled example

```
:building_construction: Platform (Oct 2-8)
Progress: Moved 31 of 40 services to the new cluster; p95 deploy time fell from 14 to 6 minutes.
Plans: Move the last 9 services, including billing, by Fri 16 Oct; start the load test on the shared Postgres.
Problems: The billing cutover needs a 30-minute write freeze, and finance hasn't picked a window yet (asked Priya Rao, needed by 13 Oct).
```
