"use client";

import { Grid3X3, Home, Lightbulb, ShoppingCart } from "lucide-react";
import clsx from "clsx";

export type MobileTab = "home" | "categories" | "cart" | "discover";

type Props = {
  active: MobileTab;
  onChange: (tab: MobileTab) => void;
  cartCount: number;
};

const items: { id: MobileTab; label: string; icon: typeof Home }[] = [
  { id: "home", label: "Home", icon: Home },
  { id: "categories", label: "Categories", icon: Grid3X3 },
  { id: "discover", label: "Discover", icon: Lightbulb },
  { id: "cart", label: "Cart", icon: ShoppingCart },
];

export default function BottomNav({ active, onChange, cartCount }: Props) {
  return (
    <nav
      className="fixed bottom-0 left-1/2 z-50 w-full max-w-[430px] -translate-x-1/2 border-t border-zinc-200 bg-white pb-[env(safe-area-inset-bottom)]"
      aria-label="Primary"
    >
      <ul className="flex">
        {items.map((item) => {
          const selected = active === item.id;
          return (
            <li key={item.id} className="flex-1">
              <button
                type="button"
                onClick={() => onChange(item.id)}
                className={clsx(
                  "relative flex w-full flex-col items-center gap-0.5 py-2.5 text-[10px] font-medium transition",
                  selected ? "text-blinkit-green" : "text-zinc-500"
                )}
                aria-current={selected ? "page" : undefined}
              >
                <span className="relative">
                  <item.icon className="h-5 w-5" strokeWidth={selected ? 2.5 : 2} aria-hidden />
                  {item.id === "cart" && cartCount > 0 && (
                    <span className="absolute -right-2 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-blinkit-green px-1 text-[9px] font-bold text-white">
                      {cartCount > 99 ? "99+" : cartCount}
                    </span>
                  )}
                </span>
                {item.label}
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
