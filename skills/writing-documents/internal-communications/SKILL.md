---
name: internal-communications
description: "Write internal updates in a fixed format: 3P weekly updates, newsletters, FAQ round-ups, status reports, leadership updates, incident write-ups, announcements. Use when asked to \"write our 3P\", \"draft the newsletter\", \"write a status report\", \"write up the incident\" or \"announce this change\". Not for long docs (use cowrite-document) or customer-facing copy (use marketing-copy)."
license: MIT
metadata:
  category: "writing-documents"
  version: "3.0.0"
---

# Internal communications

Every internal message answers three things fast: what happened or is changing, what it means for the reader, and what (if anything) they must do by when. Each type has a fixed shape in `templates/`. Pick the type, gather facts for the right time window, fill the shape, and run the checker.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `type` | yes (inferred or asked) | - | `3p`, `newsletter`, `faq`, `status`, `leadership`, `incident`, `announcement`, `general` |
| `team_or_scope` | yes for 3p/status | - | "Platform team", "whole company" |
| `period` | for periodic types | the last 7 days, ending today | `--end 2026-10-08 --days 7` |
| `audience` | yes | from the type | "execs", "all employees", "payments + support" |
| `channel` | optional | `doc` | `slack`, `email`, `doc` |
| `sources` | optional | connected tools, else the user's notes | notes, thread links, docs, dashboards |
| `house_format` | optional | `templates/<type>.md` | last week's update, the team's template |
| `sender` | optional | the user | "sent as me to #eng-all" |

## Output

The message text, ready to paste: in the template shape, for the stated channel, with every number, date and owner sourced. `comms_check.py` reports 0 errors. List any open questions or judgement calls (what you left out, unconfirmed facts) below the draft. It's a draft for the user to send; never post it yourself.

## Supporting files

- [templates/](templates/). Read the one for your type before drafting:
  - `3p-update.md`: the strict four-line format, plus granularity by team size;
  - `newsletter.md`: what's in and out, section clusters, skeleton;
  - `faq.md`: picking questions, answer rules, the "needs an official answer" list;
  - `status-report.md`, `leadership-update.md`, `incident-report.md` (blameless, timeline, action table), `announcement.md` (six questions), and `general.md` for anything else.
- [REFERENCE.md](REFERENCE.md):
  - §1 gathering sources (windows, signal per source, ranking, confidentiality);
  - §2 audience to shape and tone;
  - §3 Slack, email and doc formatting;
  - §4 sentence rules;
  - §5 bad news, incidents and org changes;
  - §6 review and sending;
  - §7 every checker code.
- [scripts/](scripts/):
  - `comms_window.py --end <date> [--days 7]` prints the look-back and look-ahead windows, the header label `(Oct 2-8)`, and mail/chat search filters.
  - `comms_check.py draft.md --type <type> [--channel slack|email|doc] [--json]` runs the format and quality checks; exit 1 on any ERROR.
- [examples/weekly-3p-from-notes.md](examples/weekly-3p-from-notes.md): messy notes → failing draft → passing 3P, with real checker output.

## Steps

