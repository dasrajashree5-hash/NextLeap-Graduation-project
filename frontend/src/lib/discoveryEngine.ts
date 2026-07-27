import { PRODUCTS, productsByCategory, type CatalogProduct } from "@/lib/catalog";

export type DiscoveryGroup = {
  emoji: string;
  title: string;
  products: CatalogProduct[];
};

type GroupSpec = { emoji: string; title: string; categories: string[]; limit?: number };

type IntentPlan = {
  keywords: RegExp;
  groups: GroupSpec[];
};

function pickFromCategories(specs: GroupSpec[]): DiscoveryGroup[] {
  const used = new Set<string>();
  return specs
    .map((spec) => {
      const pool = spec.categories.flatMap((c) => productsByCategory(c));
      const products = pool
        .filter((p) => !used.has(p.product_id))
        .slice(0, spec.limit ?? 3);
      products.forEach((p) => used.add(p.product_id));
      if (products.length === 0) {
        const fallback = PRODUCTS.filter((p) => !used.has(p.product_id)).slice(
          0,
          spec.limit ?? 2
        );
        fallback.forEach((p) => used.add(p.product_id));
        return { emoji: spec.emoji, title: spec.title, products: fallback };
      }
      return { emoji: spec.emoji, title: spec.title, products };
    })
    .filter((g) => g.products.length > 0);
}

const PLANS: IntentPlan[] = [
  {
    keywords: /pasta|spaghetti|penne|italian/i,
    groups: [
      { emoji: "🍝", title: "Main Ingredients", categories: ["Grocery", "Fruits & Vegetables"] },
      { emoji: "🧀", title: "Cheese & Toppings", categories: ["Dairy"] },
      { emoji: "🥖", title: "Sides", categories: ["Grocery", "Snacks"] },
      { emoji: "🥤", title: "Drinks", categories: ["Beverages"] },
      { emoji: "🍨", title: "Desserts", categories: ["Snacks"] },
    ],
  },
  {
    keywords: /party|house party|birthday|celebration/i,
    groups: [
      { emoji: "🍿", title: "Snacks & Munchies", categories: ["Snacks"] },
      { emoji: "🥤", title: "Drinks", categories: ["Beverages"] },
      { emoji: "🧊", title: "Quick Bites", categories: ["Grocery", "Dairy"] },
      { emoji: "🧹", title: "Party Essentials", categories: ["Household", "Personal Care"] },
    ],
  },
  {
    keywords: /gift|present|best friend/i,
    groups: [
      { emoji: "🎁", title: "Giftable Treats", categories: ["Snacks", "Beverages"] },
      { emoji: "💄", title: "Self-care Picks", categories: ["Personal Care"] },
      { emoji: "🔌", title: "Useful Extras", categories: ["Electronics"] },
    ],
  },
  {
    keywords: /date night|romantic|dinner for two/i,
    groups: [
      { emoji: "🥗", title: "Fresh Prep", categories: ["Fruits & Vegetables", "Dairy"] },
      { emoji: "🍷", title: "Sips & Pairings", categories: ["Beverages"] },
      { emoji: "🍫", title: "Sweet Finish", categories: ["Snacks"] },
      { emoji: "🧴", title: "Glow-up", categories: ["Personal Care"] },
    ],
  },
  {
    keywords: /makeup|beauty|skincare|oily skin|routine/i,
    groups: [
      { emoji: "💄", title: "Skin & Hair", categories: ["Personal Care"] },
      { emoji: "🥗", title: "Wellness Add-ons", categories: ["Health & Nutrition", "Fruits & Vegetables"] },
      { emoji: "🥤", title: "Hydration", categories: ["Beverages"] },
    ],
  },
  {
    keywords: /healthy|breakfast|gym|protein|fitness/i,
    groups: [
      { emoji: "🥗", title: "Fresh & Light", categories: ["Fruits & Vegetables", "Dairy"] },
      { emoji: "💪", title: "Protein & Nutrition", categories: ["Health & Nutrition"] },
      { emoji: "🥤", title: "Drinks", categories: ["Beverages"] },
      { emoji: "🍿", title: "Smart Snacks", categories: ["Snacks"] },
    ],
  },
  {
    keywords: /baby|newborn|infant|diaper/i,
    groups: [
      { emoji: "👶", title: "Baby Care", categories: ["Baby Care"] },
      { emoji: "🥛", title: "Daily Dairy", categories: ["Dairy"] },
      { emoji: "🧹", title: "Home Hygiene", categories: ["Household", "Personal Care"] },
    ],
  },
  {
    keywords: /dog|puppy|pet|cat|whiskas|pedigree/i,
    groups: [
      { emoji: "🐶", title: "Pet Treats & Food", categories: ["Pet Care"] },
      { emoji: "🧹", title: "Clean-up", categories: ["Household"] },
      { emoji: "🍿", title: "Your Snacks", categories: ["Snacks"] },
    ],
  },
  {
    keywords: /picnic|outdoor|weekend trip|travel|camping/i,
    groups: [
      { emoji: "🥪", title: "Packable Food", categories: ["Grocery", "Snacks"] },
      { emoji: "🥤", title: "Drinks", categories: ["Beverages"] },
      { emoji: "🍌", title: "Fresh Fruit", categories: ["Fruits & Vegetables"] },
      { emoji: "🔌", title: "Travel Gear", categories: ["Electronics"] },
    ],
  },
  {
    keywords: /household|refill|monthly|home essentials|cleaning/i,
    groups: [
      { emoji: "🧹", title: "Cleaning", categories: ["Household"] },
      { emoji: "🧴", title: "Personal Care", categories: ["Personal Care"] },
      { emoji: "🥛", title: "Staples", categories: ["Dairy", "Grocery"] },
    ],
  },
  {
    keywords: /movie|netflix|film night/i,
    groups: [
      { emoji: "🍿", title: "Movie Snacks", categories: ["Snacks"] },
      { emoji: "🥤", title: "Drinks", categories: ["Beverages"] },
      { emoji: "🍫", title: "Treats", categories: ["Snacks", "Grocery"] },
    ],
  },
];

