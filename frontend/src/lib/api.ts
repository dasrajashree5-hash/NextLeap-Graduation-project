const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    cache: "no-store",
  });
  const text = await res.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }
  if (!res.ok) {
    const msg =
      typeof data === "object" &&
      data &&
      "error" in data &&
      typeof (data as { error: { message?: string } }).error?.message === "string"
        ? (data as { error: { message: string } }).error.message
        : res.statusText;
    throw new ApiError(msg, res.status, data);
  }
  return data as T;
}

export function getApiBase(): string {
  return API_BASE;
}

export const api = {
  health: () => request<{ status: string; checks: Record<string, string> }>("/api/health"),
  reviewStats: () =>
    request<{ total_reviews: number; by_source: { source: string; count: number }[] }>(
      "/api/reviews/stats"
    ),
  analysisStatus: () =>
    request<{
      analysis_version: string;
      pending_analysis: number;
      analyzed_reviews: number;
      themes: number;
      insights: number;
    }>("/api/pipeline/analysis-status"),
  insights: (limit = 20) =>
    request<
      {
        id: number;
        problem: string;
        evidence?: string;
        confidence_score?: number;
        validation_status?: string;
        rank_score?: number;
        customer_segment?: string;
      }[]
    >(`/api/insights?limit=${limit}`),
  themes: () =>
    request<
      { id: number; label: string; category?: string; review_count: number }[]
    >("/api/themes"),
  opportunities: () =>
    request<
      {
        rank: number;
        title: string;
        total_score: number;
        reach_score: number;
        severity_score: number;
        north_star_score: number;
        effort_score: number;
      }[]
    >("/api/research/opportunities"),
  seedResearch: () =>
    request<{ interviews_loaded: number; survey_rows_loaded: number }>(
      "/api/research/seed?code=true",
      { method: "POST" }
    ),
  problemDefinition: () =>
    request<{ path: string; markdown: string }>("/api/research/problem-definition"),
  mvpStatus: () =>
    request<{
      ready: boolean;
      insight_count: number;
      opportunity_count: number;
      eval_basket_count: number;
    }>("/api/mvp/status"),
  mvpEvalBaskets: () =>
    request<{ id: string; customer_segment: string; items: { name: string }[] }[]>(
      "/api/mvp/eval-baskets"
    ),
  mvpRecommend: (body: {
    basket_items: { name: string; category?: string }[];
    customer_segment: string;
    limit?: number;
  }) =>
    request<{
      basket_categories: string[];
      suggestions: {
        product_name: string;
        category: string;
        message: string;
        insight_id: number;
        dominant_barrier: string;
        validation_status?: string;
        price_inr: number;
        rating: number;
      }[];
    }>("/api/mvp/recommend", { method: "POST", body: JSON.stringify(body) }),
  mvpEvaluate: () =>
    request<{
      summary: {
        pass_rate: number;
        category_hit_rate: number;
        total_cases: number;
        passed_cases: number;
      };
      results: { case_id: string; passed: boolean }[];
    }>("/api/mvp/evaluate", { method: "POST", body: JSON.stringify({ limit: 1 }) }),
  manualReviews: (sourceName: string, reviews: { text: string }[]) =>
    request<{ run_id: number; stats: Record<string, number> }>("/api/reviews/manual", {
      method: "POST",
      body: JSON.stringify({ source_name: sourceName, reviews }),
    }),
};
