---
name: module-interface-design
description: "Design deep modules: small interfaces that hide a lot, placed at deliberate seams and tested through the interface. Use when designing or reviewing an interface, deciding where a seam goes, merging pass-through layers, or adding import-boundary rules in CI. Not for choosing what to improve (use improve-architecture) or refactor mechanics (use safe-refactor)."
license: MIT
metadata:
  category: "engineering-practices"
  version: "3.0.0"
---

# Module Interface Design

A **deep** module gives callers a lot of behaviour for a small amount of interface to learn. Use the terms below exactly and consistently; shared language is half the value.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `target` | required | — | `src/billing/` or "the notification sending code" |
| `mode` | optional | `review` | `review` · `design` (new interface) · `deepen` (merge shallow cluster) · `enforce` (boundary rules) |
| `callers` | optional | found by search | `api/routes/*.ts`, `jobs/invoice.ts` |
| `alternatives` | optional (design) | 3 | 4 if a ports-and-adapters variant is plausible |
| `packages_root` | optional (enforce) | `src/packages` if `src/` exists, else `packages` | `libs` |
| `glossary` | optional | `GLOSSARY.md` / `CONTEXT.md` if present | domain terms to name things |

## Output

- **review**: a list of findings, each naming the module, the smell, the deletion-test result, and a proposed deeper interface.
- **design**: `alternatives` interface sketches (signature, invariants, errors, usage example, what is hidden, dependency strategy, trade-offs) plus a recommendation.
- **deepen**: the merged module with its interface, tests moved to that interface, old shallow tests deleted.
- **enforce**: boundary-rule config wired into the repo's check command, an example package, and proof the rule fails on a violation.

## Vocabulary

| Term | Meaning | Do not say |
|---|---|---|
| **Module** | anything with an interface and an implementation, at any scale: function, class, package, vertical slice | unit, component, service |
| **Interface** | everything a caller must know to use it correctly: signature *plus* invariants, call order, error modes, required config, performance | API, signature |
| **Implementation** | the code inside | |
| **Depth** | behaviour a caller (or test) can exercise per unit of interface learned | lines-of-code ratio |
| **Seam** | a place where behaviour can be changed without editing that place; where an interface lives | boundary |
| **Adapter** | a concrete thing filling a seam (Postgres repo, in-memory fake, HTTP client) | |
| **Leverage** | what callers get from depth: one implementation, many call sites and tests | |
| **Locality** | what maintainers get: change, bugs, and knowledge concentrated in one place | |

## Principles

1. **Pull complexity down.** The implementer absorbs complexity so callers do not.
2. **Deletion test.** Imagine inlining the module into its callers. Complexity spreads across many places → it earns its keep. Little changes → it is a pass-through; merge or remove it.
3. **The interface is the test surface.** Callers and tests cross the same seam. Wanting to test *past* the interface means the module has the wrong shape.
4. **One adapter is a hypothetical seam; two make it real.** Do not add a port or abstraction until two adapters exist (production + test fake counts).
5. **Depth is about the interface, not the insides.** A deep module may contain small swappable parts and internal seams for its own tests; just do not expose them.
6. **Information hiding.** Each decision likely to change (format, vendor, algorithm) is known to exactly one module.
7. **Define errors out of existence** where you can: sensible defaults, idempotent operations, clamping, instead of many error cases callers must handle.
8. **Somewhat general interfaces, specific implementations.** A slightly general interface is usually simpler and deeper than one shaped around today's single caller.
9. **Testable by construction**: accept dependencies rather than constructing them; return results rather than mutating inputs; keep the surface small.

## Supporting files

- [REFERENCE.md](REFERENCE.md): smells catalogue, dependency categories for deepening, seam discipline, replace-don't-layer testing, the design-it-several-ways procedure, and enforcement options for other languages. Read for `deepen` and `design`.
- [templates/dependency-cruiser.cjs](templates/dependency-cruiser.cjs): boundary rules for TypeScript/JavaScript packages (entry points public, subfolders private, tests through entry points, no cycles). Use in `enforce`.
- [templates/packages-README.md](templates/packages-README.md): convention doc to place in the packages folder. Use in `enforce`.

## Steps

1. **Read the glossary** (`glossary`) **and ADRs** for the area; name things in domain language.
2. **Map the module**: its interface (all of it: order rules, errors, config), its callers (`callers` if given, else `rg` for imports and call sites of `target`), and its dependencies.
3. **Branch by mode.**

**review**
4. Apply the deletion test to each module in `target`. Look for smells (REFERENCE.md): forwarding layers, required call sequences, rarely used flags, helpers extracted only for tests while bugs sit in the orchestration, the same knowledge in several modules.
5. For each finding propose the deeper interface in a few lines of code and say which callers simplify. Rank by leverage × locality gained.

