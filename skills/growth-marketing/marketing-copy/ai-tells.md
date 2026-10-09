# Machine-sounding copy: what to flag and how to fix it

Readers who decide a page was generated stop trusting its claims, so treat the patterns below as defects. Two strengths apply:

- **Never**: remove on sight.
- **Limit**: acceptable once in a section when chosen on purpose; a defect when it repeats or several appear together.

"Short copy" means headlines, subheads, hero text, CTAs, ads, social posts and email subject lines. A "section" is one hero, one page section or one short post. Button microcopy such as "No card required" is exempt from the limits.

Labels in `code` match the categories that `scripts/copy_lint.py` prints, so a lint hit can be looked up here.

## A. Sentence shapes (check these first)

Word lists miss these; shape is what gives most drafts away.

- **`contrast-reveal`** (never). A denial of something nobody claimed, followed by the "real" point: "It's not X, it's Y", "Not because X. Because Y.", "Not just X, but Y". Fix: state the point directly with its reason. *Draft:* "Ideas don't launch. Not because they're bad. Because they need a developer." *Fixed:* "Ideas stall because each one needs a developer you can't get."
- **`negation-list`** (never). Three or more "no X" items in a row. Fix: say what the product does; keep at most one absence, near the CTA. *Fixed:* "Install from the app store and it runs on your own data within five minutes."
- **`trailing-pile-on`** (never). A claim followed by comma clauses that repeat it, often ending in "…, ensuring …". Fix: one claim, one supporting fact, full stop.
- **`self-answered-question`** (never outside FAQs). "The result? Onboarding in minutes." Fix: give the result as a statement with its number.
- **`colon-reveal`** (never). "The best part: it learns." Fix: "It learns your approval rules within a week."
- **Fragment drumbeat** (limit 1 per section). "Fast. Simple. Yours."
- **`reflexive-threes`** (limit 1 per section). Every list has exactly three items. List as many as are true.
- **`em-dash-in-short-copy`** (never in short copy; one or two per page of long copy). Use a full stop or a comma.
- **Flat rhythm** (limit). Every sentence the same length; alternate short and long.
- **Avoiding plain verbs** (limit). "serves as", "boasts", "stands as". Use "is", "has" or the real verb ("The dashboard shows…").
- **Abstract actors** (limit). "Innovation drives results." Make a person or the product do the action.
- **Empty spans** (limit). "From startups to enterprises." Name the customer you actually serve.
- **Rotating synonyms** (limit). Customer, user, client and member in one paragraph. Pick the reader's word and repeat it.

## B. Openings and endings (never)

Cut the warm-up and start with the subject. Lint reports these as `stock-opener` (era and scene-setting openers such as "In today's fast-paced market", "In an era of…", "Are you tired of…", "Look no further", plus any line that starts with "Imagine", "Picture this", "Whether you're", "When it comes to" or "In a world") and `connective-filler` ("Moreover", "Additionally", "Furthermore", "It's worth noting", "It's important to note"). Preambles ("Here's the thing", "Simply put", "Rest assured") and tour-guide lines ("Without further ado", "Let's dive in") count as openers too. For endings, drop the wrap-up ("In conclusion", "At the end of the day") and the grand closer (`fake-kicker`: "And that changes everything."). Stop on the last concrete point or on the CTA.

## C. Stock marketing lines (never), with replacements

A stock line is a placeholder for a fact the writer has not found yet. Lint reports most of them as `stock-claim`. Ask which kind of fact is missing, then write it.

- **A number is missing.** Lines promising scale, speed, ease or a leap forward ("unlock the power of…", "take it to the next level", "effortless", "at your fingertips", "join thousands of happy customers") all dodge a measurement. Give the step count, the minutes, the percentage, or the customer count you can actually defend. Example: "Most teams send their first invoice 6 minutes after signing up."
- **A before and after is missing.** Change slogans ("transform the way you work", "like never before", "X, reimagined", "game-changer") need the old routine and the new one side by side, ideally both measured. Example: "Month-end used to take the finance team four days. Now the ledger matches the bank every morning and they check only the mismatches."
- **The buyer is missing.** Audience and comfort slogans ("the X you deserve", "peace of mind") should name who buys and the moment they go looking. Example: "For clinic managers who discover on Monday that Friday's rota has holes."
- **The product is missing.** Scope slogans ("everything you need", "all-in-one", "one-stop shop", "the future of X is here") should list the two or three capabilities buyers compare, and only what is live today.

## D. Words

Fashionable words drift, so treat these as current examples; sections A and E stay useful longer. Replace a flagged word with the fact behind it ("robust" → "99.99% uptime over two years"; "seamless" → "imports your billing history in about 90 seconds"); a synonym is just a new tell.

