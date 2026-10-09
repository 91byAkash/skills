# Launch playbook

Read this when planning any launch moment: a new product, a major release, a feature, a relaunch, or the ongoing rhythm of shipping announcements. For the plan around the launch (budget, AARRR, 12-month view) use the marketing-plan skill; for the go-live checklist of a site or page read [site-launch-qa.md](site-launch-qa.md).

## Contents
1. Launch as a campaign, not a day
2. Readiness gate
3. Channel map: owned, rented, borrowed
4. Five phases of a product launch
5. Launch-platform day
6. Launch-day operations
7. After the launch
8. Ongoing launches and tiers
9. Turning shipped work into announcements
10. Measurement

---

## 1. Launch as a campaign, not a day

A launch is a sequence of moments that each give people a reason to look: a waitlist, a beta invite, an early-access wave, a public day, and a series of follow-ups. Teams that put everything into one day get one spike and then silence. Plan for at least three touchpoints per audience across the weeks around the date.

Two opposite failure modes:
- **Hiding too long.** Building in silence until the product is "ready" means launching to nobody. Start collecting an audience and feedback as soon as there is something to show.
- **One more feature.** Delaying the date for scope that does not change the core promise. If the product does one job well, ship it and announce the rest later as its own moment.

## 2. Readiness gate

Before committing to a public date, check three properties of what you are launching:

| Property | Question | If no |
|---|---|---|
| Simple | Can a new user explain what it does in one sentence after a minute? | Cut scope or sharpen the promise; do not add features |
| Lovable | Do beta users come back without being chased, and say something specific they like? | Run another beta cycle; launch reach would be wasted |
| Complete | Does it finish the job it claims, end to end, without a workaround or a support ticket? | Narrow the claim to what is complete, or delay |

Operational readiness on top: onboarding and docs in place, analytics firing on the key events, support briefed with macros, pricing set and visible, legal pages live, and a named rollback owner. Use [site-launch-qa.md](site-launch-qa.md) for the page-level checks.

## 3. Channel map: owned, rented, borrowed

Sort every channel into one of three buckets; each plays a different role.

**Owned** (you control reach and data): email list, existing users and in-app surfaces, blog, docs and changelog, community space, product itself.
- The goal of every other channel is to move people here. A launch that grows the list or user base keeps paying after the day ends.
- Start an owned channel well before the launch: a waitlist page and a short pre-launch email cadence.
- Community spaces work when there is a reason to gather (peer help, templates, office hours), not as an announcement feed.

**Rented** (platform controls reach): social networks, forums, launch platforms, app stores and marketplaces, video platforms.
- Pick one or two where your buyers already spend time and go deep; follow each place's self-promotion rules.
- Use them to pull people into owned channels: a signup, a waitlist, a download.
- Assume reach can change overnight; never make a rented channel the only path to your audience.
- Marketplaces and app stores reward listing work: title, keywords, screenshots, reviews and category, treated like store optimisation.

