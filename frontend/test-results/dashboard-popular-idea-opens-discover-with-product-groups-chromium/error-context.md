# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard.spec.ts >> popular idea opens discover with product groups
- Location: e2e/dashboard.spec.ts:18:5

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('section').filter({ hasText: /pasta|Italian|sauce/i }).first()
Expected: visible
Timeout: 10000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 10000ms
  - waiting for locator('section').filter({ hasText: /pasta|Italian|sauce/i }).first()

```

```yaml
- banner:
  - paragraph: blinkit
  - paragraph: Delivery in 11 minutes
  - button "Change delivery location": Home · Koramangala 5th Block
  - button "Account"
- main:
  - heading "Discover with AI" [level=1]
  - paragraph: Plan meals, gifts, parties or everyday shopping using natural language.
  - form "Discovery search":
    - paragraph: Popular ideas
    - list "Popular ideas":
      - listitem:
        - link "🍝 Pasta Night":
          - /url: /discover?prompt=I'm%20making%20pasta%20tonight.
      - listitem:
        - link "🎁 Gift Ideas":
          - /url: /discover?prompt=Gift%20ideas%20for%20my%20best%20friend
      - listitem:
        - link "💄 Makeup Routine":
          - /url: /discover?prompt=Build%20my%20makeup%20routine
      - listitem:
        - link "💕 Date Night":
          - /url: /discover?prompt=Date%20night%20at%20home
      - listitem:
        - link "🎉 House Party":
          - /url: /discover?prompt=Planning%20a%20house%20party
      - listitem:
        - link "🏋️ High Protein":
          - /url: /discover?prompt=High%20protein%20gym%20snacks%20and%20meals
      - listitem:
        - link "👶 Baby Essentials":
          - /url: /discover?prompt=Newborn%20baby%20essentials
      - listitem:
        - link "🐶 Pet Care":
          - /url: /discover?prompt=Dog%20food%20and%20pet%20care%20essentials
      - listitem:
        - link "🏠 Monthly Refill":
          - /url: /discover?prompt=Monthly%20household%20refill
      - listitem:
        - link "🍿 Movie Night":
          - /url: /discover?prompt=Movie%20night%20snacks%20and%20drinks
      - listitem:
        - link "🧳 Travel Kit":
          - /url: /discover?prompt=Travel%20essentials%20kit
      - listitem:
        - link "🥗 Healthy Eating":
          - /url: /discover?prompt=Healthy%20eating%20and%20breakfast%20ideas
      - listitem:
        - link "☕ Coffee Break":
          - /url: /discover?prompt=Coffee%20break%20snacks%20and%20drinks
      - listitem:
        - link "🥘 Dinner for 4":
          - /url: /discover?prompt=Dinner%20for%204%20people%20tonight
    - text: What are you shopping for today?
    - textbox "What are you shopping for today?": I'm making pasta tonight.
    - button "Discover"
  - region:
    - heading "🍝 Main Ingredients" [level=2]
    - list:
      - listitem:
        - article:
          - text: 8 min
          - paragraph: Britannia Brown Bread
          - paragraph: 400 g
          - text: 4.5★ (8.0k)
          - paragraph: ₹45
          - button "Add Britannia Brown Bread to cart": ADD
      - listitem:
        - article:
          - text: 8 min
          - paragraph: Fresh Bananas (Robusta)
          - paragraph: 6 pcs
          - text: 4.6★ (9.0k)
          - paragraph: ₹49
          - button "Add Fresh Bananas (Robusta) to cart": ADD
      - listitem:
        - article:
          - text: 8 min
          - paragraph: Hybrid Tomatoes 500g
          - paragraph: 500 g
          - text: 4.4★ (11.0k)
          - paragraph: ₹32
          - button "Add Hybrid Tomatoes 500g to cart": ADD
  - region:
    - heading "🧀 Cheese & Toppings" [level=2]
    - list:
      - listitem:
        - article:
          - text: 8 min
          - paragraph: Amul Taaza Milk 1L
          - paragraph: 1 L
          - text: 4.7★ (12.0k)
          - paragraph: ₹57
          - button "Add Amul Taaza Milk 1L to cart": ADD
  - region "🥖 Sides":
    - heading "🥖 Sides" [level=2]
    - list:
      - listitem:
        - article:
          - text: 10 min
          - paragraph: Lay's Classic Salted 52g
          - paragraph: 52 g
          - text: 4.4★ (15.0k)
          - paragraph: ₹20
          - button "Add Lay's Classic Salted 52g to cart": ADD
  - region "🥤 Drinks":
    - heading "🥤 Drinks" [level=2]
    - list:
      - listitem:
        - article:
          - text: 9 min
          - paragraph: Real Fruit Power Orange 1L
          - paragraph: 1 L
          - text: 4.5★ (4.1k)
          - paragraph: ₹110
          - button "Add Real Fruit Power Orange 1L to cart": ADD
  - region "🍨 Desserts":
    - heading "🍨 Desserts" [level=2]
    - list:
      - listitem:
        - article:
          - paragraph: Dove Intense Repair Shampoo 180ml
          - paragraph: 180 ml
          - text: 4.6★ (3.2k)
          - paragraph: ₹249
          - button "Add Dove Intense Repair Shampoo 180ml to cart": ADD
      - listitem:
        - article:
          - paragraph: Pampers Baby Dry Diapers M (22)
          - paragraph: 22 pcs
          - text: 4.5★ (2.1k)
          - paragraph: ₹599
          - button "Add Pampers Baby Dry Diapers M (22) to cart": ADD
  - region "Research insights Show":
    - button "Research insights Show"
