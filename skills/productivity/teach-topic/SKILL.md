---
name: teach-topic
description: "Teach the user a topic over several sessions with a persistent workspace (mission, sources, glossary, short interactive lessons, learning records), using retrieval and spacing. Use when the user says \"teach me\", \"help me learn\", \"I want to get good at\", or asks for a course, lessons or practice. Not for a one-off question (just answer) or learning a codebase (use codebase-orientation)."
license: MIT
metadata:
  category: "productivity"
  version: "3.0.0"
---

# Teach a topic

Learning is stateful. Every session reads the workspace, teaches one small thing tied to the user's mission, checks it, and records what changed.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `topic` | required | — | "SQL window functions", "beginner yoga", "Kannada for travel" |
| `workspace` | optional | current directory | `~/learning/sql/` |
| `mission` | optional | interview the user if `MISSION.md` is missing | "write the monthly cohort report myself instead of asking the data team" |
| `level` | optional | established in the first session | "can write joins, never used GROUP BY with HAVING" |
| `session_minutes` | optional | 15 | 30 |
| `format` | optional | HTML lessons opened in the browser | Markdown if no browser |
| `lesson_request` | optional | next item in the zone of proximal development | "today: LAG and LEAD" |

## Output

Files in `workspace` (created lazily):

| Path | Purpose |
|---|---|
| `MISSION.md` | why they are learning; what success looks like; constraints; out of scope |
| `RESOURCES.md` | annotated, high-trust sources (knowledge) and communities (wisdom); gaps |
| `GLOSSARY.md` | canonical terms the user has understood |
| `lessons/NNNN-<slug>.html` | one short, self-contained lesson per file |
| `reference/<topic>.html` | compressed cheat sheets the user will revisit |
| `learning-records/NNNN-<slug>.md` | what is now known, misconceptions fixed, prior knowledge |
| `assets/` | shared stylesheet, quiz widget, other reusable components |
| `NOTES.md` | teaching preferences (pace, examples they like, dislikes) |

## Supporting files

- [REFERENCE.md](REFERENCE.md): formats for every workspace file, lesson design rules, quiz-writing rules, when to write a learning record, and learning-science notes. Read at the first session and whenever you create a new file type.
- [templates/lesson.html](templates/lesson.html): lesson skeleton (goal, example, explanation, practice with instant feedback, primary source, follow-up prompt). Copy for each lesson.
- [templates/course.css](templates/course.css) and [templates/quiz.js](templates/quiz.js): first shared assets; copy into `assets/` on the first lesson and reuse.

## Steps

**First session**
1. **Mission interview** (skip if `MISSION.md` exists): why this topic, what they will be able to do when done (observable), time per week, deadline, prior experience, what is out of scope. Push back on vague goals ("understand X") until there is a concrete one. Write `MISSION.md`.
2. **Find resources**: search for primary and high-trust sources (official docs, standard textbooks, respected courses, recognised practitioners) and moderated communities. Verify they exist and are current. Do not teach from memory on facts that may have changed. Write `RESOURCES.md` with a one-line note per entry and a Gaps section.
3. **Gauge level** with 3–5 quick diagnostic questions or tasks; record prior knowledge as learning records.

**Every session**
4. **Read state**: mission, notes, glossary, latest learning records, list of lessons.
5. **Pick the target**: the user's request, or the most mission-relevant skill just beyond what records show they can do (zone of proximal development). One skill per lesson.
6. **Warm up with retrieval**: 2–3 questions on earlier lessons, mixing in older material (spacing, interleaving for skills).
7. **Build the lesson** from the template and shared assets: one goal; a concrete example first; only the knowledge needed for the skill, with citations; a practice task with immediate feedback; a recommended primary source; a reminder to ask follow-up questions. Completable within `session_minutes` (rule of thumb: one example plus 3 practice items per 15 minutes). Open it for the user if possible. With `format=markdown`, write `lessons/NNNN-<slug>.md` in the same section order and put each quiz answer and its why inside a `<details>` block under the question.
8. **Check understanding** by having the user produce something (answer, query, pose sequence, sentence). Give targeted feedback on their answer; do not re-lecture.
9. **Record**: write a learning record when they showed real understanding, disclosed prior knowledge, fixed a misconception, or the mission shifted. Add newly understood terms to `GLOSSARY.md`. Update or create the reference sheet. Note preferences in `NOTES.md`.
10. **Close**: say what comes next and when to review (e.g. tomorrow, then in 3 days, then a week).

## Checkpoints

- Before the first lesson: mission confirmed by the user.
- Before changing the mission: confirm, update `MISSION.md`, and record the shift.
- Questions that need lived experience ("is my form right?", "how do teams really do this?"): give your best answer and point to a community from `RESOURCES.md`.

## Worked example

Topic: SQL window functions. Mission: "build the monthly cohort retention report myself by end of the month". Level: joins and GROUP BY fine; never used `OVER`.

Lesson `0003-running-totals.html`:
- Goal: "Write a running total of signups per day."
- Example first: a 6-row table of daily signups and the result column, then the query `SUM(signups) OVER (ORDER BY day)`.
- Knowledge: what `OVER` does, default frame, link to the official docs section on window frames.
- Practice: three quiz items with equal-length options (instant feedback via `assets/quiz.js`) and one task: "running total per country" (answer revealed after an attempt).
- Primary source: the database's official tutorial page on window functions.

User answers the task with `PARTITION BY country` but forgets `ORDER BY` → feedback on frame ordering → correct on retry. Learning record `0004-partition-vs-order.md`: "Understands PARTITION BY; initially omitted ORDER BY in the window, fixed after seeing unordered results." Glossary gains **Window frame**. Next: `LAG` for month-over-month change, review running totals in 3 days.

## Pitfalls

- Long lectures that exceed working memory; one skill per lesson.
- Lessons disconnected from the mission (abstract exercises the user does not care about).
- Teaching fast-moving facts from memory instead of cited sources.
- Mistaking fluency (it feels easy right now) for retention; always come back later with retrieval.
- Quizzes that leak the answer (longest option, always option B, grammatical hints).
- Rebuilding styles and widgets per lesson instead of reusing `assets/`.
- Adding glossary terms the user has not yet understood.

## Done when (per session)

- [ ] Mission exists and the lesson ties to it.
- [ ] The lesson teaches one skill, cites sources, includes practice with immediate feedback, and fits the session length.
- [ ] The user produced an answer and got feedback on it.
- [ ] Learning records, glossary, reference sheet, and notes are updated as warranted.
- [ ] Next step and review timing were stated.
