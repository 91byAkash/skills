# Company newsletter

A weekly or monthly round-up that everyone in a large company (1000+ people) reads in Slack and email. About 20-25 bullets, each 1-2 sentences, written as "we", and linked heavily. Check it with `comms_check.py --type newsletter --channel slack` (or `email`).

## What goes in, and what stays out

| Include | Leave out |
|---|---|
| Company-wide announcements and leadership posts | Team-level detail (that belongs in a 3P) |
| Milestones: launches, big deals, funding, office openings | Things only a small group needs |
| Changes that affect most employees (benefits, tools, policy) | Repeats of something already sent to everyone, unless it's a reminder of a deadline |
| External recognition: press, awards, notable customer wins | Rumour, unannounced deals, anything confidential |
| Social: all-hands recap, events, new joiners at scale | Individual performance callouts without consent |

## Sections

Pick 3-6 clusters that cover the company evenly, for example:
- {Company announcements, Progress on priorities, Leadership updates, Social}
- {Product and engineering, Go to market, People, Finance}
- {External news, Internal news}

Use nested bullets under a priority (area → 2-3 sub-points) when one initiative has several updates.

## Skeleton

```
:newspaper: <Company> weekly: <dates>

:mega: Company announcements
- We <announcement> (<link to post>).
- ...

:dart: Progress on priorities
- <Priority 1>
    - We <milestone> (<link>).
    - ...
- <Priority 2>
    - ...

:classical_building: Leadership updates
- <Exec> shared <what> in <link to post/doc>: <one-line takeaway>.

:tada: Social
- ...

Questions or something we missed? Post in #<channel>.
```

## Writing rules
- Start each bullet with what happened: "We launched…", "We closed…", "Finance published…".
- Each bullet gets one link to the source of truth (the announcement post, the doc, the press article). A link replaces explanation; don't do both.
- Put numbers in bullets ("cut onboarding from 9 to 4 days"), not adjectives ("massively improved").
- Name people when you're crediting them, and name a team when credit is shared.
- In Slack, link as `<url|text>` in API payloads, or paste the URL in the composer. In email, use descriptive link text, never "click here".
