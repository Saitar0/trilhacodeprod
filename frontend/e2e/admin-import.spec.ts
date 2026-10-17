import { randomUUID } from "node:crypto";
import { expect, test } from "@playwright/test";

const API_BASE_URL = "http://127.0.0.1:18000";

test("administrator can preview and persist an imported track", async ({ page }) => {
  test.skip(!process.env.CI, "Mutates only the ephemeral Mongo database prepared by the CI workflow.");

  let trackId: string | undefined;
  const slug = `e2e-import-${randomUUID()}`;
  const payload = {
    track: { slug, title: "E2E Imported Track" },
    nodes: [{
      ref: "phase-1",
      kind: "phase",
      title: "Phase 1",
      children: [{
        ref: "module-1",
        kind: "module",
        title: "Module 1",
        children: [{
          ref: "topic-1",
          kind: "topic",
          title: "Topic 1",
        }],
      }],
    }],
  };

  try {
    await page.route("https://**/*", (route) => route.abort());
    await page.goto("/login");
    await page.getByTestId("login-email-input").fill(
      process.env.E2E_ADMIN_EMAIL || "admin@example.com",
    );
    await page.getByTestId("login-password-input").fill(
      process.env.E2E_ADMIN_PASSWORD || "e2e-only-admin-password",
    );
    await page.getByTestId("login-submit-button").click();

    await page.goto("/admin");
    await page.getByTestId("admin-nav-import").click();
    await expect(page.getByTestId("import-confirm-button")).toBeDisabled();
    await page.getByTestId("import-json-input").fill(JSON.stringify(payload));

    const previewResponse = page.waitForResponse((response) =>
      response.url().includes("/api/import/track?dry_run=true")
      && response.request().method() === "POST",
    );
    await page.getByTestId("import-dry-run-button").click();
    const preview = await previewResponse;
    expect(preview.status()).toBe(200);
    const previewReport = await preview.json();
    expect(previewReport.summary.track).toBe("criar");
    expect(previewReport.summary.nodes_create).toBe(3);
    await expect(page.getByTestId("import-status")).toHaveText("Simulação válida");
    await expect(page.getByTestId("import-confirm-button")).toBeEnabled();

    const importResponse = page.waitForResponse((response) =>
      response.url().includes("/api/import/track?dry_run=false")
      && response.request().method() === "POST",
    );
    await page.getByTestId("import-confirm-button").click();
    const response = await importResponse;
    expect(response.status()).toBe(200);
    const report = await response.json();
    trackId = report.track.id;
    expect(report.dry_run).toBe(false);
    await expect(page.getByTestId("import-status")).toHaveText("Importado");

    const treeResponse = await page.request.get(`${API_BASE_URL}/api/tracks/${trackId}/tree`);
    expect(treeResponse.status()).toBe(200);
    const tree = await treeResponse.json();
    expect(tree.nodes).toHaveLength(3);
    expect(tree.track.slug).toBe(slug);
  } finally {
    if (trackId) {
      const cleanup = await page.request.delete(`${API_BASE_URL}/api/tracks/${trackId}`);
      expect(cleanup.status(), "remove the temporary imported track from disposable CI Mongo").toBe(200);
    }
  }
});
