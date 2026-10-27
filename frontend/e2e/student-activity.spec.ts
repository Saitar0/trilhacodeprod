import { randomUUID } from "node:crypto";
import { request as apiRequest } from "@playwright/test";
import { expect, test } from "./fixtures";

const API_BASE_URL = "http://127.0.0.1:18000";

test("student completes an immutable multiple-choice activity and resumes its result", async ({ page }) => {
  test.skip(!process.env.CI, "Creates content only in the disposable Mongo database prepared by CI.");

  const admin = await apiRequest.newContext({ baseURL: API_BASE_URL });
  const slug = `e2e-activity-${randomUUID()}`;
  let trackId: string | undefined;
  let activityId: string | undefined;

  try {
    const login = await admin.post("/api/auth/login", {
      data: {
        email: process.env.E2E_ADMIN_EMAIL || "admin@example.com",
        password: process.env.E2E_ADMIN_PASSWORD || "e2e-only-admin-password",
      },
    });
    expect(login.status(), "synthetic admin login").toBe(200);

    const trackResponse = await admin.post("/api/tracks", {
      headers: { Origin: "http://127.0.0.1:5173" },
      data: { title: "E2E Activity Track", slug, status: "draft", visibility: "public" },
    });
    expect(trackResponse.status(), "create disposable activity track").toBe(200);
    const track = await trackResponse.json();
    trackId = track.id;

    const phaseResponse = await admin.post("/api/nodes", {
      headers: { Origin: "http://127.0.0.1:5173" },
      data: { track_id: trackId, kind: "phase", title: "Synthetic phase", status: "draft" },
    });
    expect(phaseResponse.status()).toBe(200);
    const phase = await phaseResponse.json();
    const moduleResponse = await admin.post("/api/nodes", {
      headers: { Origin: "http://127.0.0.1:5173" },
      data: { track_id: trackId, parent_id: phase.id, kind: "module", title: "Synthetic module", status: "draft" },
    });
    expect(moduleResponse.status()).toBe(200);
    const moduleNode = await moduleResponse.json();
    const topicResponse = await admin.post("/api/nodes", {
      headers: { Origin: "http://127.0.0.1:5173" },
      data: { track_id: trackId, parent_id: moduleNode.id, kind: "topic", title: "Synthetic topic", status: "draft" },
    });
    expect(topicResponse.status()).toBe(200);
    const topic = await topicResponse.json();

    const blockResponse = await admin.post("/api/blocks", {
      headers: { Origin: "http://127.0.0.1:5173" },
      data: {
        node_id: topic.id,
        type: "quiz",
        title: "Synthetic multiple choice",
        status: "draft",
        data: {
          activity_schema_version: 1,
          prompt: "Qual opção identifica a resposta correta?",
          options: [
            { id: "wrong", label: "Alternativa incorreta" },
            { id: "right", label: "Alternativa correta" },
          ],
          correct_option_id: "right",
          feedback: { correct: "Resposta correta.", incorrect: "Tente mais uma vez." },
          completion_policy: "responded",
          max_attempts: 2,
        },
      },
    });
    expect(blockResponse.status()).toBe(200);
    activityId = (await blockResponse.json()).id;

    const publishResponse = await admin.post(`/api/tracks/${trackId}/publish`, {
      headers: { Origin: "http://127.0.0.1:5173" },
      data: { note: "Synthetic E2E activity", publish_children: true },
    });
    expect(publishResponse.status()).toBe(200);

    // A valid but unpublished block added after publication must remain hidden.
    const hiddenResponse = await admin.post("/api/blocks", {
      headers: { Origin: "http://127.0.0.1:5173" },
      data: {
        node_id: topic.id,
        type: "quiz",
        title: "Unpublished activity",
        status: "draft",
        data: {
          activity_schema_version: 1,
          prompt: "This must remain private.",
          options: [{ id: "x", label: "X" }, { id: "y", label: "Y" }],
          correct_option_id: "x",
        },
      },
    });
    expect(hiddenResponse.status()).toBe(200);
    const hiddenActivityId = (await hiddenResponse.json()).id as string;

    await page.route("https://**/*", (route) => route.abort());
    await page.goto("/login");
    await page.getByTestId("login-email-input").fill(process.env.E2E_STUDENT_EMAIL || "student@example.com");
    await page.getByTestId("login-password-input").fill(process.env.E2E_STUDENT_PASSWORD || "CI-only-password");
    await page.getByTestId("login-submit-button").click();
    await page.goto(`/trilhas/${trackId}/n/${topic.id}`);

    await expect(page.getByTestId("node-reader")).toBeVisible();
    await expect(page.getByText("Qual opção identifica a resposta correta?")).toBeVisible();
    await expect(page.getByText("This must remain private.")).toHaveCount(0);

    const hiddenStart = await admin.post(`/api/activities/${hiddenActivityId}/attempts`, {
      headers: { Origin: "http://127.0.0.1:5173", "Idempotency-Key": randomUUID() },
      data: { published_version_id: (await publishResponse.json()).published_activity_version_id },
    });
    expect(hiddenStart.status(), "unpublished assessment is not startable").toBe(404);

    await page.getByRole("button", { name: "Iniciar atividade" }).click();
    await page.getByRole("radio", { name: "Alternativa incorreta" }).check();
    const wrongResponse = page.waitForResponse((response) =>
      response.url().includes(`/api/activities/${activityId}/attempts/`) && response.url().endsWith("/submit"),
    );
    await page.getByRole("button", { name: "Enviar resposta" }).click();
    expect((await wrongResponse).status()).toBe(200);
    await expect(page.getByRole("heading", { name: "Resposta incorreta." })).toBeVisible();
    await expect(page.getByText("Resposta registrada. Você ainda pode iniciar outra tentativa.")).toBeVisible();

    await page.getByRole("button", { name: "Iniciar nova tentativa" }).click();
    await page.getByRole("radio", { name: "Alternativa correta" }).check();
    const correctResponsePromise = page.waitForResponse((response) =>
      response.url().includes(`/api/activities/${activityId}/attempts/`) && response.url().endsWith("/submit"),
    );
    await page.getByRole("button", { name: "Enviar resposta" }).click();
    const correctResponse = await correctResponsePromise;
    expect(correctResponse.status()).toBe(200);
    const evaluated = await correctResponse.json();
    const submitBody = correctResponse.request().postDataJSON() as Record<string, unknown>;
    const submitKey = correctResponse.request().headers()["idempotency-key"];
    expect(evaluated.result.is_correct).toBe(true);

    const apiOrigin = process.env.VITE_BACKEND_URL;
    expect(apiOrigin).toBeTruthy();
    const replay = await page.evaluate(async ({ baseUrl, path, body, key }) => {
      const response = await fetch(new URL(path, baseUrl), {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", "Idempotency-Key": key },
        body: JSON.stringify(body),
      });
      return { status: response.status, value: await response.json() };
    }, {
      baseUrl: apiOrigin!,
      path: `/api/activities/${activityId}/attempts/${evaluated.id}/submit`,
      body: submitBody,
      key: submitKey,
    });
    expect(replay.status).toBe(200);
    expect(replay.value.id).toBe(evaluated.id);
    expect(replay.value.result).toEqual(evaluated.result);

    await page.reload();
    await expect(page.getByRole("heading", { name: "Resposta correta." })).toBeVisible();
    await expect(page.getByText("O limite de tentativas desta versão foi atingido.")).toBeVisible();

    const otherOwnerRead = await admin.get(`/api/activities/${activityId}/attempts/${evaluated.id}`);
    expect(otherOwnerRead.status(), "another user cannot read a student's attempt").toBe(404);
  } finally {
    if (trackId) {
      const cleanup = await admin.delete(`/api/tracks/${trackId}`, {
        headers: { Origin: "http://127.0.0.1:5173" },
      });
      expect(cleanup.status(), "remove synthetic activity track from disposable CI Mongo").toBe(200);
    }
    await admin.dispose();
  }
});
