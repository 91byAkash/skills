# Brainstorm Ideas: reference

## Red flags (thought → what to do instead)

| Thought | Do instead |
|---|---|
| "This is too simple to need a design." | Follow the path: two sentences in chat for bounded, a spec for architectural. |
| "I'll call it bounded and skip the spec." | Doubt about the label means take the heavier path. |
| "The design is obvious, I'll start while they read it." | Present, then stop until you hear yes. |
| "I know this kind of app, so it's bounded." | Bounded is about the repo: is the flow already here to read? A new project is architectural. |
| "The spike worked, I'll keep the code." | A spike answers a question. Keeping code is a new request. |
| "It grew but I'm nearly done." | Stop, say it grew, upgrade the path. |
| "They approved the spike, so the follow-up is approved." | Each task gets its own classification and approval. |

## Approach comparison table

Use for step 5. Keep rows the same across options so they are comparable.

| Row | What to write |
|---|---|
| Summary | one line |
| How it works | 2-3 lines, mention the key component or data change |
| Benefit | the main reason to choose it |
| Cost / risk | the main reason not to |
| Effort | S (≤1 day), M (≤1 week), L (more) |
| Reversibility | easy / moderate / hard |
| Rules out | what becomes harder later |

## Spec reviewer checklist

You can run this yourself or hand it to a reviewer sub-agent with the spec path. Only flag problems that would cause a flawed implementation plan; style nits and uneven section depth do not count.

| Category | Look for |
|---|---|
| Completeness | TODO, TBD, placeholder text, empty sections |
| Consistency | contradictions between sections or with the architecture |
| Clarity | requirements ambiguous enough to build the wrong thing |
| Scope | more than one independent subsystem in a single spec |
| YAGNI | features or options nobody asked for |

Reviewer output format:
```
## Spec review
Status: Approved | Issues found
Issues:
- [Section]: <issue> - <why it matters for planning>
Recommendations (advisory):
- ...
```

## Review request wording

"Spec written and committed to `<path>`. Please review it and tell me what to change before I break it into an implementation plan."

## Visual mockups

- Offer visuals only when a question is genuinely about looks, layout, or spatial relationships (wireframes, side-by-side layouts, architecture or state diagrams). A question about a UI *topic* ("what should 'friendly' mean here?") is still a text question.
- Make the offer its own short message and wait for the answer. If declined, do not offer again.
- Decide per question: would the user understand this better by seeing it? If not, stay in text.
- Generate a page with `scripts/mockup.sh` (fragment in, standalone HTML out), keep options side by side, label each with a letter, and ask the user to answer in chat with the letter.
- Store mockups in a git-ignored folder such as `.scratch/mockups/`.
