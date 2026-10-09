# Referral, affiliate and viral programs

Contents: 1 fit check · 2 viral spectrum · 3 seven mechanisms · 4 referral vs. affiliate · 5 referral loop design · 6 incentives and sizing · 7 affiliate programs · 8 fraud · 9 metrics and benchmarks · 10 disclosure and terms · 11 launch and nurture · 12 troubleshooting.

## 1. Fit check

Referral programs amplify existing satisfaction; they don't create it. Before building: retention flattening in cohorts, satisfaction/NPS solid, customers already mention you unprompted (ask new signups "how did you hear about us?"), and LTV supports a reward. If not → fix retention first.

## 2. Viral spectrum

- **Natural** (build loops into the product): collaboration tools (value grows with invites), communication tools (can't use alone), products with user-facing outputs (pages, forms, videos, designs, links others see).
- **Limited** (don't force it): backend/infrastructure, internal-only tools, competitive-advantage tools users keep quiet about. Invest in reward referrals, content, partnerships and affiliates instead.

## 3. Seven mechanisms

1. **"Made with" badges** on user-facing output; often on free plans, removable on paid.
2. **Exposure loops**: normal use shows the product to non-users (a scheduling link shown to every invitee; an email signature). Strongest when using the product signals status.
3. **Social sharing**: native share of results, milestones and artifacts with a branded hook or hashtag.
4. **Embeds**: user content embedded elsewhere carries your brand and a link back.
5. **Watermarks**: baked into output on the free tier; paid tier removes them.
6. **Reward referrals**: the incentive-driven mechanism, for products that don't spread on their own (§5-6).
7. **Earned word of mouth**: product so good or novel that people talk; the other six make it easier to act on.

## 4. Referral vs. affiliate

| | Customer referral | Affiliate |
|---|---|---|
| Who | Existing customers | Creators, reviewers, newsletters, consultants, complementary tools (may not be customers) |
| Best for | Natural word of mouth, self-serve, lower ticket | Reaching audiences you lack, higher-ticket |
| Reward | One-time or limited, often credit | Ongoing commission |
| Trust / volume | Higher trust, lower volume | Variable trust, higher volume |

## 5. Referral loop design

Trigger moment → share action → referred person converts → reward → loop.

**Trigger moments**: right after the aha moment, after a milestone, after great support, after renewal/upgrade, after a positive survey response. Never at signup.

**Share mechanisms** (roughly by effectiveness): in-product invite → personal link → email invite → social share → code (works offline).

**Friction**: one click to get the link; pre-written message the user can edit; placement at the trigger moment, not buried in settings; referral status page showing pending/earned rewards.

**Referred experience**: landing page that names the referrer ("Priya gave you $50 off"), reward applied automatically, same onboarding quality.

## 6. Incentives and sizing

Structures: single-sided (referrer only; simpler, fine for high-value products), double-sided (both get value; usually converts better and lets the referrer feel generous), tiered (rewards grow with referral count; gamifies sustained referring).

| Type | Pros | Cons | Fits |
|---|---|---|---|
| Cash/account credit | Universal | Transactional | Marketplaces, fintech |
| Product credit | Drives usage, cheap at margin | Only valuable to active users | SaaS, subscriptions |
| Free months | Clear | Attracts freebie-seekers | Subscriptions |
| Feature unlock | Near-zero cost | Needs gated features | Freemium |
| Merch | Memorable, visible | Logistics | Brand-led consumer, newsletters (tiered) |
| Charity donation | Feel-good | Weak personal motivation | Mission-driven |

Classic patterns: storage-for-storage (reward is the product itself), ride-for-ride credit on both sides, tiered merch for newsletter subscribers (3/5/10/25 referrals), education credits for high-sharing student audiences.

Sizing: **max total reward = LTV × gross margin − target CAC**. Example: $1,200 × 70% − $200 = $640 ceiling. Typical: B2C $10-50 or 10-25% of first purchase; B2B SaaS $50-500 or 1-3 months free; enterprise custom.

Presentation: lead with the bigger-feeling number. Under ~$100 price, absolute dollars usually feel bigger ("$10 off" beats "40% off" on $25); above ~$100, test percent vs. dollars.

`retention_tool.py referral` computes the ceiling, K-factor and ROI.

## 7. Affiliate programs

**Commission structures**: percentage of first sale or first year (10-30%); flat fee per action ($5-500; demos, trials); recurring share (10-25% of subscription for 12 months or lifetime); tiered by volume (e.g., 20% → 25% → 30%).

**Attribution window**: 24h for impulse buys; 7-14 days e-commerce; 30 days SaaS/B2B; 60-90 days long cycles; lifetime for premium partners. Decide first-click vs. last-click and what happens when a customer also used a referral link.

**Power law**: roughly a fifth of affiliates drive most results. Recruit and invest in a few strong promoters (higher tiers, custom assets, co-marketing, early access, a direct contact) rather than a long tail of dormant signups.

**Buyout clause**: for top affiliates on recurring commission, the option to buy out the future stream for a lump sum (commonly ~12× the current monthly commission) protects margin and gives them a cash-out.

**Launch pushes**: give affiliates a shared date, shared assets and a reason for their audience to act now (launch bonus, cohort close) so promotion stacks on one day.

**Recruiting**: customers who create content, niche reviewers and bloggers, video creators, newsletter writers, complementary tools, consultants and agencies. Outreach: reference a specific piece of theirs, one line on why their audience fits, the commission and extras, an interest question.

**Enablement kit**: tracking links/codes; product overview and key benefits; audience description; honest comparisons; logos, images and banners; sample copy and talking points; case studies; demo or free account; FAQ and objections; payout terms and schedule; disclosure requirements.

**Choosing tooling**: payment-system integration, fraud detection, payout management (tax forms, currencies), reporting, customization, price at your scale.

## 8. Fraud

Common: self-referrals with fake accounts, referral rings, codes posted on coupon sites, disposable emails, VPN/device spoofing, affiliates bidding on your brand terms.

Controls:
- Technical: email verification, device/IP checks, reward only after qualification (paid, past refund window, or meaningful activity), minimum activity thresholds.
- Policy: clear terms, caps per period and lifetime, clawback on refunds/chargebacks, manual review of anomalies, ban brand-term bidding and coupon-site posting for affiliates.
- Structural: product credit instead of cash (less attractive to fraudsters), referred user must take a meaningful action.

## 9. Metrics and benchmarks

- **Participation**: share of customers who refer (good 10-25%, great 25-50%); active referrers in last 30 days.
- **Referrals per referrer**: average 1-2, good 2-5.
- **Referral conversion**: invites → signups → paid.
- **K-factor** = invites per user × conversion; > 1 self-sustaining (rare), 0.2-0.5 is a healthy amplifier.
- **Business impact**: % of new customers from referral; cost per referred customer vs. other channels; referred-customer LTV and churn (often notably better than average, and they refer more); payback on rewards.
- **ROI** = (margin from referred customers − rewards − tooling − management time) ÷ program cost.

## 10. Disclosure and terms

- Affiliates and incentivized referrers must disclose the material connection clearly where they promote ("I earn a commission"); provide the wording.
- Don't reward reviews conditioned on positive sentiment; many platforms ban incentivized reviews entirely.
- Terms: eligibility, what qualifies, reward timing, caps, clawbacks, prohibited methods (spam, brand bidding, coupon sites), tax responsibilities for cash rewards, right to change or end the program.
- Respect anti-spam rules: referral emails sent by your system on a user's behalf are your messages.

## 11. Launch and nurture

Before: goals and metrics; incentive and sizing approved; tooling and attribution tested end to end; landing page; fraud rules; terms; support briefed.
Launch: announce to customers (email: what they give, what they get, their link, three steps); in-app prompts at trigger moments; site page.
Nurture: reminder ~day 7 after activation; day 30 "know anyone who'd benefit?"; day 60 success story + prompt; after milestones "you achieved X; know others who'd want this?"
First 30 days: review the funnel, thank and learn from top referrers, fix friction, remind non-referrers once.

## 12. Troubleshooting

| Symptom | Fix |
|---|---|
| Few people know about it | Prompt at trigger moments; account page entry; launch email |
| Aware but not sharing | One-click share, pre-written message, better timing, stronger or more relevant reward |
| Shares don't convert | Referred landing page naming the referrer; stronger new-user reward; smoother onboarding |
| One-time referrers | Tiers, status, progress display |
| Fraud | Qualification-based payout, caps, verification |
| Low-quality referred customers | Reward after paid/retained; product credit; narrower eligibility |

A/B test: reward amount and type, single vs. double-sided, reward timing, program description and CTA copy, prompt placement and timing.
