# Cold sequence: {campaign name}

**Segment / tier:** {e.g., agencies 10-80 staff, Tier 2}
**Signal:** {signal + freshness window}
**Offer (low-friction next step):** {teardown, benchmark, pilot}
**Proof:** {customer + metric + timeframe}
**Sender / domain:** {mailbox}, warmed since {date}
**Volume:** {contacts/week}; capacity check: {outreach.py capacity output}

## Personalization fields

| Field | Source | Fallback if missing |
|---|---|---|
| {hook} | {job post URL / page} | Segment line |

## Emails

### Email 1 · day 0
Subject: {2-4 lowercase words}
Body ({25-75} words):
{observation tied to the problem}
{problem it usually causes}
{one proof line}
{interest question}

{opt-out line}
{signature + postal address}
Lint: {outreach.py lint result}

### Email 2 · day 3 · new angle: {tip / insight}
### Email 3 · day 7-8 · {case study}
### Email 4 · day 14 · {direct offer}
### Email 5 · day 21-28 · breakup (1-2-3 reply options)

## Stop rules
- Reply on any channel → stop all; opt-out → suppress everywhere.
- Pause at bounce > 2%, complaints near 0.1%, placement < 70%, reply < 1% after 300 sends.

## Results
| Sent | Replies | Positive | Meetings | Opps | Notes |
|---|---|---|---|---|---|
