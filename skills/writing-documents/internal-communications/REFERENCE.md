# Internal comms reference

Read section 1 before gathering material for a periodic update (3P, newsletter, FAQ). Read section 3 when the channel is Slack or email. Read section 5 for bad news, incidents, or org changes.

## 1. Gathering source material

Use whatever the user has connected: chat, mail, calendar, docs and trackers. If nothing is connected, ask the user for bullet notes and say the result would be richer with access. Either way, you are then mostly formatting.

**Windows.** Run `scripts/comms_window.py --end <date>`. Progress, Problems, newsletter items and FAQs come from the look-back window. Plans come from the look-ahead window plus anything said about next week. The script prints the header label and search filters, so the dates stay consistent.

**Where the signal is**

| Source | Look for | Skip |
|---|---|---|
| Chat | Posts in large channels with many reactions or long threads; announce channels; exec posts; team update threads; repeated questions with "+1"s | Banter, DMs you weren't given, private channels unless the user is asking about them |
| Mail | Company-wide or exec mails; threads with many replies; mails with FAQs in them | Newsletters from vendors, automated alerts |
| Calendar | Non-recurring meetings with many attendees (all-hands, product reviews, launch go/no-go); docs attached to them | Recurring 1:1s and standups |
| Docs | New docs with many viewers: vision, quarterly plans, launch briefs, policy changes; docs by key leads | Personal scratch docs |
| Trackers | Closed milestones, epics moved to done, burn-down vs plan, new blocker tickets | Individual ticket churn |
| Press / external | Articles, awards, analyst mentions in the window | Unverified social chatter |

**Ranking.** Prefer reach (how many people it affects), then novelty (not already told), then evidence (a link or a number exists). For a 3P, prefer the team's own updates over secondhand mentions.

**Confidentiality.** Don't move content from a private channel or a restricted doc into a wider audience's message without the user's explicit OK. Flag anything that looks sensitive (comp, legal, people issues, unannounced deals) and leave it out by default.

**Gaps.** If a section has no source (for example, no Problems found), ask. Don't invent one, and don't silently leave it out.

## 2. Audience → shape

| Audience | They want | Shape |
|---|---|---|
| Own team | Detail, owners, what's next | Bullets with owners and dates; links to tickets |
| Neighbouring teams | What affects them, interfaces, dates | Lead with impact on them; skip internals |
| Leadership | Status, risks, decisions, numbers vs plan | TL;DR ≤3 bullets → decisions → detail (templates/leadership-update.md) |
| Whole company | What changed, why, what to do | Announcement or newsletter; no jargon; one link per item |
| Execs with ~1 min | Pulse | 3P |

**Tone.** Informational is the default: matter-of-fact, specific, no hype. Urgent: put the action and deadline first, keep it short, and say what happens if people miss it. Celebratory: name people and the result; one exclamation mark at most. Formal (policy, legal, org): precise, complete, reviewed by the owner.

## 3. Channel formatting

| | Slack-style chat | Email | Doc / wiki |
|---|---|---|---|
| Bold | `*bold*` (single) | real formatting or **bold** in Markdown-rendered clients | `**bold**` |
| Links | paste the URL, or `<url\|text>` in API payloads | descriptive link text | descriptive link text |
| Length | ≤ ~150 words in the main post; detail in thread replies | subject + ≤ 1 screen; appendix below a line | any; summary on top |
| Emoji | `:shortcode:`; section markers fine | sparing; real characters | rarely |
| Mentions | `@here` / `@channel` only when everyone must act now | To = must act, Cc = FYI | n/a |
| Headers | an emoji plus a bold line | short bold lines | Markdown headings |

- **Subject lines** carry the point: "Expense tool changes on 2 Nov; submit open reports by 30 Oct", not "Expense update".
- **Threads.** Post the summary as the parent message, and put detail and follow-ups in replies.
- **Time zones.** Give times in the reader's main zone, and add a second zone for distributed teams ("16:00 IST / 11:30 CET"). Prefer dates like "Fri 16 Oct" over "next Friday".

