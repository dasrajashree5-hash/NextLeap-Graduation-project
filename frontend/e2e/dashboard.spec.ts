import { expect, test } from "@playwright/test";

test("Blinkit mobile home loads with bottom navigation", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("navigation", { name: "Primary" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Home" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Cart" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Discover" })).toBeVisible();
});

test("admin dashboard shell loads with primary navigation", async ({ page }) => {
  await page.goto("/admin");
  await expect(page.getByRole("button", { name: "Overview" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Insights" })).toBeVisible();
  await expect(page.getByRole("button", { name: "MVP demo" })).toBeVisible();
});

test("keyboard navigation reaches nav controls", async ({ page }) => {
  await page.goto("/");
  await page.keyboard.press("Tab");
  const focused = page.locator(":focus");
  await expect(focused).toBeVisible();
});
