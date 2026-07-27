"use client";

import {
  BarChart3,
  Brain,
  FlaskConical,
  LayoutDashboard,
  Loader2,
  MessageSquare,
  Rocket,
  Upload,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { api, ApiError, getApiBase } from "@/lib/api";

type Tab =
  | "overview"
  | "reviews"
  | "insights"
  | "research"
  | "mvp"
  | "problem";

const nav: { id: Tab; label: string; icon: typeof LayoutDashboard }[] = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "reviews", label: "Reviews", icon: Upload },
  { id: "insights", label: "Insights", icon: Brain },
  { id: "research", label: "Research", icon: MessageSquare },
  { id: "mvp", label: "MVP demo", icon: Rocket },
  { id: "problem", label: "Problem", icon: FlaskConical },
];

const SEGMENTS = [
  "mission_shopper",
  "student",
  "family_stockup",
  "explorer",
  "new_parent",
  "pet_owner",
];

function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded-lg bg-zinc-800/80 ${className}`}
      aria-hidden
    />
  );
}

export default function Dashboard() {
  const [tab, setTab] = useState<Tab>("overview");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [health, setHealth] = useState<string>("—");
  const [reviewTotal, setReviewTotal] = useState<number | null>(null);
  const [analysis, setAnalysis] = useState<{
    themes: number;
    insights: number;
    analyzed_reviews: number;
  } | null>(null);
  const [themes, setThemes] = useState<
    { label: string; category?: string; review_count: number }[]
  >([]);
  const [insights, setInsights] = useState<
    Awaited<ReturnType<typeof api.insights>>
  >([]);
  const [opportunities, setOpportunities] = useState<
    Awaited<ReturnType<typeof api.opportunities>>
  >([]);
  const [mvpReady, setMvpReady] = useState(false);
  const [problemMd, setProblemMd] = useState<string>("");

  const [pasteText, setPasteText] = useState("");
  const [uploadMsg, setUploadMsg] = useState<string | null>(null);

  const [segment, setSegment] = useState("mission_shopper");
  const [basketLines, setBasketLines] = useState("Amul Taaza Milk 1L\nBritannia Brown Bread");
  const [presets, setPresets] = useState<
    { id: string; customer_segment: string; items: { name: string }[] }[]
  >([]);
  const [recommendResult, setRecommendResult] = useState<Awaited<
    ReturnType<typeof api.mvpRecommend>
  > | null>(null);
  const [evalSummary, setEvalSummary] = useState<string | null>(null);
  const [mvpBusy, setMvpBusy] = useState(false);

  const loadCore = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [h, stats, aStatus, th, ins, opp, mvp, problem] = await Promise.all([
        api.health(),
        api.reviewStats(),
        api.analysisStatus(),
        api.themes(),
        api.insights(30),
        api.opportunities().catch(() => []),
        api.mvpStatus(),
        api.problemDefinition().catch(() => ({ markdown: "", path: "" })),
      ]);
      setHealth(h.status);
      setReviewTotal(stats.total_reviews);
      setAnalysis({
        themes: aStatus.themes,
        insights: aStatus.insights,
        analyzed_reviews: aStatus.analyzed_reviews,
      });
      setThemes(th);
      setInsights(ins);
      setOpportunities(opp);
      setMvpReady(mvp.ready);
      setProblemMd(problem.markdown || "_Generate via API or run research seed._");
    } catch (e) {
      setError(
        e instanceof ApiError
          ? `${e.message} (is the backend running at ${getApiBase()}?)`
          : "Failed to load dashboard data"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCore();
  }, [loadCore]);

  useEffect(() => {
    if (tab !== "mvp") return;
    api.mvpEvalBaskets().then(setPresets).catch(() => setPresets([]));
  }, [tab]);

  async function submitManualReviews() {
    const lines = pasteText
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean);
    if (!lines.length) return;
    setUploadMsg(null);
    try {
      const res = await api.manualReviews(
        `dashboard_${Date.now()}`,
        lines.map((text) => ({ text }))
      );
      setUploadMsg(`Stored ${res.stats.stored ?? lines.length} review(s). Run preprocess in API to analyze.`);
      setPasteText("");
      await loadCore();
    } catch (e) {
      setUploadMsg(e instanceof ApiError ? e.message : "Upload failed");
    }
  }

  async function runRecommend() {
    setMvpBusy(true);
    setRecommendResult(null);
    setEvalSummary(null);
    try {
      const basket_items = basketLines
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean)
        .map((name) => ({ name }));
      const res = await api.mvpRecommend({
        basket_items,
        customer_segment: segment,
        limit: 1,
      });
      setRecommendResult(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Recommend failed");
    } finally {
      setMvpBusy(false);
    }
  }

  async function runEval() {
    setMvpBusy(true);
    setEvalSummary(null);
    try {
      const res = await api.mvpEvaluate();
      setEvalSummary(
        `Pass rate ${(res.summary.pass_rate * 100).toFixed(0)}% · category hit ${(res.summary.category_hit_rate * 100).toFixed(0)}% · ${res.summary.passed_cases}/${res.summary.total_cases} cases`
      );
    } catch (e) {
      setEvalSummary(e instanceof ApiError ? e.message : "Eval failed");
    } finally {
      setMvpBusy(false);
    }
  }

  async function seedResearch() {
    try {
      await api.seedResearch();
      await loadCore();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Seed failed");
    }
  }

  return (
    <div className="flex min-h-screen">
      <aside
        className="hidden w-64 flex-shrink-0 border-r border-zinc-800 bg-zinc-950 p-6 md:block"
        aria-label="Main navigation"
      >
        <div className="mb-8">
          <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
            Blinkit
          </p>
          <h1 className="text-lg font-semibold text-blinkit">Discovery Engine</h1>
        </div>
        <nav className="space-y-1" role="tablist" aria-orientation="vertical">
          {nav.map((item) => (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={tab === item.id}
              onClick={() => setTab(item.id)}
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                tab === item.id
                  ? "bg-zinc-900 text-blinkit"
                  : "text-zinc-400 hover:bg-zinc-900/50"
              }`}
            >
              <item.icon className="h-4 w-4" aria-hidden />
              {item.label}
            </button>
          ))}
        </nav>
        <p className="mt-10 text-xs text-zinc-600">Phase 6 · MVP live</p>
      </aside>

      <main className="flex-1 p-4 md:p-10">
        <div className="mb-6 flex gap-2 overflow-x-auto md:hidden" role="tablist">
          {nav.map((item) => (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={tab === item.id}
              onClick={() => setTab(item.id)}
              className={`whitespace-nowrap rounded-full px-3 py-1.5 text-xs ${
                tab === item.id ? "bg-blinkit/20 text-blinkit" : "bg-zinc-900 text-zinc-400"
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>

        {error && (
          <div
            className="mb-6 rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-200"
            role="alert"
          >
            {error}
            <button
              type="button"
              className="ml-3 underline"
              onClick={() => {
                setError(null);
                loadCore();
              }}
            >
              Retry
            </button>
          </div>
        )}

        {tab === "overview" && (
          <section aria-labelledby="overview-heading">
            <header className="mb-8">
              <h2 id="overview-heading" className="text-2xl font-semibold">
                Overview
              </h2>
              <p className="mt-1 text-sm text-zinc-400">
                API: <code className="text-xs">{getApiBase()}</code>
              </p>
            </header>
            {loading ? (
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {[1, 2, 3, 4].map((i) => (
                  <Skeleton key={i} className="h-28" />
                ))}
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {[
                  { label: "Backend health", value: health },
                  { label: "Reviews ingested", value: reviewTotal ?? "—" },
                  { label: "Themes", value: analysis?.themes ?? "—" },
                  { label: "Insights ranked", value: analysis?.insights ?? "—" },
                ].map((c) => (
                  <div
                    key={c.label}
                    className="rounded-xl border border-zinc-800 bg-[var(--card)] p-5"
                  >
                    <p className="text-xs text-zinc-500">{c.label}</p>
                    <p className="mt-2 text-3xl font-semibold tabular-nums">{c.value}</p>
                  </div>
                ))}
              </div>
            )}
            <div className="mt-8 rounded-xl border border-zinc-800 bg-[var(--card)] p-6">
              <h3 className="flex items-center gap-2 font-medium">
                <BarChart3 className="h-4 w-4 text-blinkit" aria-hidden />
                Theme distribution
              </h3>
              {loading ? (
                <Skeleton className="mt-4 h-32" />
              ) : themes.length === 0 ? (
                <p className="mt-4 text-sm text-zinc-500">No themes yet — run clustering pipeline.</p>
              ) : (
                <ul className="mt-4 space-y-2">
                  {themes.slice(0, 8).map((t) => (
                    <li key={t.label} className="flex justify-between text-sm">
                      <span>{t.category || t.label}</span>
                      <span className="tabular-nums text-zinc-500">{t.review_count}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>
        )}

        {tab === "reviews" && (
          <section aria-labelledby="reviews-heading">
            <h2 id="reviews-heading" className="mb-4 text-2xl font-semibold">
              Review upload
            </h2>
            <p className="mb-4 text-sm text-zinc-400">
              Paste one review per line for a quick cold-start demo.
            </p>
            <label className="sr-only" htmlFor="review-paste">
              Paste reviews
            </label>
            <textarea
              id="review-paste"
              rows={8}
              value={pasteText}
              onChange={(e) => setPasteText(e.target.value)}
              placeholder="Great app but I never browse pet care..."
              className="w-full rounded-lg border border-zinc-700 bg-zinc-950 p-3 text-sm focus:border-blinkit focus:outline-none focus:ring-1 focus:ring-blinkit"
            />
            <button
              type="button"
              onClick={submitManualReviews}
              className="mt-3 rounded-lg bg-blinkit px-4 py-2 text-sm font-medium text-black hover:opacity-90"
            >
              Submit reviews
            </button>
            {uploadMsg && (
              <p className="mt-2 text-sm text-zinc-400" role="status">
                {uploadMsg}
              </p>
            )}
          </section>
        )}

        {tab === "insights" && (
          <section aria-labelledby="insights-heading">
            <h2 id="insights-heading" className="mb-6 text-2xl font-semibold">
              Insight cards
            </h2>
            {loading ? (
              <Skeleton className="h-40" />
            ) : insights.length === 0 ? (
              <p className="text-sm text-zinc-500">No insights — run analysis pipeline on backend.</p>
            ) : (
              <ul className="space-y-4">
                {insights.map((ins) => {
                  const low =
                    (ins.confidence_score ?? 1) < 0.5 ||
                    ins.validation_status === "rejected";
                  return (
                    <li
                      key={ins.id}
                      className={`rounded-xl border p-5 ${
                        low ? "border-zinc-700 bg-zinc-950/80" : "border-zinc-800 bg-[var(--card)]"
                      }`}
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs text-zinc-500">#{ins.id}</span>
                        {ins.validation_status && (
                          <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-xs">
                            {ins.validation_status}
                          </span>
                        )}
                        {low && (
                          <span className="rounded-full border border-amber-800/50 px-2 py-0.5 text-xs text-amber-200">
                            low confidence
                          </span>
                        )}
                      </div>
                      <p className="mt-2 font-medium">{ins.problem}</p>
                      {ins.evidence && (
                        <p className="mt-2 line-clamp-3 text-sm text-zinc-400">{ins.evidence}</p>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </section>
        )}

        {tab === "research" && (
          <section aria-labelledby="research-heading">
            <h2 id="research-heading" className="mb-4 text-2xl font-semibold">
              Research & opportunities
            </h2>
            <button
              type="button"
              onClick={seedResearch}
              className="mb-6 rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-900"
            >
              Seed interviews & surveys
            </button>
            {opportunities.length === 0 ? (
              <p className="text-sm text-zinc-500">
                No opportunities scored — POST /api/research/opportunities on backend.
              </p>
            ) : (
              <ol className="space-y-3">
                {opportunities.slice(0, 5).map((o) => (
                  <li
                    key={o.rank}
                    className="rounded-xl border border-zinc-800 bg-[var(--card)] p-4"
                  >
                    <span className="text-xs text-blinkit">#{o.rank}</span>
                    <p className="mt-1 font-medium">{o.title}</p>
                    <p className="mt-1 text-xs text-zinc-500">
                      Score {o.total_score.toFixed(2)} · reach {o.reach_score} · north star{" "}
                      {o.north_star_score}
                    </p>
                  </li>
                ))}
              </ol>
            )}
          </section>
        )}

        {tab === "mvp" && (
          <section aria-labelledby="mvp-heading">
            <h2 id="mvp-heading" className="text-2xl font-semibold">
              AI Smart Basket Expansion
            </h2>
            <p className="mt-1 text-sm text-zinc-400">
              Adjacent-category suggestion with barrier-aware copy tied to insight IDs.
            </p>
            {!mvpReady && !loading && (
              <p className="mt-4 rounded-lg border border-amber-900/40 bg-amber-950/20 p-3 text-sm">
                MVP not ready — generate insights first (analysis pipeline).
              </p>
            )}
            <div className="mt-6 grid gap-6 lg:grid-cols-2">
              <div className="rounded-xl border border-zinc-800 bg-[var(--card)] p-5">
                <label className="block text-sm font-medium" htmlFor="segment">
                  Customer segment
                </label>
                <select
                  id="segment"
                  value={segment}
                  onChange={(e) => setSegment(e.target.value)}
                  className="mt-2 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm"
                >
                  {SEGMENTS.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
                <label className="mt-4 block text-sm font-medium" htmlFor="basket">
                  Basket items (one per line)
                </label>
                <textarea
                  id="basket"
                  rows={5}
                  value={basketLines}
                  onChange={(e) => setBasketLines(e.target.value)}
                  className="mt-2 w-full rounded-lg border border-zinc-700 bg-zinc-950 p-3 text-sm"
                />
                {presets.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {presets.slice(0, 4).map((p) => (
                      <button
                        key={p.id}
                        type="button"
                        className="rounded-full border border-zinc-700 px-2 py-1 text-xs hover:border-blinkit"
                        onClick={() => {
                          setSegment(p.customer_segment);
                          setBasketLines(p.items.map((i) => i.name).join("\n"));
                        }}
                      >
                        {p.id}
                      </button>
                    ))}
                  </div>
                )}
                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    type="button"
                    disabled={mvpBusy || !mvpReady}
                    onClick={runRecommend}
                    className="inline-flex items-center gap-2 rounded-lg bg-blinkit px-4 py-2 text-sm font-medium text-black disabled:opacity-50"
                  >
                    {mvpBusy && <Loader2 className="h-4 w-4 animate-spin" aria-hidden />}
                    Get suggestion
                  </button>
                  <button
                    type="button"
                    disabled={mvpBusy || !mvpReady}
                    onClick={runEval}
                    className="rounded-lg border border-zinc-600 px-4 py-2 text-sm disabled:opacity-50"
                  >
                    Run eval harness
                  </button>
                </div>
                {evalSummary && (
                  <p className="mt-3 text-sm text-zinc-400" role="status">
                    {evalSummary}
                  </p>
                )}
              </div>
              <div className="rounded-xl border border-dashed border-zinc-700 bg-zinc-950/50 p-5">
                <h3 className="font-medium">Suggestion</h3>
                {!recommendResult?.suggestions?.length ? (
                  <p className="mt-4 text-sm text-zinc-500">
                    Run a recommendation to see product, barrier, and cited insight.
                  </p>
                ) : (
                  recommendResult.suggestions.map((s) => (
                    <div key={s.product_name} className="mt-4 space-y-2 text-sm">
                      <p className="text-lg font-semibold text-blinkit">{s.product_name}</p>
                      <p className="text-zinc-400">
                        {s.category} · ₹{s.price_inr} · {s.rating}/5 · barrier:{" "}
                        <strong>{s.dominant_barrier}</strong>
                      </p>
                      <p className="leading-relaxed">{s.message}</p>
                      <p className="text-xs text-zinc-500">
                        Insight #{s.insight_id}
                        {s.validation_status ? ` · ${s.validation_status}` : ""}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </section>
        )}

        {tab === "problem" && (
          <section aria-labelledby="problem-heading">
            <h2 id="problem-heading" className="mb-4 text-2xl font-semibold">
              Problem statement
            </h2>
            <article className="prose prose-invert max-w-none rounded-xl border border-zinc-800 bg-[var(--card)] p-6 text-sm">
              <pre className="whitespace-pre-wrap font-sans text-zinc-300">{problemMd}</pre>
            </article>
          </section>
        )}
      </main>
    </div>
  );
}
