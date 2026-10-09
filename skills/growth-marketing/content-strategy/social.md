# Social media reference

Contents: 1 platform playbooks · 2 limits and folds · 3 pillars and mix · 4 hooks · 5 post templates · 6 carousel frameworks · 7 short-form video · 8 X ranking signals · 9 repurposing · 10 engagement, listening and comment triage · 11 studying top performers · 12 analytics · 13 what to post when stuck.

Platform behavior changes often. Treat frequencies, times and mechanics below as starting hypotheses and confirm against your own analytics.

## 1. Platform playbooks

| Platform | Best for | Cadence (start) | Formats that work | Avoid |
|---|---|---|---|---|
| LinkedIn | B2B, founders, recruiting | 3-5 posts/week | Personal stories with business lessons, data, contrarian takes with evidence, document carousels, behind-the-scenes | Links in the post body (put in first comment), corporate speak, generic motivation, polls as a crutch |
| X | Tech, media, real-time, niche communities | 1-3 originals/day + replies | Specific opinions, teaching threads, live commentary, quote posts with added insight | Pure promotion, bursts of posts, ignoring replies, fully scheduled presence |
| Instagram | Visual brands, ecommerce, consumer | 3-7 feed posts/week + daily stories | Reels, value carousels, UGC, interactive stories | Text-heavy images, promotion-only feeds |
| TikTok | Awareness, younger audiences, consumer and creator tools | 1-2/day when growing | Native, lo-fi video, trends adapted to your niche, series | Polished ads posing as content, slow openings |
| YouTube | Search-driven education, demos, long-form | 1/week long-form, Shorts 3-5/week | Tutorials, comparisons, teardown/analysis, chapters | Clickbait titles that don't pay off |
| Facebook | Local businesses, communities, older demographics | 3-7/week | Groups, native video, events | Relying on page organic reach |
| Threads / Bluesky | Conversational, text-first audiences | Daily | Short takes, replies, community threads | Hashtag stuffing |
| Pinterest | Visual search (home, food, fashion, DIY, templates) | Several pins/week | Keyword-rich pin titles and descriptions, vertical images | Hashtags as strategy |

LinkedIn specifics: hook must land before "see more" (~210 characters); 1,200-1,500 characters often performs well; first-hour comments matter; comments > reactions; dwell time counts; tag people only when genuinely relevant.

## 2. Limits and folds

| Platform | Max length | Visible before "more" | Hashtags |
|---|---|---|---|
| LinkedIn | 3,000 chars | ~210 chars | 3-5, at the end |
| X | 280 chars (longer for paid tiers) | full post | 0-2 |
| Threads | 500 chars (+ long attachment) | first 1-2 lines | 1 topic tag |
| Instagram | 2,200 chars caption | ~125 chars | 3-5 (max 5) |
| TikTok | 4,000 chars caption | ~150 chars | 3-5 (max 5) |
| Facebook | very long | ~120 chars; short posts (40-80 chars) engage best | 0-2 |
| YouTube | title 100 (≈70 visible); description 5,000 (≈100 visible) | | 3-5; over 15 makes all ignored; first 3 show above title |
| Pinterest | title 100, description 500 | ~50 chars | prefer keywords in sentences |

Hashtags count toward limits. Front-load the message before the fold. `scripts/content_tool.py post drafts.txt --platform linkedin` checks length, fold, links and bait phrases.

## 3. Pillars and mix

Pick 3-5 social pillars you can sustain. Example for a SaaS founder: industry insights 30% (trends, data, predictions), building the company 25% (lessons, numbers, decisions), educational 25% (how-tos, frameworks), personal 15% (stories, values, opinions), promotional 5% (launches, offers). For each pillar ask: what unique perspective do we have? what does the audience ask? what has performed before? what can we produce consistently? how does it serve the business goal?

## 4. Hooks

The first line decides whether anyone reads the second. Fill every hook with a specific fact, number, or story.

| Type | Patterns |
|---|---|
| Curiosity | "I was wrong about [belief]." · "[Outcome] usually comes down to [surprising cause]." · "[Result] in [short time]." |
| Story | "Last week, [unexpected event]." · "I almost [mistake]." · "Three years ago I [past]. Today [present]." |
| Value | "How to [outcome] without [pain]:" · "[N] [things] that [outcome]:" · "Stop [mistake]. Do this instead:" |
| Contrarian | "Unpopular opinion: [claim]." · "[Common advice] cost us [specific result]." · "I stopped [practice] and [result]." |
| Proof | "We analyzed [N] [things]. Here's what the top 10% do." · "[Named customer] cut [metric] by [N]%. The process:" |

