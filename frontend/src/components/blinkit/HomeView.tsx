"use client";

import Link from "next/link";
import {
  CATEGORIES,
  CATEGORY_ICONS,
  PRODUCTS,
  productsByCategory,
} from "@/lib/catalog";
import ProductCard from "@/components/blinkit/ProductCard";
import DiscoveryHeroCard from "@/components/blinkit/DiscoveryHeroCard";

type Props = {
  search: string;
  onCategorySelect: (category: string) => void;
};

const OFFERS = [
  { title: "Flat 20% off", sub: "On personal care", emoji: "💄" },
  { title: "Buy 1 Get 1", sub: "Select snacks", emoji: "🍿" },
  { title: "Free delivery", sub: "Orders above ₹199", emoji: "🛵" },
];

export default function HomeView({ search, onCategorySelect }: Props) {
  const q = search.trim().toLowerCase();
  const filtered = q
    ? PRODUCTS.filter(
        (p) =>
          p.name.toLowerCase().includes(q) || p.category.toLowerCase().includes(q)
      )
    : null;

  const frequentlyOrdered = [...PRODUCTS]
    .sort((a, b) => b.review_count - a.review_count)
    .slice(0, 4);
  const recommended = PRODUCTS.filter((p) =>
    ["Pet Care", "Baby Care", "Health & Nutrition", "Electronics", "Personal Care"].includes(
      p.category
    )
  ).slice(0, 6);
  const continueShopping = productsByCategory("Snacks").concat(productsByCategory("Beverages")).slice(0, 6);

  return (
    <div className="space-y-5 pb-4">
      {!filtered && (
        <>
          <DiscoveryHeroCard />
        </>
      )}

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
          <ProductRail title="Frequently ordered" products={frequentlyOrdered} />
          <ProductRail
            title="Recommended for you"
            products={recommended}
            horizontal
            subtitle="Cross-category picks"
          />

          <section className="px-4" aria-labelledby="shop-by-category">
            <h2 id="shop-by-category" className="text-sm font-bold text-zinc-800">
              Categories
            </h2>
            <ul className="mt-3 grid grid-cols-4 gap-3">
              {CATEGORIES.slice(0, 8).map((cat) => (
                <li key={cat}>
                  <button
                    type="button"
                    onClick={() => onCategorySelect(cat)}
                    className="flex w-full flex-col items-center gap-1.5 rounded-xl border border-zinc-100 bg-white p-2 shadow-sm transition hover:border-blinkit-green/20 active:scale-95"
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

          <section className="px-4" aria-labelledby="offers-heading">
            <h2 id="offers-heading" className="text-sm font-bold text-zinc-800">
              Offers
            </h2>
            <ul className="mt-3 flex gap-3 overflow-x-auto pb-1 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
              {OFFERS.map((offer) => (
                <li key={offer.title} className="w-[140px] flex-shrink-0">
                  <div className="rounded-[20px] border border-amber-100 bg-gradient-to-br from-amber-50 to-white p-3 shadow-sm">
                    <span className="text-2xl" aria-hidden>
                      {offer.emoji}
                    </span>
                    <p className="mt-2 text-xs font-bold text-zinc-900">{offer.title}</p>
                    <p className="text-[10px] text-zinc-500">{offer.sub}</p>
                  </div>
                </li>
              ))}
            </ul>
          </section>

          <ProductRail title="Continue shopping" products={continueShopping} horizontal />
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
