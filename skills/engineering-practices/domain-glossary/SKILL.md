---
name: domain-glossary
description: "Build and maintain a project's domain language in GLOSSARY.md, challenge fuzzy or overloaded terms, and record hard-to-reverse decisions as ADRs. Use when asked \"what do we call X?\", naming code, tables, or tickets, one thing has two names, editing GLOSSARY.md, or writing an ADR. Not for API reference docs or specs (use write-spec)."
license: MIT
metadata:
  category: "engineering-practices"
  version: "3.0.0"
---

# Domain Glossary

Precise shared words make specs, code, tests, tickets, and agent instructions line up. This is an *active* practice: challenge terms during the conversation and write them down the moment they settle.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `topic` | required | — | "refunds and partial cancellations" |
| `context` | optional | inferred from `GLOSSARY-MAP.md` or the code area | `billing` |
| `glossary_path` | optional | `GLOSSARY.md` at repo root (or per-context path from the map) | `src/billing/GLOSSARY.md` |
| `adr_dir` | optional | `docs/adr/` (per-context `docs/adr/` for context-only decisions) | `src/billing/docs/adr/` |
| `scan` | optional | `false` | `true`: run the term-usage scan to find drift |

## Output

- Updated `GLOSSARY.md` entries (term, one-to-two sentence definition, *Avoid* list, optional "not to be confused with").
- ADRs for decisions that pass the three-part test, numbered sequentially.
- When `scan=true`: a drift report of avoided synonyms still used in code/docs, with locations.
- A list of contradictions found between what was said and what the code does.

## Supporting files

- [templates/GLOSSARY.md](templates/GLOSSARY.md), [templates/GLOSSARY-MAP.md](templates/GLOSSARY-MAP.md), [templates/adr.md](templates/adr.md): file formats. Copy when creating the first file of each kind.
- [REFERENCE.md](REFERENCE.md): entry rules, scenario probes for sharpening terms, what qualifies for an ADR, and multi-context guidance. Read when unsure whether something belongs.
- [scripts/term-usage.sh](scripts/term-usage.sh): counts each glossary term and its avoided synonyms across the repo. Run with `scan=true` or before a rename.

## Steps

1. **Find the structure.**
   - `GLOSSARY-MAP.md` exists → multiple contexts; pick the one for `topic` (ask if unclear).
   - only `GLOSSARY.md` → single context.
   - neither → create root `GLOSSARY.md` from the template when the first term is resolved (not before).
2. **Read** the relevant glossary (`glossary_path`) and recent ADRs in `adr_dir` before discussing.
3. **During the conversation**, act immediately when you notice:
   - *conflict with the glossary* → "The glossary defines Cancellation as voiding the whole Order; you seem to mean removing one line. Which?"
   - *vague or overloaded word* (account, user, job, item, status) → offer precise candidates: "Customer (who pays) or Member (who logs in)?"
   - *a relationship being described* → probe with a concrete edge-case scenario (see REFERENCE.md probes).
   - *a claim about how the system works* → check the code; surface contradictions with file references.
4. **Write the entry as soon as a term settles**, not at the end. Definition says what the thing *is* in this business, in at most two sentences, with no implementation details (no tables, classes, endpoints). List rejected synonyms under *Avoid*.
5. **Offer an ADR only if all three hold**: hard to reverse, surprising to a future reader without context, and the result of a real trade-off. Number it by scanning `adr_dir` for the highest number and adding one; create the folder lazily.
6. **Scan for drift** (`scan=true` or before renaming): `scripts/term-usage.sh <glossary_path> src docs` (use the folders that hold code and docs). Single-word synonyms are matched as whole words only, so `chargeClient` is not counted for *client*; `rg -i client` once for any word flagged as DRIFT. For each avoided synonym still in use, decide: rename now (small, local) or record a follow-up. Wide renames of public names follow `safe-migration`.
7. **Use the terms**: name new code, tests, tickets, and specs with glossary words.

## Checkpoints

- Before writing an entry: the user agreed to the term and definition (or chose between your candidates).
- Before creating an ADR: state which of the three conditions each holds; skip if any fails.

## Worked example

User: "When an account cancels, refund whatever's unused."

- Overloaded: *account*. Glossary has **Customer** (billing party) and **Member** (person with a login). Ask → "Customer".
- Fuzzy: *cancels*. Scenario probe: "A Customer on an annual plan cancels in month 4 after a mid-year upgrade. Is the refund prorated from the upgrade date or the original start?" → prorated per Subscription Period.
- Code check: `billing/refund.ts` refunds the full last invoice, contradicting "unused". Surface it.

Entries written:

```md
**Subscription Cancellation**:
A Customer ending a Subscription before its renewal date. Takes effect at the end of the current Subscription Period unless an immediate cancellation is requested.
_Avoid_: account closure, churn (churn is a metric, not an event)

**Prorated Refund**:
The unused share of the current Subscription Period's charge, returned on immediate cancellation.
_Avoid_: partial refund, credit
```

ADR? Prorating rule is easy to change → no ADR.

## Pitfalls

- Defining generic programming concepts (timeout, retry, DTO) instead of business terms.
- Definitions that describe implementation ("row in the orders table") or behaviour lists rather than what the thing is.
- Batching updates to the end of a session; terms get lost.
- Using the glossary as a spec or notes dump.
- Writing ADRs for easily reversible or obvious choices; the useful ones get buried.
- Renaming widely used identifiers in one sweep without a migration path.

## Done when

- [ ] Every term settled in the session has an entry with definition and *Avoid* list.
- [ ] No entry contains implementation details or generic programming terms.
- [ ] Contradictions between statements and code were raised with file references.
- [ ] ADRs exist only for decisions passing all three conditions, numbered sequentially.
- [ ] (scan) Drift report produced and each hit either fixed or listed as follow-up.
