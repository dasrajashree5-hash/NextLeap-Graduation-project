"use client";

import { useRouter } from "next/navigation";
import { POPULAR_CHIPS } from "@/lib/discoveryPrompts";

export default function PopularIdeasChips() {
  const router = useRouter();

  function openChip(prompt: string) {
    router.push(`/discover?prompt=${encodeURIComponent(prompt)}`);
  }

  return (
    <section className="animate-[fadeInUp_0.55s_ease-out]" aria-labelledby="popular-ideas">
      <h2 id="popular-ideas" className="px-4 text-sm font-bold text-zinc-800">
        Popular ideas
      </h2>
      <ul
        className="mt-3 flex gap-2 overflow-x-auto px-4 pb-1 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
        role="list"
      >
        {POPULAR_CHIPS.map((chip) => (
          <li key={chip.label} className="flex-shrink-0">
            <button
              type="button"
              onClick={() => openChip(chip.prompt)}
              className="rounded-full border border-zinc-200 bg-white px-3.5 py-2 text-xs font-semibold text-zinc-700 shadow-sm transition hover:border-blinkit-green/40 hover:bg-blinkit-green/5 hover:text-blinkit-green focus-visible:outline focus-visible:outline-2 focus-visible:outline-blinkit-green"
            >
              {chip.label}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
