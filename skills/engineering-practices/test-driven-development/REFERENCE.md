# TDD Reference

## Contents
- Good and bad tests
- Gate: name the break
- Change detectors and testing the right owner
- Mocking rules
- Designing for mockability
- Mutation check
- Warning signs
- Rationalizations and answers
- When stuck

## Good and bad tests

| Quality | Good | Bad |
|---|---|---|
| Focus | one behaviour; an "and" in the name means split it | `validates email and trims and lowercases` |
| Name | states the behaviour: `rejects transfer above daily limit` | `test1`, `works` |
| Interface | public API only; survives internal rewrites | calls private helpers, inspects internal state |
| Expected value | literal or hand-worked example | recomputed with the code's own logic |
| Isolation | sets up its own data; any order | depends on the previous test |
| Speed | milliseconds for unit, seconds for integration | sleeps, real network |

Good (behaviour through the interface):
```python
def test_overdue_invoice_accrues_daily_fee():
    inv = Invoice(amount=10_000, due=date(2026, 3, 1))
    assert inv.balance(on=date(2026, 3, 4)) == 10_150   # 3 days × 50, worked by hand
```
Bad (implementation detail):
```python
def test_balance_calls_fee_calculator(mocker):
    calc = mocker.patch("billing.fees.calculate")
    Invoice(amount=10_000, due=date(2026, 3, 1)).balance(on=date(2026, 3, 4))
    calc.assert_called_once()
```

Table-driven tests with literal expected values are the clearest form for rules with many cases:
```ts
test.each([
  ["Hello World", "hello-world"],
  ["  spaced  ", "spaced"],
  ["trailing---", "trailing"],
  ["Ünïcödé", "unicode"],
])("slugify(%j) = %j", (input, want) => expect(slugify(input)).toBe(want));
```

## Gate: name the break

Before writing a test body, answer: *what change to production code should make this test fail, and is that change a bug or a deliberate decision?*

```
Cannot name a breaking change      → no observable behaviour; redesign the test
Only "the source text changed"     → run the artifact and assert its effect instead
Only deliberate decisions break it → change detector; test the behaviour that depends on the decision
Expected value uses the code's logic → replace with a literal or hand-checked fixture
```

## Change detectors and testing the right owner

- Not `expect(MAX_RETRIES).toBe(5)`; instead "a failing call is attempted 5 times and never a 6th".
- Do not assert that a script or config contains a line; run it on controlled input and assert output, side effects, exit code.
- Test your contract (the route you register, the query you emit, the payload you build), not the framework's mechanics.
- Constructors, getters, constants, and pass-through methods earn tests only when they validate, normalise, default, derive, or cause side effects.
- If upstream behaviour surprised you, write one narrow characterisation test that names the assumption.

## Mocking rules

Mock at boundaries you do not control:
- external APIs (payments, email, SMS, maps)
- time and randomness (inject a clock / seed)
- databases and filesystem *sometimes*; prefer a real test DB or temp dir when fast enough

Do not mock your own modules or internal collaborators.

When you do mock:
1. Learn every side effect of the real method first; mock the slow/external level beneath what the test relies on.
2. Mirror the real response structure completely, not just the fields this test reads.
3. Make doubles specific: when arguments, counts, or order are part of the contract, assert them; give success, error, and malformed cases their own fixtures.
4. Never assert on the mock itself (`getByTestId("sidebar-mock")`). If removing the mock would fail the test, it tests the mock.
5. Cleanup only tests need lives in test utilities, not as methods on production classes.
6. If mock setup is more than half the test, switch to an integration test with real components.

## Designing for mockability

Inject boundary dependencies instead of constructing them inside:
```ts
// easy to substitute
export function chargeOrder(order: Order, payments: PaymentClient) { return payments.charge(order.total); }
// hard to substitute
export function chargeOrder(order: Order) { return new PaymentClient(process.env.PAY_KEY!).charge(order.total); }
```
Prefer specific functions per external operation (`getUser`, `listOrders`, `createOrder`) over one generic `request(endpoint, opts)`: each fake returns one shape, no branching inside test doubles, and the test shows which calls matter.

## Mutation check

Before finishing, mentally apply each mutation; at least one test should fail:
- wrong constant or argument
- wrong branch taken / condition flipped / `>` vs `>=`
- missing state change or side effect
- empty or default return
- missing validation for zero, empty, null, unauthorised, malformed input

A surviving mutation means unprotected behaviour or a tautological test. If a mutation-testing tool exists for the stack (Stryker, mutmut, cargo-mutants, PIT), run it on the changed files.

## Warning signs

- Setup and assertion share the same object, so equality is guaranteed.
- The test can only fail by crashing.
- It fails on every intentional change and never on accidental ones.
- Expected values hide behind loops, builders, or helpers.
- It greps source text, or asserts a removed symbol stays removed.
- It exists for coverage and checks no outcome.
- A production method is called only from tests.
- "Mocking just to be safe."

## Rationalizations and answers

| Thought | Answer |
|---|---|
| "Too simple to test" | Simple code breaks too; the test takes a minute. |
| "I'll add tests after" | Tests written after pass immediately and are shaped by the code you wrote; they prove little. |
| "I already tested it manually" | Manual checks leave no record and cannot be rerun on the next change. |
| "I wrote the code already; deleting it is waste" | The time is spent either way. Keep it only as throwaway exploration, then rebuild test-first. |
| "I need to explore first" | Fine: spike, throw it away, then TDD. |
| "This is hard to test" | Hard to test usually means hard to use; simplify the interface. |
| "The existing code has no tests" | Add a characterisation test around what you touch. |

Legitimate exceptions (agree with the user): throwaway prototypes, generated code, pure configuration.

## When stuck

| Problem | Try |
|---|---|
| Do not know how to start | Write the call you wish existed and the assertion first, then fill in the setup. |
| Test is complicated | The interface is complicated; simplify it. |
| Everything needs mocking | Too coupled; inject the boundary dependencies. |
| Setup is huge | Extract builders/factories; if still huge, the design needs work. |
| Flaky test | Remove time, randomness, order, and shared state; inject a clock and seed. |
