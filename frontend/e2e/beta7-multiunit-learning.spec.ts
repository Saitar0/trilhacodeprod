import { request as playwrightRequest } from "@playwright/test";
import { expect, test } from "./fixtures";

const API_BASE_URL = process.env.API_BASE_URL || "http://127.0.0.1:18000";
const TRACK_ID = process.env.BETA7_E2E_TRACK_ID || "";
const FIRST_NODE_ID = process.env.BETA7_E2E_FIRST_NODE_ID || "";
const SECOND_NODE_ID = process.env.BETA7_E2E_SECOND_NODE_ID || "";
const FIRST_QUIZ_ID = process.env.BETA7_E2E_FIRST_QUIZ_ID || "";
const SECOND_QUIZ_ID = process.env.BETA7_E2E_SECOND_QUIZ_ID || "";
const EXERCISE_ID = process.env.BETA7_E2E_EXERCISE_ID || "";
const STUDENT_EMAIL = process.env.E2E_STUDENT_EMAIL || "student@example.com";
const STUDENT_PASSWORD = process.env.E2E_STUDENT_PASSWORD || "";
const REVIEWER_EMAIL = process.env.E2E_REVIEWER_EMAIL || "reviewer@example.com";
const REVIEWER_PASSWORD = process.env.E2E_REVIEWER_PASSWORD || "";

async function login(page: import("@playwright/test").Page, email: string, password: string) {
  await page.goto("/login");
  await page.getByTestId("login-email-input").fill(email);
  await page.getByTestId("login-password-input").fill(password);
  await page.getByTestId("login-submit-button").click();
  await expect(page.getByTestId("user-menu-trigger")).toBeVisible();
}

async function logout(page: import("@playwright/test").Page) {
  await page.getByTestId("user-menu-trigger").click();
  await page.getByTestId("user-menu-logout").click();
  await expect(page.getByTestId("login-form")).toBeVisible();
}

test("learner navigates two units, completes activities, and sees scoped review progress", async ({ page }) => {
  test.skip(!TRACK_ID || !FIRST_NODE_ID || !SECOND_NODE_ID || !FIRST_QUIZ_ID || !SECOND_QUIZ_ID || !EXERCISE_ID,
    "Requires the Beta 7 owned synthetic multiunit fixture.");
  await page.route("https://**/*", (route) => route.abort());

  await login(page, STUDENT_EMAIL, STUDENT_PASSWORD);
  const treeResponse = page.waitForResponse((response) =>
    response.request().method() === "GET" && response.url().endsWith(`/api/tracks/${TRACK_ID}/tree`));
  await page.goto(`/trilhas/${TRACK_ID}`);
  expect((await treeResponse).status()).toBe(200);
  await page.getByTestId(`student-tree-node-${FIRST_NODE_ID}`).click();
  await expect(page.getByTestId("reader-title")).toHaveText("Unidade 1.1 — aula sintética");
  await expect(page.getByText("Conteúdo sintético de navegação Beta 7.", { exact: false })).toBeVisible();

  const firstLesson = await page.request.get(`${API_BASE_URL}/api/nodes/${FIRST_NODE_ID}`);
  expect(firstLesson.status()).toBe(200);
  const serialized = JSON.stringify(await firstLesson.json());
  expect(serialized).not.toContain("correct_option_id");
  expect(serialized).not.toContain("RUBRICA RESTRITA");
  expect(serialized).not.toContain("RESPOSTA PRIVADA");

  await page.getByRole("button", { name: "Iniciar atividade" }).first().click();
  await page.getByTestId("activity-option-right").first().check();
  await page.getByTestId(`content-block-${FIRST_QUIZ_ID}`).getByRole("button", { name: "Enviar resposta" }).click();
  await expect(page.getByTestId("activity-feedback").first()).toContainText("Resposta correta.");

  await page.getByTestId(`exercise-answer-${EXERCISE_ID}`).fill("Resposta sintética, preservada no banco descartável.");
  const submissionResponse = page.waitForResponse((response) =>
    response.request().method() === "POST" && response.url().endsWith("/api/submissions/submit"));
  await page.getByTestId(`exercise-submit-${EXERCISE_ID}`).click();
  const submitted = await submissionResponse;
  expect(submitted.status()).toBe(200);
  const submission = await submitted.json();
  expect(submission.status).toBe("submitted");
  await expect(page.getByTestId(`exercise-status-${EXERCISE_ID}`)).toHaveText("Enviado");

  await page.getByTestId("reader-next-button").click();
  await expect(page.getByTestId("reader-title")).toHaveText("Unidade 1.2 — aula sintética");
  await page.getByRole("button", { name: "Iniciar atividade" }).click();
  await page.getByTestId("activity-option-right").check();
  await page.getByTestId(`content-block-${SECOND_QUIZ_ID}`).getByRole("button", { name: "Enviar resposta" }).click();
  await expect(page.getByTestId("activity-feedback")).toContainText("Resposta correta.");

  const unscoped = await playwrightRequest.newContext({ baseURL: API_BASE_URL });
  try {
    const loginResponse = await unscoped.post("/api/auth/login", {
      data: { email: "unscoped@example.com", password: process.env.E2E_UNSCOPED_PASSWORD },
    });
    expect(loginResponse.status()).toBe(200);
    expect((await unscoped.get(`/api/submissions?track_id=${TRACK_ID}`)).status()).toBe(403);
    expect((await unscoped.get(`/api/submissions/${submission.id}`)).status()).toBe(404);
  } finally {
    await unscoped.dispose();
  }

  await logout(page);
  await login(page, REVIEWER_EMAIL, REVIEWER_PASSWORD);
  await page.goto("/admin/correcoes");
  const queueItem = page.getByTestId(`grading-item-${submission.id}`);
  await expect(queueItem).toBeVisible();
  await queueItem.click();
  await expect(page.getByTestId("grading-panel")).toBeVisible();
  await expect(page.getByText("RUBRICA RESTRITA — fixture Beta 7.")).toBeVisible();
  await page.getByTestId("grading-claim-button").click();
  await page.getByTestId("grading-feedback-input").fill("A explicação atende ao critério sintético.");
  const gradeResponse = page.waitForResponse((response) =>
    response.request().method() === "POST" && response.url().endsWith(`/api/submissions/${submission.id}/grade`));
  await page.getByTestId("grading-approve-button").click();
  const graded = await gradeResponse;
  expect(graded.status()).toBe(200);
  expect((await graded.json()).grading.feedback).toBe("A explicação atende ao critério sintético.");
  await expect(page.getByTestId("grading-result")).toContainText("Aprovado");

  await logout(page);
  await login(page, STUDENT_EMAIL, STUDENT_PASSWORD);
  await page.goto(`/trilhas/${TRACK_ID}/n/${FIRST_NODE_ID}`);
  await expect(page.getByTestId(`submission-feedback-${submission.id}`)).toContainText("A explicação atende ao critério sintético.");
  await expect(page.getByText("RUBRICA RESTRITA — fixture Beta 7.")).toHaveCount(0);

  const progressResponse = page.waitForResponse((response) =>
    response.request().method() === "GET" && response.url().endsWith(`/api/progress/tracks/${TRACK_ID}`));
  await page.reload();
  const progress = await progressResponse;
  expect(progress.status()).toBe(200);
  const state = await progress.json();
  expect(state.blocks[FIRST_QUIZ_ID].status).toBe("completed");
  expect(state.blocks[SECOND_QUIZ_ID].status).toBe("completed");
  expect(state.blocks[EXERCISE_ID].status).toBe("completed");
  expect(state.blocks[EXERCISE_ID].data.review_state).toBe("approved");
});
