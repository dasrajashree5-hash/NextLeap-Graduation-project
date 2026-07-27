export type CatalogProduct = {
  product_id: string;
  name: string;
  category: string;
  rating: number;
  price_inr: number;
  review_count: number;
  unit: string;
  eta_mins?: number;
};

export const CATEGORIES = [
  "Grocery",
  "Dairy",
  "Snacks",
  "Fruits & Vegetables",
  "Beverages",
  "Personal Care",
  "Baby Care",
  "Pet Care",
  "Household",
  "Health & Nutrition",
  "Electronics",
] as const;

export const CATEGORY_ICONS: Record<string, string> = {
  Grocery: "🛒",
  Dairy: "🥛",
  Snacks: "🍿",
  "Fruits & Vegetables": "🥬",
  Beverages: "🥤",
  "Personal Care": "🧴",
  "Baby Care": "👶",
  "Pet Care": "🐾",
  Household: "🧹",
  "Health & Nutrition": "💊",
  Electronics: "🔌",
};

export const PRODUCTS: CatalogProduct[] = [
  {
    product_id: "sku-d001",
    name: "Amul Taaza Milk 1L",
    category: "Dairy",
    rating: 4.7,
    price_inr: 57,
    review_count: 12000,
    unit: "1 L",
    eta_mins: 8,
  },
  {
    product_id: "sku-g001",
    name: "Britannia Brown Bread",
    category: "Grocery",
    rating: 4.5,
    price_inr: 45,
    review_count: 8000,
    unit: "400 g",
    eta_mins: 8,
  },
  {
    product_id: "sku-s001",
    name: "Lay's Classic Salted 52g",
    category: "Snacks",
    rating: 4.4,
    price_inr: 20,
    review_count: 15000,
    unit: "52 g",
    eta_mins: 10,
  },
  {
    product_id: "sku-pc001",
    name: "Dove Intense Repair Shampoo 180ml",
    category: "Personal Care",
    rating: 4.6,
    price_inr: 249,
    review_count: 3200,
    unit: "180 ml",
    eta_mins: 12,
  },
  {
    product_id: "sku-bc001",
    name: "Pampers Baby Dry Diapers M (22)",
    category: "Baby Care",
    rating: 4.5,
    price_inr: 599,
    review_count: 2100,
    unit: "22 pcs",
    eta_mins: 15,
  },
  {
    product_id: "sku-pet001",
    name: "Pedigree Adult Chicken Treats 70g",
    category: "Pet Care",
    rating: 4.4,
    price_inr: 99,
    review_count: 980,
    unit: "70 g",
    eta_mins: 12,
  },
  {
    product_id: "sku-hn001",
    name: "MuscleBlaze Whey 1kg",
    category: "Health & Nutrition",
    rating: 4.3,
    price_inr: 2499,
    review_count: 450,
    unit: "1 kg",
    eta_mins: 20,
  },
  {
    product_id: "sku-hh001",
    name: "Surf Excel Matic Liquid 1L",
    category: "Household",
    rating: 4.6,
    price_inr: 320,
    review_count: 5600,
    unit: "1 L",
    eta_mins: 10,
  },
  {
    product_id: "sku-bev001",
    name: "Real Fruit Power Orange 1L",
    category: "Beverages",
    rating: 4.5,
    price_inr: 110,
    review_count: 4100,
    unit: "1 L",
    eta_mins: 9,
  },
  {
    product_id: "sku-el001",
    name: "boAt Type-C Cable 1m",
    category: "Electronics",
    rating: 4.2,
    price_inr: 199,
    review_count: 12000,
    unit: "1 pc",
    eta_mins: 25,
  },
  {
    product_id: "sku-pc002",
    name: "Colgate MaxFresh Toothpaste 150g",
    category: "Personal Care",
    rating: 4.7,
    price_inr: 89,
    review_count: 22000,
    unit: "150 g",
    eta_mins: 8,
  },
  {
    product_id: "sku-pet002",
    name: "Whiskas Temptations Cat Treats 35g",
    category: "Pet Care",
    rating: 4.5,
    price_inr: 75,
    review_count: 640,
    unit: "35 g",
    eta_mins: 12,
  },
  {
    product_id: "sku-fv001",
    name: "Fresh Bananas (Robusta)",
    category: "Fruits & Vegetables",
    rating: 4.6,
    price_inr: 49,
    review_count: 9000,
    unit: "6 pcs",
    eta_mins: 8,
  },
  {
    product_id: "sku-fv002",
    name: "Hybrid Tomatoes 500g",
    category: "Fruits & Vegetables",
    rating: 4.4,
    price_inr: 32,
    review_count: 11000,
    unit: "500 g",
    eta_mins: 8,
  },
];

export function productsByCategory(category: string): CatalogProduct[] {
  return PRODUCTS.filter((p) => p.category === category);
}

export function formatInr(amount: number): string {
  return `₹${amount}`;
}
