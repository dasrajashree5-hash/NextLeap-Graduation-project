# Review analysis

Covers preprocessing (Phase 3), LLM analysis, clustering, and insights (Phase 4).

---

## Preprocessing (Phase 3)

### Cleaning

1. Strip HTML tags (preserve inner text).
2. Remove ASCII control characters except newline/tab.
3. Unicode normalize to **NFKC** (emoji preserved).
4. Collapse repeated whitespace to a single space.

Output is stored in `reviews.clean_text` (original kept in `raw_text`).

### Spam and noise filters

A review is marked `is_spam=true` when any rule matches:

| Rule | Condition |
|------|-----------|
| Empty after clean | No usable text |
| Rating-only | Fewer than 3 tokens and no letters |
| Single token | One word only (unless ≥ 8 chars) |
| Repeated characters | Same character > 60% of string |
| URL-heavy | URLs > 30% of tokens |
| Promotional | ≥ 3 promo keywords (offer, discount, click, subscribe, …) |

Spam rows are still version-stamped but **not embedded**.

### Deduplication

**Pass 1 — exact:** SHA-256 of normalized clean text (`dedupe_hash`). If another review already owns the hash, `is_duplicate=true`.

**Pass 2 — near:** MinHash LSH (128 permutations, threshold 0.95). Near-duplicates are marked duplicate; the earliest review id is kept as canonical.

### Language and translation

- Detector: `langdetect` with probability when available → `language`, `language_confidence`.
- **English (`en`):** no translation; analysis text = `clean_text`.
- **Hinglish heuristic:** mixed Latin + Indic scripts, or Hindi detected with mostly Latin letters → `prompts/hinglish_translate.v1.txt`.
- **Other non-English:** `prompts/translate.v1.txt` via Groq.

Original text remains in `clean_text`; English translation in `translated_text`.

### Tokenisation

- `token_count` = whitespace token count on text used for embedding (translation if present, else clean).
- `needs_chunking=true` when `token_count > 400` or length > 2000 characters (approx. context budget guard).

### Embeddings

- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Store: ChromaDB collection `blinkit_reviews`, metadata `{review_id, source_id, language}`
- Relational pointer: `embeddings.vector_ref` = `chroma:blinkit_reviews:{review_id}`

### Idempotency

`preprocessing_version` (currently **`1.0.0`**) is set when a row completes the pipeline.

`POST /api/pipeline/preprocess` only selects rows where `preprocessing_version` is null or ≠ current version.

Re-run with no changes → **processed: 0**.

---

## LLM analysis (Phase 4)

### Client

All Groq calls go through `LLMClient` (`backend/app/llm/`):

- Async batching with concurrency limit
- Exponential backoff on HTTP 429 and 5xx
- Token accounting and estimated USD cost per run
- Response cache keyed on `(prompt_version_hash, input_hash)`
- Hard **per-run cost ceiling** (`LLM_RUN_COST_CEILING_USD`)

Translation (Phase 3) uses the same client via the synchronous `complete()` wrapper.

### Structured output

Every analysis prompt must return JSON validated against a Pydantic schema. Flow:

1. Parse JSON from the model response (strip fences if present).
2. Validate with Pydantic.
3. On failure → one **repair** call (`json_repair.v1.txt`) with the invalid payload.
4. Still invalid → row marked `analysis_failed=true`; nothing is coerced into the DB.

Each stored row records `model_version` and `prompt_version`.

### Per-review consolidated extraction

Single call (`review_analysis.v1.txt`) per eligible review:

| Field | Description |
|-------|-------------|
| `sentiment` | positive / neutral / negative |
| `sentiment_intensity` | 0–1 |
| `emotion` | primary emotion label |
| `complaint_category` | mapped taxonomy category when applicable |
| `motivation` | why the user engaged |
| `unmet_need` | gap or frustration |
| `jtbd` | job-to-be-done statement |
| `shopping_behaviour` | habit / mission / browse / replenishment / … |
| `customer_segment` | inferred segment label |

### Discovery-specific extraction

Same call includes a `discovery` object:

