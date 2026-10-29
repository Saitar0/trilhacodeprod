import { expect, test } from "./fixtures";
import { request } from "@playwright/test";

test.describe.configure({ retries: 0 });

const BATCH_ID = process.env.BETA7_1_E2E_BATCH_ID || "";
const STUDENT_EMAIL = process.env.E2E_STUDENT_EMAIL || "";
const STUDENT_PASSWORD = process.env.E2E_STUDENT_PASSWORD || "";
const REVIEWER_EMAIL = process.env.E2E_REVIEWER_EMAIL || "";
const REVIEWER_PASSWORD = process.env.E2E_REVIEWER_PASSWORD || "";
const API_BASE_URL = process.env.API_BASE_URL || "http://127.0.0.1:18000";

async function login(page: import("@playwright/test").Page, email: string, password: string) {
  await page.goto("/beta7-1-preview");
  const form = page.getByTestId("beta71-preview-login");
  const preview = page.getByTestId("beta71-preview");
  await expect(form.or(preview)).toBeVisible({ timeout: 10_000 });
  if (await form.isVisible()) {
    await page.getByTestId("preview-email").fill(email);
    await page.getByTestId("preview-password").fill(password);
    await page.getByTestId("preview-login-submit").click();
    const alert = page.getByRole("alert");
    await expect(preview.or(alert)).toBeVisible({ timeout: 10_000 });
    if (await alert.isVisible().catch(() => false)) {
      const safeMessage = (await alert.innerText()).replaceAll(email, "[synthetic-email]")
        .replaceAll(password, "[synthetic-password]").slice(0, 160);
      throw new Error(`Synthetic login did not establish the preview session: ${safeMessage}`);
    }
  }
  await expect(page.getByTestId("beta71-preview")).toBeVisible();
}

async function logout(page: import("@playwright/test").Page) {
  await page.getByRole("button", { name: "Sair" }).click();
  await expect(page.getByTestId("beta71-preview-login")).toBeVisible();
}

