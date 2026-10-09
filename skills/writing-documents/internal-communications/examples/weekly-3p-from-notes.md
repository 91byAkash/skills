# Example: a weekly 3P from raw notes

**Request.** "Write our 3P for this week. Notes below." The user is on the Platform team. Today is Thu 8 Oct 2026.

**Notes as given**
```
- migration going well, 31/40 services moved
- deploys way faster now (14min -> 6min p95)
- still need billing + 8 others
- finance hasn't given us a freeze window for billing, blocking
- Priya said she'd confirm
- also fixed a bunch of flaky tests, ~40
- want to start load testing pg next
```

**1. Scope.** The team name is in the request context ("Platform"). Confirm the period:

```
$ python3 scripts/comms_window.py --end 2026-10-08
Progress/Problems window: 2026-10-02 .. 2026-10-08
Plans window:             2026-10-09 .. 2026-10-15
Header label:             (Oct 2-8)
```

**2. First draft (too literal):**
```
Platform team update
Progress: We worked on the migration. Made progress on the API. Fixed bugs. Shipped stuff.
Problems: Need help from someone.
Plans: Finish migration next week.
```

```
$ python3 scripts/comms_check.py draft.md --type 3p
draft.md:2: WARN vague 'worked on' describes activity; state the outcome or number
draft.md:2: WARN vague 'Made progress' describes activity; state the outcome or number
draft.md:3: WARN ask request without a named owner or a date
draft.md:4: WARN relative-date 'next week' without an absolute date; add one (e.g. 'Fri 16 Oct')
draft.md:1: ERROR 3p-header first line must be '<emoji> <Team name> (<dates covered>)'
draft.md:2: ERROR 3p-length Progress has 4 sentences; 1-3 allowed
draft.md:2: WARN 3p-data Progress has no number; add a metric where one exists
draft.md: ERROR 3p-format sections must be Progress, Plans, Problems in that order (found ['Progress', 'Problems', 'Plans'])
28 words, ~7s read; 3 error(s), 5 warning(s)
```

**3. Fix it.** Add the header with an emoji and dates. Put outcomes with numbers in Progress, and keep the two most meaningful items (the 40 flaky tests are team-internal, so drop them). Give Plans an absolute date. Have Problems name the blocker, the person and the date it's needed by. Ask the user for the date; they say "by the 13th".

```
:building_construction: Platform (Oct 2-8)
Progress: Moved 31 of 40 services to the new cluster; p95 deploy time fell from 14 to 6 minutes.
Plans: Move the last 9 services, including billing, by Fri 16 Oct; start the load test on the shared Postgres.
Problems: The billing cutover needs a 30-minute write freeze, and finance hasn't picked a window yet (asked Priya Rao, needed by 13 Oct).
```

```
$ python3 scripts/comms_check.py final.md --type 3p --channel slack
66 words, ~17s read; 0 error(s), 0 warning(s)
```

**4. Hand-off.** Show the final text to the user to post. It goes out under their name, so don't post it yourself. Mention one judgement call: the flaky-test fix was left out as too granular, and it can go back in if they want it.
