// e2e/<feature>.spec.ts: skeleton. Swap the feature, routes and labels for your own.
// Each test proves one user goal, passes in any order, and creates the data it needs.
import { test as base, expect } from "@playwright/test";

type Seeded = { account: { key: string; addresses: number } };

// `account` fixture: seeds through the backend API (never by clicking through the UI),
// keyed per test so parallel workers cannot see each other's rows, and cleans up after.
const test = base.extend<Seeded>({
  account: async ({ request }, use, info) => {
    const key = `w${info.workerIndex}-${info.testId}`;
    const seeded = await request.post("/api/test/accounts", { data: { key, addresses: 2 } });
    expect(seeded.ok(), "seed endpoint should accept the fixture").toBeTruthy();
    await use({ key, addresses: 2 });
    await request.delete(`/api/test/accounts/${key}`);
  },
});

// Signed-in state is produced once by the setup project; see REFERENCE.md "Auth reuse".
test.use({ storageState: ".auth/user.json" });

test.describe("saved addresses", () => {
  test.beforeEach(async ({ page, account }) => {
    await page.goto(`/account/addresses?seed=${account.key}`);
  });

  test("a new address appears at the top of the list", async ({ page, account }) => {
    const form = page.getByRole("form", { name: "New address" });
    await form.getByLabel("Street").fill("12 Harbour Road");
    await form.getByLabel("Postcode").fill("D02 X285");
    await form.getByRole("button", { name: "Save address" }).click();

    const rows = page.getByRole("listitem");
    await expect(rows).toHaveCount(account.addresses + 1);
    await expect(rows.first()).toContainText("12 Harbour Road");
  });

  test("a missing postcode is reported next to the field", async ({ page, account }) => {
    const form = page.getByRole("form", { name: "New address" });
    await form.getByLabel("Street").fill("12 Harbour Road");
    await form.getByRole("button", { name: "Save address" }).click();

    await expect(form.getByLabel("Postcode")).toHaveAttribute("aria-invalid", "true");
    await expect(page.getByRole("listitem")).toHaveCount(account.addresses);
  });

  test("lookup outage falls back to manual entry", async ({ page }) => {
    // Break only the third-party dependency under test; the app's own backend stays real.
    await page.route("**/address-lookup/**", (route) => route.fulfill({ status: 503, body: "" }));
    await page.getByRole("searchbox", { name: "Find address" }).fill("D02");

    await expect(page.getByText("Enter the address manually")).toBeVisible();
    await expect(page.getByLabel("Street")).toBeEditable();
  });
});
