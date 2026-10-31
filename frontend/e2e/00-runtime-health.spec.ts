import { expect, test } from "./fixtures";

test("frontend starts with a valid browser-to-API contract", async ({ page }) => {
  const pageErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.name || "Error"));

  const frontendResponse = await page.goto("/login");
  expect(frontendResponse?.status()).toBe(200);
  expect(frontendResponse?.headers()["content-type"]).toContain("text/html");
  await expect(page.getByTestId("login-form")).toBeVisible();
  await expect(page.getByTestId("login-email-input")).toBeVisible();

  const apiOrigin = process.env.VITE_BACKEND_URL;
  expect(apiOrigin, "VITE_BACKEND_URL must be set before Vite starts").toBeTruthy();
  if (!apiOrigin) throw new Error("VITE_BACKEND_URL is not configured for the E2E browser");

  const result = await page.evaluate(async (url) => {
    const response = await fetch(url, { credentials: "include" });
    const contentType = response.headers.get("content-type") || "";
    const body = await response.json().catch(() => null) as { error?: { code?: string } } | null;
    return {
      status: response.status,
      contentType: contentType.split(";")[0],
      errorCode: body && typeof body === "object" ? body.error?.code || null : null,
    };
  }, new URL("/api/auth/me", apiOrigin).toString());

  expect(result.status, "unauthenticated /api/auth/me must return 401").toBe(401);
  expect(result.contentType).toBe("application/json");
  expect(result.errorCode).toBe("unauthorized");
  expect(pageErrors).toEqual([]);
});
