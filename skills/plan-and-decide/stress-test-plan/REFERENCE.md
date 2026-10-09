# Grill the Plan: reference

## Question bank by area

Use these to find decisions you have missed. Only ask the ones that are real for this topic, and only once their prerequisites are settled.

| Area | Questions that usually matter |
|---|---|
| Goal and success | Who is this for? What changes for them? How will we know it worked (metric, date)? What happens if we do nothing? |
| Scope | What is explicitly out? What is the smallest version that is still useful? Which part is fixed by an external deadline? |
| Users and roles | Who can do what? Is there an admin or support override? What about anonymous or suspended users? |
| Data | What is the source of truth? Which fields are new? What is the lifecycle (create, update, archive, delete)? Retention and export? |
| Existing behaviour | What must keep working exactly as today? Which callers or clients depend on current shapes? |
| Edge cases | Empty, duplicate, concurrent edits, very large input, partial failure halfway through, timezone and locale, clock skew. |
| Failure | What happens when a dependency is down? Retry or fail fast? Is the operation idempotent? Who gets alerted? |
| Security and privacy | Who must not see this? Is any data personal or regulated? What is logged? |
| Performance | Expected volume today and in 12 months? Latency budget? Batch or real-time? |
| Rollout | Feature flag? Migration of existing data? Backfill? Rollback plan? Who is told? |
| Operations | Who owns it after launch? What dashboard or alert proves it is healthy? |
| Cost | Third-party pricing, infrastructure, support load. |

## Choosing a recommendation

- Prefer the option that is easiest to reverse when the evidence is thin.
- Prefer what the codebase already does unless the user wants to change direction.
- Prefer the smaller scope; flag the bigger one as a later decision.
- If two options are genuinely equal, say so and pick one so the user can just say yes.

## When to write an ADR

Write one only when all three hold:
1. Hard to reverse (data model, public API, vendor lock-in, security posture).
2. Surprising to a future reader without the context.
3. A real trade-off with a rejected alternative worth naming.

Use the ADR format and numbering rule from `domain-glossary` (`templates/adr.md`: a title plus one to three sentences; Status, Considered options and Consequences only when they add something). Number files `NNNN-kebab-title.md`, one above the highest in `adr_dir`.

## Workflow mode

Use when the topic is a recurring piece of work the user wants specified so it can be automated or delegated (a weekly report, triaging inbound email, publishing release notes). The output is one spec file per workflow, by default `workflows/<name>.md`, plus a `NOTES.md` that records the user's tools, channels and vocabulary.

Vocabulary (use it only where the workflow needs it; mandate nothing structural):

| Term | Meaning | Questions it raises |
|---|---|---|
| Loop | A recurring pattern in the user's work or life (daily, weekly, per event). Spotting loops shows what is predictable enough to delegate. | Which loops recur? Which feel tedious but predictable? |
| Workflow | The written spec of one loop; running it is one iteration of the loop. | What is the input, the output, and who consumes it? |
| Trigger | What starts a run: an event (new email, new issue, file lands) or a schedule (every Monday 09:00). Prefer events when available. | Is there an event we can hook instead of polling? |
| Checkpoint | A point where a human verifies or decides. A workflow may have none. | Which step genuinely needs judgment? Can it be moved later? |
| Push right | Put the checkpoint as late as possible so the human is asked once, with everything prepared. | What can be done before asking? |
| Brief | What a checkpoint shows: a short decision-ready summary with a link to the full asset, never the raw output. | What does the human need to decide in under a minute? |

Workflow-mode rules:
- If `NOTES.md` is empty or thin, interview about the user's world (tools, channels, recurring obligations) before specifying anything.
- Sharpen fuzzy terms into canonical ones and record them in `NOTES.md`.
- Create, edit, or delete spec files as the interview settles things.
- Done when an implementer could build the workflow without asking a single question.
