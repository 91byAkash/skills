# Teach topic: reference

## Contents
- Learning science in brief
- MISSION.md
- RESOURCES.md
- GLOSSARY.md
- Learning records
- Lesson design
- Quiz rules
- Reference sheets
- Assets

## Learning science in brief

- **Knowledge vs skill**: knowledge is acquired (keep it easy to take in; difficulty wastes working memory); skill is built by effortful practice (difficulty is the tool).
- **Fluency vs storage strength**: feeling fluent right after a lesson predicts little; durable memory comes from retrieving after a delay.
- **Retrieval practice**: ask before you tell; recall beats rereading.
- **Spacing**: review at growing intervals (1 day, 3 days, 1 week, 2–3 weeks).
- **Interleaving**: mix related problem types in practice once each is learned individually (skills, not first exposure).
- **Worked examples → faded examples → independent problems** for novices.
- **Immediate, specific feedback** on the learner's own output.
- **Wisdom** comes from practice with real people; point to communities for judgment calls.

## MISSION.md

```md
# Mission: <topic>

## Why
<1–3 sentences: the concrete real-world goal and what changes when they reach it>

## Success looks like
- <observable ability, e.g. "write the cohort retention query without help">
- <…>

## Constraints
- <time per week, deadline, budget, equipment, preferences>

## Out of scope
- <adjacent topics deliberately excluded for now>
```
Rules: one mission per workspace; concrete over abstract; under one screen; revise when goals change (and record the change).

## RESOURCES.md

```md
# <Topic> resources

## Knowledge
- [Official docs: Window functions](https://…)
  Authoritative syntax and semantics. Use for: frame clauses, function list.

## Wisdom (communities)
- [<moderated forum or group>](https://…)
  Active, well-moderated. Use for: query reviews, real-world patterns.

## Gaps
- No good beginner material on <subtopic> yet.
```
Rules: high-trust only (primary sources, recognised experts, peer-reviewed, moderated communities); annotate every entry with what it covers and when to use it; prune wrong or shallow entries; list gaps to drive future search.

## GLOSSARY.md

```md
# <Topic> glossary
<one sentence on scope>

## Terms
**Window frame**:
The set of rows, relative to the current row, that a window function reads.
_Avoid_: window range, scope
```
Rules: add a term only once the user understands it; pick one word per concept and list avoided aliases; one or two sentences, saying what it is; use glossary terms inside other definitions; every lesson follows the glossary.

## Learning records

`learning-records/NNNN-<slug>.md`, numbered sequentially (highest + 1), folder created when first needed.
```md
# <What is now known or established>
<1–3 sentences: what was learned or disclosed and why it matters for what to teach next.>
```
Optional: `Status: active | superseded by NNNN`, **Evidence** (how they showed it), **Implications** (what it unlocks or rules out).

Write one when: the user demonstrated real understanding of something non-trivial; disclosed prior knowledge (record the depth claimed); a misconception was corrected; the mission shifted.

## Lesson design

- File: `lessons/NNNN-<dash-slug>.html`, self-contained except for `../assets/` links.
- Structure: goal (one sentence, a skill) → concrete example → minimal explanation with citations → practice with immediate feedback → recap (3 bullets) → primary source → "ask me anything that is unclear" prompt → links to previous/next lessons and reference sheets.
- Short: completable in the session length; one tangible win.
- Clean typography (readable measure, generous whitespace, high contrast); printable.
- For physical skills (yoga, cooking, music): a checklist of real-world steps with what "good" looks and feels like, and safety notes; ask the user to report back.
- For code: runnable snippets and a small task with the expected output.

## Quiz rules

- Every option the same length (words, and characters where possible) and grammatically parallel.
- Vary the correct position across questions; no "all of the above".
- Plausible distractors drawn from real misconceptions.
- Explain why each wrong option is wrong in the feedback.
- Prefer production (type the answer, write the query) over recognition when practicing skills.

## Reference sheets

Compressed essence for later lookup: syntax tables, algorithms, sequences, routines, glossaries. Update after each lesson. Lessons link to them; users revisit these more than lessons.

## Assets

Start with a shared stylesheet and quiz widget (templates in this skill). Before authoring a lesson, check `assets/` and reuse; when a lesson needs something reusable (a simulator, diagram helper, flashcard widget), build it as an asset and link it.
