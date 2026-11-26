// Browser checks on a phone and a desktop, in both themes:
// no console errors, no sideways scroll, the hands render, the theme toggle sticks,
// and axe finds no serious or critical accessibility violations.
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const sizes = [
  { name: "phone", width: 375, height: 812 },
  { name: "desktop", width: 1440, height: 900 },
];

for (const size of sizes) {
  for (const scheme of ["dark", "light"]) {
    test(`${size.name} ${scheme}`, async ({ browser }) => {
      const context = await browser.newContext({ viewport: size, colorScheme: scheme });
      const page = await context.newPage();
      const errors = [];
      page.on("pageerror", (e) => errors.push(e.message));
      // Vercel serves its analytics script only in production, so a 404 for it locally is expected
      page.on("console", (m) => { if (m.type() === "error" && !(m.location().url || "").includes("/_vercel/")) errors.push(m.text()); });

      await page.goto("/");
      await expect(page.locator("h1")).toHaveText("Aryan Awasthi");
      await expect(page.locator("html")).toHaveAttribute("data-theme", scheme);
      await page.waitForFunction(() => document.getElementById("tstep").textContent === "t = 0", null, { timeout: 15000 });
      await expect(page.locator(".art")).toHaveClass(/live/);

      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      expect(scrollWidth).toBeLessThanOrEqual(size.width);

      const axe = await new AxeBuilder({ page }).exclude(".art").analyze();
      const serious = axe.violations.filter((v) => ["serious", "critical"].includes(v.impact));
      expect(serious.map((v) => `${v.id}: ${v.help}`)).toEqual([]);

      expect(errors).toEqual([]);
      await context.close();
    });
  }
}

test("theme toggle is remembered", async ({ page }) => {
  await page.goto("/");
  const start = await page.locator("html").getAttribute("data-theme");
  await page.locator("#theme-btn").click();
  const flipped = start === "light" ? "dark" : "light";
  await expect(page.locator("html")).toHaveAttribute("data-theme", flipped);
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-theme", flipped);
});
