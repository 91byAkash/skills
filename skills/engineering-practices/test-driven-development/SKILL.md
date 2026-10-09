---
name: test-driven-development
description: "Test-driven development: red-green-refactor in vertical slices, tests at agreed seams, mocks only at boundaries, and proof each test can fail. Use when building a feature or fixing a bug test-first, the user says \"TDD\" or \"red-green\", or when writing or reviewing tests. Not for browser end-to-end tests (use browser-testing) or interface design (use module-interface-design)."
license: MIT
metadata:
  category: "engineering-practices"
  version: "3.0.0"
---

# Test-Driven Development

Write the test first, watch it fail for the right reason, write the least code that passes, repeat. The loop is easy; the value is in tests worth keeping.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `behavior` | required | — | "orders over ₹5,000 get free shipping" or bug "slugify keeps trailing dashes" |
| `kind` | optional | `feature` | `bugfix` (start from a reproducing test) |
| `seams` | optional | proposed by you, confirmed by user | `checkout(cart) → Quote` public function; `POST /quotes` |
| `test_cmd` | optional | detected (`npm test`, `pytest`, `go test ./...`, `cargo test`) | `pnpm vitest run` |
| `single_test_cmd` | optional | based on `test_cmd` | `pnpm vitest run src/quote.test.ts -t "free shipping"` |
| `glossary` | optional | `GLOSSARY.md` / `CONTEXT.md` if present | domain terms for test names |

## Output

- New tests at the agreed seams, each named as a behaviour, each seen failing before the code existed.
- The minimal production code that makes them pass.
- A short log: the slices done, the failure message seen for each red, and the full-suite result.

## Supporting files

- [REFERENCE.md](REFERENCE.md): good vs bad tests, the "name the break" gate, mocking rules and designing for mockability, the mutation check, warning signs, rationalizations, and when-stuck fixes. Read when writing or changing any test or adding a mock.

## Steps

1. **Learn the vocabulary.** Read the glossary and any ADRs for the area so test names use domain terms.
2. **Propose seams.** A seam is the public boundary where behaviour is observable without reaching inside (a public function, an HTTP endpoint, a CLI command, a message handler). List each proposed seam with one line on what it catches and what it misses. Prefer few, high-level seams. Confirm with the user when the choice is not obvious; if the interface itself is in doubt, switch to `module-interface-design` first.
3. **List behaviours as slices**, smallest first: happy path, then each rule, then edge and error cases. Do not write them all as tests yet.
4. **Red.** Write one test for the next slice:
   - name states behaviour: `gives free shipping at exactly 5000`
   - before writing the body, name the production change that would make it fail (see the gate in REFERENCE.md)
   - expected values are literals or hand-checked examples, never recomputed with the code's own logic
5. **Verify red.** Run `single_test_cmd`.
   - fails with the expected assertion message → go on
   - errors (import, typo, setup) → fix the test until it *fails* cleanly
   - passes → it tests existing behaviour or is tautological; rewrite it
6. **Green.** Write the least code that passes. No options, hooks, or generality no test asks for.
7. **Verify green.** Run the single test, then the **whole suite** (`test_cmd`). Fix failures now. Output should be free of new warnings. Any failure you did not cause still goes in the report by name.
8. **Repeat** 4–7 for the next slice. One seam, one test, one minimal change per cycle (vertical slices).
9. **Refactor only when green**, as a separate step (or leave it for review): remove duplication, improve names. Run the suite after each change. No new behaviour during refactor.
10. **Mutation check** before finishing: imagine a wrong constant, a flipped branch, a missing side effect, an empty return, missing validation. At least one test should fail for each. For the one or two riskiest conditions (boundaries, permission checks), actually make the edit, run `single_test_cmd`, see it fail, and revert the edit (`git diff` must be clean of it afterwards). If a mutation-testing tool is already set up (REFERENCE.md), run it on the changed files instead. If a mutation survives, add the missing test.

**Bug fixes** (`kind=bugfix`): step 4 is a test that reproduces the bug at the highest sensible seam; confirm it fails with the bug's symptom; then fix. The test stays as the regression guard.

## Checkpoints

- After step 2: seams agreed.
- After each red: you can say *why* it failed in one sentence.
- Before reporting done: full suite run and result recorded.

## Worked example

`behavior`: free shipping for orders ≥ ₹5,000; seam: `quote(cart)`.

```ts
test("charges standard shipping below 5000", () => {
  expect(quote(cart([{ price: 4999 }])).shipping).toBe(80);
});
```
Run → `TypeError: quote is not a function`. That is an error, not a failure; add an empty exported `quote` returning `{ shipping: 0 }`. Run → `expected 80, received 0`. Correct red.

Green: `return { shipping: 80 }`. Next slice:

```ts
test("gives free shipping at exactly 5000", () => {
  expect(quote(cart([{ price: 2500 }, { price: 2500 }])).shipping).toBe(0);
});
```
Red: `expected 0, received 80`. Green: `const subtotal = sum(prices); return { shipping: subtotal >= 5000 ? 0 : 80 }`. Full suite green. Mutation check: `>` instead of `>=` → the "exactly 5000" test fails. Good.

## Pitfalls

- **Implementation-coupled tests**: asserting on private helpers, internal call counts, or reading the database directly instead of through the interface. They break on refactor and miss real bugs.
- **Tautological tests**: `expect(add(a, b)).toBe(a + b)`, or an expected value built by the same helper the code uses.
- **Horizontal slicing**: all tests first, then all code. You end up testing imagined shapes.
- **Test-after called TDD**: a test you never saw fail may not be able to fail.
- **Weakening a test to get green.** Fix the code, or go back and agree a different behaviour.
- **Mocking your own modules.** Mock only what you do not control (network, clock, randomness, third-party services, sometimes the filesystem or DB).
- Forcing unit tests onto pure wiring or config; cover those with one higher-level or smoke test.

## Done when

- [ ] Seams were agreed and every test sits at one of them.
- [ ] Every new test was seen failing with the expected message before the code existed.
- [ ] Production code does nothing no test requires.
- [ ] The full suite passes and the run is recorded (including any pre-existing failures, by name).
- [ ] The mutation check finds no unprotected behaviour.
- [ ] No mocks of internal collaborators; no assertions on mocks themselves.
