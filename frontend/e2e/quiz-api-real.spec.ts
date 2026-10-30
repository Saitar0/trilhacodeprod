import { chromium, expect, request as apiRequest, test, type APIRequestContext, type Page } from "@playwright/test";
import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { randomUUID } from "node:crypto";

const API_BASE_URL = process.env.E2E_API_BASE_URL || "http://127.0.0.1:18000";
const API_RATE_LIMIT_URL = process.env.E2E_RATE_LIMIT_API_URL || "http://127.0.0.1:18001";
const FRONTEND_ON = process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:5174";
const FRONTEND_OFF = process.env.PLAYWRIGHT_FLAG_OFF_URL || "http://127.0.0.1:5175";
const FRONTEND_ABSENT = process.env.PLAYWRIGHT_FLAG_ABSENT_URL || "http://127.0.0.1:5176";
const FRONTEND_RATE_LIMIT = process.env.PLAYWRIGHT_RATE_LIMIT_URL || "http://127.0.0.1:5177";
const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || "e2e-admin@example.com";
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || "E2E-Test-Admin-59!";
const ARTIFACT_DIR = process.env.E2E_ARTIFACT_DIR;
const EMAIL_DIR = process.env.E2E_EMAIL_DIR;

let quizStudentEmail: string;
let quizStudentPassword: string;
let rateStudentEmail: string;
let rateStudentPassword: string;

type Question = {
  question_id: string;
  order: number;
  prompt: string;
  options: Array<{ option_id: string; text: string }>;
};

type QuizFixture = {
  trackId: string;
  topicId: string;
  topicTitle: string;
  quizId: string;
  versionId: string;
  title: string;
  questions: Question[];
  correctOptionByQuestion: Record<string, string>;
  blocks: Array<{ id: string; importRef: string; correctIndex: number }>;
};

let adminApi: APIRequestContext;
let fixture: QuizFixture;

test.describe.configure({ mode: "serial" });
test.setTimeout(120_000);

async function login(api: APIRequestContext, email: string, password: string) {
  const response = await api.post("/api/auth/login", { data: { email, password } });
  expect(response.status(), "login in isolated E2E backend").toBe(200);
}

async function enterFirstTopic(page: Page, baseUrl = FRONTEND_ON, email = quizStudentEmail, password = quizStudentPassword) {
  page.setDefaultTimeout(15_000);
  await page.goto(`${baseUrl}/login`);
  const emailInput = page.getByTestId("login-email-input");
  if (await emailInput.count()) {
    await emailInput.fill(email);
    await page.getByTestId("login-password-input").fill(password);
    await page.getByTestId("login-submit-button").click();
  }
  await expect(page.getByTestId("catalog-track-card-trilha-code")).toBeVisible();
  await page.goto(`${baseUrl}/trilhas/${fixture.trackId}`);
  await page.getByTestId(`student-tree-node-${fixture.topicId}`).click();
  await expect(page.getByTestId("reader-title")).toHaveText(fixture.topicTitle);
}

async function createVerifiedQuizStudent(): Promise<{ email: string; password: string }> {
  expect(EMAIL_DIR, "E2E_EMAIL_DIR points to this run's isolated local mailbox").toBeTruthy();
  const email = `e2e-quiz-${randomUUID()}@example.com`;
  const password = `E2E-Quiz-${randomUUID()}!`;
  const registered = await adminApi.post("/api/auth/register", {
    data: { name: "Aluno E2E Quiz", email, password },
  });
  expect(registered.status(), "register a dedicated student in the disposable backend").toBe(202);

  let token: string | undefined;
  const mailDeadline = Date.now() + 10_000;
  while (!token && Date.now() < mailDeadline) {
    const messages = (await readdir(EMAIL_DIR!)).filter((name) => name.endsWith(".eml"));
    for (const name of messages) {
      const message = await readFile(join(EMAIL_DIR!, name), "utf8");
      if (!message.toLowerCase().includes(`to: ${email.toLowerCase()}`)) continue;
      const decoded = message
        .replace(/=\r?\n/g, "")
        .replace(/=([0-9A-F]{2})/gi, (_encoded, hex: string) => String.fromCharCode(Number.parseInt(hex, 16)));
      token = decoded.match(/[?&]token=([A-Za-z0-9_-]{32,})/)?.[1];
      if (token) break;
    }
    if (!token) await new Promise((resolve) => setTimeout(resolve, 100));
  }
  expect(token, "the isolated local mailbox contains this user's verification token").toBeTruthy();
  const verified = await adminApi.post("/api/auth/verify-email", { data: { token } });
  expect(verified.status(), "verify the dedicated disposable student").toBe(200);
  return { email, password };
}

