import { expect, test } from "./fixtures";
import { request } from "@playwright/test";

test.describe.configure({ retries: 0 });

const BATCH_ID = process.env.BETA7_1_E2E_BATCH_ID || "";
const PRIVATE_TRACK_ID = process.env.BETA9_PRIVATE_TRACK_ID || "";
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
  if (PRIVATE_TRACK_ID) {
    const privateReadStatus = await page.evaluate(async (trackId) => {
      const response = await fetch(`/api/tracks/${trackId}/tree`, { credentials: "include" });
      return response.status;
    }, PRIVATE_TRACK_ID);
    expect(privateReadStatus).toBe(404);
  }
  await expect(page.getByTestId("preview-phase-progress")).toContainText("BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA");
  for (const moduleId of ["1", "2", "3"]) {
    await expect(page.getByTestId(`preview-module-${moduleId}`)).toBeVisible();
  }

  const expected = ["1.1", "1.2", "2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "3.4", "3.5"];
  let existingProjectSubmissionCount = 0;
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
      // The preceding HTTP regression intentionally submits and reviews one
      // delivery in this same owned fixture; preserve that history in the E2E.
      existingProjectSubmissionCount = await page.locator('[data-testid^="preview-project-submission-state-"]').count();
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
  expect(delivery.attempt).toBe(existingProjectSubmissionCount + 1);

  await logout(page);
  await login(page, REVIEWER_EMAIL, REVIEWER_PASSWORD);
  await page.getByTestId("preview-unit-3.5").click();
  await expect(page.getByTestId("project-rubric-status")).toContainText("PROPOSED");
  await expect(page.getByTestId("project-approve-disabled")).toBeDisabled();
  const reviewItem = page.getByTestId(`preview-review-item-${delivery.id}`);
  await expect(reviewItem).toBeVisible();
  const reviewerApi = await request.newContext({ baseURL: API_BASE_URL });
  try {
    const reviewerLogin = await reviewerApi.post("/api/auth/login", {
      data: { email: REVIEWER_EMAIL, password: REVIEWER_PASSWORD },
    });
    expect(reviewerLogin.status()).toBe(200);
    const rubricResponse = await reviewerApi.get(`/api/beta7-2/assessment/batches/${BATCH_ID}/project/rubric`);
    expect(rubricResponse.status()).toBe(200);
    const rubric = await rubricResponse.json();
    expect(rubric.state).toBe("PROPOSED");
    expect(rubric.criteria.map((criterion: {
      criterion_id: string;
      provenance: { source_artifact_id: string; source_sha256: string; source_revision: string; source_state: string };
      observable_evidence: string[];
    }) => ({
      criterion_id: criterion.criterion_id,
      source_artifact_id: criterion.provenance.source_artifact_id,
      source_sha256: criterion.provenance.source_sha256,
      source_revision: criterion.provenance.source_revision,
      source_state: criterion.provenance.source_state,
      has_observable_evidence: criterion.observable_evidence.length > 0,
    }))).toEqual([
      {
        criterion_id: "3.5:M01",
        source_artifact_id: "f1-3-5-marco-01-escopo",
        source_sha256: "2541ab7ef86bec2e02f065fceb3fe8a581f6135aa5e03722f1120ac124663c0d",
        source_revision: "migration@147dc68:tracked-clean-first-phase-files",
        source_state: "rascunho",
        has_observable_evidence: true,
      },
      {
        criterion_id: "3.5:M02",
        source_artifact_id: "f1-3-5-marco-02-repositorio-setup",
        source_sha256: "69ed88657b0b19796058b8c8d6816f6800965abd17d860ca3b4fcd3a6e3ac5f9",
        source_revision: "migration@147dc68:tracked-clean-first-phase-files",
        source_state: "rascunho",
        has_observable_evidence: true,
      },
      {
        criterion_id: "3.5:M03",
        source_artifact_id: "f1-3-5-marco-03-historico-seguro",
        source_sha256: "2df7903a472803d96a5a357a5fef5b1497bdb6bc20e233d79edc7b1a5fb942d8",
        source_revision: "migration@147dc68:tracked-clean-first-phase-files",
        source_state: "rascunho",
        has_observable_evidence: true,
      },
      {
        criterion_id: "3.5:M04",
        source_artifact_id: "f1-3-5-marco-04-publicacao-remota",
        source_sha256: "b922364218f2952c3c7785f70d53799ecd4d1267e302ef8cfac48e0613387e55",
        source_revision: "migration@147dc68:tracked-clean-first-phase-files",
        source_state: "rascunho",
        has_observable_evidence: true,
      },
    ]);
    const forbiddenApproval = await reviewerApi.post(
      `/api/beta7-2/assessment/batches/${BATCH_ID}/project/submissions/${delivery.id}/assess`,
      {
        data: {
          project_version: delivery.source_sha256,
          rubric_id: rubric.rubric_id,
          rubric_version: rubric.version,
          expected_revision: 0,
          outcome: "APPROVED",
          feedback: "Approval must remain blocked without pedagogical sign-off.",
          criteria: [],
        },
        headers: { "Idempotency-Key": "beta72-forbidden-approval", Origin: "http://127.0.0.1:3000" },
      },
    );
    expect(forbiddenApproval.status()).toBe(409);
  } finally {
    await reviewerApi.dispose();
  }
  const reviewResponsePromise = page.waitForResponse((response) =>
    response.url().endsWith(`/project/submissions/${delivery.id}/assess`) && response.request().method() === "POST");
  await reviewItem.getByRole("button", { name: "Registrar feedback e solicitar revisão" }).click();
  expect((await reviewResponsePromise).status()).toBe(200);

  await logout(page);
  await login(page, STUDENT_EMAIL, STUDENT_PASSWORD);
  await page.getByTestId("preview-unit-3.5").click();
  const reviewedDelivery = page.getByTestId(`preview-project-submission-state-${delivery.id}`);
  await expect(reviewedDelivery).toContainText("NEEDS_REVISION");
  await expect(reviewedDelivery).toContainText("decisão pedagógica");
  await expect(page.locator('[data-testid^="project-assessment-"]').first()).toContainText("NEEDS_REVISION");
  await page.getByTestId("preview-project-delivery").fill("Nova entrega vinculada à solicitação de revisão.");
  const resubmissionResponsePromise = page.waitForResponse((response) =>
    response.url().endsWith(`/api/beta7-1/preview/batches/${BATCH_ID}/project/submissions`)
      && response.request().method() === "POST");
  await page.getByTestId("preview-project-submit").click();
  const resubmissionResponse = await resubmissionResponsePromise;
  expect(resubmissionResponse.status()).toBe(200);
  const resubmission = await resubmissionResponse.json();
  expect(resubmission.attempt).toBe(existingProjectSubmissionCount + 2);
  expect(resubmission.previous_submission_id).toBe(delivery.id);
  await page.reload();
  await expect(page.getByTestId("beta71-preview")).toBeVisible();
  await page.getByTestId("preview-unit-3.5").click();
  await expect(page.getByTestId(`preview-project-submission-state-${delivery.id}`)).toContainText("SUPERSEDED_BY_RESUBMISSION");
  await expect(page.getByTestId(`preview-project-submission-state-${resubmission.id}`))
    .toContainText(`Tentativa ${resubmission.attempt}`);
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
    expect((await apiContext.get(`/api/beta7-2/assessment/batches/${BATCH_ID}/project/rubric`)).status()).toBe(404);
  } finally {
    await apiContext.dispose();
  }
});
