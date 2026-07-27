"use client";

import { ChevronRight } from "lucide-react";
import { CATEGORIES, CATEGORY_ICONS, productsByCategory } from "@/lib/catalog";
import ProductCard from "@/components/blinkit/ProductCard";

type Props = {
  selectedCategory: string | null;
  onSelectCategory: (category: string | null) => void;
};

export default function CategoriesView({ selectedCategory, onSelectCategory }: Props) {
  if (selectedCategory) {
    const items = productsByCategory(selectedCategory);
    return (
      <div className="px-4 pb-4">
        <button
          type="button"
          onClick={() => onSelectCategory(null)}
          className="mb-4 flex items-center gap-1 text-sm font-medium text-blinkit-green"
        >
          ← All categories
        </button>
        <div className="flex items-center gap-3">
          <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-3xl shadow-sm">
            {CATEGORY_ICONS[selectedCategory] ?? "📦"}
          </span>
          <div>
            <h2 className="text-lg font-bold text-zinc-900">{selectedCategory}</h2>
            <p className="text-xs text-zinc-500">{items.length} items</p>
          </div>
        </div>
        <ul className="mt-5 grid grid-cols-2 gap-3">
          {items.map((p) => (
            <li key={p.product_id}>
              <ProductCard product={p} />
            </li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <div className="px-4 pb-4">
      <h2 className="text-lg font-bold text-zinc-900">All categories</h2>
      <p className="mt-1 text-xs text-zinc-500">Everything on Blinkit, delivered fast</p>
      <ul className="mt-4 divide-y divide-zinc-100 rounded-2xl border border-zinc-100 bg-white shadow-sm">
        {CATEGORIES.map((cat) => {
          const count = productsByCategory(cat).length;
          return (
            <li key={cat}>
              <button
                type="button"
                onClick={() => onSelectCategory(cat)}
                className="flex w-full items-center gap-3 px-4 py-3.5 text-left active:bg-zinc-50"
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-50 text-xl">
                  {CATEGORY_ICONS[cat] ?? "📦"}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-zinc-800">{cat}</p>
                  <p className="text-xs text-zinc-500">{count} products</p>
                </div>
                <ChevronRight className="h-4 w-4 text-zinc-400" aria-hidden />
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