| Field | Description |
|-------|-------------|
| `mentions_non_grocery_category` | user discusses categories beyond core groceries |
| `named_categories` | explicit category names |
| `discovery_barriers` | subset of: awareness, trust, price, search, quality_doubt, habit |
| `latent_cross_category_intent` | implied interest in adjacent categories |
| `cross_category_detail` | short explanation |

Stored in `analyses.discovery_json`.

### Analysis idempotency

`analysis_version` (currently **`1.0.0`**) on `reviews`.

`POST /api/pipeline/analyze` selects embedded, non-spam, non-duplicate reviews missing the current version (unless `force=true`).

---

## Clustering

1. Load embedding vectors from ChromaDB for eligible reviews.
2. **UMAP** reduce to 5 dimensions (`n_neighbors=15`, `min_dist=0.1`).
3. **HDBSCAN** cluster (`min_cluster_size=5`, `min_samples=3`).
4. For each cluster (label ≠ −1), take the **10 reviews closest to the centroid** (in original embedding space).
5. LLM labels the cluster (`cluster_label.v1.txt`) → `themes` row + `clusters` row.
6. Assign `review_themes` for cluster members with confidence from membership probability when available.

### Theme taxonomy

Labels must map to one of:

Category Discovery, Shopping Habit, Price, Search, Recommendations, Trust, Delivery, Availability, Subscription, Coupons

---

## Insights

### Generation

`insight_generation.v1.txt` aggregates each theme cluster (label, description, sample reviews, analysis summaries) and returns a JSON array of insight objects.

**Required fields** (all must be present or the insight is dropped):

- problem, evidence, frequency, example_review_ids, customer_segment, business_impact, opportunity, confidence_score (initial LLM estimate — overwritten by formula)

Every `example_review_ids` entry must exist in the database; uncitable insights are discarded.

### Confidence score (explainable formula)

Not an LLM guess. Weighted sum stored in `confidence_score` with breakdown in `confidence_breakdown`:

| Component | Weight | Computation |
|-----------|--------|-------------|
| Volume | 0.25 | `min(1, log10(frequency+1) / 2)` |
| Cross-source | 0.20 | distinct `source_id` count among cited reviews / max(1, num_sources_in_db) |
| Coherence | 0.20 | cluster `coherence_score` or 0.5 default |
| Sentiment consistency | 0.20 | 1 − (entropy of sentiment labels in cited set) |
| Recency | 0.15 | mean recency of cited `posted_at` vs newest review in corpus |

### Ranking

`rank_score = confidence_score × business_impact_weight`

`business_impact_weight` is derived from keyword heuristics on `business_impact` (north-star / discovery / retention language scores higher). Used to sort the opportunity dashboard.

### Cross-source triangulation

For each insight, compare sentiment and theme agreement across source types (Play Store, App Store, csv, …):

| Agreement | Rule |
|-----------|------|
| `high_confidence` | ≥3 sources and ≥70% sentiment agreement |
| `consistent` | ≥2 sources and ≥55% agreement |
| `weak` | single source or low agreement |
| `contradicting` | ≥2 sources and <40% agreement |

Stored in `validations` with `source_type=cross_source`.

---

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/pipeline/preprocess` | Batch preprocess + embed |
| `GET` | `/api/pipeline/status` | Preprocess pending counts |
| `POST` | `/api/pipeline/analyze` | Per-review LLM analysis |
| `POST` | `/api/pipeline/cluster` | UMAP + HDBSCAN + cluster labels |
| `POST` | `/api/pipeline/insights` | Generate insights, score, rank, triangulate |
| `GET` | `/api/pipeline/analysis-status` | Analysis / cluster / insight counts |
| `GET` | `/api/insights` | Ranked insight list |
| `GET` | `/api/insights/{id}` | Single insight with validation |
| `GET` | `/api/themes` | Theme distribution |

Query/body: `limit` (default 100 for analyze), `force` (reprocess).

---

## Prompt files

Versioned as `backend/app/prompts/<name>.v<N>.txt` with a YAML front matter block:

```yaml
---
model: llama-3.3-70b-versatile
schema: ReviewAnalysisOutput
---
```

Golden-set examples live in `backend/tests/fixtures/prompt_golden/` (prompt evaluation).
