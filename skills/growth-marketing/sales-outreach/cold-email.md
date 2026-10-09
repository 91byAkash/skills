# Cold email and multichannel reference

Contents: 1 principles · 2 frameworks · 3 personalization · 4 subject lines · 5 follow-ups and breakup · 6 deliverability · 7 benchmarks and funnel math · 8 multichannel cadence · 9 LinkedIn · 10 calls and video · 11 replies and booking · 12 agent permissions.

## 1. Principles

- **Sound like a peer**, not a vendor. Read it aloud: would a smart colleague in their industry send this?
- **Every sentence earns its place**; 25-75 words for a first touch, never past ~120.
- **"You" over "I/we"**; first sentence about them.
- **Show you did the homework**: an observation that connects to the problem you solve. If you remove the personal opener and the email still works, the personalization isn't doing its job.
- **One ask, low friction**: an interest question ("Worth exploring?", "Is this on your radar?") beats a meeting request. Asking for 30 minutes from a stranger is the most common first-touch mistake.
- **Plain text**, no images, no link in touch 1, no tracking pixels, no HTML signatures.
- Grade 6-8 reading level; short paragraphs; mobile-friendly.
- Avoid: "I hope this finds you well", "My name is… and I work at…", "I wanted to reach out", jargon (synergy, leverage, best-in-class, cutting-edge, revolutionize), feature dumps, fake "Re:/Fwd:", manufactured urgency, "quick call".

## 2. Frameworks

Pick by situation, not habit:

| Framework | Shape | Use when |
|---|---|---|
| Observation → problem → proof → ask | Noticed X → usually means Y → we helped Z do W → interested? | Default; you have a specific observation |
| Question → value → ask | Struggling with X? → we do Y → result → open to learning more? | Clear common pain |
| Trigger → insight → ask | Congrats on X → that usually brings challenge Y → here's what's worked → worth a chat? | Recent event |
| Story → bridge → ask | Similar company had problem → solved it like this → relevant to you? | Strong case study |
| Problem → agitate → solve | Problem → cost of ignoring it → how you fix it | Pain is acute and known |
| Before → after → bridge | Current state → desired state → how to get there | Clear transformation |
| Situation → complication → question | Context → what changed → question | Thoughtful, consultative buyers |

Proof that works in a sentence: a named customer in their segment, a metric with a timeframe, a specific before/after.

## 3. Personalization

| Level | Example | Value |
|---|---|---|
| 0 Merge fields | Hi {first_name} at {company} | None; everyone does it |
| 1 Segment | "Agencies your size usually…" | OK for Tier 3 |
| 2 Signal | "Saw you're hiring a second finance ops person" | Strong if tied to the problem |
| 3 Insight | "Your pricing page lists annual-only; teams like that often…" | Best for Tier 1 |

Hooks by source: job posts, recent launches/announcements, their content or talks, tech stack, mutual connections or customers, events attended, funding or growth news, public reviews of their product. Tie every hook to why you're writing; never fake familiarity.

## 4. Subject lines

2-4 words, lowercase, looks like a colleague's email: "finance ops hire", "month-end close", "{company} + receipts", "question about reporting". Not: clickbait, ALL CAPS, emoji, fake reply prefixes, "quick question" (overused), anything that promises what the body doesn't deliver. Preview text (first line) matters as much as the subject; don't spend it on "Hi Jane, my name is".

## 5. Follow-ups and breakup

- 3-5 emails total; most replies come from the first email or early follow-ups, but follow-ups add materially.
- Spacing: day 0 → 3 → 7-8 → 14 → 21-28; gaps widen.
- Each follow-up stands alone and adds something: new angle, case study, short tip, relevant resource, a different stakeholder framing. Never "just checking in", "bumping this", "did you see my last email".
- Can reply in-thread (keeps context) or new thread for a new angle.
- Breakup email: short, respectful, gives an easy out, and you must honor it (no more touches for 6+ months unless they engage). A 1-2-3 reply format lowers effort: "Reply 1 if it's not a priority, 2 if I should talk to someone else, 3 if the timing's off and I should check back in a quarter."

Example sequence angles: (1) signal + problem + proof + interest question; (2) two-line tip they can use without you; (3) mini case study with a metric; (4) direct offer of the low-commitment next step; (5) breakup.

## 6. Deliverability

Setup:
- Send from secondary domains (similar to the main brand, redirecting to it), never the primary.
- SPF, DKIM, DMARC on every sending domain; start DMARC at p=none, move to quarantine/reject once reports are clean.
- 2-3 mailboxes per domain; Google-hosted mailboxes ~20-30 cold sends/day each (Outlook-hosted lower); stay below provider limits.
- Warmup: weeks 1-2 warmup traffic only; weeks 3-4 at 5-10 cold sends/day ramping; full volume from week 5; keep warmup running.
- Use real mailboxes from the providers; avoid resold or shared-infrastructure inboxes.
- Large providers enforce bulk-sender rules (authentication, one-click unsubscribe for bulk, low complaint rates); Outlook.com has rejected non-compliant high-volume mail since May 2025.

