# Browser Testing Reference

Sections are independent; jump to the one you need.

## Contents
- Locators
- Waiting and assertions
- Auth reuse
- Test data
- Network mocking and failure simulation
- Clock and time
- Files: upload and download
- Iframes, popups, new tabs
- Multi-user and real-time
- Emulation: mobile, color scheme, permissions, geolocation
- Accessibility and visual checks
- Debugging and tracing
- Flaky test causes
- Configuration and CI
- Evidence for pull requests
- Choosing what to test where

## Locators

| Prefer | Example | Notes |
|---|---|---|
| Role + name | `getByRole("button", { name: "Save" })` | matches how users and assistive tech see the page |
| Label | `getByLabel("Email")` | form fields |
| Placeholder | `getByPlaceholder("Search")` | only if no label |
| Text | `getByText("Order placed")` | non-interactive content |
| Test id | `getByTestId("order-total")` | when no stable semantics exist (totals, canvases) |
| CSS / XPath | `locator(".cart > li:nth-child(2)")` | last resort; breaks on refactors |

- Narrow by chaining: `page.getByRole("row", { name: "Invoice 1043" }).getByRole("button", { name: "Pay" })`.
- Filter: `locator("li").filter({ hasText: "Pending" })`.
- Strictness: a locator that matches several elements throws on action. Fix the locator; do not reach for `.first()` unless order is the point.
- Agent tools that expose an accessibility snapshot with element refs: use refs for one-off actions, but convert to role/label locators when writing durable tests.

## Waiting and assertions

- Actions auto-wait for the element to be attached, visible, stable, enabled, and receiving events.
- Web-first assertions retry until timeout: `toBeVisible`, `toHaveText`, `toHaveValue`, `toHaveURL`, `toHaveCount`, `toBeChecked`.
- Wait for the thing you need: `page.waitForResponse(r => r.url().includes("/api/cart") && r.ok())`, `page.waitForURL("**/done")`.
- `networkidle` is useful for one-off inspection of legacy pages; avoid it in tests (long-polling and analytics keep the network busy).
- Never assert on a value read once (`expect(await el.textContent()).toBe(...)`), because it does not retry. Assert on the locator.

## Auth reuse

Create the session once, save it, reuse it in every test.

```ts
// auth.setup.ts  (a "setup" project that other projects depend on)
import { test as setup } from "@playwright/test";
setup("login", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill(process.env.E2E_USER!);
  await page.getByLabel("Password").fill(process.env.E2E_PASS!);
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL("/dashboard");
  await page.context().storageState({ path: ".auth/user.json" });
});
```

- One storage file per role (`admin.json`, `member.json`). Gitignore `.auth/`.
- Faster still: log in via API (`request.post("/api/login")`) and save that context's state.
- Test the login UI itself in one dedicated test, not in every test.
- MFA: use a test-only TOTP secret and generate codes in the test, or a backend flag that disables MFA for seeded test users.

## Test data

- Seed through an API or factory per test; tag records with the test id so cleanup can find them.
- Unique values per worker (`user-${testInfo.workerIndex}@example.test`) avoid collisions.
- Do not depend on data created by another test.
- Reset or clean up in `afterEach` only what you created; a full DB reset per test is slow.

## Network mocking and failure simulation

```ts
await page.route("**/api/prices", r => r.fulfill({ json: [{ sku: "A", price: 5 }] }));      // fake body
await page.route("**/api/prices", async r => {                                            // modify real response
  const res = await r.fetch(); const body = await res.json();
  body[0].price = 0; await r.fulfill({ response: res, json: body });
});
await page.route("**/analytics/**", r => r.abort());                                       // block
await page.route("**/api/save", r => r.abort("timedout"));                                 // network failure
await page.route("**/api/slow", async r => { await new Promise(f => setTimeout(f, 3000)); await r.continue(); }); // latency
await context.setOffline(true);                                                             // offline
```

- Mock third parties (payments, maps, email, OAuth providers). Keep your own backend real when feasible.
- Recorded traffic (HAR) can replay a complex API: `page.routeFromHAR("fixtures/api.har", { url: "**/api/**" })`.
- Always test at least one error path per critical flow: 500, timeout, offline.

## Clock and time

```ts
await page.clock.install({ time: new Date("2026-01-31T23:59:00Z") });
await page.goto("/billing");
await page.clock.fastForward("02:00");       // cross midnight / month end
```
Use for trial expiry, countdowns, session timeouts, date pickers, and timezone edges (`test.use({ timezoneId: "Asia/Kolkata", locale: "en-IN" })`).

## Files: upload and download

```ts
await page.getByLabel("Upload invoice").setInputFiles("fixtures/invoice.pdf");
const [download] = await Promise.all([page.waitForEvent("download"), page.getByRole("button", { name: "Export" }).click()]);
await download.saveAs(`${testInfo.outputDir}/export.csv`);
```
Then assert on the saved file's contents, not just that a download happened.

