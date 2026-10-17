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

test("administrator can compare a published track version with the current state", async ({ page }) => {
  await page.route("https://**/*", (route) => route.abort());
  await page.goto("/login");

  await page.getByTestId("login-email-input").fill(process.env.E2E_ADMIN_EMAIL || "admin@example.com");
  await page.getByTestId("login-password-input").fill(process.env.E2E_ADMIN_PASSWORD || "e2e-only-admin-password");
  await page.getByTestId("login-submit-button").click();

  await expect(page.getByTestId("login-form")).toHaveCount(0);
  await page.goto("/admin");
  await page.getByTestId("admin-nav-tracks").click();
  await page.getByTestId("admin-track-open-trilha-code").click();
  await expect(page.getByTestId("editor-track-title")).toContainText("Trilha Code");

  const unique = Date.now();
  const publishNote = `E2E history publication ${unique}`;
  const currentDescription = `E2E current history description ${unique}`;

  await page.getByTestId("editor-settings-button").click();
  await page.getByTestId("track-form-description").fill(`E2E pre-publication description ${unique}`);
  const firstUpdate = page.waitForResponse((response) =>
    response.url().includes("/api/tracks/") && response.request().method() === "PUT" && response.status() === 200,
  );
  await page.getByTestId("track-form-save").click();
  await firstUpdate;
  await expect(page.getByTestId("track-form-dialog")).toBeHidden();

  await page.getByTestId("editor-publish-button").click();
  await page.getByTestId("publish-note-input").fill(publishNote);
  const publishResponse = page.waitForResponse((response) =>
    response.url().includes("/api/tracks/") && response.url().endsWith("/publish") &&
    response.request().method() === "POST" && response.status() === 200,
  );
  await page.getByTestId("publish-confirm-button").click();
  await publishResponse;
  await expect(page.getByTestId("publish-dialog")).toBeHidden();

  await page.getByTestId("editor-settings-button").click();
  await page.getByTestId("track-form-description").fill(currentDescription);
  const secondUpdate = page.waitForResponse((response) =>
    response.url().includes("/api/tracks/") && response.request().method() === "PUT" && response.status() === 200,
  );
  await page.getByTestId("track-form-save").click();
  await secondUpdate;
  await expect(page.getByTestId("track-form-dialog")).toBeHidden();

  await page.getByTestId("editor-versions-button").click();
  await expect(page.getByTestId("versions-list")).toContainText(publishNote);
  await expect(page.getByTestId("diff-summary")).toBeVisible();
  await expect(page.getByTestId("diff-section-track")).toContainText("descrição");
  await expect(page.getByTestId("diff-section-track")).toContainText(currentDescription);
  const changes = Number(await page.getByTestId("diff-summary").locator("span").innerText());
  expect(changes).toBeGreaterThan(0);
});

