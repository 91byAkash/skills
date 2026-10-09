# Map a Large Effort: reference

## Ticket types

| Type | Who drives | Resolved by | Use when |
|---|---|---|---|
| research | agent alone (AFK) | a sub-agent following research-primary-sources; findings linked from the ticket | a fact outside the working directory is needed (third-party API limits, pricing, standards) |
| prototype | with the human (HITL) | prototype-to-decide; artifact linked | "how should it look / behave" is the open question |
| interview | with the human (HITL) | stress-test-plan plus domain-glossary | default; a conversation settles it |
| task | either | doing the enabling chore | nothing to decide yet, but a decision is blocked until something is done (provision access, sign up for a trial, export sample data) |

## Fog or ticket?

Test: can you state the question precisely now? (Not: can you answer it now.)
- Precise but blocked → ticket, with blocked-by links.
- Vague, still in scope → Unresolved fog. One fog patch may later become several tickets, or none.
- Beyond the destination → Ruled out (close the ticket if one exists).

## Trackers

Preferred: the tracker's native parent/child and blocked-by relations, so the frontier is visible in its UI.

Fallback when the tracker has no native blocking: add a line `Blocked by: <ticket name> (<link>)` at the end of the ticket body and check those links when computing the frontier.

Local Markdown tracker (no issue tracker available):
```
.maps/<map-slug>/
  MAP.md                 # map body
  tickets/
    001-token-format.md  # front matter: type, status (open|closed), assignee, blocked_by: [002]
    002-gateway-jwt.md
```
Frontier query: tickets with `status: open`, empty `assignee`, and every id in `blocked_by` closed. `scripts/frontier.py .maps/<map-slug>` computes it (and checks for cycles); front matter format is in the header of `templates/ticket.md`.

## Concurrency

- Several sessions may work frontier tickets at once. Claim by assigning before reading deeply.
- Re-read the map immediately before appending to Decision log; append, never rewrite others' lines.
- If two sessions produced conflicting decisions, open an interview ticket naming both.

## Sizing a ticket

A ticket should fit one focused session: one question, a handful of files or sources, a decision expressible in a few lines. If a resolution would need several unrelated decisions, split it before claiming.
