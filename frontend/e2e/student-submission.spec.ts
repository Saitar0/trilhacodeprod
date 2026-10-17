import { expect, request as apiRequest, test } from "@playwright/test";

const API_BASE_URL = "http://127.0.0.1:18000";

test("student can submit an exercise and retain the answer after reload", async ({ page }) => {
  test.skip(!process.env.CI, "Mutates only the ephemeral Mongo database prepared by the CI workflow.");

  const api = await apiRequest.newContext({ baseURL: API_BASE_URL });
  let blockId: string | undefined;

  try {
    const adminLogin = await api.post("/api/auth/login", {
      data: {
        email: process.env.E2E_ADMIN_EMAIL || "admin@example.com",
        password: process.env.E2E_ADMIN_PASSWORD || "e2e-only-admin-password",
      },
    });
    expect(adminLogin.status(), "admin setup login").toBe(200);

    const tracksResponse = await api.get("/api/tracks?limit=500");
    expect(tracksResponse.status()).toBe(200);
    const track = (await tracksResponse.json()).find((item: { slug: string }) => item.slug === "trilha-code");
    expect(track, "CI seeded track").toBeTruthy();

    const treeResponse = await api.get(`/api/tracks/${track.id}/tree`);
    expect(treeResponse.status()).toBe(200);
    const topic = (await treeResponse.json()).nodes.find(
      (node: { kind: string; title: string }) => node.kind === "topic" && node.title === "Variáveis e tipos",
    );
    expect(topic, "CI seeded first topic").toBeTruthy();

    const blockResponse = await api.post("/api/blocks", {
      data: {
        node_id: topic.id,
        type: "exercise_open",
        title: "E2E submission exercise",
        status: "published",
        data: { prompt: "Describe a variable.", allow_resubmit: true },
      },
    });
    expect(blockResponse.status(), "create a temporary exercise in disposable CI Mongo").toBe(200);
    blockId = (await blockResponse.json()).id;

    const studentApi = await apiRequest.newContext({ baseURL: API_BASE_URL });
    const studentEmail = `e2e_student_${Date.now()}@example.com`;
    const studentPassword = "e2e-only-student-password";
    try {
      const registration = await studentApi.post("/api/auth/register", {
        data: { name: "E2E Student", email: studentEmail, password: studentPassword },
      });
      expect(registration.status(), "create an isolated disposable E2E student").toBe(200);
    } finally {
      await studentApi.dispose();
    }

    await page.route("https://**/*", (route) => route.abort());
    await page.goto("/login");
    await page.getByTestId("login-email-input").fill(studentEmail);
    await page.getByTestId("login-password-input").fill(studentPassword);
    await page.getByTestId("login-submit-button").click();

    await page.getByTestId("catalog-track-card-trilha-code").click();
    await page.getByTestId("track-start-button").click();
    await expect(page.getByTestId(`exercise-submission-${blockId}`)).toBeVisible();

    const answer = "A variable stores a value.";
    await page.getByTestId(`exercise-answer-${blockId}`).fill(answer);
    await page.getByTestId(`exercise-submit-${blockId}`).click();
    await expect(page.getByTestId(`exercise-status-${blockId}`)).toHaveText("Enviado");

    await page.reload();
    await expect(page.getByTestId(`exercise-status-${blockId}`)).toHaveText("Enviado");
    await expect(page.getByTestId(`exercise-answer-${blockId}`)).toHaveValue(answer);
  } finally {
    if (blockId) {
      const cleanup = await api.delete(`/api/blocks/${blockId}`);
      expect(cleanup.status(), "remove the temporary exercise from disposable CI Mongo").toBe(200);
    }
    await api.dispose();
  }
});
