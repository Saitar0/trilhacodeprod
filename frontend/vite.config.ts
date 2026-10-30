import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [react(), tsconfigPaths({ loose: true })],
  cacheDir: process.env.BETA9_FULLSTACK_TEST === "1" ? "/tmp/beta9-vite-cache" : undefined,
  server: {
    host: "0.0.0.0",
    port: 3000,
    strictPort: true,
    ...(process.env.BETA9_FULLSTACK_TEST === "1"
      ? {
        allowedHosts: ["web"],
        proxy: { "/api": { target: "http://api:8000", changeOrigin: false } },
      }
      : {}),
  },
  preview: { host: "0.0.0.0", port: 3000, strictPort: true },
  test: {
    include: ["src/**/*.{test,spec}.{js,ts,jsx,tsx}"],
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    clearMocks: true,
  },
});
