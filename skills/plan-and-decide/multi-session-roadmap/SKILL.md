---
name: multi-session-roadmap
description: "Chart an effort too big for one session as a map of decision tickets (research, prototype, interview, task) and resolve one per session. Use when an idea is clearly multi-session (\"rebuild onboarding\", \"migrate the data layer\"), several people or agents will share it, or the user wants a roadmap of decisions. Not for slicing a decided plan into build tasks (use plan-tasks)."
license: MIT
metadata:
  category: "plan-and-decide"
  version: "3.0.0"
---

# Multi-Session Roadmap

Find the way before charging at the destination. The map is planning: each ticket settles a decision, and the map is finished when nothing is left to decide before someone goes and builds.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `idea` or `map` | yes | – | idea: "Replace our homegrown auth"; map: issue URL/number to continue |
| `mode` | optional | `chart` if given an idea, `work` if given a map | `work` |
| `tracker` | optional | the repo's configured issue tracker; else local Markdown in `.maps/<slug>/` | GitHub Issues, Linear, local |
| `ticket` | optional (work mode) | first frontier ticket | "Decide session storage" |
| `assignee` | optional | the person driving the map | `@me` |
| `notes` | optional | none | "Domain: payments. Consult domain-glossary. Execution allowed inside the map." |

## Output

- **Map issue** labelled `map` with a Destination line and sections Standing notes, Decision log, Unresolved fog, Ruled out ([templates/map.md](templates/map.md)).
- **Ticket issues** as children of the map, each labelled with one type (`map:research`, `map:prototype`, `map:interview`, `map:task`), body = one question sized for one session ([templates/ticket.md](templates/ticket.md)), blocked-by links using the tracker's native dependencies.
- Per worked ticket: a resolution comment, the ticket closed, and one line appended to the map's Decision log.

## Supporting files

- [templates/map.md](templates/map.md): map body. Use when charting.
- [templates/ticket.md](templates/ticket.md): ticket body and resolution comment. Use for every ticket.
- [REFERENCE.md](REFERENCE.md): ticket-type table, fog vs ticket test, local-Markdown tracker layout, concurrency rules. Read before charting the first time or when using a tracker without native blocking.
- [scripts/frontier.py](scripts/frontier.py): for the local Markdown tracker, lists frontier / claimed / blocked / closed tickets and fails on unknown blocker ids, bad types, or blocking cycles. Run after wiring (chart step 4) and at the start of every work session.

## Rules

- **One ticket per session**, except research tickets, which may run in parallel sub-agents.
- **Refer by name.** In anything a human reads, use the ticket title with its link inside, never a bare `#42`.
- **The map is an index, not a store.** A decision lives only in its ticket; the map gives a one-line gist plus link.
- **Claim first.** Assign the ticket to the driver before any work; an open, unassigned ticket is unclaimed.
- **Frontier** = open, unblocked (all blockers closed), unclaimed tickets.
- **HITL tickets need the human.** Prototype and interview tickets resolve only through a live exchange; never answer your own questions.
- **Only map labels** on map and tickets; no implementation or triage labels; they are decisions, not build work.

## Steps: chart mode

1. **Name the destination.** Grill the user (see `stress-test-plan`) until you can write 1-2 lines describing what "arrived" looks like: a spec ready to hand off, a locked decision, or an in-place change. The destination fixes scope.
2. **Survey breadth-first.** Fan out across the whole space, not deep on one thread: list open decisions and the first steps takeable now.
   - If no fog appears (everything fits one session), then stop: say a map is unnecessary and ask how to proceed.
3. **Create the map issue** from the template: Destination and Standing notes filled, Decision log empty, fog written into Unresolved fog.
4. **Create tickets you can state precisely now**, as children of the map. Then, in a second pass (ids now exist), wire blocking edges and cross-references with real ids. Never write placeholder ids; they auto-link to unrelated issues. Local tracker: run `scripts/frontier.py .maps/<slug>` and fix every PROBLEM line before moving on.
5. **Launch research tickets** in parallel sub-agents using `research-primary-sources`; each writes findings to a throwaway `research/<slug>` branch or note and links it from the ticket.
6. **Stop.** Charting is a whole session; it resolves nothing by hand. Report: destination, number of tickets, frontier list by name.

## Steps: work mode

1. **Load the map body only** (low-res view); fetch other ticket bodies only when needed.
2. **Choose**: the named `ticket`, else the first frontier ticket (local tracker: the first line under FRONTIER from `scripts/frontier.py`). Claim it by setting `assignee`.
3. **Resolve by type** (read the label; the body never states the type):
   - research → sub-agent with `research-primary-sources`;
   - prototype → `prototype-to-decide`, link the artifact;
   - interview → `stress-test-plan` plus `domain-glossary`;
   - task → do the enabling chore (create an account, export sample data) and report what it unblocks.
4. **Record**: resolution comment (answer, rationale, links to assets), close the ticket, append `- [<title>](link): <one-line gist>` to Decision log.
5. **Update the map**: create newly visible tickets (create, then wire); graduate fog that is now specific into tickets and delete it from Unresolved fog; if a ticket turns out beyond the destination, close it and add one line to Ruled out with the reason; edit any ticket the decision invalidates.
6. **Check arrival.** If the frontier is empty and Unresolved fog is empty, then the way is clear: tell the user the map is complete and name the hand-off (`write-spec`, `plan-tasks`).

## Checkpoints

- Destination fits in two lines and every ticket plausibly serves it.
- Every ticket body is a single question answerable in one session.
- After wiring: at least one ticket is on the frontier; no cycles in blocking.
- After each resolution: the decision appears exactly once (its ticket) and the map has only the gist.

## Worked example

Idea: "Move from session cookies to token auth for the mobile app."
- Destination: "An approved spec for token auth covering web and mobile, ready for plan-tasks."
- Tickets created: `Which token format and lifetime?` (interview); `Does our gateway validate JWTs natively?` (research); `Refresh-token rotation UX on mobile` (prototype, blocked by token format); `Get staging access to the identity provider` (task).
- Unresolved fog: "logout everywhere semantics", "service-to-service auth" (cannot phrase sharply yet).
- Ruled out: "SSO for enterprise customers" (beyond destination).
- Session 2 works the interview ticket: decision "opaque access tokens, 15 min; rotating refresh tokens, 30 days" → closed, gist added; prototype ticket becomes frontier; "logout everywhere" graduates into an interview ticket.

## Pitfalls

- Pre-slicing fog into tiny tickets you cannot yet phrase; fog is coarser than tickets.
- Putting out-of-scope work in Unresolved fog; scope, not sharpness, decides.
- Resolving several tickets in one session, which blurs decisions and skips claims.
- Restating decisions in the map, which then drifts from the tickets.
- Doing the build inside the map without a Standing notes entry allowing it; the urge to build is the sign you reached the edge of the map.
- Forgetting that other sessions may edit the tracker concurrently; re-read before writing.

## Done when

- [ ] Chart mode: map exists with destination, notes, fog and out-of-scope; tickets created and wired; research launched; frontier reported by name.
- [ ] Work mode: exactly one ticket resolved (plus research), closed with a resolution comment, gist appended, map updated.
- [ ] Arrival: frontier and Unresolved fog both empty, hand-off named.
