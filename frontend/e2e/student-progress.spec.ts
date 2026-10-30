import { expect, test } from "@playwright/test";

async function expectNoHorizontalOverflow(page: import("@playwright/test").Page, width: number, area: string) {
  await page.setViewportSize({ width, height: 800 });
  const documentWidth = await page.evaluate(() => new Promise<number>((resolve) => {
    requestAnimationFrame(() => requestAnimationFrame(() => {
      resolve(Math.max(document.documentElement.scrollWidth, document.body.scrollWidth));
    }));
  }));
  expect(documentWidth, `${area} overflows at ${width}px`).toBeLessThanOrEqual(width);
}

test("student can sign in, complete a topic, retain progress, and sign out", async ({ page }) => {
  await page.route("https://**/*", (route) => route.abort());
  await page.goto("/login");

  await page.getByTestId("login-email-input").fill(process.env.E2E_STUDENT_EMAIL || "student@example.com");
  await page.getByTestId("login-password-input").fill(process.env.E2E_STUDENT_PASSWORD || "CI-only-password");
  await page.getByTestId("login-submit-button").click();

  await expect(page.getByTestId("catalog-track-card-trilha-code")).toBeVisible();
  for (const width of [360, 390]) {
    await expectNoHorizontalOverflow(page, width, "catalog");
  }

  await page.getByTestId("catalog-track-card-trilha-code").click();
  await expect(page.getByTestId("track-title")).toHaveText("Trilha Code");
  for (const width of [360, 390]) {
    await expectNoHorizontalOverflow(page, width, "track overview");
  }

  // The E2E database may retain the seeded learner's last activity across
  // repeated local runs. Start a fresh track or resume that persisted state.
  const start = page.getByTestId("track-start-button");
  if (await start.count()) {
    await start.click();
  } else {
    await page.getByTestId("track-resume-button").click();
  }

  await expect(page.getByTestId("node-reader")).toBeVisible();
  for (const width of [360, 390]) {
    await expectNoHorizontalOverflow(page, width, "node reader");
  }

  const reset = page.getByTestId("topic-reset-button");
  if (await reset.count()) await reset.click();
  await page.getByTestId("topic-mark-completed-button").click();
  await expect(page.getByTestId("topic-reset-button")).toBeVisible();

  await page.reload();
  await expect(page.getByTestId("topic-reset-button")).toBeVisible();

  await page.getByTestId("user-menu-trigger").click();
  await page.getByTestId("user-menu-logout").click();
  await expect(page.getByTestId("login-form")).toBeVisible();
});

