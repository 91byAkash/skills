# Status report (project or weekly)

For stakeholders who need to know whether something is on track and whether they have to act. Check it with `comms_check.py --type status`.

```
Status: On track | At risk | Off track: <one-line reason>
Target: <milestone> by <absolute date> (was <old date> if it moved)

Progress
- <outcome with number>
- <outcome>

Next
- <what, who, by when>

Risks and blockers
- <risk>: impact <what slips, by how much>; help needed <from whom, by when>

Metrics
| Metric | Now | Target | Last week |
|---|---|---|---|
```

Rules:
- Choose the status honestly. "At risk" means the date slips unless something changes, and the earlier you say it, the cheaper it is to fix.
- If the status changed since the last report, say why on the status line.
- Every risk says what it would cost and what help would remove it. If no help is needed, say "watching; no action needed".
- Keep the same structure every week so readers can diff updates by eye.
