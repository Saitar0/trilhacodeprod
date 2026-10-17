import { expect, test } from "@playwright/test";

test("student can sign in, complete a topic, retain progress, and sign out", async ({ page }) => {
  await page.route("https://**/*", (route) => route.abort());
  await page.goto("/login");

  await page.getByTestId("login-email-input").fill(process.env.E2E_STUDENT_EMAIL || "student@example.com");
  await page.getByTestId("login-password-input").fill(process.env.E2E_STUDENT_PASSWORD || "CI-only-password");
  await page.getByTestId("login-submit-button").click();

  await expect(page.getByTestId("catalog-track-card-trilha-code")).toBeVisible();
  for (const width of [360, 390]) {
    await page.setViewportSize({ width, height: 800 });
    const documentWidth = await page.evaluate(() => Math.max(document.documentElement.scrollWidth, document.body.scrollWidth));
    expect(documentWidth, `catalog overflows at ${width}px`).toBeLessThanOrEqual(width);
  }

  await page.getByTestId("catalog-track-card-trilha-code").click();
  await expect(page.getByTestId("track-title")).toHaveText("Trilha Code");
  for (const width of [360, 390]) {
    await page.setViewportSize({ width, height: 800 });
    const documentWidth = await page.evaluate(() => Math.max(document.documentElement.scrollWidth, document.body.scrollWidth));
    expect(documentWidth, `track overview overflows at ${width}px`).toBeLessThanOrEqual(width);
  }

  await page.getByTestId("track-start-button").click();

  await expect(page.getByTestId("node-reader")).toBeVisible();
  for (const width of [360, 390]) {
    await page.setViewportSize({ width, height: 800 });
    const documentWidth = await page.evaluate(() => Math.max(document.documentElement.scrollWidth, document.body.scrollWidth));
    expect(documentWidth, `node reader overflows at ${width}px`).toBeLessThanOrEqual(width);
  }

  await page.getByTestId("topic-mark-completed-button").click();
  await expect(page.getByTestId("topic-reset-button")).toBeVisible();

  await page.reload();
  await expect(page.getByTestId("topic-reset-button")).toBeVisible();

  await page.getByTestId("user-menu-trigger").click();
  await page.getByTestId("user-menu-logout").click();
  await expect(page.getByTestId("login-form")).toBeVisible();
});