function answersWithCorrectCount(correctCount: number) {
  return [...fixture.questions]
    .sort((left, right) => left.order - right.order)
    .map((question, index) => {
      const correctOptionId = fixture.correctOptionByQuestion[question.question_id];
      const selected = index < correctCount
        ? correctOptionId
        : question.options.find((option) => option.option_id !== correctOptionId)?.option_id;
      if (!selected) throw new Error(`Questão sem alternativa incorreta para fixture: ${question.question_id}`);
      return { question_id: question.question_id, option_id: selected };
    });
}

async function selectCorrectCount(page: Page, correctCount: number) {
  for (const [index, question] of [...fixture.questions].sort((left, right) => left.order - right.order).entries()) {
    const correctOptionId = fixture.correctOptionByQuestion[question.question_id];
    const correctIndex = question.options.findIndex((option) => option.option_id === correctOptionId);
    const selectedIndex = index < correctCount ? correctIndex : (correctIndex + 1) % question.options.length;
    await page.getByTestId(`quiz-option-${fixture.quizId}-${question.question_id}-${selectedIndex}`).check();
  }
}

async function createPublishedQuiz(): Promise<QuizFixture> {
  const tracksResponse = await adminApi.get("/api/tracks?limit=500");
  expect(tracksResponse.status()).toBe(200);
  const tracks = await tracksResponse.json() as Array<{ id: string; slug: string }>;
  const track = tracks.find((item) => item.slug === "trilha-code");
  expect(track, "the disposable database has the seeded public track").toBeTruthy();

  const treeResponse = await adminApi.get(`/api/tracks/${track!.id}/tree`);
  expect(treeResponse.status()).toBe(200);
  const tree = await treeResponse.json() as { nodes: Array<{ id: string; kind: string; title: string; parent_id: string | null }> };
  const seededTopic = tree.nodes.find((node) => node.kind === "topic" && node.title === "Variáveis e tipos");
  expect(seededTopic, "the seeded topic provides a valid module parent").toBeTruthy();
  const topicTitle = `Quiz E2E ${randomUUID().slice(0, 8)}`;
  const topicResponse = await adminApi.post("/api/nodes", {
    data: {
      track_id: track!.id,
      parent_id: seededTopic!.parent_id,
      kind: "topic",
      title: topicTitle,
      summary: "Tópico descartável para validar o fluxo real de quiz.",
      status: "published",
      meta: { e2e_only: true },
    },
  });
  expect(topicResponse.status(), "create isolated test topic").toBe(200);
  const topic = await topicResponse.json() as { id: string };

  const theoryResponse = await adminApi.post("/api/blocks", {
    data: {
      node_id: topic.id,
      type: "theory_text",
      title: "Leitura de apoio",
      status: "published",
      data: { body: "Conteúdo de apoio continua disponível." },
    },
  });
  expect(theoryResponse.status(), "create a non-assessment block for feature-off checks").toBe(200);

  const createdBlocks: QuizFixture["blocks"] = [];
  const suiteId = randomUUID().replaceAll("-", "");
  for (let index = 0; index < 10; index += 1) {
    const correctIndex = index % 4;
    const questionNumber = index + 1;
    const importRef = `e2e-${suiteId}-q${questionNumber}`;
    const response = await adminApi.post("/api/blocks", {
      data: {
        node_id: topic.id,
        type: "quiz",
        title: `E2E questão ${questionNumber}`,
        status: "published",
        data: {
          question: `Enunciado E2E ${questionNumber}`,
          options: ["Alternativa A", "Alternativa B", "Alternativa C", "Alternativa D"],
          correct_index: correctIndex,
          explanation: `Explicação E2E privada ${questionNumber}.`,
          import_ref: importRef,
        },
      },
    });
    expect(response.status(), `create disposable quiz question ${index}`).toBe(200);
    createdBlocks.push({ id: (await response.json()).id as string, importRef, correctIndex });
  }

  const publication = await adminApi.post(`/api/admin/quizzes/${topic.id}/versions`);
  expect(publication.status(), "publish immutable test quiz version").toBe(200);
  const published = await publication.json() as { quiz_id: string; version_id: string; title: string };
  const publicResponse = await adminApi.get(`/api/quizzes/${published.quiz_id}`);
  expect(publicResponse.status()).toBe(200);
  const publicQuiz = await publicResponse.json() as {
    questions: Question[];
    version_id: string;
    title: string;
  };
  expect(publicQuiz.questions).toHaveLength(10);

  const correctOptionByQuestion: Record<string, string> = {};
  for (const question of publicQuiz.questions) {
    const block = createdBlocks.find((candidate) => candidate.importRef === question.question_id);
    expect(block, `published question ${question.question_id} maps to its source block`).toBeTruthy();
    correctOptionByQuestion[question.question_id] = question.options[block!.correctIndex].option_id;
  }

  return {
    trackId: track!.id,
    topicId: topic.id,
    topicTitle,
    quizId: published.quiz_id,
    versionId: publicQuiz.version_id,
    title: publicQuiz.title,
    questions: publicQuiz.questions,
    correctOptionByQuestion,
    blocks: createdBlocks,
  };
}

