"use client";

import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";

export default function DiscoverView() {
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState<Awaited<ReturnType<typeof api.insights>>>([]);
  const [themes, setThemes] = useState<Awaited<ReturnType<typeof api.themes>>>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [ins, th] = await Promise.all([api.insights(12), api.themes()]);
      setInsights(ins);
      setThemes(th.slice(0, 6));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load discovery data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-5 px-4 pb-4">
      <div>
        <h2 className="text-lg font-bold text-zinc-900">Why users don&apos;t explore</h2>
        <p className="mt-1 text-xs text-zinc-500">
          AI-synthesized barriers from Play Store, App Store, and research — powering cart
          suggestions.
        </p>
      </div>

      {error && (
        <div className="rounded-xl bg-red-50 p-3 text-xs text-red-700" role="alert">
          {error}
          <button type="button" className="ml-2 underline" onClick={load}>
            Retry
          </button>
        </div>
      )}

      <section aria-labelledby="theme-chips">
        <h3 id="theme-chips" className="text-sm font-bold text-zinc-800">
          Top themes
        </h3>
        {loading ? (
          <div className="mt-2 h-8 animate-pulse rounded-lg bg-zinc-200" />
        ) : themes.length === 0 ? (
          <p className="mt-2 text-xs text-zinc-500">No themes yet.</p>
        ) : (
          <ul className="mt-2 flex flex-wrap gap-2">
            {themes.map((t) => (
              <li
                key={t.id}
                className="rounded-full border border-zinc-200 bg-white px-3 py-1 text-[11px] font-medium text-zinc-700 shadow-sm"
              >
                {t.category || t.label}{" "}
                <span className="text-zinc-400">({t.review_count})</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="insight-feed">
        <h3 id="insight-feed" className="text-sm font-bold text-zinc-800">
          Insight feed
        </h3>
        {loading ? (
          <ul className="mt-3 space-y-3">
            {[1, 2, 3].map((i) => (
              <li key={i} className="h-24 animate-pulse rounded-2xl bg-zinc-200" />
            ))}
          </ul>
        ) : insights.length === 0 ? (
          <p className="mt-3 text-sm text-zinc-500">
            No insights yet — ingest reviews and run analysis on the backend.
          </p>
        ) : (
          <ul className="mt-3 space-y-3">
            {insights.map((ins) => {
              const low = (ins.confidence_score ?? 1) < 0.5;
              return (
                <li
                  key={ins.id}
                  className={`rounded-2xl border p-4 shadow-sm ${
                    low ? "border-zinc-200 bg-zinc-50" : "border-zinc-100 bg-white"
                  }`}
                >
                  <div className="flex flex-wrap gap-2">
                    {ins.validation_status && (
                      <span className="rounded-full bg-blinkit-green/10 px-2 py-0.5 text-[10px] font-semibold text-blinkit-green">
                        {ins.validation_status}
                      </span>
                    )}
                    {low && (
                      <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] text-amber-800">
                        lower confidence
                      </span>
                    )}
                  </div>
                  <p className="mt-2 text-sm font-semibold text-zinc-900">{ins.problem}</p>
                  {ins.evidence && (
                    <p className="mt-1 line-clamp-3 text-xs leading-relaxed text-zinc-600">
                      {ins.evidence}
                    </p>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
}
