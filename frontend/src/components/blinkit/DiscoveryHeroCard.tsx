"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles } from "lucide-react";
import { DISCOVERY_INPUT_PLACEHOLDER, POPULAR_CHIPS } from "@/lib/discoveryPrompts";

function SparkleField() {
  const stars = [
    { top: "12%", left: "8%", size: 10, opacity: 0.35 },
    { top: "22%", left: "78%", size: 8, opacity: 0.45 },
    { top: "55%", left: "92%", size: 12, opacity: 0.3 },
    { top: "68%", left: "14%", size: 7, opacity: 0.4 },
    { top: "38%", left: "48%", size: 6, opacity: 0.25 },
    { top: "82%", left: "62%", size: 9, opacity: 0.35 },
  ];
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
      {stars.map((s, i) => (
        <Sparkles
          key={i}
          className="absolute text-white"
          style={{
            top: s.top,
            left: s.left,
            width: s.size,
            height: s.size,
            opacity: s.opacity,
          }}
        />
      ))}
      <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/12 blur-3xl" />
      <div className="absolute -bottom-12 -left-8 h-36 w-36 rounded-full bg-yellow-300/25 blur-2xl" />
      <div className="absolute right-1/4 top-1/3 h-24 w-24 rounded-full bg-teal-200/15 blur-2xl" />
    </div>
  );
}

export default function DiscoveryHeroCard() {
  const router = useRouter();
  const [value, setValue] = useState("");

  function goDiscover(prompt?: string) {
    const text = (prompt ?? value).trim();
    if (text) {
      router.push(`/discover?prompt=${encodeURIComponent(text)}`);
    } else {
      router.push("/discover");
    }
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    goDiscover();
  }

  return (
    <section className="px-4" aria-label="AI Discovery">
      <div className="relative overflow-hidden rounded-[22px] bg-gradient-to-br from-blinkit-green via-emerald-600 to-teal-700 px-5 pb-6 pt-6 text-white shadow-[0_12px_40px_-12px_rgba(49,134,22,0.55)] animate-[fadeInUp_0.5s_ease-out] min-h-[320px]">
        <SparkleField />

        <div className="relative">
          <p className="flex items-center gap-1.5 text-base font-bold tracking-tight">
            <Sparkles className="h-5 w-5 shrink-0" aria-hidden />
            Discover with AI
          </p>
          <p className="mt-2 max-w-[95%] text-[13px] leading-relaxed text-white/92">
            Plan meals, gifts, parties or everyday shopping using natural language.
          </p>

          <p
            id="popular-ideas-hero"
            className="mt-5 text-[11px] font-semibold uppercase tracking-wide text-white/75"
          >
            Popular ideas
          </p>
          <ul
            className="mt-2.5 flex gap-2 overflow-x-auto pb-1 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
            aria-labelledby="popular-ideas-hero"
          >
            {POPULAR_CHIPS.map((chip) => (
              <li key={chip.label} className="flex-shrink-0">
                <button
                  type="button"
                  onClick={() => goDiscover(chip.prompt)}
                  className="whitespace-nowrap rounded-full border border-white/35 bg-white/15 px-3.5 py-2 text-xs font-semibold text-white shadow-sm backdrop-blur-sm transition hover:border-white/55 hover:bg-white/25 focus-visible:outline focus-visible:outline-2 focus-visible:outline-white"
                >
                  {chip.label}
                </button>
              </li>
            ))}
          </ul>

          <div className="my-5 h-px bg-white/20" role="presentation" />

          <form onSubmit={onSubmit} aria-label="Start AI discovery">
            <label className="sr-only" htmlFor="home-discovery-prompt">
              {DISCOVERY_INPUT_PLACEHOLDER}
            </label>
            <div className="rounded-2xl bg-white p-3 shadow-lg ring-1 ring-black/5">
              <textarea
                id="home-discovery-prompt"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder={DISCOVERY_INPUT_PLACEHOLDER}
                rows={3}
                className="w-full resize-none border-0 bg-transparent text-sm leading-relaxed text-zinc-800 placeholder:text-zinc-400 focus:outline-none focus:ring-0"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    goDiscover();
                  }
                }}
              />
              <div className="mt-1 flex justify-end">
                <button
                  type="submit"
                  className="inline-flex items-center gap-1.5 rounded-xl bg-blinkit-green px-4 py-2.5 text-sm font-bold text-white shadow-md transition hover:bg-blinkit-green-dark active:scale-[0.98] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blinkit-green"
                >
                  <Sparkles className="h-4 w-4" aria-hidden />
                  Discover
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
}
