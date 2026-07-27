"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { CatalogProduct } from "@/lib/catalog";

export type CartLine = {
  product: CatalogProduct;
  qty: number;
};

type CartContextValue = {
  lines: CartLine[];
  itemCount: number;
  subtotal: number;
  add: (product: CatalogProduct) => void;
  decrement: (productId: string) => void;
  remove: (productId: string) => void;
  clear: () => void;
  qtyFor: (productId: string) => number;
};

const CartContext = createContext<CartContextValue | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>([]);

  const add = useCallback((product: CatalogProduct) => {
    setLines((prev) => {
      const idx = prev.findIndex((l) => l.product.product_id === product.product_id);
      if (idx >= 0) {
        const next = [...prev];
        next[idx] = { ...next[idx], qty: next[idx].qty + 1 };
        return next;
      }
      return [...prev, { product, qty: 1 }];
    });
  }, []);

  const decrement = useCallback((productId: string) => {
    setLines((prev) =>
      prev
        .map((l) =>
          l.product.product_id === productId ? { ...l, qty: l.qty - 1 } : l
        )
        .filter((l) => l.qty > 0)
    );
  }, []);

  const remove = useCallback((productId: string) => {
    setLines((prev) => prev.filter((l) => l.product.product_id !== productId));
  }, []);

  const clear = useCallback(() => setLines([]), []);

  const qtyFor = useCallback(
    (productId: string) => lines.find((l) => l.product.product_id === productId)?.qty ?? 0,
    [lines]
  );

  const itemCount = useMemo(() => lines.reduce((s, l) => s + l.qty, 0), [lines]);
  const subtotal = useMemo(
    () => lines.reduce((s, l) => s + l.product.price_inr * l.qty, 0),
    [lines]
  );

  const value = useMemo(
    () => ({
      lines,
      itemCount,
      subtotal,
      add,
      decrement,
      remove,
      clear,
      qtyFor,
    }),
    [lines, itemCount, subtotal, add, decrement, remove, clear, qtyFor]
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart(): CartContextValue {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}
