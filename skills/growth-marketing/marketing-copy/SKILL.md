---
name: marketing-copy
description: "Write, edit and refresh marketing page copy (homepage, landing, pricing, feature pages, headlines, CTAs, microcopy) in customer language. Use when asked to write or rewrite page copy, improve a headline or CTA, polish a draft, make copy \"less AI-sounding\", or refresh an old page. Not for conversion audits (use conversion-optimization) or email sequences (use email-sequences)."
license: MIT
metadata:
  category: "growth-marketing"
  version: "3.0.0"
---

# Marketing Copy

Scope: page and short-form copy, clarity tests, a machine-sounding-pattern blacklist, a seven-sweep edit, content refresh, and buyer-psychology models applied to copy. Ad campaign structure lives in paid-ads.

Clear beats clever. Copy that names the reader's situation in their own words, makes one specific promise, proves it, and asks for one action outperforms polished generic prose.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `mode` | required | inferred | `write`, `edit`, `refresh`, `short-form`, `psychology-review` |
| `page_type` | required for write | ask | homepage, landing, pricing, feature, about, comparison, launch |
| `primary_action` | required | ask | start trial, book demo, join waitlist |
| `audience` | required | from context file | agency finance leads, 10-80 staff |
| `traffic_source` | optional | mixed | paid social ad promising "receipts in 10 seconds" |
| `awareness_stage` | optional | infer | unaware, problem-aware, solution-aware, product-aware, most aware |
| `proof` | optional | ask | 1,240 customers, 4.8/5 from 310 reviews, named case study |
| `voice` | optional | from context file | plain, warm, direct; no slang |
| `draft` | required for edit/refresh | none | pasted copy or URL |
| `constraints` | optional | none | 60-char headline, legal claims review, regional spelling |

Read `.agents/product-marketing.md` first (customer language, objections, proof, voice). If missing, run customer-research or ask for the minimum: who, problem, outcome, alternatives, proof.

## Output

- **write**: copy by section (headline, subhead, CTA, sections, secondary CTAs, FAQ, final CTA), annotations on key choices, 2-3 alternatives with rationale for each headline and CTA, page title + meta description, and `[NEED: …]` flags for missing proof or differentiators. Template: [templates/page-copy.md](templates/page-copy.md).
- **edit**: marked-up copy or a change table (original → revision → reason, grouped by sweep), plus a score summary. Template: [templates/edit-report.md](templates/edit-report.md).
- **refresh**: gap grid vs top results, Keep/Revise/New outline, revised copy, publishing notes (meta, schema, links, URL plan).
- **short-form**: 5-10 variants per element with the angle each tests.
- **psychology-review**: which principles the page uses, misses or misuses, with concrete edits.

## Supporting files

- [REFERENCE.md](REFERENCE.md): writing principles, clarity tests ("Now you can…", discomfort → vision → path, perception gap), headline formulas, page structures by type, section-writing tips, CTA rules, voice. Read for any write task.
- [ai-tells.md](ai-tells.md): "never" and "limit" patterns, the grouped cliché vocabulary the lint uses, rewrite rules, self-check. Read before delivering any draft.
- [editing.md](editing.md): seven sweeps, reviewer-panel scoring, quick word/sentence checks, plain-English swaps, content refresh workflow. Read for edit and refresh.
- [psychology.md](psychology.md): ~60 buyer-psychology and decision models with copy applications and misuse warnings. Read for psychology reviews or when a page lacks a persuasion mechanism.
- [examples/before-after.md](examples/before-after.md): annotated rewrites (hero, feature section, pricing blurb, CTA set).
- [scripts/copy_lint.py](scripts/copy_lint.py): flags the cliché vocabulary by group (hype verbs, inflated adjectives, vague abstractions, filler intensifiers, chatbot vocabulary, stock openers and claims, unsourced proof, connective filler) and buzzword stacks, plus contrast reveals, negation lists, colon reveals, em dashes in short copy, weak CTAs, vague proof ("trusted by thousands"), long sentences, passive voice, plain-English swaps; reports Flesch score and you/we ratio. `python3 scripts/copy_lint.py draft.md`; `--vocab` prints the word groups that ai-tells.md section D mirrors.

## Steps

