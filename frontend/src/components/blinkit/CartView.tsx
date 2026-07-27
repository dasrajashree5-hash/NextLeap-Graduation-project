"use client";

import { useCallback, useEffect, useState } from "react";
import { Loader2, Sparkles, Trash2 } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { formatInr, CATEGORY_ICONS } from "@/lib/catalog";
import { useCart } from "@/lib/cart";

const SEGMENTS = [
  { id: "mission_shopper", label: "Mission shopper" },
  { id: "family_stockup", label: "Family stock-up" },
  { id: "explorer", label: "Explorer" },
  { id: "student", label: "Student" },
  { id: "new_parent", label: "New parent" },
  { id: "pet_owner", label: "Pet owner" },
];

export default function CartView() {
  const { lines, subtotal, itemCount, decrement, add, remove, clear } = useCart();
  const [segment, setSegment] = useState("mission_shopper");
  const [busy, setBusy] = useState(false);
  const [mvpReady, setMvpReady] = useState<boolean | null>(null);
  const [suggestion, setSuggestion] = useState<Awaited<
    ReturnType<typeof api.mvpRecommend>
  > | null>(null);
  const [suggestionError, setSuggestionError] = useState<string | null>(null);

  useEffect(() => {
    api.mvpStatus().then((s) => setMvpReady(s.ready)).catch(() => setMvpReady(false));
  }, []);

  const fetchSuggestion = useCallback(async () => {
    if (!lines.length) return;
    setBusy(true);
    setSuggestionError(null);
    try {
      const res = await api.mvpRecommend({
        basket_items: lines.map((l) => ({
          name: l.product.name,
          category: l.product.category,
        })),
        customer_segment: segment,
        limit: 1,
      });
      setSuggestion(res);
    } catch (e) {
      setSuggestion(null);
      setSuggestionError(
        e instanceof ApiError
          ? e.message
          : "Could not load AI suggestion. Is the backend running?"
      );
    } finally {
      setBusy(false);
    }
  }, [lines, segment]);

  useEffect(() => {
    if (lines.length >= 2 && mvpReady) {
      fetchSuggestion();
    } else {
      setSuggestion(null);
    }
  }, [lines.length, mvpReady, segment, fetchSuggestion]);

  if (itemCount === 0) {
    return (
      <div className="flex flex-col items-center px-6 py-16 text-center">
        <span className="text-5xl" aria-hidden>
          🛒
        </span>
        <h2 className="mt-4 text-lg font-bold text-zinc-900">Your cart is empty</h2>
        <p className="mt-2 text-sm text-zinc-500">
          Add milk, bread, or snacks — we will suggest one item from a new category at checkout.
        </p>
      </div>
    );
  }

  const deliveryFee = subtotal >= 199 ? 0 : 25;
  const total = subtotal + deliveryFee;
  const topSuggestion = suggestion?.suggestions?.[0];

  return (
    <div className="space-y-4 px-4 pb-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-zinc-900">My cart</h2>
        <button
          type="button"
          onClick={clear}
          className="text-xs font-medium text-red-600"
        >
          Clear all
        </button>
      </div>

      <ul className="space-y-3">
        {lines.map((line) => {
          const icon = CATEGORY_ICONS[line.product.category] ?? "📦";
          return (
            <li
              key={line.product.product_id}
              className="flex gap-3 rounded-2xl border border-zinc-100 bg-white p-3 shadow-sm"
            >
              <div className="flex h-16 w-16 flex-shrink-0 items-center justify-center rounded-xl bg-zinc-50 text-2xl">
                {icon}
              </div>
              <div className="min-w-0 flex-1">
                <p className="line-clamp-2 text-sm font-medium text-zinc-800">
                  {line.product.name}
                </p>
                <p className="text-xs text-zinc-500">{line.product.unit}</p>
                <p className="mt-1 text-sm font-bold">{formatInr(line.product.price_inr)}</p>
              </div>
              <div className="flex flex-col items-end justify-between">
                <button
                  type="button"
                  onClick={() => remove(line.product.product_id)}
                  className="text-zinc-400 hover:text-red-500"
                  aria-label={`Remove ${line.product.name}`}
                >
                  <Trash2 className="h-4 w-4" />
                </button>
                <div className="flex items-center rounded-lg bg-blinkit-green text-white">
                  <button
                    type="button"
                    onClick={() => decrement(line.product.product_id)}
                    className="px-2 py-1 text-sm font-bold"
                    aria-label="Decrease"
                  >
                    −
                  </button>
                  <span className="min-w-[1.5rem] text-center text-sm font-bold">
                    {line.qty}
                  </span>
                  <button
                    type="button"
                    onClick={() => add(line.product)}
                    className="px-2 py-1 text-sm font-bold"
                    aria-label="Increase"
                  >
                    +
                  </button>
                </div>
              </div>
            </li>
          );
        })}
      </ul>

      <section
        className="rounded-2xl border-2 border-dashed border-blinkit-green/40 bg-blinkit-green/5 p-4"
        aria-labelledby="smart-basket-heading"
      >
        <div className="flex items-start gap-2">
          <Sparkles className="mt-0.5 h-5 w-5 flex-shrink-0 text-blinkit-green" aria-hidden />
          <div className="min-w-0 flex-1">
            <h3 id="smart-basket-heading" className="text-sm font-bold text-zinc-900">
              Smart basket expansion
            </h3>
            <p className="mt-0.5 text-xs text-zinc-600">
              One adjacent-category pick with barrier-aware copy from validated insights.
            </p>
            <label className="mt-3 block text-[10px] font-semibold uppercase text-zinc-500">
              Shopper segment
            </label>
            <select
              value={segment}
              onChange={(e) => setSegment(e.target.value)}
              className="mt-1 w-full rounded-lg border border-zinc-200 bg-white px-2 py-2 text-xs"
            >
              {SEGMENTS.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {mvpReady === false && (
          <p className="mt-3 text-xs text-amber-800">
            Run the analysis pipeline on the backend to enable live suggestions.
          </p>
        )}

        {busy && (
          <p className="mt-3 flex items-center gap-2 text-sm text-zinc-600">
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            Finding your discovery pick…
          </p>
        )}

        {suggestionError && (
          <p className="mt-3 text-xs text-red-600" role="alert">
            {suggestionError}
          </p>
        )}

        {topSuggestion && !busy && (
          <div className="mt-4 rounded-xl bg-white p-3 shadow-sm">
            <p className="text-[10px] font-bold uppercase tracking-wide text-blinkit-green">
              Try something new
            </p>
            <p className="mt-1 text-base font-bold text-zinc-900">{topSuggestion.product_name}</p>
            <p className="text-xs text-zinc-500">
              {topSuggestion.category} · {formatInr(topSuggestion.price_inr)} ·{" "}
              {topSuggestion.rating}★ · barrier: {topSuggestion.dominant_barrier}
            </p>
            <p className="mt-2 text-sm leading-relaxed text-zinc-700">{topSuggestion.message}</p>
            <p className="mt-2 text-[10px] text-zinc-400">
              Insight #{topSuggestion.insight_id}
              {topSuggestion.validation_status
                ? ` · ${topSuggestion.validation_status}`
                : ""}
            </p>
            <button
              type="button"
              className="mt-3 w-full rounded-xl bg-blinkit-green py-2.5 text-sm font-bold text-white"
            >
              Add to cart — {formatInr(topSuggestion.price_inr)}
            </button>
          </div>
        )}

        {lines.length < 2 && (
          <p className="mt-3 text-xs text-zinc-500">Add 2+ items to trigger a suggestion.</p>
        )}
      </section>

      <div className="rounded-2xl border border-zinc-100 bg-white p-4 shadow-sm">
        <div className="flex justify-between text-sm">
          <span className="text-zinc-600">Item total</span>
          <span className="font-medium">{formatInr(subtotal)}</span>
        </div>
        <div className="mt-2 flex justify-between text-sm">
          <span className="text-zinc-600">Delivery fee</span>
          <span className="font-medium">
            {deliveryFee === 0 ? (
              <span className="text-blinkit-green">FREE</span>
            ) : (
              formatInr(deliveryFee)
            )}
          </span>
        </div>
        <div className="mt-3 flex justify-between border-t border-zinc-100 pt-3 text-base font-bold">
          <span>Total</span>
          <span>{formatInr(total)}</span>
        </div>
      </div>

      <button
        type="button"
        className="w-full rounded-xl bg-blinkit py-3.5 text-center text-sm font-bold text-blinkit-ink shadow-md"
      >
        Proceed to pay · {formatInr(total)}
      </button>
    </div>
  );
}