**Borrowed** (someone else's audience): partners and integrations, newsletters, podcasts, creators, press, co-hosted events, reviewers.
- Fastest path to credibility and new reach; score candidates with `partners` in [scripts/launch_tool.py](scripts/launch_tool.py); the full partner playbook (types, formats, pitch, agreement) is in the marketing-plan skill.
- Make it easy: pre-written blurbs, assets, a clear angle for their audience, and a reason they look good sharing it.
- A physical product example: sending a free unit to a respected reviewer in the niche, with no script attached, often beats a paid placement.

Prioritise by audience fit, then by effort. A plan with depth in four channels beats a plan with a line in fifteen. Cutting launch assets into channel-native pieces and resharing across each channel's half-life: `REFERENCE.md` §10 in the `content-strategy` skill.

## 4. Five phases of a product launch

| Phase | Who | Goal | Key moves |
|---|---|---|---|
| 1. Internal | Team, friends | Find obvious breakage | Dogfood the core job, fix blockers, write the one-sentence promise |
| 2. Alpha | Hand-picked users (5-20) | Validate the job is solved | Landing page with waitlist, personal onboarding, interview each user, announce that it exists |
| 3. Beta | Wider invited group | Prove people return and talk about it | Invite from waitlist in waves, collect quotes and metrics, teasers and build-in-public posts, start supporter list |
| 4. Early access | Open but gated | Scale feedback, test pricing and messaging | Release in batches (for example 5-10% of the waitlist at a time) or all at once; product-market-fit survey; pricing test; leaked screenshots and previews |
| 5. Full launch | Everyone | Maximise reach and conversion | Self-serve signup, pricing live, launch-platform day, email to full list, partners, press, in-app, directories |

If the waitlist is small (< a few hundred), skip batching and open early access fully; batching only helps when demand exceeds capacity or you need learning between waves.

## 5. Launch-platform day

Launch platforms (product-discovery communities and their alternatives) are worth one well-prepared day for products whose early adopters browse them: tools for makers, marketers, developers and tech-forward teams. They suit poorly products for non-technical niches, regulated buyers or local services.

**Pros**: concentrated early-adopter traffic, a credibility badge, backlinks, feedback from a vocal crowd. **Cons**: the crowd is not your buyer, traffic fades in 48 hours, and a poor showing is public.

Preparation, counting back from launch day (the `timeline` command in [scripts/launch_tool.py](scripts/launch_tool.py) dates these):
- **3 weeks out**: use the platform as a member daily: comment usefully on other launches, follow active makers. A dormant account launching cold gets little reach and can trip anti-manipulation filters.
- **2 weeks out**: create the upcoming/teaser page and send traffic to it to collect "notify me" subscribers.
- **10 days out**: optionally ask a respected member to post it for you; trade value (a mention, an intro), never cash. Helpful, not required.
- **1 week out**: gallery images in the platform's sizes, a tagline, a short description, the maker's first comment (why you built it, what is different, what to try first), and a customer's first comment lined up.
- **3 days out**: email the list and supporters with the date and an ask for honest feedback.
- **1 day out**: test the product in a clean browser, confirm the video plays, the CTA lands on signup, and the listing preview renders.

On the day:
- Launch at the start of the platform's daily cycle, on a Tuesday-Thursday; weekend days draw a fraction of the traffic.
- The first hours decide placement: have supporters ready to visit and comment early.
- Ask for **feedback**, never for votes. Vote requests and messaging strangers get posts hidden.
- Reply to every comment quickly and substantively; responsiveness and comment quality count more than raw votes.
- Share across owned channels and communities where you are already a member.

After: publish a recap with real numbers and lessons the next day; cross-post where promotion is welcome. Post to a technical community's "show" section only if there is a genuine technical story (architecture, novel approach); a generic "we launched" post gets flagged.

Alternatives and companions: smaller launch sites, software directories and AI or no-code directories. Treat them as a submission batch, not as separate launch days; see [directories.md](directories.md).

## 6. Launch-day operations

- **Run sheet** with times, owners and links for every post and email ([templates/launch-day-runbook.md](templates/launch-day-runbook.md)).
- **One channel for the team** (a launch room) where anyone posts issues, mentions and questions.
- **Owners**: comment replies, social replies, support inbox, metrics, incident/rollback. One person can hold two roles, never all.
- **Hourly check**: traffic by source, signups, activation event, error rate, payment success. A broken signup during a spike is the most expensive bug of the year.
- **Pre-written replies** for the top 10 questions and objections (pricing, competitors, data, roadmap), personalised before posting.
- **Freeze**: no deploys on launch day except fixes.

## 7. After the launch

The weeks after are where most of the value is captured:
- **Onboarding sequence** tuned for the launch cohort (they arrive curious, not committed); hand to email-sequences.
- **Roundup email** to everyone who engaged but did not sign up: what launched, what people said, one clear CTA.
- **Comparison pages** for the competitors launch-day commenters mentioned; honest tables, when to pick each.
- **Site updates**: new screenshots, testimonials from launch feedback, updated pricing or feature pages, social proof badges.
- **Interactive demo or recorded walkthrough** for visitors who will not sign up yet.
- **Customer stories** from early adopters 2-4 weeks in, with numbers.
- **Directories and review sites** in batches over the following weeks; ask activated users for reviews.
- **Retrospective** within two weeks: what moved the metric, what was effort without return, what to repeat.

## 8. Ongoing launches and tiers

After the first launch, keep a steady rhythm of smaller moments. Each signals that the product is alive, gives sales and support something new to say, and resurfaces the product to people who passed earlier.

| Tier | What qualifies | Effort | Channels |
|---|---|---|---|
| Major | New product, big capability, pricing overhaul, new segment | Full campaign, 4-8 weeks | Everything: email to all, launch platform, press, partners, in-app, site, sales enablement |
| Medium | Meaningful feature, notable integration, big improvement | 1-3 weeks | Email to relevant segment, in-app, blog/changelog, social, partner co-announce |
| Minor | Small feature, polish, fixes, small integration | Days | Changelog, in-app note, monthly digest |

Rules:
- Space major and medium launches so each gets attention; batch minor ones into a digest.
- Match tier to customer impact, not engineering effort. A two-day change that removes the top complaint can be medium.
- Re-launches are allowed: a rebuilt product, a new audience, or a big redesign can carry a second launch-platform day after enough time and change.
- Public changelog and a "what's new" surface in-app show active development even between campaigns.

## 9. Turning shipped work into announcements

A repeatable loop for teams that ship continuously.

1. **Collect what shipped** in the window (a week or a sprint): merged changes, release notes, feature-flag rollouts. Exclude anything still behind a flag, in a limited rollout, or reverted. **Only market what everyone can use today.**
2. **Translate each change into a user sentence**: "You can now ___." If the sentence needs internal jargon or describes plumbing ("refactored the sync service"), it is a minor item or not an announcement; if it unlocks a job ("You can now send a proposal from your phone"), it is a candidate.
3. **Assign a tier** with the table above. A refactor that makes a page twice as fast can be worth a minor note with a number.
4. **Ground every claim**: describe only behaviour that exists, name limits honestly (plans, platforms, regions), avoid speed or accuracy numbers you have not measured, and check screenshots match the released UI.
5. **List pages that just became wrong**: pricing and plan tables, feature pages, comparison pages, docs, onboarding emails, sales decks, help articles, the homepage. Stale pages after a launch cost more trust than the launch earns.
6. **List new content opportunities**: a how-to, a template, a use-case page, a comparison update, a short demo video, a post for the integration partner.
7. **Draft the digest** using standard changelog headings (Added, Changed, Fixed, Removed, Deprecated, Security), with a short intro naming the most important change ([templates/shipped-digest.md](templates/shipped-digest.md)).
8. **Stage drafts for human review**; never publish automatically. Someone who knows the release confirms each claim.

## 10. Measurement

Set a target before the launch for one primary metric and two or three supporting ones.

| Layer | Metrics |
|---|---|
| Reach | Visits by source, waitlist and upcoming-page signups, list growth, mentions |
| Conversion | Signup rate by source, trial starts, demo requests |
| Activation | Share of launch signups reaching the activation event in 7 days |
| Revenue | Paid conversions, plan mix, revenue from launch cohort at 30 days |
| Durability | 30/60-day retention of launch cohort vs. normal cohorts; organic traffic 30 days later |

Launch cohorts often retain worse than steady-state signups (curiosity traffic); judge the launch by the 30-day cohort, not day-one signups. Tag every launch link with campaign parameters so sources are separable.