**design**
4. Write the constraints any interface must satisfy, dependency categories (REFERENCE.md), and a rough sketch to make constraints concrete.
5. Produce `alternatives` radically different designs (minimal entry points; maximum flexibility; optimised for the most common caller; ports-and-adapters). If parallel helpers are available, give each one design brief.
6. Present each, compare on depth, locality, and seam placement, then recommend one (or a hybrid). Be opinionated.

**deepen**
4. Classify each dependency (in-process, local stand-in, owned remote, true external) to decide how the merged module will be tested.
5. Write tests at the new interface first (see `test-driven-development`), merge the shallow modules behind it, move callers, delete tests that targeted the old shallow pieces.
6. Run the full suite after each caller moves.

**enforce**
4. Steps 4-9 are for TS/JS. For other languages, pick the tool from REFERENCE.md "Enforcement in other ecosystems", then do the same scaffold, wiring and pass → fail → pass proof. Detect package manager (`pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, `bun.lockb` → bun, else npm) and `packages_root`. If a boundary config already exists, merge rules rather than overwrite.
5. Install the tool as a dev dependency (`dependency-cruiser`; recent majors need Node 22+, so on older Node pin `dependency-cruiser@16`), copy [templates/dependency-cruiser.cjs](templates/dependency-cruiser.cjs) to `.dependency-cruiser.cjs`, set `PACKAGES_ROOT`. For TypeScript it also needs a `typescript` version it supports (`npx depcruise --info` lists `.ts` with a ✔). TypeScript 7 is not supported yet; with it, `.ts` files are skipped silently and the check passes on `0 modules`. Pin `typescript@5` in that case.
6. Add `"lint:boundaries": "depcruise <source root>"` (e.g. `depcruise src`: the whole source root, so code outside `packages_root` is checked too) and run it from the same umbrella script as typecheck (`check`/`ci`/`validate`). Do not add path aliases.
7. Scaffold `<packages_root>/example/` with `index.ts` (entry point delegating to `lib/impl.ts`) and `tests/example.test.ts` importing only `../index`.
8. **Prove it bites**: run → pass, and the summary counts more than 0 modules; add `import { x } from "../lib/impl"` to the test → must fail with `test-reaches-into-internals`; revert → pass. Also import a package's `lib/` file from app code → must fail with `outside-reaches-into-module`. If either does not fail, fix the config or the scanned path.
9. Copy [templates/packages-README.md](templates/packages-README.md) into `<packages_root>/README.md` and add one line pointing to it from `AGENTS.md` (create if missing).

## Checkpoints

- design: user picks a design before implementation.
- deepen: new interface tests are green before deleting old ones.
- enforce: pass → fail → pass observed.

## Worked example

`target`: notification code. Callers do:

```ts
const tpl = templates.load("invoice_due");
const body = renderer.render(tpl, { invoice });
const prefs = await prefsRepo.get(user.id);
if (prefs.email) await mailer.send(user.email, body.subject, body.html);
if (prefs.sms && body.sms) await sms.send(user.phone, body.sms);
```
repeated in 7 places. Deletion test on `renderer`: it forwards to the template engine (pass-through). On the cluster as a whole: knowledge of preferences and channels is spread across 7 callers, so the cluster needs one deep module.

Proposed interface:
```ts
notify(user: User, event: "invoice_due", data: { invoice: Invoice }): Promise<void>
```
Hidden: template lookup, rendering, preference checks, channel fan-out, retries. Dependencies: template engine (in-process), prefs DB (local stand-in), mail/SMS providers (true external → injected port with a fake adapter in tests). Tests call `notify` with the fake and assert which messages were sent. 7 callers shrink to one line each; old `renderer` tests are deleted.

## Pitfalls

- Splitting code into many tiny classes and calling it "clean": each one is shallow and callers must learn them all.
- Introducing an interface with a single implementation "for flexibility".
- Exposing internal seams (strategy objects, hooks) through the public interface just so tests can reach them.
- Measuring depth by implementation size; padding does not add leverage.
- Keeping old shallow tests after deepening; they lock the old structure in place.
- A single giant barrel `index.ts` re-exporting internals defeats boundary rules; prefer several small entry points.

## Done when

- [ ] Findings or designs use the vocabulary above consistently.
- [ ] Each proposed interface states invariants, errors, and what it hides, with a usage example.
- [ ] (design) A recommendation is made after comparing on depth, locality, seam placement.
- [ ] (deepen) Tests sit at the new interface, old shallow tests are gone, full suite green.
- [ ] (enforce) Boundary check runs with typecheck, and a deliberate violation was seen failing.
