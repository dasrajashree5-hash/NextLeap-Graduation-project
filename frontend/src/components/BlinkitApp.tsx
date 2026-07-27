"use client";

import { useState } from "react";
import BottomNav, { type MobileTab } from "@/components/blinkit/BottomNav";
import CartView from "@/components/blinkit/CartView";
import CategoriesView from "@/components/blinkit/CategoriesView";
import DiscoverView from "@/components/blinkit/DiscoverView";
import HomeView from "@/components/blinkit/HomeView";
import MobileHeader from "@/components/blinkit/MobileHeader";
import SearchBar from "@/components/blinkit/SearchBar";
import { CartProvider, useCart } from "@/lib/cart";

function BlinkitShell() {
  const [tab, setTab] = useState<MobileTab>("home");
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<string | null>(null);
  const { itemCount } = useCart();

  const showSearch = tab === "home" || tab === "categories";

  function goCategory(cat: string) {
    setCategory(cat);
    setTab("categories");
  }

  return (
    <div className="mx-auto min-h-screen max-w-[430px] bg-blinkit-surface shadow-xl">
      <div className="sticky top-0 z-40">
        {tab !== "cart" && <MobileHeader />}
        {showSearch && (
          <SearchBar
            value={search}
            onChange={setSearch}
            placeholder={
              tab === "categories" ? "Search in categories" : 'Search "milk, bread, chips"'
            }
          />
        )}
      </div>

      <main className="min-h-[calc(100vh-8rem)] pb-24 pt-2">
        {tab === "home" && (
          <HomeView search={search} onCategorySelect={goCategory} />
        )}
        {tab === "categories" && (
          <CategoriesView
            selectedCategory={category}
            onSelectCategory={setCategory}
          />
        )}
        {tab === "cart" && <CartView />}
        {tab === "discover" && <DiscoverView />}
      </main>

      <BottomNav active={tab} onChange={setTab} cartCount={itemCount} />
    </div>
  );
}

export default function BlinkitApp() {
  return (
    <CartProvider>
      <BlinkitShell />
    </CartProvider>
  );
}
