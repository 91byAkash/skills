---
name: browser-testing
description: "Drive a real browser to verify a web change, reproduce a frontend bug, or write and de-flake end-to-end tests. Use when you need evidence a UI change works, an E2E test is failing or flaky, or a flow needs E2E coverage. Not for unit-testing logic (use test-driven-development), design critique (use ui-polish-review) or accessibility audits (use accessibility-audit)."
license: MIT
metadata:
  category: "engineering-workflows"
  version: "3.0.0"
---

# Browser Testing and Automation

Works with any automation library (Playwright, Puppeteer, Selenium, WebDriver BiDi) or an agent browser tool. Examples use Playwright because its locator and auto-wait model is the clearest; translate as needed.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `task` | required | — | "verify the coupon field applies 10% and shows the new total" |
| `mode` | optional | inferred from task | `verify` · `e2e` (write tests) · `fix-flaky` · `automate` |
| `url` | optional | detected dev-server URL | `http://localhost:5173/checkout` |
| `start` | optional | none (assume running) | `npm run dev` on port `5173`; several allowed (API + web) |
| `auth` | optional | none | test user `qa@example.test` via saved storage state |
| `viewports` | optional | `1280x800` and `390x844` | add `768x1024` for tablet layouts |
| `browsers` | optional | Chromium | `chromium,firefox,webkit` for release checks |
| `test_dir` | optional (e2e) | existing E2E folder, else `e2e/` | `tests/e2e/` |
| `repeat` | optional (fix-flaky) | `20` | `50` for a rare flake |
| `evidence_dir` | optional | `.artifacts/browser/` | `docs/pr-123/` |

## Output

- **verify / automate**: a short report: what was checked, pass/fail per check, screenshots at key states, console errors, failed requests (status ≥ 400 or network errors).
- **e2e**: new or updated test files that pass locally and pass `repeat` times in a row; any helpers or fixtures they need.
- **fix-flaky**: root cause, the fix (in test or app), and the repeat-run result before and after.

## Supporting files

- [scripts/with_server.py](scripts/with_server.py): starts one or more servers, waits for their ports (IPv4 and IPv6, so `localhost`-bound dev servers are found), runs your command, always tears down. Fails if a port is already taken (a stale server would be tested instead) unless `--reuse`. Run it with no arguments for usage when the app is not already running.
- [examples/inspect_page.py](examples/inspect_page.py) `URL [--out DIR] [--channel chrome]`: reconnaissance script that screenshots a page and lists interactive elements with their accessible names and a role locator that resolves, plus console messages. `--channel chrome` uses an installed browser when Playwright's own browsers are not downloaded. Use before writing locators for an unfamiliar page.
- [templates/e2e.spec.ts](templates/e2e.spec.ts): test file skeleton with fixtures, network mocking, and accessible locators.
- [REFERENCE.md](REFERENCE.md): locators, waiting, auth reuse, mocking, clocks, files, iframes, multi-user, tracing, CI config, flake causes. Read the section for the situation you hit.

## Steps

1. **Get the app running.** If `start` is given or nothing answers at `url`:
   `python3 scripts/with_server.py --server "npm run dev" --port 5173 -- <your command>`.
   For a static HTML file, open `file:///abs/path.html` directly, or read the HTML to find selectors.
2. **Reconnaissance before action.** Load the page, wait for a meaningful element (a heading, the form), not a fixed sleep. Then take a screenshot and an accessibility snapshot (or run `examples/inspect_page.py <url>`). Pick locators from what is actually rendered.
3. **Choose locators in this order:** role + accessible name → label → placeholder → visible text → test id → CSS. If you need CSS, that is a hint the markup lacks semantics; note it.
4. **Act and observe after every step**: the visible result, console errors, failed network requests. Attach listeners *before* navigating so nothing is missed.
5. **Assert with auto-waiting assertions** (`await expect(locator).toHaveText(...)`) and web-first checks. If you catch yourself writing `sleep`/`waitForTimeout`, replace it with a wait on the condition you actually need (element, response, URL).
6. **Check layouts at each `viewport`**. At narrow widths check: nothing overflows horizontally, menus collapse, tap targets ≥ 44 px, sticky elements do not cover inputs.
7. **Branch by mode:**
   - `verify` → report results with evidence; stop.
   - `e2e` → go to 8.
   - `fix-flaky` → go to 10.
   - `automate` → wrap steps in a script with error handling and retries on *navigation* only; respect robots/terms and rate-limit yourself.
