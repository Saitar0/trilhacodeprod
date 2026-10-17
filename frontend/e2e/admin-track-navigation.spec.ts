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
  await expect(page.getByRole("button", { name: "Mover Trilha Code para cima" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Mover Trilha Code para baixo" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Ações para Trilha Code" })).toBeVisible();
  await page.getByTestId("admin-track-open-trilha-code").click();
  await expect(page.getByTestId("editor-track-title")).toContainText("Trilha Code");

  await page.getByTestId("editor-settings-button").click();
  await page.getByTestId("track-form-description").fill("E2E persisted track description");
  const updateResponse = page.waitForResponse((response) =>
    response.url().includes("/api/tracks/") && response.request().method() === "PUT" && response.status() === 200,
  );
  await page.getByTestId("track-form-save").click();
  await updateResponse;
  await expect(page.getByTestId("track-form-dialog")).toBeHidden();

  await page.reload();
  await page.getByTestId("editor-settings-button").click();
  await expect(page.getByTestId("track-form-description")).toHaveValue("E2E persisted track description");
});