Social-specific tells to avoid (plus everything in marketing-copy ai-tells.md): one-short-sentence-per-line posts end to end; engagement bait ("Agree?", "Thoughts?", "Let that sink in", "Read that again"); manufactured vulnerability with no real story; emoji bullets on every line; em dashes. Keep fragments and lists of three to one per post. End on the point or a real question you want answered.

## 5. Post templates

**Story post (LinkedIn)**: unexpected outcome or lesson → when/where → the challenge → what you tried → the turning point → the result (number) → the lesson for the reader → optional real question.

**Contrarian take**: the opinion, stated plainly → what changed your mind (with a number) → 2-3 reasons → what to do instead → invite pushback with a specific question.

**List post**: "[N] things I learned about [topic] after [credibility]" → numbered points with one-line explanations → the wrap-up insight.

**How-to**: "How to [outcome] in [time]" → steps, each with why it matters or the common mistake → result.

**Teaching thread (X)**: post 1 = specific promise + proof; posts 2-8 = one step or idea each, self-contained; final = summary + pointer to the full resource (link in reply where links are penalized).

**Breakdown thread**: "[Company/campaign] did [result]. Here's how:" → context → 4-6 moves with evidence → what to copy and what not to.

**Story thread**: hook → setup → conflict → turning point → result → lesson.

**Carousel cover**: count + deliverable + audience ("9 expense-policy clauses agencies forget").

**Reel/short script**: hook (0-3s) → beats → CTA (last 3-5s).

## 6. Carousel frameworks

Rules: slide 1 is the thumbnail and must stand alone; one visual template for all interior slides; one idea per slide; the last slide converts the swipe into an action (save, follow, comment keyword, link in comments/bio).

| Content | Framework | Slide plan |
|---|---|---|
| List of resources/tools/tips | Value stack (4-14 slides) | Cover with exact count and deliverable → one item/category per slide with 3-6 concrete sub-items → action close |
| Personal result with a system | Problem → proof (6-10) | Specific result with number → the real problem reframed → the system (named tools/steps) → the detail (literal template/prompt/process; the save-worthy part) → proof artifact (screenshot) |
| Several techniques on one theme | Hack list (6-10) | Stat implying most people fail → why the usual approach fails → one named technique per slide with bad vs good → one-line synthesis + CTA |
| Strong opinion | Rant with fairness pivot (4-8) | Provocative claim → escalating specific examples → "to be fair…" what you're not attacking → firm signed close |
| Product/workflow | Demo walkthrough (5-11) | Product + finished outcome → pain it replaces → numbered step overview → one real screenshot per step → result + CTA |

## 7. Short-form video

Hook types: curiosity (engagement), value (saves), story (watch time), controversial (comments). The first 1-3 seconds need movement, a face or a bold text overlay, and the payoff promise.

Script template:
```
Title · platform · length · format (talking head / slideshow / demo / screen recording / b-roll)
Hook 0-3s: visual · audio · on-screen text
Body: [timestamp] beat … [timestamp] beat …
CTA last 3-5s: verbal · text · action (follow, comment, link)
Production: sound choice · b-roll list · graphics/captions
```

Structures: tip (hook → 3 steps → result, 20-40s), story arc (45-60s: setup → conflict → resolution → lesson), POV/skit (15-30s), before/after, myth vs fact. Visual patterns: talking head (trust), slideshow (easy to batch), screen recording (software demos), b-roll with voiceover (lifestyle). Audio: trending sounds for reach in entertainment niches; original audio/voiceover for education and authority; always burn in captions (most viewing is muted).

Posting: start with test windows around morning, lunch and evening local time and keep what your data supports. Cadence: growing 1-4/day, maintaining ~1/day to 3/week, testing 2-5/week. Batch: ideate 10-20 concepts (30 min) → script 5-10 (1 hour) → film in one session (2 hours) → edit and schedule.

## 8. X ranking signals

