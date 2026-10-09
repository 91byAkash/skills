# Shape session sheet

Keep this in the conversation, or in a scratch file beside the article (never in the raw pile, which is read-only). Record each landed block with `scripts/ledger.py land`.

## 1. Settings
- Raw pile (read-only): `<path>`
- Article file: `<path>`
- Reader: <who, what they already do and know>
- Takeaway: <the one sentence a reader should leave with>
- Length / venue: <e.g. ~1,200 words, team blog>

## 2. Prerequisites (grounded before the opening)
| Concept | Why the reader already has it |
|---|---|
| deploy pipeline | readers are engineers who ship weekly |

Everything not listed here must be grounded by a block before a later block uses it.

## 3. Candidate openings (2-3, each implying a different thesis)
| # | Opening (draft text) | Thesis it commits to | Requires | Grounds |
|---|---|---|---|---|
| A | "Our deploys take 14 minutes. A year ago they took six." | slowness crept in, nobody chose it | deploy pipeline | slow deploys |
| B | "Every team added one check. Nobody removed one." | ownership, not tooling, is the problem | CI check | gate |
| C | "We can't remove it, we don't know who owns it." | orphaned checks are a social bug | - | orphaned check |

The user picks one or composes a hybrid. The choice defines what the rest must deliver.

## 4. Block log
| # | Block (one line) | Form | Why this form | Requires | Grounds |
|---|---|---|---|---|---|
| 1 | | paragraph | carries an argument | | |

## 5. Gaps found in the pile
- <"need an example of a gate that caught a real bug": ask the user, or cut the section>

## 6. Challenges to raise during the session
- Redundancy: name what the reader gains from this block that the block before did not give them. If nothing, merge or cut.
- Load-bearing test: delete the block in your head and read on. If no later block stumbles, it goes.
- Form: a list hides the links between items; prose hides parallel structure. Say which this block needs and why.
- Overloaded sentence: when one sentence carries two claims, give each its own sentence or drop the weaker one.
- Drift: compare the current block with the promise the opening made. If they no longer match, bend the text back or rewrite the opening to fit where the piece actually went.
