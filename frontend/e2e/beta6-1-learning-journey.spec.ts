import { request as playwrightRequest } from "@playwright/test";
import { expect, test } from "./fixtures";

const API_BASE_URL = process.env.API_BASE_URL || "http://127.0.0.1:18000";
const TRACK_ID = process.env.BETA6_E2E_TRACK_ID || "";
const NODE_ID = process.env.BETA6_E2E_NODE_ID || "";
const QUIZ_ID = process.env.BETA6_E2E_QUIZ_ID || "";
const EXERCISE_ID = process.env.BETA6_E2E_EXERCISE_ID || "";
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

test("learner studies, submits a quiz and exercise, and receives scoped manual feedback", async ({ page }) => {
  test.skip(!TRACK_ID || !NODE_ID || !QUIZ_ID || !EXERCISE_ID, "Requires the owned Beta 6.1 synthetic fixture.");
  await page.route("https://**/*", (route) => route.abort());

  await login(page, STUDENT_EMAIL, STUDENT_PASSWORD);
  const treeResponse = page.waitForResponse((response) =>
    response.request().method() === "GET" && response.url().endsWith(`/api/tracks/${TRACK_ID}/tree`));
  const lessonResponse = page.waitForResponse((response) =>
    response.request().method() === "GET" && response.url().endsWith(`/api/nodes/${NODE_ID}`));
  await page.goto(`/trilhas/${TRACK_ID}/n/${NODE_ID}`);
  const [tree, lesson] = await Promise.all([treeResponse, lessonResponse]);
  expect(tree.status()).toBe(200);
  expect(lesson.status()).toBe(200);
  const lessonBody = await lesson.json();
  const serializedLesson = JSON.stringify(lessonBody);
  expect(serializedLesson).not.toContain("correct_option_id");
  expect(serializedLesson).not.toContain("RESPOSTA PRIVADA BETA 6.1");
  expect(serializedLesson).not.toContain("RUBRICA RESTRITA BETA 6.1");
  await expect(page.getByTestId("reader-title")).toHaveText("Aula Beta 6.1");
  await expect(page.getByText("Conteúdo didático", { exact: false })).toBeVisible();

  await page.getByRole("button", { name: "Iniciar atividade" }).click();
  await page.getByTestId("activity-option-right").check();
  await page.getByTestId(`content-block-${QUIZ_ID}`).getByRole("button", { name: "Enviar resposta" }).click();
  await expect(page.getByTestId("activity-feedback")).toContainText("Resposta correta.");

  const exerciseResponse = page.waitForResponse((response) =>
    response.request().method() === "POST" && response.url().endsWith("/api/submissions/submit"));
  const answer = "Uma variável associa um nome a um valor e permite reutilizá-lo.";
  await page.getByTestId(`exercise-answer-${EXERCISE_ID}`).fill(answer);
  await page.getByTestId(`exercise-submit-${EXERCISE_ID}`).click();
  const submitted = await exerciseResponse;
  expect(submitted.status()).toBe(200);
  const submission = await submitted.json();
  expect(submission.status).toBe("submitted");
  expect(submission.grading_context).toBeUndefined();
  await expect(page.getByTestId(`exercise-status-${EXERCISE_ID}`)).toHaveText("Enviado");

  const unscoped = await playwrightRequest.newContext({ baseURL: API_BASE_URL });
  try {
    const loginResponse = await unscoped.post("/api/auth/login", {
      data: { email: "unscoped@example.com", password: process.env.E2E_UNSCOPED_PASSWORD },
    });
    expect(loginResponse.status()).toBe(200);
    const queue = await unscoped.get(`/api/submissions?track_id=${TRACK_ID}`);
    expect(queue.status()).toBe(403);
    const detail = await unscoped.get(`/api/submissions/${submission.id}`);
    expect(detail.status()).toBe(404);
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
  await expect(page.getByText("RUBRICA RESTRITA BETA 6.1")).toBeVisible();
  await expect(page.getByText("RESPOSTA PRIVADA BETA 6.1")).toBeVisible();
  await page.getByTestId("grading-claim-button").click();
  await expect(page.getByTestId("grading-status")).toHaveText("Em correção");
  await page.getByTestId("grading-feedback-input").fill("Sua explicação relaciona nome e valor corretamente.");
  const gradingResponse = page.waitForResponse((response) =>
    response.request().method() === "POST" && response.url().endsWith(`/api/submissions/${submission.id}/grade`));
  await page.getByTestId("grading-approve-button").click();
  const graded = await gradingResponse;
  expect(graded.status()).toBe(200);
  expect((await graded.json()).grading.feedback).toBe("Sua explicação relaciona nome e valor corretamente.");
  await expect(page.getByTestId("grading-result")).toContainText("Aprovado");
  await expect(page.getByTestId("grading-result")).toContainText("Sua explicação relaciona nome e valor corretamente.");

  await logout(page);
  await login(page, STUDENT_EMAIL, STUDENT_PASSWORD);
  const mySubmissionsResponse = page.waitForResponse((response) =>
    response.request().method() === "GET" && new URL(response.url()).pathname === "/api/submissions/mine");
  await page.goto(`/trilhas/${TRACK_ID}/n/${NODE_ID}`);
  const mySubmissions = await mySubmissionsResponse;
  expect(mySubmissions.status()).toBe(200);
  const ownSubmission = (await mySubmissions.json()).find((item: { id: string }) => item.id === submission.id);
  expect(ownSubmission?.grading?.feedback).toBe("Sua explicação relaciona nome e valor corretamente.");
  await expect(page.getByTestId(`exercise-status-${EXERCISE_ID}`)).toHaveText("Corrigido");
  await expect(page.getByTestId(`submission-feedback-${submission.id}`)).toContainText("Aprovado");
  await expect(page.getByTestId(`submission-feedback-${submission.id}`)).toContainText("Sua explicação relaciona nome e valor corretamente.");
  await expect(page.getByText("RUBRICA RESTRITA BETA 6.1")).toHaveCount(0);
  await expect(page.getByText("RESPOSTA PRIVADA BETA 6.1")).toHaveCount(0);

  const progressResponse = page.waitForResponse((response) =>
    response.request().method() === "GET" && response.url().endsWith(`/api/progress/tracks/${TRACK_ID}`));
  await page.reload();
  const progress = await progressResponse;
  expect(progress.status()).toBe(200);
  const progressBody = await progress.json();
  expect(progressBody.blocks[QUIZ_ID].status).toBe("completed");
  expect(progressBody.blocks[EXERCISE_ID].status).toBe("completed");
  await expect(page.getByText("Sua explicação relaciona nome e valor corretamente.")).toBeVisible();
});
