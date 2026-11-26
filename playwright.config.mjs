import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "tests",
  timeout: 45000,
  reporter: [["list"]],
  use: { baseURL: "http://localhost:4173" },
  webServer: { command: "python3 -m http.server 4173", url: "http://localhost:4173", reuseExistingServer: true },
});
