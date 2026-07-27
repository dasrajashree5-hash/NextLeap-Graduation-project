"use client";

import { Mic, Search } from "lucide-react";

type Props = {
  value?: string;
  onChange?: (v: string) => void;
  placeholder?: string;
};

export default function SearchBar({
  value = "",
  onChange,
  placeholder = 'Search "milk, bread, chips"',
}: Props) {
  return (
    <div className="-mt-1 bg-blinkit px-4 pb-4">
      <label className="relative block">
        <span className="sr-only">Search products</span>
        <Search
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400"
          aria-hidden
        />
        <input
          type="search"
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          placeholder={placeholder}
          className="w-full rounded-xl border-0 bg-white py-3 pl-10 pr-10 text-sm text-zinc-800 shadow-md placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-blinkit-green/40"
        />
        <Mic
          className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400"
          aria-hidden
        />
      </label>
    </div>
  );
}