test.beforeAll(async () => {
  expect(process.env.E2E_ARTIFACT_DIR, "E2E_ARTIFACT_DIR points to this run's unique temporary folder").toBeTruthy();
  expect(EMAIL_DIR, "E2E_EMAIL_DIR points to this run's isolated local mailbox").toBeTruthy();
  adminApi = await apiRequest.newContext({ baseURL: API_BASE_URL });
  await login(adminApi, ADMIN_EMAIL, ADMIN_PASSWORD);
  ({ email: quizStudentEmail, password: quizStudentPassword } = await createVerifiedQuizStudent());
  ({ email: rateStudentEmail, password: rateStudentPassword } = await createVerifiedQuizStudent());
  fixture = await createPublishedQuiz();
});

test.afterAll(async () => {
  // Keep the disposable topic, quiz snapshot, and attempts until the external
  // backend-restart replay probe finishes; the entire database is temporary.
  await adminApi?.dispose();
});

test("real API lifecycle: score, retries, gated review, history, idempotency, and isolation", async ({ page }) => {
  const publicResponsePromise = page.waitForResponse((response) =>
    response.url() === `${API_BASE_URL}/api/quizzes/${fixture.quizId}` && response.request().method() === "GET",
  );
  await enterFirstTopic(page);
  await expect(page.getByTestId(`quiz-api-session-${fixture.quizId}`)).toBeVisible();
  const firstPublicResponse = await publicResponsePromise;
  expect(firstPublicResponse.status()).toBe(200);
  const publicPayload = await firstPublicResponse.json();
  expect(publicPayload.questions).toHaveLength(10);
  for (const protectedField of ["correct_index", "correct_option_id", "explanation", "content_hash", "answer_key"]) {
    expect(JSON.stringify(publicPayload)).not.toContain(protectedField);
  }

  const anonymous = await apiRequest.newContext({ baseURL: API_BASE_URL });
  const unauthenticated = await anonymous.get(`/api/quizzes/${fixture.quizId}`);
  expect(unauthenticated.status()).toBe(401);
  await anonymous.dispose();

  const beforeAttemptReview = await page.context().request.get(
    `${API_BASE_URL}/api/quizzes/${fixture.quizId}/versions/${fixture.versionId}/review`,
    { headers: { origin: FRONTEND_ON } },
  );
  expect(beforeAttemptReview.status()).toBe(403);
  const fakeGrade = await page.context().request.post(`${API_BASE_URL}/api/quizzes/${fixture.quizId}/attempts`, {
    data: { version_id: fixture.versionId, answers: [], passed: true, score_percent: 100, attempt_number: 1 },
    headers: { "Idempotency-Key": randomUUID() },
  });
  expect(fakeGrade.status()).toBe(422);

  await selectCorrectCount(page, 7);
  let firstIntentKey: string | undefined;
  let firstRequestPayload: { version_id: string; answers: Array<{ question_id: string; option_id: string }> } | undefined;
  await page.route(`**/api/quizzes/${fixture.quizId}/attempts`, async (route) => {
    if (route.request().method() === "POST") {
      firstIntentKey = route.request().headers()["idempotency-key"];
      firstRequestPayload = route.request().postDataJSON();
      await route.abort("timedout");
      return;
    }
    await route.continue();
  });
  await page.getByTestId(`quiz-submit-${fixture.quizId}`).click();
  await expect(page.getByRole("alert")).toContainText("Suas respostas foram mantidas");
  expect(firstIntentKey).toBeTruthy();
  await page.unroute(`**/api/quizzes/${fixture.quizId}/attempts`);

  await page.reload();
  await expect(page.getByTestId(`quiz-api-session-${fixture.quizId}`)).toBeVisible();
  await expect(page.getByText("Um envio anterior não recebeu confirmação.")).toBeVisible();
  const firstRetryRequestPromise = page.waitForRequest((request) =>
    request.url() === `${API_BASE_URL}/api/quizzes/${fixture.quizId}/attempts` && request.method() === "POST",
  );
  const firstRetryResponsePromise = page.waitForResponse((response) =>
    response.url() === `${API_BASE_URL}/api/quizzes/${fixture.quizId}/attempts` && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Reenviar esta tentativa" }).click();
  const firstRetryRequest = await firstRetryRequestPromise;
  const firstRetryResponse = await firstRetryResponsePromise;
  expect(firstRetryRequest.headers()["idempotency-key"]).toBe(firstIntentKey);
  expect(firstRetryResponse.status()).toBe(200);
  const firstAttemptResult = await firstRetryResponse.json();
  const firstResult = page.getByTestId("quiz-result");
  await expect(firstResult).toContainText("Aprovado · nota 70%");
  await expect(firstResult).toContainText("Tentativa 1 de 3");
  await expect(firstResult).toContainText("2 tentativas restantes");
  await expect(page.getByText("Respostas corretas e explicações serão liberadas após a terceira tentativa válida.")).toBeVisible();
  await expect(page.getByTestId("quiz-review")).toHaveCount(0);
  await expect(page.getByText("Explicação E2E privada 1.")).toHaveCount(0);

  const firstReplay = await page.context().request.post(`${API_BASE_URL}/api/quizzes/${fixture.quizId}/attempts`, {
    data: firstRequestPayload!,
    headers: { "Idempotency-Key": firstIntentKey! },
  });
  expect(firstReplay.status()).toBe(200);
  const firstReplayBody = await firstReplay.json();
  expect(firstReplayBody.attempt_number).toBe(1);
  expect(firstReplayBody.attempt_id).toBe(firstAttemptResult.attempt_id);
  expect(firstReplayBody.review_available).toBe(false);
  expect(JSON.stringify(firstReplayBody)).not.toContain("explanation");

  await page.getByRole("button", { name: "Iniciar próxima tentativa" }).click();
  await selectCorrectCount(page, 9);
  let secondIntentKey: string | undefined;
  let secondRequestPayload: { version_id: string; answers: Array<{ question_id: string; option_id: string }> } | undefined;
  let secondSavedResponse: Record<string, unknown> | undefined;
  await page.route(`**/api/quizzes/${fixture.quizId}/attempts`, async (route) => {
    if (route.request().method() === "POST") {
      secondIntentKey = route.request().headers()["idempotency-key"];
      secondRequestPayload = route.request().postDataJSON();
      const actualResponse = await route.fetch();
      secondSavedResponse = await actualResponse.json() as Record<string, unknown>;
      await route.abort("failed");
      return;
    }
    await route.continue();
  });
  await page.getByTestId(`quiz-submit-${fixture.quizId}`).click();
  await expect(page.getByRole("alert")).toContainText("Suas respostas foram mantidas");
  await expect.poll(() => secondSavedResponse?.attempt_number).toBe(2);
  await page.unroute(`**/api/quizzes/${fixture.quizId}/attempts`);
  expect(secondIntentKey).toBeTruthy();

  if (ARTIFACT_DIR) {
    await mkdir(ARTIFACT_DIR, { recursive: true });
    await writeFile(join(ARTIFACT_DIR, "quiz-restart-replay.json"), JSON.stringify({
      track_id: fixture.trackId,
      topic_id: fixture.topicId,
      topic_title: fixture.topicTitle,
      quiz_id: fixture.quizId,
      student_email: quizStudentEmail,
      student_password: quizStudentPassword,
      ...secondRequestPayload,
      attempt_version_id: secondRequestPayload?.version_id,
      idempotency_key: secondIntentKey,
      expected_attempt_id: secondSavedResponse?.attempt_id,
      expected_attempt_number: secondSavedResponse?.attempt_number,
      expected_attempts_used: secondSavedResponse?.attempts_used,
    }, null, 2), "utf8");
  }

  await page.close();
  const reopenedPage = await page.context().newPage();
  await reopenedPage.goto(`${FRONTEND_ON}/trilhas/${fixture.trackId}/n/${fixture.topicId}`);
  await expect(reopenedPage.getByTestId("reader-title")).toHaveText(fixture.topicTitle);
  await expect(reopenedPage.getByTestId(`quiz-api-session-${fixture.quizId}`)).toBeVisible();
  await expect(reopenedPage.getByTestId("quiz-result")).toContainText("1 tentativa restante");
  await expect(reopenedPage.getByText("melhor nota: 90%")).toBeVisible();
  await expect(reopenedPage.getByTestId("quiz-result")).toContainText("Tentativa 2 de 3");
  await expect(reopenedPage.getByTestId("quiz-result")).toContainText("O servidor confirmou o envio anterior pela mesma chave");
  const historyAfterLostResponse = reopenedPage.getByTestId("quiz-history");
  await expect(historyAfterLostResponse).toContainText("Histórico de tentativas (2)");
  await expect(historyAfterLostResponse).toContainText("Tentativa 2");
  await expect(reopenedPage.getByRole("button", { name: "Reenviar esta tentativa" })).toHaveCount(0);
  const recoveryResponse = await reopenedPage.context().request.post(
    `${API_BASE_URL}/api/quizzes/${fixture.quizId}/recovery`,
    { data: { version_id: fixture.versionId, idempotency_key: secondIntentKey } },
  );
  expect(recoveryResponse.status()).toBe(200);
  const recoveredBody = await recoveryResponse.json();
  expect(recoveredBody.state).toBe("confirmed");
  expect(recoveredBody.attempt.attempt_id).toBe(secondSavedResponse?.attempt_id);
  expect(JSON.stringify(recoveredBody)).not.toContain("explanation");
  const reviewBeforeThird = await reopenedPage.context().request.get(
    `${API_BASE_URL}/api/quizzes/${fixture.quizId}/versions/${fixture.versionId}/review`,
  );
  expect(reviewBeforeThird.status()).toBe(403);

  await reopenedPage.getByRole("button", { name: "Iniciar próxima tentativa" }).click();
  await selectCorrectCount(reopenedPage, 6);
  const submitButton = reopenedPage.getByTestId(`quiz-submit-${fixture.quizId}`);
  let thirdSubmitRequests = 0;
  reopenedPage.on("request", (request) => {
    if (request.url() === `${API_BASE_URL}/api/quizzes/${fixture.quizId}/attempts` && request.method() === "POST") {
      thirdSubmitRequests += 1;
    }
  });
  await submitButton.evaluate((button) => {
    const form = button.closest("form");
    form?.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
    form?.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
  });
  await expect(reopenedPage.getByTestId("quiz-result")).toContainText("Tentativa 3 de 3");
  await expect(reopenedPage.getByTestId("quiz-result")).toContainText("Ainda não aprovado · nota 60%");
  await expect(reopenedPage.getByTestId("quiz-result")).toContainText("melhor nota 90%");
  await expect(reopenedPage.getByTestId("quiz-review")).toBeVisible();
  await expect(reopenedPage.getByText("Explicação E2E privada 1.")).toBeVisible();
  await expect.poll(() => thirdSubmitRequests).toBe(1);

  const history = reopenedPage.getByTestId("quiz-history");
  await expect(history).toContainText("Histórico de tentativas (3)");
  await expect(history).toContainText("Tentativa 1");
  await expect(history).toContainText("Tentativa 2");
  await expect(history).toContainText("Tentativa 3");
  const review = await reopenedPage.context().request.get(
    `${API_BASE_URL}/api/quizzes/${fixture.quizId}/versions/${fixture.versionId}/review`,
  );
  expect(review.status()).toBe(200);
  if (ARTIFACT_DIR) {
    const restartFixturePath = join(ARTIFACT_DIR, "quiz-restart-replay.json");
    const restartFixture = JSON.parse(await readFile(restartFixturePath, "utf8")) as Record<string, unknown>;
    await writeFile(restartFixturePath, JSON.stringify({
      ...restartFixture,
      expected_history_count: 3,
    }, null, 2), "utf8");
  }
  expect((await review.json()).questions[0].explanation).toContain("Explicação");

  const fourthAttempt = await reopenedPage.context().request.post(`${API_BASE_URL}/api/quizzes/${fixture.quizId}/attempts`, {
    data: { version_id: fixture.versionId, answers: answersWithCorrectCount(10) },
    headers: { "Idempotency-Key": randomUUID() },
  });
  expect(fourthAttempt.status()).toBe(409);
  const finalHistory = await reopenedPage.context().request.get(`${API_BASE_URL}/api/quizzes/${fixture.quizId}/attempts`);
  expect((await finalHistory.json()).total).toBe(3);

  const adminHistory = await adminApi.get(`/api/quizzes/${fixture.quizId}/attempts`);
  expect(adminHistory.status()).toBe(200);
  expect((await adminHistory.json()).total).toBe(0);
});

test("recovers the latest persisted result after browser storage is lost", async ({ browser }) => {
  const context = await browser.newContext();
  const recoveryPage = await context.newPage();
  let submissionPosts = 0;
  recoveryPage.on("request", (request) => {
    if (request.url() === `${API_BASE_URL}/api/quizzes/${fixture.quizId}/attempts` && request.method() === "POST") {
      submissionPosts += 1;
    }
  });

  try {
    await enterFirstTopic(recoveryPage);
    await expect(recoveryPage.getByTestId("quiz-result")).toContainText("Tentativa 3 de 3");
    await expect(recoveryPage.getByTestId("quiz-result")).toContainText("tentativa mais recente registrada pelo servidor");
    await expect(recoveryPage.getByTestId("quiz-review")).toBeVisible();
    expect(submissionPosts).toBe(0);
    const recovery = await recoveryPage.context().request.post(
      `${API_BASE_URL}/api/quizzes/${fixture.quizId}/recovery`,
      { data: { version_id: fixture.versionId } },
    );
    expect(recovery.status()).toBe(200);
    const payload = await recovery.json();
    expect(payload.state).toBe("latest_confirmed");
    expect(payload.attempt.attempt_number).toBe(3);
    expect(payload.attempts_used).toBe(3);
    expect(JSON.stringify(payload)).not.toContain("correct_option_id");
  } finally {
    await context.close();
  }
});

test("API flag false shows an accessible unavailable state without local grading or assessment progress", async ({ page }) => {
  const quizRequests: string[] = [];
  const assessmentProgressRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/quizzes/")) quizRequests.push(request.url());
    if (request.method() === "POST" && /\/api\/progress\/(?!visit(?:\?|$))/.test(request.url())) {
      assessmentProgressRequests.push(request.url());
    }
  });
  await enterFirstTopic(page, FRONTEND_OFF);
  await expect(page.getByTestId("quiz-unavailable")).toContainText("nenhuma resposta será corrigida ou registrada");
  await expect(page.getByText("Conteúdo de apoio continua disponível.")).toBeVisible();
  await expect(page.getByTestId(`quiz-option-${fixture.blocks[0].id}-${fixture.blocks[0].correctIndex}`)).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Enviar tentativa" })).toHaveCount(0);
  await expect(page.getByText("Correto.")).toHaveCount(0);
  expect(quizRequests).toEqual([]);
  expect(assessmentProgressRequests).toEqual([]);
});

