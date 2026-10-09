# Domain Glossary Reference

## Entry rules

- **Be opinionated.** Where several words exist for one concept, choose one; put the rest under *Avoid*.
- **Tight definitions**: one or two sentences, saying what the thing *is*.
- **Project-specific only.** If a new hire from another industry would already know the word's meaning here, leave it out.
- **Group** under subheadings (Ordering, Payments, Fulfilment) once clusters appear; a flat list is fine when small.
- **Distinguish neighbours** with "Not to be confused with" when two terms are often mixed up.
- **Statuses and lifecycle states** deserve entries when they carry business meaning (e.g. *Pending Settlement*).

## Scenario probes

Use concrete edge cases to force precision:

| Concept type | Probe |
|---|---|
| Lifecycle | "What happens to X if Y happens halfway through?" (Order with one item out of stock) |
| Identity | "If the same person signs up twice with different emails, is that one Customer or two?" |
| Ownership | "When a Member leaves a Team, who owns the Projects they created?" |
| Quantity / money | "Is a Discount applied before or after Tax? Per line or per Order?" |
| Time | "Does a Trial end at midnight in the Customer's zone or ours?" |
| Reversal | "Can a Shipment be un-dispatched? What do we call that?" |
| Plurality | "Can an Invoice cover several Orders? Can an Order have several Invoices?" |

## What qualifies for an ADR

All three must hold: hard to reverse, surprising without context, real trade-off.

Typical qualifiers:
- architectural shape (monorepo; event-sourced writes with projected reads)
- integration style between contexts (events vs synchronous calls)
- technology with lock-in (database, message bus, identity provider, hosting)
- ownership and scope boundaries, including explicit "no"s
- deliberate deviations from the obvious path (hand-written SQL instead of an ORM, and why)
- constraints invisible in code (compliance region, partner latency contract)
- rejected alternatives whose rejection is non-obvious

Not ADRs: library picks that are cheap to swap, naming choices (those go in the glossary), anything you would simply reverse if wrong.

ADR format ([templates/adr.md](templates/adr.md)): a title that states the choice and one short paragraph saying what was chosen over what, and why. Lifecycle (`proposed | accepted | deprecated | replaced by NNNN`), rejected alternatives and knock-on effects are optional lines, added only when a future reader would otherwise have to rediscover them.

## Multi-context repos

- `GLOSSARY-MAP.md` at the root lists contexts, where each glossary lives, and how contexts relate (events, shared types).
- The same word may legitimately mean different things in two contexts (*Account* in Billing vs Identity). Record each in its own glossary and note the mapping in the map's relationships section.
- System-wide decisions go in root `docs/adr/`; context-only decisions in that context's `docs/adr/`.

## Renames

- Small, internal names: rename in the same change as the glossary update.
- Public names (API fields, DB columns, event names, URLs): plan with `safe-migration` (add new, dual-write/read, migrate callers, remove old).
- UI copy: coordinate with product/support so help docs change at the same time.
