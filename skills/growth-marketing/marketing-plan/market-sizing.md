# Market sizing

Use this when a plan has to show that a market can carry the revenue target, when a target needs a realistic ceiling, or when someone simply asks "how big is this?". What you hand back is a range with its reasoning and a recommendation (go, go narrow, test first, or park), never a single impressive figure. `sizing` in [scripts/plan_tool.py](scripts/plan_tool.py) does the arithmetic.

## Step 1: Write the scope sentence

One sentence naming who buys, where, for what job, and how they pay, plus what you are deliberately leaving out. A fuzzy category gives a meaningless number.

> Independent physiotherapy clinics in the UK and Ireland with 2-15 practitioners, buying appointment and billing software on a monthly per-clinic subscription. Excluded: hospital groups, other therapy types, other countries.

## Step 2: Decide which number you need

Three nested figures, each narrower than the last:

- **Whole category (TAM)**: yearly spend if every conceivable buyer of the category bought. Only the category definition limits it. Investors ask for it; it says nothing about whether anyone will buy from you, so skip it unless requested.
- **Serviceable share (SAM)**: the slice your product can serve today, after geography, segment, language, price point, integrations and compliance.
- **Winnable share (SOM)**: what you can realistically capture in one to three years given channels, budget, sales capacity, conversion and competition. Marketing plans are built on this one.

## Step 3: Estimate it at least two ways

The clinic figures below only demonstrate the arithmetic; they are not market data.

| Method | How it works | Suits | Watch out for |
|---|---|---|---|
| Count the buyers | buyers you can reach × yearly spend each × share you expect to win | Markets where buyers can be counted: B2B niches, local services, agencies, marketplaces | The buyer count and the win rate are both guesses; say so |
| Follow the searches | monthly high-intent searches × share of clicks you can earn × visit-to-trial × trial-to-paid | Categories people search for by name | Misses demand nobody searches for; it covers one channel, so treat it as a minimum |
| Read the rivals | what competitors visibly earn: published revenue, headcount × revenue per head, review volume, pricing, hiring, ad spend | Any market with visible incumbents | If rivals together out-earn your SAM, your SAM is drawn too tight or they serve segments you cut |
| Add up your channels | new customers each channel can bring per month with today's people and budget × 12 × yearly spend | Early-stage plans | It is a capacity number: low by design |

Worked numbers for the clinics (yearly plan $1,440):

- Count the buyers: about 9,500 clinics fit the scope (registry and association lists), so SAM ≈ $13.7M/year; winning 2-4% over roughly two years gives $274k-$547k ARR.
- Follow the searches: ~3,200 searches a month × 15% of clicks × 5% start a trial × 25% convert ≈ 72 clinics a year ≈ $104k/year, from search alone.
- Add up your channels: associations ~3 clinics a month, search and content ~6, one SDR ~4; 13 × 12 × $1,440 ≈ $225k/year.

## Step 4: Put the estimates side by side

| Estimate | Year 1-2 figure | Rests on | Confidence |
|---|---|---|---|
| Count the buyers | $274k-$547k | a 2-4% win rate | Medium |
| Follow the searches | ~$104k, search only | earning 15% of clicks | Medium |
| Add up your channels | ~$225k | partner and SDR output holding up | Low |

How to read the comparison:

1. Line up like with like first; a one-channel figure can only set a minimum.
2. Where two estimates overlap, quote the overlap.
3. If two estimates sit more than about three times apart, something underneath is wrong. Track it down before showing anyone a number (`sizing` prints the same warning).
4. Buyer count clearly ahead of channel capacity (about 1.8× in the example) means people would buy but you cannot yet reach them. That is a budget and channel question; put it in the funding-stage part of the plan.
5. Channel capacity ahead of the buyer count usually means the buyer list is incomplete or the channel guesses are generous.
6. Analyst reports are a sanity check on the whole category at most; a global figure must never be the main method for a local or niche market.

## Step 5: Grade the evidence and write it up

Grade each input:

- **High**: two or more independent kinds of evidence agree, or your own commercial data backs it.
- **Medium**: credible but partial, e.g. a rival's revenue that is estimated rather than published.
- **Low**: a reasonable inference with little behind it.
- **Unknown**: missing or conflicting; make it a validation task in the plan.

Inputs ranked by how much weight they bear: your own CRM, conversion and churn data first; then what the market visibly does (rival ads, prices, reviews, job posts); then search and other demand proxies; then third-party reports; then expert opinion; last, uncited figures, trend pieces and AI summaries.

Write-up rules: give a range, never a precise single figure; separate observed facts from assumptions; name the methods and whether they agree; attach a confidence grade; finish with the one assumption that moves the answer most and how you would test it.

> We put SAM at about $12-15M a year (medium confidence), built from clinic counts and the plan price and in line with what rivals appear to earn. The answer is most sensitive to how many clinics will switch systems before their current contract ends; ten switching interviews would settle it.

## Step 6: Decide whether to go in

A large number alone is not a reason to enter. Answer nine questions with 2 (yes), 1 (partly) or 0 (no) and add them up (maximum 18):

1. Do buyers already show the need through purchases or searches?
2. Is there someone with a budget who has paid for something similar before?
3. Is there a trigger that makes the problem urgent rather than nice to fix?
4. Can you name channels that reach these buyers at a known cost?
5. Could a cheap test produce a signal within about two weeks?
6. Do buyers complain about gaps the incumbents leave open?
7. Can you demonstrate results quickly and convincingly?
8. Is the regulatory and operational load manageable?
9. Does it play to the team's skills, assets and existing audience?

| Score | Call | What the plan does |
|---|---|---|
| 15-18 | Go | Plan against the full SOM range |
| 11-14 | Go narrow | Pick one segment or wedge and size SOM for it alone |
| 7-10 | Test first | The first 90 days are a validation sprint with explicit kill criteria |
| 0-6 | Park | Log it under open decisions unless you hold an unusual advantage |

Pair the score with the size × frequency gate in [marketing-plan.md](marketing-plan.md): even a big SOM in the small-and-rare quadrant limits what you can spend to acquire a customer and which channels pay back.

## Traps

- Presenting the whole-category number as evidence that people will buy.
- Applying a global report to a local or niche decision.
- Mistaking search volume for market size.
- Relying on a single method with nothing to check it against.
- Forgetting the do-nothing options (spreadsheets, agencies, inertia) that compete for the same budget.
- A revenue target above the SOM range with no explanation of the gap.
