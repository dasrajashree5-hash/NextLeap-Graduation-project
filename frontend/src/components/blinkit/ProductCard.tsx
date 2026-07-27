"use client";

import { Minus, Plus } from "lucide-react";
import type { CatalogProduct } from "@/lib/catalog";
import { CATEGORY_ICONS, formatInr } from "@/lib/catalog";
import { useCart } from "@/lib/cart";

type Props = {
  product: CatalogProduct;
  compact?: boolean;
};

export default function ProductCard({ product, compact }: Props) {
  const { add, decrement, qtyFor } = useCart();
  const qty = qtyFor(product.product_id);
  const icon = CATEGORY_ICONS[product.category] ?? "📦";

  return (
    <article
      className={`flex flex-col rounded-xl border border-zinc-100 bg-white shadow-sm ${
        compact ? "w-[140px] flex-shrink-0" : "w-full"
      }`}
    >
      <div
        className={`relative flex items-center justify-center rounded-t-xl bg-gradient-to-b from-zinc-50 to-white ${
          compact ? "h-[100px]" : "h-[120px]"
        }`}
      >
        <span className="text-4xl" aria-hidden>
          {icon}
        </span>
        {product.eta_mins && product.eta_mins <= 10 && (
          <span className="absolute left-2 top-2 rounded bg-blinkit-green/10 px-1.5 py-0.5 text-[10px] font-semibold text-blinkit-green">
            {product.eta_mins} min
          </span>
        )}
      </div>
      <div className="flex flex-1 flex-col p-2.5">
        <p className="line-clamp-2 text-xs font-medium leading-snug text-zinc-800">
          {product.name}
        </p>
        <p className="mt-0.5 text-[10px] text-zinc-500">{product.unit}</p>
        <div className="mt-1 flex items-center gap-1 text-[10px] text-zinc-500">
          <span className="font-medium text-zinc-700">{product.rating}★</span>
          <span>({(product.review_count / 1000).toFixed(1)}k)</span>
        </div>
        <div className="mt-auto flex items-end justify-between pt-2">
          <p className="text-sm font-bold text-zinc-900">{formatInr(product.price_inr)}</p>
          {qty === 0 ? (
            <button
              type="button"
              onClick={() => add(product)}
              className="rounded-md border-2 border-blinkit-green bg-blinkit-green/5 px-3 py-1 text-xs font-bold uppercase tracking-wide text-blinkit-green transition hover:bg-blinkit-green hover:text-white"
              aria-label={`Add ${product.name} to cart`}
            >
              ADD
            </button>
          ) : (
            <div
              className="flex items-center rounded-md bg-blinkit-green text-white"
              role="group"
              aria-label={`Quantity for ${product.name}`}
            >
              <button
                type="button"
                onClick={() => decrement(product.product_id)}
                className="rounded-l-md p-1.5 hover:bg-blinkit-green-dark"
                aria-label="Decrease quantity"
              >
                <Minus className="h-3.5 w-3.5" />
              </button>
              <span className="min-w-[1.25rem] text-center text-xs font-bold">{qty}</span>
              <button
                type="button"
                onClick={() => add(product)}
                className="rounded-r-md p-1.5 hover:bg-blinkit-green-dark"
                aria-label="Increase quantity"
              >
                <Plus className="h-3.5 w-3.5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </article>
  );
}