1. **Load context and set the brief.** One page, one primary action. Note audience, awareness stage, traffic source and what visitors already know. If proof or differentiator is missing → continue but flag `[NEED: proof]` / `[NEED: differentiator]`; never invent numbers, quotes or logos.
2. **Mine the message.** Pull 5-10 customer phrases for the problem, the outcome and objections. Draft the core message as discomfort → better state → path (the product + CTA). Check it against the perception gap: if the page serves risk-averse and early-adopter buyers, split the framing rather than averaging.
3. **Choose structure by page type** (REFERENCE.md §4). If traffic comes from an ad or email → mirror its promise in the headline (message match). If the audience is unaware/problem-aware → longer page that opens on the problem; if most aware → short page that leads with the offer and terms.
4. **Write the hero.** 8-10 headline candidates from different formula families (outcome, problem, audience, differentiation, proof). Keep those that pass "Now you can…" (compelling and true) and the swap test (wouldn't work unchanged on a competitor's site). Subhead adds the specifics (who, how, how fast) in 1-2 sentences. CTA = action verb + what they get ("Start my free trial", "See pricing for my team"); add one risk reducer near it.
5. **Write sections**, one idea each: proof bar → problem → 3-5 benefits (outcome headline + how + proof) → how it works (3-4 steps) → objections (FAQ, comparison, guarantee) → final CTA (recap + same CTA + risk reversal). Customer language over company language; benefits over features (feature → so that → outcome).
6. **Run the self-check**: `copy_lint.py`, then ai-tells.md self-check ("never" patterns in headlines, sentences > 20 words, "limit" patterns per section, read aloud). Fix by rewriting from facts, not synonym swaps.
7. **Edit pass** (for edit mode or your own draft): seven sweeps in order: clarity → voice → so what → prove it → specificity → emotion → zero risk, looping back to earlier sweeps after each change. For launch, pricing or high-traffic pages, score with a 3-4 lens reviewer panel until every lens ≥ 7 and average ≥ 8.
8. **Refresh mode**: read the current results page for the main query, grid coverage vs top 5, classify gaps (expected / common / distinctive / uncovered), propose a Keep/Revise/New outline and 2-3 titles, wait for approval, then rewrite. Keep the URL and ranking anchors; add a visible "Last updated" date and year next to every statistic.
9. **Deliver** with annotations, alternatives, meta content, open `[NEED]` flags, and a test suggestion (headline or CTA A/B via analytics-and-experiments).

## Checkpoints

- After step 2: core message and 5+ customer phrases agreed before drafting full pages.
- After step 4: hero options reviewed before writing the rest.
- Before delivery: lint clean or each remaining hit justified; every claim has proof or a flag.
- Refresh: outline approved before rewriting.

## Worked example

**Brief**: expense tool landing page for paid social traffic; ad promise "Receipts in 10 seconds"; audience agency finance leads; proof: 1,240 agencies, 4.8/5 (310 reviews), case study "close in 2 days instead of 5".
- Customer phrases: "chasing receipts", "the 28th dread", "card statements with no context".
- Weak original hero: "The all-in-one spend management solution for modern teams" (fails "Now you can…", fails swap test, two capped words).
- Candidates: (a) "Get every receipt 10 seconds after the card is used" (outcome + ad match) (b) "Stop chasing receipts at month-end" (problem) (c) "Expense cards for agencies that collect their own receipts" (audience + mechanism).
- Chosen: (a) headline, subhead "Your team snaps the receipt when the card pings. You close the month in 2 days, not 5. Used by 1,240 agencies." CTA "Start my 14-day trial" + "No card required".
- Sections: proof bar (4.8/5, logos) → problem in their words ("the last three days of every month") → 3 benefits (receipt capture, approval rules, accounting sync) → how it works (issue cards, team spends, books sync) → FAQ (accounting integrations first, from objection research) → final CTA.
- Lint: 0 bans; one long sentence split. Test proposed: (a) vs (b) headline.

## Pitfalls

- Clever or abstract headlines that need decoding; feature lists without "so that".
- Company language ("leverage our platform") instead of customer words.
- Unsupported superlatives, invented stats or testimonials; "trusted by thousands" without a count.
- Headline that doesn't match the ad or email that sent the visitor.
- Several competing CTAs of equal weight; weak CTA verbs (Submit, Learn more).
- Machine-sounding patterns: contrast reveals, negation lists, colon reveals, em dashes in short copy, buzzword stacks; and replacing them with new formulaic tics.
- Editing away the brand's voice; rewriting a ranking page and changing its URL or anchors.
- Manipulative psychology (fake scarcity, confirmshaming, hidden costs).

## Related skills

customer-research (language and proof), conversion-optimization (layout, forms, page tests), pricing-and-offers (offer and pricing page structure), email-sequences, paid-ads (ad copy), seo-optimization (titles, meta, refresh targeting), ai-search-optimization (answer blocks), analytics-and-experiments (copy tests).

## Done when

- [ ] One primary action; headline passes "Now you can…" and the swap test; matches the traffic source.
- [ ] Every section has one idea; benefits tied to outcomes; objections answered near the CTA.
- [ ] Claims have proof or `[NEED]` flags; nothing invented.
- [ ] Lint and self-check run; remaining hits justified.
- [ ] Alternatives (2-3) for headline and CTA with rationale; meta title/description included.
- [ ] Edit/refresh deliverables include reasons for every change (and approved outline for refresh).
