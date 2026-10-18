import { expect, request as apiRequest, test } from "@playwright/test";
import { mkdir, readFile, readdir } from "node:fs/promises";
import { join } from "node:path";

const API_BASE_URL = "http://127.0.0.1:18000";

test("student can submit an exercise and retain the answer after reload", async ({ page }) => {
  test.skip(!process.env.CI, "Mutates only the ephemeral Mongo database prepared by the CI workflow.");

  const api = await apiRequest.newContext({ baseURL: API_BASE_URL });
  let blockId: string | undefined;
  let practicalBlockId: string | undefined;

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

    const practicalBlockResponse = await api.post("/api/blocks", {
      data: {
        node_id: topic.id,
        type: "practical_challenge",
        title: "E2E practical challenge",
        status: "published",
        data: { prompt: "Write a short function.", starter_code: "def solution():\n    pass" },
      },
    });
    expect(practicalBlockResponse.status(), "create a temporary practical challenge in disposable CI Mongo").toBe(200);
    practicalBlockId = (await practicalBlockResponse.json()).id;

    const studentApi = await apiRequest.newContext({ baseURL: API_BASE_URL });
    const studentEmail = `e2e_student_${Date.now()}@example.com`;
    const studentPassword = "e2e-only-student-password";
    let verificationToken: string | undefined;
    try {
      const registration = await studentApi.post("/api/auth/register", {
        data: { name: "E2E Student", email: studentEmail, password: studentPassword },
      });
      expect(registration.status(), "create an isolated disposable E2E student").toBe(202);
      const mailbox = process.env.AUTH_TEST_MAIL_DIR || join(process.cwd(), "..", "backend", ".local-emails");
      await mkdir(mailbox, { recursive: true });
      await expect.poll(async () => {
        const mailFiles = (await readdir(mailbox)).filter((file) => file.endsWith(".eml"));
        for (const file of mailFiles) {
          const message = await readFile(join(mailbox, file), "utf8");
          if (message.includes(`To: ${studentEmail}`) && message.includes("Confirme seu e-mail")) {
            const body = message.split(/\r?\n\r?\n/).slice(1).join("\n")
              .replace(/=\r?\n/g, "")
              .replace(/=([0-9A-F]{2})/gi, (_match, hex: string) => String.fromCharCode(parseInt(hex, 16)));
            verificationToken = body.match(/[?&]token=([A-Za-z0-9_-]{32,})/)?.[1];
          }
        }
        return Boolean(verificationToken);
      }, { timeout: 5000 }).toBe(true);
    } finally {
      await studentApi.dispose();
    }

    await page.route("https://**/*", (route) => route.abort());
    expect(verificationToken, "local test mailbox contains the verification link").toBeTruthy();
    await page.goto(`/auth/confirm-email?token=${verificationToken}`);
    await expect(page.getByRole("button", { name: "Confirmar e-mail" })).toBeVisible();
    await page.getByRole("button", { name: "Confirmar e-mail" }).click();
    await expect(page.getByRole("status")).toHaveText("E-mail confirmado. Você já pode entrar.");
    await page.goto("/login");
    await page.getByTestId("login-email-input").fill(studentEmail);
    await page.getByTestId("login-password-input").fill(studentPassword);
    await page.getByTestId("login-submit-button").click();

    await page.getByTestId("catalog-track-card-trilha-code").click();
    await page.getByTestId("track-start-button").click();
    await expect(page.getByTestId(`exercise-submission-${blockId}`)).toBeVisible();
    await expect(page.getByLabel("Código da resposta para E2E practical challenge")).toBeVisible();

    for (const width of [360, 390]) {
      await page.setViewportSize({ width, height: 900 });
      const documentWidth = await page.evaluate(() => Math.max(document.documentElement.scrollWidth, document.body.scrollWidth));
      expect(documentWidth, `exercise screen overflows at ${width}px`).toBeLessThanOrEqual(width);
      await expect(page.getByLabel(`Sua resposta para E2E submission exercise`)).toBeVisible();
      const overlapsStickyFooter = await page.getByTestId(`exercise-answer-${blockId}`).evaluate((element) => {
        const answer = element.getBoundingClientRect();
        const reader = element.closest('[data-testid="node-reader"]');
        const footer = reader?.querySelector('[data-testid="topic-mark-completed-button"]')?.closest('footer')?.getBoundingClientRect();
        return !!footer && Math.max(answer.top, footer.top) < Math.min(answer.bottom, footer.bottom);
      });
      expect(overlapsStickyFooter, `exercise answer is covered by the sticky footer at ${width}px`).toBe(false);
    }

    const answer = "A variable stores a value.";
    await page.getByTestId(`exercise-answer-${blockId}`).fill(answer);
    await page.getByTestId(`exercise-submit-${blockId}`).click();
    await expect(page.getByTestId(`exercise-status-${blockId}`)).toHaveText("Enviado");

    const updatedAnswer = "A variable stores a value that can be updated.";
    await page.getByTestId(`exercise-answer-${blockId}`).fill(updatedAnswer);
    await expect(page.getByTestId(`exercise-submit-${blockId}`)).toHaveText("Atualizar envio");
    await page.getByTestId(`exercise-submit-${blockId}`).click();
    await expect(page.getByTestId(`exercise-status-${blockId}`)).toHaveText("Enviado");

    await page.reload();
    await expect(page.getByTestId(`exercise-status-${blockId}`)).toHaveText("Enviado");
    await expect(page.getByTestId(`exercise-answer-${blockId}`)).toHaveValue(updatedAnswer);
  } finally {
    for (const [createdBlockId, description] of [
      [blockId, "temporary exercise"],
      [practicalBlockId, "temporary practical challenge"],
    ] as const) {
      if (createdBlockId) {
        const cleanup = await api.delete(`/api/blocks/${createdBlockId}`);
        expect(cleanup.status(), `remove the ${description} from disposable CI Mongo`).toBe(200);
      }
    }
    await api.dispose();
  }
});