8. **Write the test** from [templates/e2e.spec.ts](templates/e2e.spec.ts): one user goal per test, independent of order, data seeded through API/fixtures, third-party services mocked, own backend real when practical, auth reused from storage state.
9. **Validate the test**: run it (`npx playwright test <file> --reporter=list`, plus `--project=<name>` for each entry in `browsers` if the config defines per-browser projects); if it fails, read the trace, fix locator/wait/assertion, rerun. Then `--repeat-each=<repeat>` (default 20). Also make it fail on purpose once (break the expected text) to prove it can fail.
10. **Fix flakiness**: reproduce with `--repeat-each=<repeat> --workers=4`; open the trace of a failing run; classify the cause using the table in [REFERENCE.md](REFERENCE.md#flaky-test-causes); fix the cause. Adding retries or longer timeouts is not a fix. Report the pass rate before and after.
11. **Collect evidence** into `evidence_dir`: screenshots named by step (`01-cart.png`, `02-coupon-applied.png`), trace zip for failures, a console/network summary.

## Checkpoints

- After step 2: confirm the page you see is the page under test (right URL, logged-in state, feature flag on).
- Before writing more than one test: confirm the first test passes `repeat` times.
- If the app itself is broken (not the test) → stop and report the bug with a reproduction before writing tests around it.

## Worked example

Task: "verify the coupon field applies 10%". App not running.

```bash
python3 scripts/with_server.py --server "npm run dev" --port 5173 -- python3 check_coupon.py
```

```python
# check_coupon.py
from playwright.sync_api import sync_playwright, expect
with sync_playwright() as p:
    page = p.chromium.launch().new_page(viewport={"width": 1280, "height": 800})
    errors = []
    page.on("console", lambda m: m.type == "error" and errors.append(m.text))
    page.on("response", lambda r: r.status >= 400 and errors.append(f"{r.status} {r.url}"))
    page.goto("http://localhost:5173/checkout")
    expect(page.get_by_role("heading", name="Checkout")).to_be_visible()
    page.screenshot(path=".artifacts/browser/01-checkout.png")
    page.get_by_label("Coupon code").fill("SAVE10")
    page.get_by_role("button", name="Apply").click()
    expect(page.get_by_test_id("order-total")).to_have_text("$90.00")
    page.screenshot(path=".artifacts/browser/02-coupon.png")
    print("errors:", errors or "none")
```

Report: "Coupon SAVE10 applies: total $100.00 → $90.00 (02-coupon.png). Console: none. Network: none failed. At 390 px the Apply button wraps under the input but remains usable."

## Pitfalls

- Inspecting the DOM before the app has rendered; wait for a real element (or, for legacy pages, network idle) first.
- `sleep` instead of condition waits; it is both slow and flaky.
- Asserting on class names, internal state, or exact pixel positions instead of what the user sees.
- Tests sharing a user/account and colliding when run in parallel; give each worker its own data.
- Logging in through the UI in every test; save storage state once.
- Mocking your own backend so heavily that the test proves nothing.
- Leaving browsers or dev servers running after the task; always close/tear down.
- Automating third-party sites without permission, or submitting real forms/payments during a "verification".

## Done when

- [ ] Every check in `task` has a pass/fail with evidence (screenshot or assertion output).
- [ ] Console errors and failed requests were captured and reported (or "none").
- [ ] Each requested viewport was checked.
- [ ] (e2e) New tests pass locally `repeat` times in a row and were seen failing once on purpose.
- [ ] (fix-flaky) Root cause named; pass rate before/after reported; no blanket retries or timeout bumps added.
- [ ] Servers and browsers are shut down.