- navigation "Primary":
  - list:
    - listitem:
      - button "Home"
    - listitem:
      - button "Categories"
    - listitem:
      - button "Discover"
    - listitem:
      - button "Cart"
- alert
```

# Test source

```ts
  1  | import { expect, test } from "@playwright/test";
  2  | 
  3  | test("Blinkit mobile home loads with bottom navigation", async ({ page }) => {
  4  |   await page.goto("/");
  5  |   await expect(page.getByRole("navigation", { name: "Primary" })).toBeVisible();
  6  |   await expect(page.getByRole("button", { name: "Home" })).toBeVisible();
  7  |   await expect(page.getByRole("button", { name: "Cart" })).toBeVisible();
  8  |   await expect(page.getByRole("button", { name: "Discover" })).toBeVisible();
  9  | });
  10 | 
  11 | test("admin dashboard shell loads with primary navigation", async ({ page }) => {
  12 |   await page.goto("/admin");
  13 |   await expect(page.getByRole("button", { name: "Overview" })).toBeVisible();
  14 |   await expect(page.getByRole("button", { name: "Insights" })).toBeVisible();
  15 |   await expect(page.getByRole("button", { name: "MVP demo" })).toBeVisible();
  16 | });
  17 | 
  18 | test("popular idea opens discover with product groups", async ({ page }) => {
  19 |   await page.goto("/");
  20 |   await page.getByRole("link", { name: /Pasta Night/i }).click();
  21 |   await expect(page).toHaveURL(/\/discover\?prompt=/);
  22 |   await expect(page.getByRole("navigation", { name: "Primary" }).getByRole("button", { name: "Discover" })).toHaveAttribute(
  23 |     "aria-current",
  24 |     "page"
  25 |   );
> 26 |   await expect(page.locator("section").filter({ hasText: /pasta|Italian|sauce/i }).first()).toBeVisible({
     |                                                                                             ^ Error: expect(locator).toBeVisible() failed
  27 |     timeout: 10_000,
  28 |   });
  29 | });
  30 | 
  31 | test("keyboard navigation reaches nav controls", async ({ page }) => {
  32 |   await page.goto("/");
  33 |   await page.keyboard.press("Tab");
  34 |   const focused = page.locator(":focus");
  35 |   await expect(focused).toBeVisible();
  36 | });
  37 | 
```