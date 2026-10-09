# Incident report (internal summary)

Blameless: describe what the system allowed, not who slipped. Use one zone for every timestamp, and give it. Check it with `comms_check.py --type incident`.

```
# <Incident title>: <date> (SEV<n>)

Summary
<2-3 sentences: what broke, who was affected, for how long, whether it's resolved.>

## Impact
- Who/what: <customers, regions, internal teams>
- Duration: <start-end, zone> (<minutes>)
- Scale: <requests failed, orders delayed, revenue at risk, SLA breach yes/no>

## Timeline (<zone>)
| Time | Event |
|---|---|
| 14:02 | Alert: checkout error rate 12% |
| 14:09 | Incident declared; <role> incident commander |
| ... | ... |
| 15:20 | Fully recovered |

## Root cause
<the technical and process causes, five-whys deep; contributing factors>

## Resolution
<what stopped the bleeding, and what restored full service>

## What went well / what was hard
- ...

## Action items
| Action | Owner | Due | Ticket |
|---|---|---|---|
| Add a canary stage for config pushes | Ravi Menon | 2026-10-20 | OPS-412 |
```

Rules:
- Before publishing, verify impact numbers against dashboards or logs, not memory.
- Every action item has a named owner and a date. "Team: improve monitoring" is not an action item.
- Customer-facing wording is a separate message. This one can name internal systems.
- Send a short "investigating / mitigated / resolved" update during the incident. Write this full report afterwards (usually within 5 business days).
