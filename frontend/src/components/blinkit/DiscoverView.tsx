"use client";

import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, Sparkles } from "lucide-react";
import ProductCard from "@/components/blinkit/ProductCard";
import { api, ApiError } from "@/lib/api";
import { runDiscoverySearch, type DiscoveryGroup } from "@/lib/discoveryEngine";
import { POPULAR_CHIPS } from "@/lib/discoveryPrompts";

function DiscoverViewInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const promptParam = searchParams.get("prompt");

  const [input, setInput] = useState("");
  const [groups, setGroups] = useState<DiscoveryGroup[] | null>(null);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const lastAutoPrompt = useRef<string | null>(null);

  const [insightsLoading, setInsightsLoading] = useState(true);
  const [insights, setInsights] = useState<Awaited<ReturnType<typeof api.insights>>>([]);
  const [insightsError, setInsightsError] = useState<string | null>(null);
  const [showResearch, setShowResearch] = useState(false);

  const runSearch = useCallback(async (prompt: string) => {
    const trimmed = prompt.trim();
    if (!trimmed) {
      setGroups(null);
      return;
    }
    setSearching(true);
    setSearchError(null);
    try {
      const result = await runDiscoverySearch(trimmed);
      setGroups(result);
    } catch {
      setSearchError("Something went wrong. Please try again.");
    } finally {
      setSearching(false);
    }
  }, []);

  useEffect(() => {
    if (promptParam == null) return;
    const decoded = promptParam.trim();
    if (decoded === lastAutoPrompt.current) return;
    lastAutoPrompt.current = decoded;
    setInput(decoded);
    void runSearch(decoded);
  }, [promptParam, runSearch]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setInsightsLoading(true);
      try {
        const ins = await api.insights(6);
        if (!cancelled) setInsights(ins);
      } catch (e) {
        if (!cancelled) {
          setInsightsError(e instanceof ApiError ? e.message : "Failed to load insights");
        }
      } finally {
        if (!cancelled) setInsightsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = input.trim();
    if (trimmed) {
      router.replace(`/discover?prompt=${encodeURIComponent(trimmed)}`, { scroll: false });
      void runSearch(trimmed);
    } else {
      router.replace("/discover", { scroll: false });
      setGroups(null);
    }
  }

  function applyChip(prompt: string) {
    setInput(prompt);
    router.replace(`/discover?prompt=${encodeURIComponent(prompt)}`, { scroll: false });
    void runSearch(prompt);
  }

  return (
    <div className="space-y-5 pb-4">
      <div className="px-4">
        <h1 className="text-lg font-bold text-zinc-900">AI Discovery</h1>
        <p className="mt-1 text-xs text-zinc-500">
          Describe a meal, occasion, or need — we&apos;ll group picks from across Blinkit.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-3 px-4" aria-label="Discovery search">
        <label className="sr-only" htmlFor="discover-prompt">
          What do you need?
        </label>
        <div className="flex gap-2">
          <input
            id="discover-prompt"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder='Try "I&apos;m making pasta tonight"'
            className="min-w-0 flex-1 rounded-xl border border-zinc-200 bg-white px-3 py-3 text-sm shadow-sm focus:border-blinkit-green focus:outline-none focus:ring-2 focus:ring-blinkit-green/20"
            autoComplete="off"
          />
          <button
            type="submit"
            disabled={searching}
            className="flex shrink-0 items-center gap-1.5 rounded-xl bg-blinkit-green px-4 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-blinkit-green-dark disabled:opacity-70"
          >
            {searching ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            ) : (
              <Sparkles className="h-4 w-4" aria-hidden />
            )}
            <span className="sr-only sm:not-sr-only">Discover</span>
          </button>
        </div>
        <ul className="flex gap-2 overflow-x-auto pb-1 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {POPULAR_CHIPS.slice(0, 6).map((chip) => (
            <li key={chip.label} className="shrink-0">
              <button
                type="button"
                onClick={() => applyChip(chip.prompt)}
                className="rounded-full border border-zinc-200 bg-white px-3 py-1.5 text-[11px] font-medium text-zinc-600 hover:border-blinkit-green/30"
              >
                {chip.label}
              </button>
            </li>
          ))}
        </ul>
      </form>

      {searchError && (
        <div className="mx-4 rounded-xl bg-red-50 p-3 text-xs text-red-700" role="alert">
          {searchError}
        </div>
      )}

      {searching && (
        <div className="px-4" aria-live="polite">
          <ul className="space-y-4">
            {[1, 2, 3].map((i) => (
              <li key={i} className="h-36 animate-pulse rounded-2xl bg-zinc-200" />
            ))}
          </ul>
        </div>
      )}

      {!searching && groups && groups.length > 0 && (
        <div className="space-y-5 px-4">
          {groups.map((group) => (
            <section key={group.title} aria-labelledby={`group-${group.title}`}>
              <h2
                id={`group-${group.title}`}
                className="text-sm font-bold text-zinc-800"
              >
                {group.emoji} {group.title}
              </h2>
              <ul className="mt-3 flex gap-3 overflow-x-auto pb-1 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
                {group.products.map((p) => (
                  <li key={`${group.title}-${p.product_id}`}>
                    <ProductCard product={p} compact />
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      )}

      {!searching && !groups && (
        <p className="px-4 text-center text-sm text-zinc-500">
          Enter a prompt above or pick a popular idea from Home.
        </p>
      )}

      <section className="border-t border-zinc-100 px-4 pt-4" aria-labelledby="research-toggle">
        <button
          type="button"
          id="research-toggle"
          onClick={() => setShowResearch((v) => !v)}
          className="flex w-full items-center justify-between text-left text-sm font-bold text-zinc-800"
          aria-expanded={showResearch}
        >
          Research insights
          <span className="text-xs font-normal text-blinkit-green">
            {showResearch ? "Hide" : "Show"}
          </span>
        </button>
        {showResearch && (
          <div className="mt-3 space-y-3">
            {insightsError && (
              <p className="text-xs text-red-600" role="alert">
                {insightsError}
              </p>
            )}
            {insightsLoading ? (
              <div className="h-20 animate-pulse rounded-xl bg-zinc-200" />
            ) : insights.length === 0 ? (
              <p className="text-xs text-zinc-500">No insights loaded yet.</p>
            ) : (
              <ul className="space-y-2">
                {insights.map((ins) => (
                  <li
                    key={ins.id}
                    className="rounded-xl border border-zinc-100 bg-white p-3 text-xs shadow-sm"
                  >
                    <p className="font-semibold text-zinc-900">{ins.problem}</p>
                    {ins.evidence && (
                      <p className="mt-1 line-clamp-2 text-zinc-600">{ins.evidence}</p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </section>
    </div>
  );
}

export default function DiscoverView() {
  return (
    <Suspense
      fallback={
        <div className="px-4 py-8">
          <div className="h-10 animate-pulse rounded-xl bg-zinc-200" />
        </div>
      }
    >
      <DiscoverViewInner />
    </Suspense>
  );
}