const DEFAULT_GROUPS: GroupSpec[] = [
  { emoji: "⭐", title: "Top picks for you", categories: ["Grocery", "Dairy", "Snacks"], limit: 4 },
  { emoji: "🥤", title: "Drinks & more", categories: ["Beverages", "Fruits & Vegetables"] },
  { emoji: "✨", title: "Explore categories", categories: ["Personal Care", "Pet Care", "Baby Care"] },
];

export function discoverFromPrompt(prompt: string): DiscoveryGroup[] {
  const text = prompt.trim();
  if (!text) return pickFromCategories(DEFAULT_GROUPS);

  for (const plan of PLANS) {
    if (plan.keywords.test(text)) {
      return pickFromCategories(plan.groups);
    }
  }

  const tokens = text.toLowerCase().split(/\W+/).filter(Boolean);
  const scored = PRODUCTS.map((p) => {
    const hay = `${p.name} ${p.category}`.toLowerCase();
    const score = tokens.reduce((s, t) => (hay.includes(t) ? s + 1 : s), 0);
    return { product: p, score };
  })
    .filter((x) => x.score > 0)
    .sort((a, b) => b.score - a.score);

  if (scored.length > 0) {
    const byCat = new Map<string, CatalogProduct[]>();
    for (const { product } of scored) {
      const list = byCat.get(product.category) ?? [];
      if (list.length < 3) list.push(product);
      byCat.set(product.category, list);
    }
    return [...byCat.entries()].slice(0, 4).map(([cat, products]) => ({
      emoji: "🛒",
      title: cat,
      products,
    }));
  }

  return pickFromCategories(DEFAULT_GROUPS);
}

/** Simulated network + model latency for demo UX */
export function runDiscoverySearch(prompt: string): Promise<DiscoveryGroup[]> {
  const groups = discoverFromPrompt(prompt);
  return new Promise((resolve) => {
    window.setTimeout(() => resolve(groups), 700);
  });
}
