import { randomUUID } from "node:crypto";
import axe from "axe-core";
import { expect, test } from "./fixtures";

const API_BASE_URL = "http://127.0.0.1:18000";

test("administrator can preview and persist an imported track and node edit", async ({ page }) => {
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
    await expect(page.getByTestId("login-form")).toHaveCount(0);

    await page.goto("/admin");
    await page.getByTestId("admin-nav-import").click();
    const importForm = page.getByTestId("import-form");
    const jsonInput = page.getByRole("textbox", { name: "JSON da trilha" });
    const simulateButton = page.getByTestId("import-dry-run-button");
    const confirmButton = page.getByTestId("import-confirm-button");

    await expect(jsonInput).toBeVisible();
    await expect(confirmButton).toBeDisabled();
    await page.addScriptTag({ content: axe.source });
    const violations = await importForm.evaluate(async (container) => {
      const axe = (window as Window & {
        axe: {
          run: (context: Element, options: unknown) => Promise<{
            violations: Array<{ id: string; impact: string | null }>;
          }>;
        };
      }).axe;
      const results = await axe.run(container, {
        runOnly: {
          type: "tag",
          values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
        },
      });
      return results.violations.map(({ id, impact }) => ({ id, impact }));
    });
    expect(violations).toEqual([]);

    await jsonInput.fill(JSON.stringify(payload));
    await page.getByTestId("import-load-example").focus();
    await page.keyboard.press("Tab");
    await expect(jsonInput).toBeFocused();
    await page.keyboard.press("Tab");
    await expect(simulateButton).toBeFocused();

    const previewResponse = page.waitForResponse((response) =>
      response.url().includes("/api/import/track?dry_run=true")
      && response.request().method() === "POST",
    );
    await page.keyboard.press("Enter");
    const preview = await previewResponse;
    expect(preview.status()).toBe(200);
    const previewReport = await preview.json();
    expect(previewReport.summary.track).toBe("criar");
    expect(previewReport.summary.nodes_create).toBe(3);
    await expect(page.getByTestId("import-status")).toHaveText("Simulação válida");
    await expect(confirmButton).toBeEnabled();
    await page.keyboard.press("Tab");
    await expect(confirmButton).toBeFocused();

    const tracksBeforeApply = await page.request.get(`${API_BASE_URL}/api/tracks?limit=500`);
    expect(tracksBeforeApply.status()).toBe(200);
    const existingTracks = await tracksBeforeApply.json();
    expect(existingTracks.some((track: { slug: string }) => track.slug === slug)).toBe(false);

    const importResponse = page.waitForResponse((response) =>
      response.url().includes("/api/import/track?dry_run=false")
      && response.request().method() === "POST",
    );
    await page.keyboard.press("Enter");
    const response = await importResponse;
    expect(response.status()).toBe(200);
    const report = await response.json();
    trackId = report.track.id;
    expect(report.dry_run).toBe(false);
    expect(report.summary.nodes_create).toBe(3);
    await expect(page.getByTestId("import-status")).toHaveText("Importado");

    const treeResponse = await page.request.get(`${API_BASE_URL}/api/tracks/${trackId}/tree`);
    expect(treeResponse.status()).toBe(200);
    const tree = await treeResponse.json();
    expect(tree.nodes).toHaveLength(3);
    expect(tree.track.slug).toBe(slug);

    const topic = tree.nodes.find((node: { kind: string }) => node.kind === "topic");
    expect(topic).toBeTruthy();
    await page.getByTestId("import-open-track").click();
    await page.getByTestId(`admin-tree-select-${topic.id}`).click();
    await expect(page.getByTestId("node-title-input")).toHaveValue("Topic 1");

    const updatedTitle = "Topic 1 edited in E2E";
    await page.getByTestId("node-title-input").fill(updatedTitle);
    const updateResponse = page.waitForResponse((item) =>
      item.url().includes(`/api/nodes/${topic.id}`)
      && item.request().method() === "PUT",
    );
    await page.getByTestId("node-save-button").click();
    const savedNode = await updateResponse;
    expect(savedNode.status()).toBe(200);

    await page.reload();
    await expect(page.getByTestId("node-title-input")).toHaveValue(updatedTitle);
  } finally {
    if (trackId) {
      const cleanup = await page.request.delete(`${API_BASE_URL}/api/tracks/${trackId}`);
      expect(cleanup.status(), "remove the temporary imported track from disposable CI Mongo").toBe(200);
    }
  }
});