Content and list:
- Plain text, no link in touch 1 (add later only if needed), open and click tracking off, no attachments, no images.
- Opt-out line ("Not relevant? Reply 'no' and I won't follow up") plus postal address.
- Verify every list; keep bounce rate under 2%; remove role addresses where risky; suppress opt-outs across all tools.

Monitoring: seed/placement tests weekly; postmaster dashboards for domain reputation; blocklist checks; DMARC aggregate reports.

Stop-loss (pause the campaign or mailbox when any hits):
- bounce > 2%;
- inbox placement < 70%;
- spam complaints approaching 0.1% (hard ceiling 0.3%);
- listed on a major blocklist;
- reply rate < 1% after 300+ sends (targeting or copy problem, not volume).

Capacity: `outreach.py capacity --contacts-per-week 600 --touches 4` → mailboxes and domains needed.

## 7. Benchmarks and funnel math (directional)

- Average reply ~3-4%; top quartile ~5-6%; top decile 10%+; positive replies are typically a third to half of replies.
- Most replies come from the first email (often more than half); later follow-ups add the rest.
- Meetings: often 0.5-1% of contacts for untargeted lists; signal-based Tier 1-2 can reach several times that.
- Example funnel: 1,000 contacts → ~34 replies → 10-15 positive → 5-8 meetings → 1-2 customers.
- Plan backwards: `outreach.py funnel --deals 6 --close 0.2` gives meetings and contacts needed.

## 8. Multichannel cadence

Tier 1 example (21 days):

| Day | Channel | Touch |
|---|---|---|
| 1 | LinkedIn | View profile; engage with a recent post genuinely (no pitch) |
| 2 | Email | Touch 1 |
| 4 | LinkedIn | Connection request, no note or a one-line note with no pitch |
| 5 | Phone | Call; if voicemail, 20-30s referencing the email |
| 7 | Email | Follow-up: new angle |
| 9 | LinkedIn | Message if connected: useful resource, no ask |
| 12 | Video | 60-90s personalized video (e.g., walk through their page) |
| 14 | Email | Case study |
| 17 | Phone | Second call |
| 21 | Email | Breakup |

Tier 2: email-led with LinkedIn connection + 1 message and a call for best fits. Tier 3: email only.

Rules: a reply on any channel stops every channel; an opt-out anywhere is everywhere; one sender owns an account (no two reps on one company); 4-7 emails and at most 3 LinkedIn messages per sequence; space touches so no day has two channels unless the first got engagement.

## 9. LinkedIn

- Platform limits shift; keep connection requests around 100/week (15-25/day) and avoid spikes.
- Acceptance often 25-30% for targeted requests; message reply rates often 7-10%.
- Profile first: clear headline about who you help; recent useful posts make outreach land.
- Modes: manual (safest, best for Tier 1), assisted (tool queues, human sends), automated (fastest, highest account-restriction risk and terms exposure). Choose deliberately and document the risk.
- Message: no pitch in the connection note; after accepting, a short relevant message or resource; ask only after a reply.

## 10. Calls and video

Call opener (permission-based): "Hi {name}, it's {me} from {company}. This is a cold call; can I take 30 seconds to tell you why I called, then you decide if we keep talking?" Then: one-line problem → relevant proof → interest question. Disqualify fast when not a fit.
Voicemail: 20-30 seconds; name, the reason (one line tied to their signal), "I'll send a note too", number said twice slowly. Don't expect callbacks; the voicemail lifts email replies.
Video: 60-90 seconds; show their site/page/report on screen; thumbnail with their name or site; send as a link in a follow-up (not touch 1).

## 11. Replies and booking

| Class | Action |
|---|---|
| Positive | Reply within minutes; propose two specific times + a booking link; send the invite immediately when they pick |
| Information request | Answer briefly and specifically; offer a short call to go deeper |
| Objection | Acknowledge, answer once with proof, ask one question (enablement.md objections) |
| Not now | Ask when to check back; set a dated reminder; send nothing in between unless useful |
| Referral | Thank them; email the referred person citing the referral (with permission) |
| Wrong person | Ask who owns it; thank them |
| Out of office | Pause; resume after their return date |
| Unsubscribe / hostile | Remove everywhere; brief apology if appropriate; never argue |
| Bounce | Remove; check list source quality |

Common objections in reply: "Not interested" → respect, offer one-line reason to revisit or close; "We use X" → ask what they'd improve, offer contrast only on that; "No budget" → ask about timing and what would make it a priority; "Send info" → send one short relevant item and ask one question.

Booking: confirm the day before with something useful (agenda, a question, a relevant insight); reschedule a no-show once, politely; after a second no-show, move to nurture.

## 12. Agent permissions

| Action | Agent alone | Human approves |
|---|---|---|
| Research, briefs, list building | Yes | Spot-check samples |
| Drafting emails | Yes | Tier 1 and new segments before send |
| Sending first touches | No (until accuracy proven) | Yes |
| OOO, bounce, unsubscribe handling | Yes | No |
| Not-now reminders | Yes | No |
| Positive, objection, referral replies | Draft only | Yes |
| Changing sending volume/domains | No | Yes |
