---
name: codebase-orientation
description: "Explore an unfamiliar repository read-only and produce an orientation map, or in locate mode a short list of path:line citations for where a behaviour lives. Use when starting in a new codebase, onboarding someone, before planning a change, or asking \"where is X handled?\". Not for judging architecture quality (use improve-architecture) or changing code."
license: MIT
metadata:
  category: "engineering-workflows"
  version: "3.0.0"
---

# Codebase Orientation

Read-only. Change nothing; produce a map or a list of citations someone can act on.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `repo` | optional | current directory | `~/code/shop` |
| `mode` | optional | `map` | `locate` |
| `question` | yes in `locate` mode | – | "Where is the discount applied at checkout?" |
| `depth` | optional | `standard` | `quick` or `deep`; see the depth rule under map-mode steps |
| `focus` | optional | whole repo | `packages/api` (a subfolder to map or search in) |
| `output_path` | optional | chat only | `docs/ORIENTATION.md` (the only file this skill may write) |

## Output

- **map mode**: an orientation note per [templates/orientation.md](templates/orientation.md): one-paragraph purpose, stack, layout table, entry points, 2-3 traced flows, how to build/run/test (commands verified or marked unverified), conventions, hot spots, open questions.
- **locate mode**: only an evidence block, one citation per line, ranges you actually read:
  ```
  src/checkout/pricing.ts:88-121  applyDiscounts(): where coupon and tier discounts combine
  src/checkout/pricing.test.ts:40-77  tests covering stacked discounts
  ```
  or the single line `no relevant locations found`.

## Supporting files

- [scripts/repo-map.sh](scripts/repo-map.sh): one read-only pass that prints tree, languages, manifests, scripts/targets, CI files, docs, test locations, likely entry points, recent churn (lockfiles and deleted files skipped), largest files. `repo-map.sh [DIR] [TREE_DEPTH]`; DIR may be the `focus` subfolder. Run first in map mode.
- [templates/orientation.md](templates/orientation.md): the orientation note skeleton.

## Steps: map mode

**Depth rule.** `quick` (≈5-10 min): all steps, but step 6 traces one flow and step 9 uses only the script's churn and size lists. `standard` (≈15-30 min): 2-3 flows. `deep`: 2-3 flows plus the tests covering each hop, run both build and test in step 7, and read every ADR.

1. **Run `scripts/repo-map.sh <repo> [2|3]`** for the overview (tree, file counts by language, manifests, scripts, CI files, churn). With `focus`, run it on `<repo>/<focus>`, then on `<repo> 1` as well, because install/test commands and CI usually live at the root.
2. **Read the human docs**: README, CONTRIBUTING, agent instruction files (AGENTS.md and similar), `docs/`, glossary, ADRs. Note what they claim so you can check it.
3. **Identify the stack** from manifests (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`, `composer.json`), framework config files, and Docker/compose files.
4. **Classify directories**: application code, libraries/packages, tests, config, scripts, generated/vendored (do not read generated code), infra/deploy.
5. **Find entry points**: `main`/`bin` fields, `cmd/`, `src/index.*`, `app.py`/`manage.py`, server bootstrap, route registries, CLI command tables, job schedulers, event consumers, frontend root component and router.
6. **Trace 2-3 representative flows** end to end (e.g. one HTTP request from route → handler → service → storage → response; one background job; one UI action). Record file:line for each hop.
7. **Find how to build, run and test**: package scripts, Makefile/Taskfile targets, CI workflow steps (the most reliable source). Run the test or build command to verify only when dependencies are already installed, it needs no network or credentials, and it finishes in about 2 minutes. Never run installs, migrations, deploys or anything that touches external services. Otherwise mark it "unverified" and say why (e.g. "needs DATABASE_URL").
8. **Note conventions**: naming, folder patterns, error handling, logging, dependency injection, state management, test style, lint/format config.
9. **Note hot spots and risks**: most-churned files, huge files, TODO/FIXME clusters (`rg -c "TODO|FIXME" | sort -t: -k2 -nr | head`), missing tests, places docs disagree with code.
10. **Write the note** (template). Separate verified facts from inferences; every claim about code cites a path. Save it to `output_path` if given (say so in chat with a 3-line summary); otherwise reply with the note in chat.

## Steps: locate mode

1. In the first round (inside `focus` if given), fan out several searches at once across complementary guesses: path patterns (`rg --files | rg -i 'discount|coupon|promo'`), symbols and strings (`rg -n "applyDiscount|coupon" --type ts`), error messages or UI copy the user mentioned, route names, config keys, test names.
2. Read the most promising hits; follow imports/callers for one or two more rounds only if needed.
3. Stop as soon as you can name the locations. Cite only ranges you read; never estimate a range or cite past end of file.
4. Reply with the evidence block only. If nothing relevant was found, say so in one line rather than guessing.

## Checkpoints

- Generated, vendored, and build-output folders excluded from reading.
- Every command listed is either verified (ran it) or marked unverified.
- Each traced flow has file:line for every hop.
- Locate mode replies contain citations only.

## Worked example (map, quick)

```
Purpose: B2B ordering portal (Next.js frontend + Node API) for wholesale customers.
Stack: TypeScript, Next.js 14 (apps/web), Fastify (apps/api), Postgres via Prisma, Vitest, Playwright.
Layout: apps/web (UI), apps/api (HTTP API), packages/db (Prisma schema + client), packages/ui (shared components), infra/ (Terraform), scripts/ (one-off ops).
Entry points: apps/api/src/server.ts:12 (Fastify bootstrap), apps/api/src/routes/index.ts:5 (route registry), apps/web/app/layout.tsx.
Flow - place order: web/app/cart/actions.ts:30 → api/routes/orders.ts:44 → api/services/orderService.ts:71 → packages/db (orders, order_lines) → emits order.created (api/events/bus.ts:18).
Run/test: pnpm i; pnpm dev (verified); pnpm test (verified: 312 passed); pnpm e2e (unverified, needs browsers).
Conventions: services return Result<T, AppError>; zod schemas at route boundaries; tests beside source as *.test.ts.
Hot spots: orderService.ts (48 commits / 6 months, 1,100 lines); pricing has no tests.
Open questions: README says Redis is required; nothing imports a Redis client.
```

## Pitfalls

- Reading generated code, lockfiles, or vendored dependencies.
- Trusting the README over CI config and code.
- Listing directories without saying what they are for.
- Stating commands as working without running or marking them.
- In locate mode: padding the answer with explanation, or citing ranges you never read.

## Done when

- [ ] Map mode: note covers purpose, stack, layout, entry points, traced flows, build/run/test, conventions, hot spots, open questions, with paths cited.
- [ ] Locate mode: evidence block of read ranges, or an explicit "no relevant locations found".
- [ ] No files were modified other than `output_path`, if one was given.