## Iframes, popups, new tabs

```ts
const frame = page.frameLocator("iframe[title='Card details']");
await frame.getByLabel("Card number").fill("4242 4242 4242 4242");
const popup = await Promise.all([page.waitForEvent("popup"), page.getByText("Open help").click()]).then(([p]) => p);
await expect(popup).toHaveURL(/help/);
```

## Multi-user and real-time

Separate browser contexts behave like separate users (own cookies and storage):

```ts
const alice = await (await browser.newContext({ storageState: ".auth/alice.json" })).newPage();
const bob   = await (await browser.newContext({ storageState: ".auth/bob.json" })).newPage();
await alice.getByRole("textbox", { name: "Message" }).fill("hi"); await alice.keyboard.press("Enter");
await expect(bob.getByText("hi")).toBeVisible();
```
WebSockets: `page.on("websocket", ws => ws.on("framereceived", f => ...))` to observe; route or mock at the server for deterministic tests.

## Emulation: mobile, color scheme, permissions, geolocation

```ts
test.use({ ...devices["Pixel 7"] });                       // viewport, UA, touch
await page.emulateMedia({ colorScheme: "dark", reducedMotion: "reduce" });
await context.grantPermissions(["geolocation", "clipboard-read"]);
await context.setGeolocation({ latitude: 28.61, longitude: 77.21 });
```
Mobile checks: horizontal overflow (`document.documentElement.scrollWidth > innerWidth`), tap target size, virtual keyboard covering inputs, hover-only menus.

## Accessibility and visual checks

- Automated scan per page (e.g. axe integration) catches roughly a third of issues; still tab through the flow and check focus order and visible focus.
- Visual regression: `await expect(page).toHaveScreenshot("checkout.png", { mask: [page.getByTestId("timestamp")] })`. Mask dynamic content, disable animations, fix fonts and viewport, and generate baselines on the same OS as CI.

## Debugging and tracing

- Run headed and slow: `npx playwright test file.spec.ts --headed --debug`.
- Trace: `trace: "retain-on-failure"` in config, then `npx playwright show-trace trace.zip`. The trace has a DOM snapshot, console, and network for every step.
- Listen to `console`, `pageerror`, `requestfailed`, and `response` (status ≥ 400) in every investigation.
- Generate a locator interactively with the recorder (`npx playwright codegen <url>`), then clean it up to role/label form.

## Flaky test causes

| Symptom | Likely cause | Fix |
|---|---|---|
| Passes alone, fails in suite | shared data or state leak | per-test data; isolate storage; remove order dependence |
| Fails only with many workers | resource contention, same account | per-worker accounts; fewer workers for that file only |
| "element not found" intermittently | asserting before render; stale locator | web-first assertion on the right element |
| Click does nothing | element covered by animation/overlay or not hydrated yet | wait for the hydrated state (enabled button, app-ready flag); disable animations in test |
| Wrong value read | reading text once instead of asserting | assert on the locator |
| Fails around midnight / month end | real clock | install a fixed clock |
| Fails on CI only | slower machine, different fonts/timezone/locale | condition waits; pin timezone/locale; CI-generated baselines |
| Random 500s | test hitting a real third party | mock it |

Process: reproduce with `--repeat-each=N --workers=4`, open a failing trace, identify the step, apply the fix, rerun with the same N, report before/after pass rates.

## Configuration and CI

```ts
// playwright.config.ts (essentials)
export default defineConfig({
  testDir: "e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,            // a retry reveals flakes in the report; it is not a fix
  reporter: process.env.CI ? [["html", { open: "never" }], ["list"]] : "list",
  use: { baseURL: "http://localhost:5173", trace: "retain-on-failure", screenshot: "only-on-failure" },
  projects: [
    { name: "setup", testMatch: /.*\.setup\.ts/ },
    { name: "chromium", use: { ...devices["Desktop Chrome"] }, dependencies: ["setup"] },
  ],
  webServer: { command: "npm run dev", url: "http://localhost:5173", reuseExistingServer: !process.env.CI },
});
```
CI: install browsers with system deps, run headless, shard large suites (`--shard=1/4`), upload the HTML report and traces as artifacts on failure.

## Evidence for pull requests

- For UI changes, attach before/after screenshots at each relevant viewport and, for interactions, a short video or GIF.
- Name files by step; crop to the relevant region; add alt text describing what changed.
- Never include real customer data or secrets in screenshots.

## Choosing what to test where

| Concern | Best layer |
|---|---|
| Pure logic, formatting, validation rules | unit |
| Component states and props | component test |
| API contracts, permissions | API test (no browser) |
| A user achieving a goal across pages | E2E |
| Look and layout | visual regression on a few key pages |

Keep E2E to critical journeys (sign-up, checkout, core create/edit flows); push detail down to faster layers.