test("absent API flag is also unavailable and leaves theory readable", async ({ page }) => {
  const quizRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/quizzes/")) quizRequests.push(request.url());
  });
  await enterFirstTopic(page, FRONTEND_ABSENT);
  await expect(page.getByTestId("quiz-unavailable")).toBeVisible();
  await expect(page.getByText("Conteúdo de apoio continua disponível.")).toBeVisible();
  await expect(page.getByTestId(`quiz-option-${fixture.blocks[0].id}-${fixture.blocks[0].correctIndex}`)).toHaveCount(0);
  expect(quizRequests).toEqual([]);
});

test("pending idempotent intent survives closing and reopening the browser profile", async () => {
  const originalFixture = fixture;
  fixture = await createPublishedQuiz();
  const profileDir = join(ARTIFACT_DIR!, "quiz-browser-profile-" + randomUUID());
  let context = await chromium.launchPersistentContext(profileDir, { headless: true });
  let retryKey: string | undefined;
  let committedAttemptId: string | undefined;
  try {
    const page = context.pages()[0] || await context.newPage();
    await enterFirstTopic(page);
    await selectCorrectCount(page, 7);
    await page.route(`**/api/quizzes/${fixture.quizId}/attempts`, async (route) => {
      if (route.request().method() === "POST") {
        retryKey = route.request().headers()["idempotency-key"];
        const response = await route.fetch();
        expect(response.status()).toBe(200);
        committedAttemptId = (await response.json()).attempt_id as string;
        await route.abort("failed");
        return;
      }
      await route.continue();
    });
    await page.getByTestId(`quiz-submit-${fixture.quizId}`).click();
    await expect(page.getByRole("alert")).toContainText("Suas respostas foram mantidas");
    expect(retryKey).toBeTruthy();
    const stored = await page.evaluate(() => {
      const key = Object.keys(localStorage).find((item) => item.startsWith("trilhacode:quiz-intent:"));
      return key ? localStorage.getItem(key) : null;
    });
    expect(stored).toContain(retryKey!);
    expect(stored).not.toMatch(/correct_index|answer_key|explanation|score_percent/);
    await context.close();

    context = await chromium.launchPersistentContext(profileDir, { headless: true });
    const resumedPage = context.pages()[0] || await context.newPage();
    let retrySubmissionCount = 0;
    resumedPage.on("request", (request) => {
      if (request.url() === `${API_BASE_URL}/api/quizzes/${fixture.quizId}/attempts` && request.method() === "POST") {
        retrySubmissionCount += 1;
      }
    });
    await enterFirstTopic(resumedPage);
    await expect(resumedPage.getByTestId("quiz-result")).toContainText("Tentativa 1 de 3");
    await expect(resumedPage.getByTestId("quiz-result")).toContainText("O servidor confirmou o envio anterior pela mesma chave");
    await expect(resumedPage.getByRole("button", { name: "Reenviar esta tentativa" })).toHaveCount(0);
    expect(retrySubmissionCount).toBe(0);
    const recovery = await resumedPage.context().request.post(
      `${API_BASE_URL}/api/quizzes/${fixture.quizId}/recovery`,
      { data: { version_id: fixture.versionId, idempotency_key: retryKey } },
    );
    expect(recovery.status()).toBe(200);
    const recovered = await recovery.json();
    expect(recovered.state).toBe("confirmed");
    expect(recovered.attempt.attempt_id).toBe(committedAttemptId);
    const storedAfter = await resumedPage.evaluate(() => Object.keys(localStorage).some((item) => item.startsWith("trilhacode:quiz-intent:")));
    expect(storedAfter).toBe(false);
  } finally {
    await context.close();
    fixture = originalFixture;
  }
});

