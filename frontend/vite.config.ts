import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [react(), tsconfigPaths({ loose: true })],
  server: { host: "0.0.0.0", port: 3000, strictPort: true },
  preview: { host: "0.0.0.0", port: 3000, strictPort: true },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    clearMocks: true,
  },
});
