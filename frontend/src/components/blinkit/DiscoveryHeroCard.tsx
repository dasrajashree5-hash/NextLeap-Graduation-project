"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Sparkles } from "lucide-react";
import { HERO_EXAMPLES } from "@/lib/discoveryPrompts";

const ROTATE_MS = 3500;

export default function DiscoveryHeroCard() {
  const router = useRouter();
  const [index, setIndex] = useState(0);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const id = window.setInterval(() => {
      setVisible(false);
      window.setTimeout(() => {
        setIndex((i) => (i + 1) % HERO_EXAMPLES.length);
        setVisible(true);
      }, 280);
    }, ROTATE_MS);
    return () => window.clearInterval(id);
  }, []);

  function goDiscover() {
    router.push("/discover");
  }

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      goDiscover();
    }
  }

  return (
    <section className="px-4" aria-label="AI Discovery">
      <div
        role="button"
        tabIndex={0}
        onClick={goDiscover}
        onKeyDown={onKeyDown}
        className="group relative overflow-hidden rounded-[22px] bg-gradient-to-br from-blinkit-green via-emerald-600 to-teal-700 p-5 text-white shadow-[0_12px_40px_-12px_rgba(49,134,22,0.55)] transition-transform duration-300 hover:scale-[1.01] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blinkit-green animate-[fadeInUp_0.5s_ease-out]"
      >
        <div
          className="pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-full bg-white/10 blur-2xl"
          aria-hidden
        />
        <div
          className="pointer-events-none absolute -bottom-10 -left-6 h-28 w-28 rounded-full bg-yellow-300/20 blur-xl"
          aria-hidden
        />

        <div className="relative flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <p className="flex items-center gap-1.5 text-sm font-semibold tracking-tight">
              <Sparkles className="h-4 w-4 shrink-0" aria-hidden />
              Discover with AI
            </p>
            <p className="mt-2 text-[13px] leading-relaxed text-white/90">
              Plan meals, occasions, gifts or shopping needs using natural language.
            </p>
            <p
              className={`mt-4 min-h-[1.5rem] text-base font-medium transition-opacity duration-300 ${
                visible ? "opacity-100" : "opacity-0"
              }`}
              aria-live="polite"
              aria-atomic
            >
              {HERO_EXAMPLES[index]}
            </p>
          </div>
          <span className="text-3xl opacity-90" aria-hidden>
            ✨
          </span>
        </div>

        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            goDiscover();
          }}
          className="relative mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-white px-4 py-3 text-sm font-bold text-blinkit-green shadow-md transition hover:bg-zinc-50 active:scale-[0.98]"
        >
          Try AI Discovery
          <ArrowRight className="h-4 w-4" aria-hidden />
        </button>
      </div>
    </section>
  );
}