## 4. Sentence-level rules

- Use outcomes, not activity: "cut p95 from 14 to 6 min", not "worked on performance".
- Every number gets its comparison: vs target, vs last period, or of a total ("31 of 40").
- Use names, not pronouns, for owners. "We'll look into it" has no owner.
- Spell out acronyms and code names once, for readers outside the team.
- Use the active voice and short sentences. One idea per bullet.
- Cut the warm-up ("I wanted to share a quick update…") and the recap at the end.
- For prose polish beyond this, use long-form-writing.

## 5. Hard messages

- **Bad news early.** Put the slip, its size, the cause and the plan in the first lines. Don't bury it under good news.
- **Blameless incidents.** Describe what the system allowed ("the deploy tool let a config skip validation"), not who did it. Give timestamps in one zone. Every action item has an owner and a due date. Verify numbers against dashboards before sending.
- **During an incident**, send short updates on a fixed cadence (for example every 30 minutes): current state, impact, next update time. Write the full report afterwards.
- **Org changes.** Tell the affected people first, in person or one-to-one, then post broadly. Lead with what changes for whom and what stays the same. Name the person to talk to.
- **Unknowns.** Say "not decided yet; expected by <date>". Don't speculate, especially in an FAQ.
- **Needs an official voice.** Comp, legal, layoffs, M&A and security disclosures go back to the owner (People, Legal, the exec). Draft only if they ask.

## 6. Review and sending

- Run `comms_check.py --type <type> --channel <channel>` and fix every ERROR. Then read the WARNs and fix them, or decide to keep them.
- Check every number, date and name against its source. Check every link opens and is shareable with the audience.
- Anything that goes out under the user's name is a draft until they approve it. Show the final text and the recipients, and never post or send on your own.
- For recurring updates, keep last period's version and compare: same structure, and changes are easy to see.

## 7. comms_check.py checks

| Code | Level | Fires when |
|---|---|---|
| read-time | ERROR for 3p, else WARN | over 125% of the budget (3p 60s, status 120s, leadership 90s, announcement 120s, newsletter 240s, faq/incident 300s) at 230 wpm |
| placeholder | ERROR | `[...]`, `[insert…]`, TBD, TODO, XXX |
| relative-date | WARN | today/tomorrow/next week/EOD/ASAP on a line with no absolute date |
| time-zone | WARN | a clock time with no zone on the line |
| vague | WARN | worked on, made progress, various, looked into, aligned on… |
| ask | WARN | please/need you/can you… without a named owner or a date on the line |
| acronym | WARN | 3+ letter caps never expanded `(ABC)`, minus a common list |
| bottom-line | WARN | status/leadership/announcement/incident/general opens with a bare label (uses the Subject line if present) |
| channel | WARN | Slack: `**`, paragraphs > 90 words with no bullets; email: no Subject line |
| 3p-header / 3p-format / 3p-length / 3p-data | ERROR / ERROR / ERROR / WARN | header not `<emoji> <Team> (<dates>)`; lines other than Progress/Plans/Problems in order; >3 sentences; no number in Progress |
| newsletter-* | WARN | outside 15-30 bullets, < 3 sections, bullet > 2 sentences, few links, no "we" |
| faq-* | ERROR/WARN | Q/A count mismatch; long answers; hedged answer not flagged as unconfirmed; no source |
| status-* | ERROR/WARN | no Status line; at risk with no help asked; no numbers |
| leadership-* | WARN | > 5 headline bullets; no decisions/asks |
| incident-* | ERROR/WARN | missing Impact/Timeline/Root cause/Resolution/Action items; timeline without a zone; action without owner and date; blame words |
| announcement | WARN | missing what / why / who / when / what to do / where to ask |

Heuristics, not grammar: a WARN can be a false positive. Use `--json` when another tool consumes the result.
