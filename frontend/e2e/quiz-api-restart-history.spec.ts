import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { expect, test } from "@playwright/test";

const ARTIFACT_DIR = process.env.E2E_ARTIFACT_DIR;
const API_BASE_URL = process.env.E2E_API_BASE_URL || "http://127.0.0.1:18000";

test("quiz history remains available in the real browser after an API process restart", async ({ page }) => {
  test.skip(
    process.env.E2E_RUN_RESTART_HISTORY !== "1",
    "Run explicitly after restarting the isolated API with the same disposable database.",
  );
  expect(ARTIFACT_DIR, "E2E_ARTIFACT_DIR points to this run's isolated temporary folder").toBeTruthy();
  const fixture = JSON.parse(await readFile(join(ARTIFACT_DIR!, "quiz-restart-replay.json"), "utf8")) as {
    track_id: string;
    topic_id: string;
    topic_title: string;
    quiz_id: string;
    student_email: string;
    student_password: string;
    attempt_version_id: string;
    idempotency_key: string;
    expected_attempt_id: string;
    expected_attempt_number: number;
    expected_attempts_used: number;
    expected_history_count: number;
    expected_active_version_id: string;
  };

  await page.goto("/login");
  await page.getByTestId("login-email-input").fill(fixture.student_email);
  await page.getByTestId("login-password-input").fill(fixture.student_password);
  await page.getByTestId("login-submit-button").click();
  await expect(page.getByTestId("catalog-track-card-trilha-code")).toBeVisible();

  await page.goto(`/trilhas/${fixture.track_id}/n/${fixture.topic_id}`);
  await expect(page.getByTestId("reader-title")).toHaveText(fixture.topic_title);
  await expect(page.getByTestId(`quiz-api-session-${fixture.quiz_id}`)).toBeVisible();
  await expect(page.getByText("3 tentativas restantes")).toBeVisible();
  const history = page.getByTestId("quiz-history");
  await expect(history).toContainText(`Histórico de tentativas (${fixture.expected_history_count})`);
  await expect(history).toContainText("90%");
  const historyResponse = await page.context().request.get(
    `${API_BASE_URL}/api/quizzes/${fixture.quiz_id}/attempts`,
  );
  expect(historyResponse.status()).toBe(200);
  const persistedHistory = await historyResponse.json() as {
    total: number;
    items: Array<{ attempt_id: string; attempt_number: number; score_percent: number }>;
  };
  expect(persistedHistory.total).toBe(fixture.expected_history_count);
  expect(persistedHistory.items).toContainEqual(expect.objectContaining({
    attempt_id: fixture.expected_attempt_id,
    attempt_number: fixture.expected_attempt_number,
    score_percent: 90,
  }));
  const recovery = await page.context().request.post(
    `${API_BASE_URL}/api/quizzes/${fixture.quiz_id}/recovery`,
    { data: { version_id: fixture.attempt_version_id, idempotency_key: fixture.idempotency_key } },
  );
  expect(recovery.status()).toBe(200);
  const recovered = await recovery.json();
  expect(recovered.state).toBe("confirmed");
  expect(recovered.attempts_used).toBe(fixture.expected_history_count);
  expect(recovered.attempt.attempt_id).toBe(fixture.expected_attempt_id);
  expect(recovered.attempt.version_id).toBe(fixture.attempt_version_id);
  expect(recovered.attempt.attempt_number).toBe(fixture.expected_attempt_number);
  expect(JSON.stringify(recovered)).not.toContain("correct_option_id");
  expect(JSON.stringify(recovered)).not.toContain("explanation");
  const publicResponse = await page.context().request.get(`${API_BASE_URL}/api/quizzes/${fixture.quiz_id}`);
  expect(publicResponse.status()).toBe(200);
  const publicQuiz = await publicResponse.json() as {
    version_id: string;
    attempts_used: number;
    attempts_remaining: number;
    review_available: boolean;
  };
  expect(publicQuiz).toMatchObject({
    version_id: fixture.expected_active_version_id,
    attempts_used: 0,
    attempts_remaining: 3,
    review_available: false,
  });
});