The X recommendation code published in 2026 scores each post with separate predicted probabilities for many actions and sums them with weights (weights themselves weren't published). Scored positives include likes, replies, reposts, quote posts and clicks into quoted posts, post clicks, profile clicks, three kinds of shares (generic, via DM, via copied link), video quality views above a minimum duration, dwell time, photo expands, and follows. Predicted negatives (not interested, mute, block, report) subtract. Muted keywords filter posts before scoring; an author-diversity step decays repeated posts from the same author in one feed.

Practical rules (structure verified; specific numbers are practitioner reports):
1. Make a specific claim in the first ~8 words; dwell is scored.
2. Space original posts (~60 minutes) so your own posts don't decay each other.
3. Name the topic early so topic routing can place the post.
4. Write for the DM share and the follow, not the like.
5. Quote with added insight rather than plain reposting.
6. Make people curious enough to visit your profile; keep bio and pinned post strong.
7. Name specific tools, companies and numbers; avoid spammy or rage vocabulary that many users mute.
8. Video needs to clear the minimum duration (~8 seconds reported) and carry captions.
9. Stay for the first ~30 minutes to answer replies.
10. Space reruns of evergreen posts; recently seen content is filtered.

These mechanics are X-specific; the general lessons (hook early, be specific, reply fast) travel.

## 9. Repurposing

| Source | Outputs |
|---|---|
| Blog post | LinkedIn insight post (link in comments), carousel of main points, X thread, Instagram carousel, short video summary |
| Podcast/video | 3-5 clips (15-60s), 1-2 text posts, 1 thread, 1 carousel of the framework, 1 newsletter section or blog recap |
| Webinar/event | Slide carousel, Q&A thread, quote graphics, poll-result posts, clips |
| Newsletter | Main-insight post, curated-links thread, stat graphic, opinion post |

Content atoms to look for: quotable moment (15-60s), complete mini-story (60-90s), tactical tip (30-60s), contrarian take, surprising stat, behind-the-scenes moment.

Podcast workflow: transcribe → mark 5-10 best moments → cut clips → write standalone captions (each must make sense alone) → burn in subtitles → schedule over 1-2 weeks. Reshare evergreen pieces every 3-6 months.

Weekly batching (2-3 hours): review pillars → write 5 LinkedIn posts → 3 threads + short posts → 1 carousel + reel ideas → schedule → leave time for live engagement.

## 10. Engagement, listening and comment triage

Daily routine (~30 min): reply to every comment on your posts (5 min); comment on 5-10 posts from target accounts (15 min); reshare with added insight (5 min); 2-3 genuine DMs to new connections (5 min; for outbound sequences see sales-outreach).

Relationship building: list 20-50 accounts (peers, customers, adjacent creators); engage consistently; share their work with credit; graduate to collaborations (podcasts, co-created posts, webinars).

**Listening loop**: pull new posts from defined sources (target accounts, keywords, competitor names, communities) → drop anything older than 24h or off-topic → score → keep the top 10 → draft comments by tier → a human reviews and posts → log what went live and what got replies.

| Score dimension | Weight |
|---|---|
| ICP fit (author is a target buyer or influencer) | 2× |
| Intent (problem, question, shopping) | 2× |
| Comment opportunity (we can add something specific) | 2× |
| Reach potential (traction rising) | 1× |
| Recency (posted in last 1-4 hours) | 1× |

Comment tiers:
- Tier 1, relationship builder (target accounts, high intent): 2-4 sentences, a specific insight or counter-example from experience with numbers, a follow-up question; no link.
- Tier 2, visibility (high-reach adjacent post): one sharp sentence adding the piece most people miss.
- Tier 3, light touch: one specific reaction quoting a line.
- Never: "Great post!", emoji-only, "+1", "This is gold".

Sources: community sites with public search or feeds, tech news search, open social networks with public APIs, RSS for blogs/podcasts/channels; for networks without open access, saved searches and lists in the browser. Respect each platform's terms and rate limits.

## 11. Studying top performers

1. Pick 10-20 accounts in the niche with consistent posting (3+/week), high engagement relative to followers, and audience overlap.
2. Collect 300-1,000 posts (export or manual for small sets): text, format, hook, length, topic, CTA, time, likes/comments/shares/saves.
3. Rank by engagement rate; study the top 10%: hook types, length, format, topic, emotional trigger, CTA that drives comments, save-worthy topics.
4. Codify a playbook: hook patterns, structures, length bands, formats, topics, CTA styles.
5. Layer your own voice and proof; don't clone.
6. Convert attention: profile → lead magnet or newsletter → product. Track which posts drive profile visits and signups.

## 12. Analytics

Metrics: awareness (impressions, reach, follower growth rate), engagement (engagement rate, comments, shares/reposts, saves, DM shares), conversion (link clicks, profile visits, DMs received, signups and leads attributed via UTMs).

Weekly review: top 3 and bottom 3 posts (why?), follower growth trend, engagement-rate trend, best times from your data. Low engagement → test new hooks, formats, times, and engage more with others. Falling reach → remove body links, post more consistently, reply more, test video/visual formats.

## 13. What to post when stuck

Starting out: document the journey, share what you're learning, curate and comment on industry news, engage heavily with established accounts. Stuck: answer a question from a customer call, turn a support ticket into a how-to, share a number from the business, react to a trend with your data, repost an old winner with a new angle, run a teardown of a public example.
