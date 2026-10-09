# Deep Modules Reference

## Contents
- Smells of shallowness
- Dependency categories when deepening
- Seam discipline
- Testing after deepening: replace, do not layer
- Designing the interface several ways
- Rejected framings
- Enforcement in other ecosystems

## Smells of shallowness

| Smell | What it looks like | Usual fix |
|---|---|---|
| Pass-through | method only forwards to another with the same args | inline it; merge layers |
| Required sequence | callers must call `init`, `configure`, `run`, `close` in order | one operation that does the sequence |
| Flag creep | options most callers never set | defaults inside; separate entry point for the rare case |
| Leaky knowledge | the same format/vendor detail appears in several modules | one owner hides it |
| Test-only extraction | pure helpers pulled out for unit tests while bugs live in the glue | test the orchestration through the outer interface |
| Exception sprawl | callers handle many error cases that could be defined away | idempotence, defaults, clamping |
| Conjoined modules | you cannot understand one without reading the other | merge them |

## Dependency categories when deepening

Classify each dependency of the cluster; the category decides the testing strategy.

1. **In-process**: pure computation, in-memory state. Merge freely; test through the new interface directly. No adapter.
2. **Local stand-in available**: a database with an embeddable or containerised test version, an in-memory filesystem. Test with the stand-in running in the suite; the seam stays internal.
3. **Remote but owned**: your own services across the network. Define a port at the seam; production uses an HTTP/RPC adapter, tests use an in-memory adapter. Logic lives in one deep module even if deployment is split.
4. **True external**: third-party services. Inject the dependency as a port; tests supply a fake adapter that records calls and returns realistic responses.

## Seam discipline

- A port with one adapter is indirection, not a seam. Add it when the second adapter (often the test fake) actually exists.
- A deep module may have internal seams used only by its own tests; keep them out of the public interface.
- Put the seam where variation actually happens (the vendor call), not one layer above "just in case".

## Testing after deepening: replace, do not layer

- New tests target the deepened module's interface; that is the test surface.
- Delete the old unit tests on the shallow pieces once the new ones cover the behaviour; keeping them freezes the old structure.
- Assert observable outcomes through the interface, never internal state.
- A test that must change when internals change is testing past the interface.

## Designing the interface several ways

First ideas are rarely best. Procedure:

1. **Frame the problem** for the user: constraints, dependencies with their categories, a rough code sketch (illustrative, not a proposal).
2. **Generate radically different designs** (in parallel if helpers are available), each from its own brief that includes file paths, coupling details, dependency categories, and the vocabulary:
   - A: minimal: 1 to 3 entry points, maximum leverage each
   - B: flexible: many use cases and extension points
   - C: common-caller first: make the default case trivial
   - D: ports and adapters around cross-seam dependencies (when relevant)
3. **Each design reports**: interface (types, methods, params, invariants, order, errors); a usage example; what is hidden; dependency strategy and adapters; where leverage is high and where thin.
4. **Present one at a time**, then compare in prose on depth, locality, and seam placement. Recommend one or a hybrid and say why.

## Rejected framings

- Depth as implementation-lines ÷ interface-lines: rewards padding. Use depth as leverage.
- "Interface" meaning only a language `interface` keyword or public method list: too narrow; include every fact a caller must know.
- "Boundary": overloaded (bounded contexts, network edges). Say seam or interface.

## Enforcement in other ecosystems

| Ecosystem | Tool | Rule shape |
|---|---|---|
| TS/JS | dependency-cruiser, ESLint `no-restricted-imports`, Nx module boundaries | outsiders import only package root files |
| Python | import-linter (`layers`, `forbidden`, `independence` contracts) | `pkg.*.internal` forbidden from outside `pkg` |
| Java/Kotlin | ArchUnit tests, JPMS `module-info` exports | only exported packages visible |
| Go | `internal/` directories (compiler-enforced) | put implementation under `pkg/internal/` |
| Rust | `pub(crate)`, workspace crates | expose a small `pub` API from `lib.rs` |
| .NET | `internal` + `InternalsVisibleTo` for tests sparingly; NetArchTest | |

Python example (`.importlinter`):
```ini
[importlinter]
root_package = app

[importlinter:contract:billing-private]
name = billing internals are private
type = forbidden
source_modules = app.api, app.jobs
forbidden_modules = app.billing.internal
```
Always prove a rule fails on a deliberate violation before trusting it.