The groups below are the exact vocabulary `scripts/copy_lint.py` checks, under the same labels it prints. Single words also catch their inflections ("unlocks", "elevated", "seamlessly"), and hyphenated entries also match the spaced form. "Never" entries are flagged every time. "Limit" entries are tolerated once in a section; two from the hype, adjective or abstraction groups in one line come back as `buzzword-stack`, which means rebuild the paragraph. To change the vocabulary, edit `WORD_GROUPS` in the script, run `copy_lint.py --vocab`, and paste the output between the markers.

- **Hype verbs** promise motion without saying what moves.
- **Inflated adjectives** claim quality without a measure.
- **Vague abstractions** name a category of benefit instead of the benefit.
- **Filler intensifiers** add emphasis and no information.
- **Chatbot vocabulary** is ornate wording that marketers rarely use and generated text uses constantly.
- **Stock openers, stock claims, unsourced proof and connective filler** are covered in sections B, C and E.

<!-- lint-vocabulary:start -->
- **`hype-verb`** (limit): unlock · elevate · empower · harness · supercharge · unleash · streamline · revolutionize · reimagine · skyrocket · amplify · democratize · future-proof · level up.
- **`inflated-adjective`** (limit): seamless · robust · cutting-edge · world-class · revolutionary · game-changing · next-gen · state-of-the-art · groundbreaking · unparalleled · unmatched · frictionless · effortless · intuitive · industry-leading · mission-critical.
- **`vague-abstraction`** (limit): solution · ecosystem · synergy · paradigm shift · actionable insights · end-to-end · one-stop shop · value-add · touchpoint · north star · move the needle · low-hanging fruit.
- **`filler-intensifier`** (limit): truly · incredibly · literally · actually · really · very · just · basically · extremely · absolutely · remarkably · exceptionally · undeniably · profoundly.
- **`chatbot-vocabulary`** (never): delve · tapestry · testament to · realm · embark · meticulous · myriad · underscore · bustling · symphony of · labyrinth · treasure trove · navigate the complexities · unwavering.
- **`stock-opener`** (never): in today's fast-paced · in today's digital age · in an era of · look no further · are you tired of · ready to take your · let's dive in · here's the thing · rest assured · simply put · without further ado.
- **`stock-claim`** (never): game-changer · take it to the next level · the future of · transform the way · everything you need · all-in-one · join thousands · you deserve · unlock the power · this changes everything · peace of mind · at your fingertips · like never before · the possibilities are endless.
- **`unsourced-proof`** (never): studies show · research shows · experts agree · leading experts · widely regarded.
- **`connective-filler`** (never): additionally · moreover · furthermore · it's worth noting · it's important to note · in conclusion · at the end of the day · great question.
<!-- lint-vocabulary:end -->

## E. Claims, voice and layout

| Problem | Example | Do instead |
|---|---|---|
| Qualifiers piled on one verb | "may help to possibly lower" | Claim only what you can show, and shrink the claim until you can |
| Inflated importance | "a watershed moment for the industry" | State the fact |
| Unnamed authorities (`unsourced-proof`, `vague-proof`) | "studies show", "experts agree", "widely regarded", "trusted by thousands" | Cite the source or remove the claim |
| Coined labels | "the integration tax" | Use only if defined once and reused across the site |
| Over-familiar or fake-candid openers | "Great question!" (`connective-filler`), "I'll be honest, I was skeptical too…" | Remove unless a true story follows |
| Announcing an explanation instead of giving it | "Here's how it works", "Picture it like this…" | Start with the explanation itself |
| `hype-punctuation` | "!!", "?!" | None in body copy |
| Decorative layout | emoji bullets in B2B, a bold label on every bullet, bullets all opening with the same verb ("Ensures… Provides… Enables…"), Title Case Everywhere, Unicode ornaments, "What / Why / How" headings | Headings that make a claim, varied bullet grammar, sentence case |

## F. How to rewrite

- Go back to the facts (mechanism, number, customer, step) and write from them; swapping words only produces new tells.
- Each claim sentence should carry at least one number, name, mechanism or concrete action.
- Competitor test: if the line would read just as well on a rival's site, it is not done.
- A paragraph carrying more than one "limit" pattern gets rebuilt from its facts; patching individual words leaves the shape intact.
- Never invent a figure to sound specific; leave `[NEED: proof]` and ask.
- Use rhetorical devices deliberately; the same device in every line is a habit, and so is fixing every reveal the same way (", because…").
- Keep the brand's register; a formal sentence with a specific claim is fine.
- If no headline passes the competitor test, ship the strongest one and flag the missing differentiator.

## G. Self-check before handing over

- [ ] Run `scripts/copy_lint.py draft.md`; fix or justify every hit.
- [ ] Section A shapes hide behind a few characters. In short copy only, find every negation (`not `, `isn't`, `no `, `without`), question mark, colon and dash, and decide for each one whether it forms one of those shapes.
- [ ] Re-read every sentence longer than 20 words; more than two commas usually hides a pile-on.
- [ ] Count limited patterns per section (fragments, threes, limited words).
- [ ] Read the copy aloud and mark anything you would not say to a customer face to face.