test("API outage with the flag enabled shows a recoverable error without local grading fallback", async ({ page }) => {
  await enterFirstTopic(page);
  await page.route(`**/api/quizzes/${fixture.quizId}`, (route) => route.abort("failed"));
  await page.reload();
  await expect(page.getByRole("alert")).toContainText("Suas respostas foram mantidas; tente novamente.");
  await expect(page.getByRole("button", { name: "Carregar quiz novamente" })).toBeVisible();
  await expect(page.getByTestId(`quiz-option-${fixture.blocks[0].id}-${fixture.blocks[0].correctIndex}`)).toHaveCount(0);
  await expect(page.getByText("Correto.")).toHaveCount(0);
});

test("expired session is reported by the UI after the real API rejects the missing cookie", async ({ page }) => {
  await page.route(`**/api/quizzes/${fixture.quizId}`, (route) => route.abort("failed"));
  await enterFirstTopic(page);
  await expect(page.getByRole("button", { name: "Carregar quiz novamente" })).toBeVisible();
  await page.context().clearCookies();
  await page.unroute(`**/api/quizzes/${fixture.quizId}`);
  const retryResponsePromise = page.waitForResponse((response) =>
    response.url() === `${API_BASE_URL}/api/quizzes/${fixture.quizId}` && response.request().method() === "GET",
  );
  await page.getByRole("button", { name: "Carregar quiz novamente" }).click();
  const retryResponse = await retryResponsePromise;
  expect(retryResponse.status()).toBe(401);
  await expect(page.getByRole("alert")).toContainText("Sua sessão expirou");
});

