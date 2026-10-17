import { expect, test } from "@playwright/test";

test("administrator can open the seeded track editor", async ({ page }) => {
  await page.route("https://**/*", (route) => route.abort());
  await page.goto("/login");

  await page.getByTestId("login-email-input").fill(process.env.E2E_ADMIN_EMAIL || "admin@example.com");
  await page.getByTestId("login-password-input").fill(process.env.E2E_ADMIN_PASSWORD || "e2e-only-admin-password");
  await page.getByTestId("login-submit-button").click();

  await expect(page.getByTestId("login-form")).toHaveCount(0);
  await page.goto("/admin");
  await expect(page.getByTestId("admin-nav-dashboard")).toBeVisible();
  await page.getByTestId("admin-nav-tracks").click();
  await expect(page.getByTestId("admin-track-row-trilha-code")).toBeVisible();
  await page.getByTestId("admin-track-open-trilha-code").click();
  await expect(page.getByTestId("editor-track-title")).toContainText("Trilha Code");
});