1. **Identify the type.** Map the request onto one template:
   - weekly team pulse → `3p`;
   - company round-up → `newsletter`;
   - "what is everyone asking" → `faq`;
   - project health → `status`;
   - for execs → `leadership`;
   - outage write-up → `incident`;
   - change, launch or policy → `announcement`;
   - anything else → `general`.
   If two types fit, ask which one. If the user has a house format (last week's update, a team template), follow it over the template.
2. **Pin the scope.**
   - 3P or status: confirm the team name. Ask if it isn't stated; don't guess from the channel.
   - Periodic types: run `comms_window.py --end <today>` to get the windows and the header label.
   - `general`: ask about audience, purpose, tone and format constraints (templates/general.md).
3. **Gather facts** (REFERENCE §1).
   - If chat, mail, calendar, docs or trackers are connected, search the look-back window for high-signal items: big channels, many reactions or replies, exec posts, non-recurring big meetings, much-viewed docs. Search ahead for Plans.
   - If nothing is connected, ask for notes and mention that access would improve the result.
   - If the user pasted the facts, skip the search and format them.
   - Keep each fact with its source link.
4. **Filter and rank.** Keep items by reach, then novelty, then evidence. Cut granular team detail from company-level messages. Drop confidential or unannounced items unless the user explicitly OKs them. If a required section has nothing (no Problems), ask; don't invent one.
5. **Draft in the template shape.**
   - Put the bottom line first.
   - Prefer outcomes with numbers over activity.
   - Use absolute dates, and give a zone with any time.
   - Name an owner for every ask or action.
   - Use the channel's formatting (REFERENCE §3), e.g. single `*bold*` in Slack.
6. **Handle sensitive content.** Bad news goes in the first lines, with size, cause and plan. Incidents are blameless. Org changes: check that the affected people were told first. Comp, legal, layoffs and M&A need an official voice, so flag them rather than answer (REFERENCE §5).
7. **Check.** Run `comms_check.py draft.md --type <type> --channel <channel>`.
   - Fix every ERROR.
   - For each WARN, either fix it or keep it on purpose. A relative date in a quote is fine; an ask with no owner is not.
   - If the read time is over budget, cut detail into links or a thread reply. Don't shrink the font of the facts.
8. **Verify.** Check each number, date and name against its source, and check that links open for the whole audience. If a fact can't be verified, mark it for the user rather than guessing.
9. **Hand off.** Present the final text, the intended channel and recipients, and the judgement calls. If the user wants it sent, they send it, or they explicitly approve a send through the proper tool. For recurring updates, keep this period's copy beside last period's.

## Checkpoints

- After step 2: the type, team, window and audience are settled. Don't draft a 3P without a team name.
- After step 4: every kept item has a source, and nothing confidential crosses audiences.
- After step 7: `comms_check.py` reports 0 errors, and the remaining WARNs are deliberate.
- Before hand-off: the bottom line is in the first line, or the subject for email.

## Worked example

The Platform team's notes say "31/40 services moved, deploys 14→6 min, billing blocked on finance freeze window, Priya to confirm, 40 flaky tests fixed, load test pg next". `comms_window.py --end 2026-10-08` gives `(Oct 2-8)`. A literal first draft fails with 3 errors: no emoji/team/date header, 4 sentences in Progress, and sections out of order. It also gets 5 warnings: vague "worked on", a relative "next week", an ask with no owner, and more. The rewrite keeps two outcomes with numbers, drops the team-internal flaky-test item, dates the plan "by Fri 16 Oct", and names the blocker owner and deadline:

```
:building_construction: Platform (Oct 2-8)
Progress: Moved 31 of 40 services to the new cluster; p95 deploy time fell from 14 to 6 minutes.
Plans: Move the last 9 services, including billing, by Fri 16 Oct; start the load test on the shared Postgres.
Problems: The billing cutover needs a 30-minute write freeze, and finance hasn't picked a window yet (asked Priya Rao, needed by 13 Oct).
```

The checker reports `66 words, ~17s read; 0 error(s), 0 warning(s)`. The full walkthrough is in [examples/weekly-3p-from-notes.md](examples/weekly-3p-from-notes.md).

## Pitfalls

- **Activity instead of outcomes.** "Worked on the migration" tells a reader nothing; "31 of 40 services moved" does.
- **Burying the ask or the bad news** under good news or context. Execs stop reading after two lines.
- **Relative dates and zoneless times.** "Next Friday" and "at 4" mean different things to different readers and in different weeks.
- **Asks without owners.** "We need a decision" goes nowhere. Name the person and the date.
- **Breaking the 3P format**: adding bullets, headings, a fourth section, or dropping Problems when there are none. Write "None this week."
- **Too granular for the audience.** Team chores in a company newsletter, or ticket IDs in a leadership update.
- **Leaking across audiences.** Private-channel content or unannounced deals in a broad post.
- **Guessing in an FAQ.** Say it's unconfirmed and when an answer is expected. Route comp, legal and org questions to their owner.
- **Blame in incident reports.** Name the system gap, not the person.
- **Slack formatting from Markdown habits.** `**bold**` shows literally, and long paragraphs don't get read.
- **Posting on the user's behalf** without approval.

## Done when

- [ ] The type is chosen, and the house format is used if one exists.
- [ ] The team name, period (via `comms_window.py` for periodic types) and audience are confirmed.
- [ ] Every item is sourced, numbers have a comparison, dates are absolute, and asks and actions have owners and dates.
- [ ] Sensitive items are handled: bad news up front, blameless, nothing confidential crossing audiences, official-voice items flagged.
- [ ] `comms_check.py --type <type> --channel <channel>` exits 0, and the remaining WARNs were reviewed.
- [ ] The read time is within budget (3P ≤ 60 s).
- [ ] The draft, recipients and judgement calls have gone to the user, and nothing was sent without their approval.

Related skills: cowrite-document (long docs behind an announcement, such as decision docs and design docs), long-form-writing (prose polish and style lint), system-diagrams (a diagram for an incident or architecture change), excel-spreadsheets (metrics tables behind a status report), powerpoint-decks (turning a leadership update into slides), word-documents and pdf-files (formal memos).