test("rate limit 429 is visible in the real client and honors Retry-After", async ({ page }) => {
  // The separately isolated API process is configured to 2 reads/minute so
  // the browser can exercise a real 429 deterministically without changing
  // production settings or the primary E2E server.
  await enterFirstTopic(page, FRONTEND_RATE_LIMIT, rateStudentEmail, rateStudentPassword);
  const studentBurst = await apiRequest.newContext({ baseURL: API_RATE_LIMIT_URL });
  try {
    await login(studentBurst, rateStudentEmail, rateStudentPassword);
    const burst = await Promise.all(Array.from({ length: 5 }, () =>
      studentBurst.get(`/api/quizzes/${fixture.quizId}`),
    ));
    const limited = burst.find((response) => response.status() === 429);
    expect(limited, "the real API rate limiter returns HTTP 429 under a burst").toBeTruthy();
    expect(limited?.headers()["retry-after"]).toBeTruthy();
  } finally {
    await studentBurst.dispose();
  }

  await page.reload();
  await expect(page.getByRole("alert")).toContainText("Muitas solicitações. Aguarde antes de tentar novamente.");
  const retryButton = page.getByRole("button", { name: /Tente novamente em/ });
  await expect(retryButton).toBeDisabled();
});

test("quiz versions are immutable and the publish limit is applied to the isolated user", async () => {
  const extraImportRef = `e2e-version-${randomUUID().replaceAll("-", "")}`;
  const blockResponse = await adminApi.post("/api/blocks", {
    data: {
      node_id: fixture.topicId,
      type: "quiz",
      title: "E2E alteração de versão",
      status: "published",
      data: {
        question: "Questão da versão seguinte",
        options: ["A", "B"],
        correct_index: 1,
        explanation: "Explicação privada da nova versão.",
        import_ref: extraImportRef,
      },
    },
  });
  expect(blockResponse.status()).toBe(200);
  const newBlockId = (await blockResponse.json()).id as string;
  fixture.blocks.push({ id: newBlockId, importRef: extraImportRef, correctIndex: 1 });

  const newVersionResponse = await adminApi.post(`/api/admin/quizzes/${fixture.quizId}/versions`);
  expect(newVersionResponse.status()).toBe(200);
  const newVersion = await newVersionResponse.json();
  expect(newVersion.version_id).not.toBe(fixture.versionId);

  const sameContentPublication = await adminApi.post(`/api/admin/quizzes/${fixture.quizId}/versions`);
  expect(sameContentPublication.status()).toBe(200);
  expect((await sameContentPublication.json()).version_id).toBe(newVersion.version_id);

  const studentApi = await apiRequest.newContext({ baseURL: API_BASE_URL });
  try {
    await login(studentApi, quizStudentEmail, quizStudentPassword);
    const newPublicVersion = await studentApi.get(`/api/quizzes/${fixture.quizId}`);
    expect(newPublicVersion.status()).toBe(200);
    const newPublic = await newPublicVersion.json();
    expect(newPublic.version_id).toBe(newVersion.version_id);
    expect(newPublic.attempts_used).toBe(0);
    expect(newPublic.attempts_remaining).toBe(3);
    if (ARTIFACT_DIR) {
      const restartFixturePath = join(ARTIFACT_DIR, "quiz-restart-replay.json");
      const restartFixture = JSON.parse(await readFile(restartFixturePath, "utf8")) as Record<string, unknown>;
      await writeFile(restartFixturePath, JSON.stringify({
        ...restartFixture,
        expected_active_version_id: newVersion.version_id,
      }, null, 2), "utf8");
    }
    expect(newPublic.passed).toBe(false);
  } finally {
    await studentApi.dispose();
  }

  const publishBurst = await Promise.all(Array.from({ length: 10 }, () =>
    adminApi.post(`/api/admin/quizzes/${fixture.quizId}/versions`),
  ));
  const publishLimited = publishBurst.find((response) => response.status() === 429);
  expect(publishLimited, "the real publish limiter returns 429 under a burst").toBeTruthy();
  expect(publishLimited?.headers()["retry-after"]).toBeTruthy();
});

