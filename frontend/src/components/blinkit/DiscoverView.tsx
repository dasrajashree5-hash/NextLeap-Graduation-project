"use client";

import Link from "next/link";
import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, Sparkles } from "lucide-react";
import ProductCard from "@/components/blinkit/ProductCard";
import { api, ApiError } from "@/lib/api";
import { runDiscoverySearch, type DiscoveryGroup } from "@/lib/discoveryEngine";
import { discoverHref } from "@/lib/discoveryNavigation";
import { DISCOVERY_INPUT_PLACEHOLDER, POPULAR_CHIPS } from "@/lib/discoveryPrompts";

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
      router.replace(discoverHref(trimmed), { scroll: false });
      void runSearch(trimmed);
    } else {
      router.replace("/discover", { scroll: false });
      setGroups(null);
    }
  }

  function submitFromKeyboard() {
    const trimmed = input.trim();
    if (trimmed) {
      router.replace(discoverHref(trimmed), { scroll: false });
      void runSearch(trimmed);
    }
  }

  function applyChip(prompt: string) {
    setInput(prompt);
    router.replace(discoverHref(prompt), { scroll: false });
    void runSearch(prompt);
  }

  return (
    <div className="space-y-5 pb-4">
      <div className="px-4">
        <h1 className="flex items-center gap-1.5 text-lg font-bold text-zinc-900">
          <Sparkles className="h-5 w-5 text-blinkit-green" aria-hidden />
          Discover with AI
        </h1>
        <p className="mt-1 text-xs leading-relaxed text-zinc-500">
          Plan meals, gifts, parties or everyday shopping using natural language.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4 px-4" aria-label="Discovery search">
        <div>
          <p id="discover-popular" className="text-xs font-bold text-zinc-800">
            Popular ideas
          </p>
          <ul
            className="mt-2 flex gap-2 overflow-x-auto pb-1 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
            aria-labelledby="discover-popular"
          >
            {POPULAR_CHIPS.map((chip) => (
              <li key={chip.label} className="shrink-0">
                <Link
                  href={discoverHref(chip.prompt)}
                  onClick={(e) => {
                    e.preventDefault();
                    applyChip(chip.prompt);
                  }}
                  className="inline-block whitespace-nowrap rounded-full border border-zinc-200 bg-white px-3.5 py-2 text-xs font-semibold text-zinc-700 shadow-sm transition hover:border-blinkit-green/40 hover:bg-blinkit-green/5 hover:text-blinkit-green"
                >
                  {chip.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <label className="sr-only" htmlFor="discover-prompt">
          {DISCOVERY_INPUT_PLACEHOLDER}
        </label>
        <div className="rounded-2xl border border-zinc-100 bg-white p-3 shadow-card">
          <textarea
            id="discover-prompt"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={DISCOVERY_INPUT_PLACEHOLDER}
            rows={3}
            className="w-full resize-none border-0 bg-transparent text-sm leading-relaxed text-zinc-800 placeholder:text-zinc-400 focus:outline-none focus:ring-0"
            autoComplete="off"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submitFromKeyboard();
              }
            }}
          />
          <div className="mt-1 flex justify-end">
            <button
              type="submit"
              disabled={searching}
              className="inline-flex items-center gap-1.5 rounded-xl bg-blinkit-green px-4 py-2.5 text-sm font-bold text-white shadow-md transition hover:bg-blinkit-green-dark disabled:opacity-70 active:scale-[0.98]"
            >
              {searching ? (
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              ) : (
                <Sparkles className="h-4 w-4" aria-hidden />
              )}
              Discover
            </button>
          </div>
        </div>
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
