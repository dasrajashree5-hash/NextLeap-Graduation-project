"use client";

import Link from "next/link";
import { Sparkles, Zap } from "lucide-react";
import {
  CATEGORIES,
  CATEGORY_ICONS,
  PRODUCTS,
  productsByCategory,
} from "@/lib/catalog";
import ProductCard from "@/components/blinkit/ProductCard";

type Props = {
  search: string;
  onCategorySelect: (category: string) => void;
};

export default function HomeView({ search, onCategorySelect }: Props) {
  const q = search.trim().toLowerCase();
  const filtered = q
    ? PRODUCTS.filter(
        (p) =>
          p.name.toLowerCase().includes(q) || p.category.toLowerCase().includes(q)
      )
    : null;

  const dairy = productsByCategory("Dairy").slice(0, 4);
  const snacks = productsByCategory("Snacks").slice(0, 4);
  const discover = PRODUCTS.filter((p) =>
    ["Pet Care", "Baby Care", "Health & Nutrition", "Electronics"].includes(p.category)
  ).slice(0, 6);

  return (
    <div className="space-y-5 pb-4">
      <section
        className="mx-4 overflow-hidden rounded-2xl bg-gradient-to-r from-blinkit-green to-emerald-600 p-4 text-white shadow-md"
        aria-label="Promotional offer"
      >
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="flex items-center gap-1 text-xs font-semibold uppercase tracking-wide opacity-90">
              <Zap className="h-3.5 w-3.5" aria-hidden />
              Explore beyond groceries
            </p>
            <h2 className="mt-1 text-lg font-bold leading-tight">
              Try a new category this week
            </h2>
            <p className="mt-1 text-xs opacity-90">
              AI picks one adjacent item for your cart — grounded in real customer insights.
            </p>
          </div>
          <Sparkles className="h-8 w-8 flex-shrink-0 opacity-80" aria-hidden />
        </div>
      </section>

      <section className="px-4" aria-labelledby="shop-by-category">
        <h2 id="shop-by-category" className="text-sm font-bold text-zinc-800">
          Shop by category
        </h2>
        <ul className="mt-3 grid grid-cols-4 gap-3">
          {CATEGORIES.slice(0, 8).map((cat) => (
            <li key={cat}>
              <button
                type="button"
                onClick={() => onCategorySelect(cat)}
                className="flex w-full flex-col items-center gap-1.5 rounded-xl border border-zinc-100 bg-white p-2 shadow-sm transition active:scale-95"
              >
                <span className="flex h-12 w-12 items-center justify-center rounded-full bg-zinc-50 text-2xl">
                  {CATEGORY_ICONS[cat] ?? "📦"}
                </span>
                <span className="line-clamp-2 text-center text-[10px] font-medium leading-tight text-zinc-700">
                  {cat}
                </span>
              </button>
            </li>
          ))}
        </ul>
      </section>

      {filtered ? (
        <section className="px-4" aria-labelledby="search-results">
          <h2 id="search-results" className="text-sm font-bold text-zinc-800">
            Results ({filtered.length})
          </h2>
          <ul className="mt-3 grid grid-cols-2 gap-3">
            {filtered.map((p) => (
              <li key={p.product_id}>
                <ProductCard product={p} />
              </li>
            ))}
          </ul>
          {filtered.length === 0 && (
            <p className="mt-4 text-center text-sm text-zinc-500">No products found.</p>
          )}
        </section>
      ) : (
        <>
          <ProductRail title="Dairy & breakfast" products={dairy} />
          <ProductRail title="Snacks & munchies" products={snacks} horizontal />
          <ProductRail
            title="Discover something new"
            products={discover}
            horizontal
            subtitle="Cross-category picks"
          />
        </>
      )}

      <p className="px-4 text-center text-[10px] text-zinc-400">
        Growth team demo ·{" "}
        <Link href="/admin" className="font-medium text-blinkit-green underline">
          Open discovery dashboard
        </Link>
      </p>
    </div>
  );
}

function ProductRail({
  title,
  subtitle,
  products,
  horizontal,
}: {
  title: string;
  subtitle?: string;
  products: typeof PRODUCTS;
  horizontal?: boolean;
}) {
  return (
    <section className="px-4" aria-labelledby={`rail-${title}`}>
      <div className="flex items-baseline justify-between">
        <h2 id={`rail-${title}`} className="text-sm font-bold text-zinc-800">
          {title}
        </h2>
        {subtitle && <span className="text-[10px] text-zinc-500">{subtitle}</span>}
      </div>
      {horizontal ? (
        <ul className="mt-3 flex gap-3 overflow-x-auto pb-1 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {products.map((p) => (
            <li key={p.product_id}>
              <ProductCard product={p} compact />
            </li>
          ))}
        </ul>
      ) : (
        <ul className="mt-3 grid grid-cols-2 gap-3">
          {products.map((p) => (
            <li key={p.product_id}>
              <ProductCard product={p} />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