test("typed quiz prerequisite unlocks only from the persisted server assessment", async ({ page }) => {
  const previousFixture = fixture;
  const credentials = await createVerifiedQuizStudent();
  fixture = await createPublishedQuiz();
  try {
    const treeResponse = await adminApi.get(`/api/tracks/${fixture.trackId}/tree`);
    expect(treeResponse.status()).toBe(200);
    const tree = await treeResponse.json() as {
      track: { settings: Record<string, unknown> };
      nodes: Array<{ id: string; parent_id: string | null }>;
    };
    await adminApi.put(`/api/tracks/${fixture.trackId}`, {
      data: { settings: { ...tree.track.settings, enforce_prerequisites: true } },
    });
    const topic = tree.nodes.find((node) => node.id === fixture.topicId);
    expect(topic?.parent_id).toBeTruthy();
    const dependentResponse = await adminApi.post("/api/nodes", {
      data: {
        track_id: fixture.trackId,
        parent_id: topic!.parent_id,
        kind: "topic",
        title: `Quiz gated topic ${randomUUID().slice(0, 8)}`,
        status: "published",
      },
    });
    expect(dependentResponse.status()).toBe(200);
    const dependent = await dependentResponse.json() as { id: string; title: string };
    const block = await adminApi.post("/api/blocks", {
      data: {
        node_id: dependent.id,
        type: "theory_text",
        title: "Conteúdo condicionado",
        status: "published",
        data: { body: "Este conteúdo só aparece após a aprovação autoritativa." },
      },
    });
    expect(block.status()).toBe(200);
    const relation = await adminApi.post("/api/relations", {
      data: {
        node_id: dependent.id,
        target_id: fixture.quizId,
        type: "prerequisite",
        enforced: true,
        prerequisite_kind: "quiz_passed",
      },
    });
    expect(relation.status()).toBe(200);

    await enterFirstTopic(page, FRONTEND_ON, credentials.email, credentials.password);
    await page.goto(`${FRONTEND_ON}/trilhas/${fixture.trackId}/n/${dependent.id}`);
    await expect(page.getByTestId("reader-title")).toHaveText(dependent.title);
    await expect(page.getByTestId("locked-panel")).toBeVisible();
    await expect(page.getByRole("main").getByTestId("context-prerequisite-states"))
      .toContainText("Quiz ainda não aprovado");

    const fakeCompletion = await page.context().request.post(`${API_BASE_URL}/api/progress`, {
      data: {
        node_id: fixture.quizId,
        status: "completed",
        data: { passed: true, score: 100 },
      },
    });
    expect(fakeCompletion.status()).toBe(200);
    const stillLocked = await page.context().request.get(`${API_BASE_URL}/api/progress/tracks/${fixture.trackId}`);
    expect((await stillLocked.json()).locks).toHaveProperty(dependent.id);

    await page.goto(`${FRONTEND_ON}/trilhas/${fixture.trackId}/n/${fixture.topicId}`);
    await selectCorrectCount(page, 7);
    await page.getByTestId(`quiz-submit-${fixture.quizId}`).click();
    await expect(page.getByTestId("quiz-result")).toContainText("Aprovado");
    const unlocked = await page.context().request.get(`${API_BASE_URL}/api/progress/tracks/${fixture.trackId}`);
    expect((await unlocked.json()).locks).not.toHaveProperty(dependent.id);

    await page.goto(`${FRONTEND_ON}/trilhas/${fixture.trackId}/n/${dependent.id}`);
    await expect(page.getByTestId("locked-panel")).toHaveCount(0);
    await expect(page.getByText("Este conteúdo só aparece após a aprovação autoritativa.")).toBeVisible();
    await expect(page.getByRole("main").getByTestId("context-prerequisite-states"))
      .toContainText("Quiz aprovado");
  } finally {
    fixture = previousFixture;
  }
});