test("synthetic learner traverses the ten reviewed units and submits the project", async ({ page }) => {
  test.skip(!BATCH_ID || !STUDENT_EMAIL || !STUDENT_PASSWORD || !REVIEWER_EMAIL || !REVIEWER_PASSWORD,
    "Requires the Beta 7.1 owned real-curriculum fixture.");
  await page.route("https://**/*", (route) => route.abort());

  await login(page, STUDENT_EMAIL, STUDENT_PASSWORD);
  await expect(page.getByTestId("preview-phase-progress")).toContainText("BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA");
  for (const moduleId of ["1", "2", "3"]) {
    await expect(page.getByTestId(`preview-module-${moduleId}`)).toBeVisible();
  }

  const expected = ["1.1", "1.2", "2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "3.4", "3.5"];
  for (const unitId of expected) {
    await page.getByTestId(`preview-unit-${unitId}`).click();
    await expect(page.getByTestId("preview-unit-title")).toContainText(unitId);
    await expect(page.getByTestId(`preview-progress-${unitId}`)).toBeVisible();
    if (unitId !== "3.5") {
      await expect(page.locator('[data-testid^="preview-topic-"]').first()).toBeVisible();
      await expect(page.locator('[data-testid^="preview-segment-"]').first()).toBeVisible();
      await expect(page.getByTestId("preview-completion-criterion")).toBeVisible();
    } else {
      await expect(page.getByTestId("preview-project")).toBeVisible();
      await expect(page.locator('[data-testid^="project-artifact-"]')).toHaveCount(1);
    }
  }

  await page.getByTestId("preview-unit-1.1").click();
  const firstQuestion = page.locator('[data-testid^="preview-question-"]').first();
  const firstQuestionId = (await firstQuestion.getAttribute("data-testid"))?.replace("preview-question-", "") || "";
  await firstQuestion.locator('input[type="radio"]').first().check();
  const quizResponsePromise = page.waitForResponse((response) =>
    response.url().includes(`/api/beta7-1/preview/batches/${BATCH_ID}/units/1.1/quizzes/${firstQuestionId}/attempts`)
      && response.request().method() === "POST");
  await firstQuestion.getByRole("button", { name: "Enviar resposta" }).click();
  const quizResponse = await quizResponsePromise;
  expect(quizResponse.status()).toBe(200);
  const quizReceipt = await quizResponse.json();
  expect(quizReceipt.state).toBe("ANSWERED");
  expect(quizReceipt).not.toHaveProperty("is_correct");
  await expect(page.getByTestId("preview-progress-1.1")).toContainText("1 / 5 questões respondidas");

  const exercise = page.locator('[data-testid^="preview-exercise-"]').first();
  const exerciseId = (await exercise.getAttribute("data-testid"))?.replace("preview-exercise-", "") || "";
  await page.getByTestId(`preview-exercise-answer-${exerciseId}`).fill("Resposta sintética da prévia Beta 7.1.");
  const exerciseResponsePromise = page.waitForResponse((response) =>
    response.url().includes(`/units/1.1/exercises/${exerciseId}/submissions`) && response.request().method() === "POST");
  await page.getByTestId(`preview-exercise-submit-${exerciseId}`).click();
  const exerciseResponse = await exerciseResponsePromise;
  expect(exerciseResponse.status()).toBe(200);
  await expect(page.getByTestId(`preview-exercise-state-${exerciseId}`)).toContainText("AWAITING_REVIEW");

  await page.getByTestId("preview-unit-2.1").click();
  await expect(page.getByTestId("preview-unit-title")).toContainText("2.1");
  const secondModuleQuestion = page.locator('[data-testid^="preview-question-"]').first();
  await secondModuleQuestion.locator('input[type="radio"]').first().check();
  const moduleTwoQuestionId = (await secondModuleQuestion.getAttribute("data-testid"))?.replace("preview-question-", "") || "";
  const moduleTwoAttempt = page.waitForResponse((response) =>
    response.url().includes(`/units/2.1/quizzes/${moduleTwoQuestionId}/attempts`) && response.request().method() === "POST");
  await secondModuleQuestion.getByRole("button", { name: "Enviar resposta" }).click();
  expect((await moduleTwoAttempt).status()).toBe(200);

  await page.getByTestId("preview-unit-3.5").click();
  await expect(page.getByTestId("preview-project")).toBeVisible();
  await expect(page.locator('[data-testid^="project-artifact-"]')).toHaveCount(1);
  await expect(page.locator('[data-testid*="rubrica"]')).toHaveCount(0);
  await expect(page.locator('[data-testid*="checklist"]')).toHaveCount(0);
  await page.getByTestId("preview-project-delivery").fill("Entrega sintética de evidências do projeto incremental.");
  const deliveryResponsePromise = page.waitForResponse((response) =>
    response.url().endsWith(`/api/beta7-1/preview/batches/${BATCH_ID}/project/submissions`)
      && response.request().method() === "POST");
  await page.getByTestId("preview-project-submit").click();
  const deliveryResponse = await deliveryResponsePromise;
  expect(deliveryResponse.status()).toBe(200);
  const delivery = await deliveryResponse.json();
  expect(delivery.state).toBe("AWAITING_REVIEW");

  await logout(page);
  await login(page, REVIEWER_EMAIL, REVIEWER_PASSWORD);
  await page.getByTestId("preview-unit-3.5").click();
  const reviewItem = page.getByTestId(`preview-review-item-${delivery.id}`);
  await expect(reviewItem).toBeVisible();
  const reviewResponsePromise = page.waitForResponse((response) =>
    response.url().endsWith(`/project/submissions/${delivery.id}/review`) && response.request().method() === "POST");
  await reviewItem.getByRole("button", { name: "Solicitar revisão com feedback" }).click();
  expect((await reviewResponsePromise).status()).toBe(200);

  await logout(page);
  await login(page, STUDENT_EMAIL, STUDENT_PASSWORD);
  await page.getByTestId("preview-unit-3.5").click();
  const reviewedDelivery = page.getByTestId(`preview-project-submission-state-${delivery.id}`);
  await expect(reviewedDelivery).toContainText("NEEDS_REVISION");
  await expect(reviewedDelivery).toContainText("critérios pedagógicos finais");
  await page.reload();
  await expect(page.getByTestId("beta71-preview")).toBeVisible();
  await page.getByTestId("preview-unit-1.1").click();
  await expect(page.getByTestId("preview-progress-1.1")).toContainText("1 / 5 questões respondidas");

  const apiContext = await request.newContext({ baseURL: API_BASE_URL });
  try {
    const loggedIn = await apiContext.post("/api/auth/login", {
      data: { email: "beta7-1-unscoped@example.com", password: process.env.E2E_UNSCOPED_PASSWORD },
    });
    expect(loggedIn.status()).toBe(200);
    expect((await apiContext.get(`/api/beta7-1/preview/batches/${BATCH_ID}`)).status()).toBe(404);
    expect((await apiContext.get(`/api/beta7-1/preview/batches/${BATCH_ID}/project/restricted`)).status()).toBe(404);
  } finally {
    await apiContext.dispose();
  }
});
