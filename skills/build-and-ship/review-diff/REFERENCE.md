# Code Review: reference

## Five-axis checklist

| Axis | Check |
|---|---|
| Correctness | matches the spec/task; edge cases (empty, null, max, unicode, time zones); error paths; concurrency and retries; idempotency; tests cover the change |
| Readability | names reveal intent; straightforward control flow; no clever tricks; no commented-out code; comments explain why, not what |
| Architecture | follows existing patterns; no new coupling across module boundaries; right abstraction level; refactors reduce concepts rather than move them; no feature logic in shared modules; file sizes stay healthy |
| Security | no secrets; input validated at trust boundaries; parameterized queries; output encoding; authz checked on every path; external data and model output treated as untrusted; safe defaults |
| Performance | no N+1 queries; no unbounded loops, reads or result sets; pagination on list endpoints; no blocking calls on hot paths; caching has invalidation |

## Smell baseline (judgment calls; repo standards override)

| Smell | Looks like | Fix |
|---|---|---|
| Mysterious name | name does not say what it does or holds | rename; if no honest name exists the design is murky |
| Duplicated code | same logic shape in several hunks | extract and call from both |
| Feature envy | method uses another object's data more than its own | move it to that data |
| Data clumps | same fields/params always travel together | introduce a type |
| Primitive obsession | strings/numbers standing in for domain concepts | small value type, parsed at the boundary |
| Repeated switches | same switch on the same type in several places | polymorphism or one shared map |
| Shotgun surgery | one logical change edits many scattered files | gather what changes together |
| Divergent change | one module edited for unrelated reasons | split by reason to change |
| Speculative generality | hooks, params, abstractions with no current need | delete; inline until needed |
| Message chains | `a.b().c().d()` | hide the walk behind one method |
| Middle man | class/function that only delegates | call the real target |
| Refused bequest | subclass ignores most of what it inherits | composition instead of inheritance |

## Structural remedies (propose the move, not just the problem)

- Replace a chain of conditionals with a typed model or explicit dispatcher.
- Collapse duplicate branches into one flow.
- Separate orchestration from business logic.
- Move feature logic out of shared modules into the owning package.
- Reuse the canonical helper instead of a near-duplicate.
- Make a type boundary explicit so downstream branching disappears.
- Delete pass-through wrappers.
- Extract a helper or split a large file.
Prefer the remedy that removes moving parts over one that spreads them.

## Change size

| Lines changed | Verdict |
|---|---|
| ~100 | good, one sitting |
| ~300 | acceptable if one logical change |
| ~1000 | split it |

Exceptions: whole-file deletions, automated refactors (verify intent, not every line).
Splitting: stack (sequential), by file group (different reviewers), horizontal (stubs/shared code first), vertical (smaller full-stack slices).

## Dependency changes

Adding: does the existing stack already solve it? size/bundle impact? maintained? known vulnerabilities (`npm audit`, `pip-audit`, `cargo audit`)? license compatible?

Upgrading:
1. Read the changelog, not the version number; patch releases can change behaviour.
2. One dependency (or tight group) per change so a break has an obvious cause and clean revert.
3. Suite green before and after; thin coverage around the dependency is itself a finding.
4. Review the lockfile diff (transitive changes), never hand-edit it, always commit it.

## Disagreements

1. Technical facts and data beat opinion.
2. The style guide is the authority on style.
3. Design is judged on engineering principles, not taste.
4. Consistency with the codebase is acceptable if it does not lower overall health.
If the author has full context and still disagrees on a judgment call, defer and record it.

## Terse format

`<file>:L<line>: <severity> <problem>. <fix>.` One line per finding, exact symbol names in backticks, the why only when the fix is not obvious. Drop "I noticed", "you might want to consider", hedges, and restating the code. Switch to full prose for security findings, architectural disagreements, or when the author is new to the codebase.
