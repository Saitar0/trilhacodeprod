import { mkdir, writeFile } from "node:fs/promises";
import { dirname } from "node:path";
import { expect, test as base } from "@playwright/test";

function safeLocation(value: string): string {
  try {
    const url = new URL(value);
    return url.origin + url.pathname;
  } catch {
    return "unavailable";
  }
}

export const test = base.extend({
  page: async ({ page }, use, testInfo) => {
    const diagnostics = {
      pageErrors: [] as string[],
      consoleErrors: [] as string[],
      failedRequests: [] as Array<{ method: string; location: string; error: string }>,
      apiResponses: [] as Array<{ location: string; status: number; contentType: string }>,
    };
    page.on("pageerror", (error) => diagnostics.pageErrors.push(error.name || "Error"));
    page.on("console", (message) => {
      if (message.type() === "error") diagnostics.consoleErrors.push(safeLocation(message.location().url));
    });
    page.on("requestfailed", (request) => {
      const errorText = request.failure()?.errorText || "";
      const safeError = errorText.match(/^(net::ERR_[A-Z_]+|NS_ERROR_[A-Z_]+|TimeoutError)/)?.[0] || "request_failed";
      diagnostics.failedRequests.push({
        method: request.method(),
        location: safeLocation(request.url()),
        error: safeError,
      });
    });
    page.on("response", (response) => {
      const url = new URL(response.url());
      if (!url.pathname.startsWith("/api/")) return;
      const contentType = response.headers()["content-type"] || "";
      diagnostics.apiResponses.push({
        location: safeLocation(response.url()),
        status: response.status(),
        contentType: contentType.split(";")[0],
      });
    });

    // Playwright's fixture continuation is named use; it is not a React Hook.
    // eslint-disable-next-line react-hooks/rules-of-hooks
    await use(page);
    if (testInfo.status === testInfo.expectedStatus) return;
    const finalPage = await page.evaluate(() => ({
      location: window.location.origin + window.location.pathname,
      title: document.title,
      loginFormCount: document.querySelectorAll('[data-testid="login-form"]').length,
      confirmationButtonCount: [...document.querySelectorAll("button")]
        .filter((button) => button.textContent?.trim() === "Confirmar e-mail").length,
      previewLoginCount: document.querySelectorAll('[data-testid="beta71-preview-login"]').length,
      previewRootCount: document.querySelectorAll('[data-testid="beta71-preview"]').length,
    })).catch(() => ({ location: "unavailable", title: "unavailable", loginFormCount: 0, confirmationButtonCount: 0 }));
    const diagnosticsPath = testInfo.outputPath("browser-diagnostics.json");
    await mkdir(dirname(diagnosticsPath), { recursive: true });
    await writeFile(diagnosticsPath, JSON.stringify({ ...diagnostics, finalPage }, null, 2), "utf8");
    await page.screenshot({
      path: testInfo.outputPath("browser-screenshot.png"),
      fullPage: true,
      mask: [page.locator("input, textarea"), page.getByTestId("user-menu-trigger")],
    }).catch(() => undefined);
  },
});

export { expect };
