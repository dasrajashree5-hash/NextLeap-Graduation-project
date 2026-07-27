# Implementation Plan

**Project:** AI-Powered Product Discovery Engine for Blinkit
**Companion doc:** [`problemstatement.md`](./problemstatement.md)

---

## 1. Purpose of This Document

This plan converts the problem statement into a buildable, phase-by-phase sequence. Each phase is independently shippable, has explicit deliverables, and ends with acceptance criteria that must pass before the next phase begins.

Development follows a **documentation-first** workflow: the relevant doc in `docs/` is written or updated *before* the code for that phase.

---

## 2. Technology Decisions

These are locked in so that no phase stalls on tooling debates.

| Layer | Choice | Rationale |
|-------|--------|-----------|
| LLM provider | **Groq** (`llama-3.3-70b-versatile`) | Required by the brief; fast and low cost for high-volume review analysis |
| Backend | **FastAPI** (Python 3.11+) | Async, native Pydantic validation, good fit for LLM pipelines |
| Embeddings | **sentence-transformers** (`all-MiniLM-L6-v2`) | Runs locally, no per-call cost, sufficient quality for review clustering |
| Vector store | **ChromaDB** locally, **Supabase pgvector** in production | Zero-setup for development, managed for deploy |
| Relational DB | **SQLite** locally, **PostgreSQL / Supabase** in production | Same SQLAlchemy models for both |
| Clustering | **HDBSCAN** + **UMAP** | Density-based, no need to pre-specify cluster count |
| Frontend | **Next.js 14** (App Router), **Tailwind**, **ShadCN**, **Framer Motion**, **Recharts** | Portfolio-quality dashboard |
| Fallback frontend | **Streamlit** | Case 1 single-service deployment |
| Deployment | Vercel (frontend), Railway or Render (backend), Supabase (DB + vectors) | Free tiers, matches the brief |
| Testing | **pytest**, **Vitest**, **Playwright** | Unit, component, and end-to-end coverage |

See [testing-strategy.md](./testing-strategy.md) for levels, golden-set policy, and CI commands.

### LLM abstraction rule

All model calls go through a single `LLMClient` interface. Groq is the default implementation; swapping in another provider must require no changes outside `backend/app/llm/`.

---

## 3. Target Repository Structure

```
blinkit-discovery-engine/
├── docs/
│   ├── problemStatement.md
│   ├── context.md
│   ├── architecture.md
│   ├── implementation-plan.md
│   ├── workflow.md
│   ├── review-analysis.md
│   ├── research-plan.md
│   ├── interview-guide.md
│   ├── survey-plan.md
│   ├── problem-definition.md
│   ├── mvp-design.md
│   ├── deployment-plan.md
│   ├── edge-cases.md
│   └── future-roadmap.md
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entrypoint
│   │   ├── config.py               # Pydantic Settings, env loading
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── api/routes/             # reviews, analysis, insights, research, mvp
│   │   ├── collectors/             # play_store, app_store, csv, json, manual
│   │   ├── preprocessing/          # clean, dedupe, language, translate, tokenize
│   │   ├── embeddings/             # encoder + vector store adapters
│   │   ├── llm/                    # LLMClient, Groq impl, retry, JSON repair
│   │   ├── prompts/                # versioned prompt templates
│   │   ├── analysis/               # themes, sentiment, JTBD, segments
│   │   ├── clustering/             # UMAP + HDBSCAN, cluster labelling
│   │   ├── insights/               # insight generator, confidence scoring
│   │   ├── research/               # interviews, surveys, triangulation
│   │   ├── mvp/                    # discovery recommendation engine
│   │   └── core/                   # logging, errors, cache, rate limiting
│   ├── tests/
│   ├── data/                       # sample CSVs, fixtures
│   └── requirements.txt
├── frontend/
│   ├── app/                        # Next.js routes
│   ├── components/
│   ├── lib/                        # API client, types
│   └── package.json
├── streamlit_app/                  # Case 1 deployment
├── .env.example
├── docker-compose.yml
└── README.md
```

---

## 4. Data Model

Defined once in Phase 1 so every later phase writes against a stable schema.

| Table | Key fields |
|-------|-----------|
| `sources` | `id`, `name`, `type` (play_store / app_store / reddit / interview / survey / csv), `config_json` |
| `reviews` | `id`, `source_id`, `external_id`, `raw_text`, `clean_text`, `rating`, `language`, `translated_text`, `author_hash`, `posted_at`, `is_spam`, `is_duplicate`, `dedupe_hash` |
| `embeddings` | `review_id`, `vector_ref`, `model_name`, `created_at` |
| `themes` | `id`, `label`, `description`, `category` (Discovery / Trust / Price / Search / Delivery / Availability / …), `review_count` |
| `review_themes` | `review_id`, `theme_id`, `confidence` |
| `analyses` | `review_id`, `sentiment`, `emotion`, `jtbd`, `segment`, `unmet_need`, `motivation`, `model_version`, `prompt_version` |
| `clusters` | `id`, `theme_id`, `centroid_ref`, `size`, `coherence_score` |
| `insights` | `id`, `problem`, `evidence`, `frequency`, `example_review_ids`, `customer_segment`, `business_impact`, `opportunity`, `confidence_score`, `validation_status` |
| `interviews` | `id`, `participant_segment`, `transcript`, `notes`, `jtbd`, `pain_points`, `conducted_at` |
| `surveys` | `id`, `question`, `response`, `respondent_segment`, `submitted_at` |
| `validations` | `insight_id`, `source_type`, `agreement` (consistent / contradicting / weak / high_confidence), `notes` |
| `runs` | `id`, `phase`, `status`, `started_at`, `finished_at`, `error`, `cost_estimate` |

Every LLM-written row carries `model_version` and `prompt_version` so results stay reproducible and auditable.

---

## 5. Phase Plan

### Phase 1 — Project Setup

**Docs first:** `context.md`, `architecture.md`, `implementation-plan.md`

**Tasks**

1. Initialise the repository, `.gitignore`, MIT license, and README skeleton.
2. Create the folder structure from section 3.
3. Set up Python 3.11 virtual environment and `requirements.txt`; set up the Next.js app with Tailwind and ShadCN.
4. Build `config.py` on Pydantic Settings, reading `GROQ_API_KEY`, `DATABASE_URL`, `VECTOR_STORE`, `LOG_LEVEL`, `ENVIRONMENT`. Commit `.env.example` and never a real `.env`.
5. Define all SQLAlchemy models from section 4 and wire Alembic migrations.
6. Add `core/logging.py` (structured JSON logs, request IDs) and `core/errors.py` (typed exceptions plus a global FastAPI exception handler).
7. Expose `GET /health` returning database, vector store, and Groq reachability.
8. Add `docker-compose.yml` for Postgres and the backend.

**Acceptance criteria**

- `uvicorn app.main:app` starts clean and `/health` returns all green.
- `alembic upgrade head` creates every table.
- The Next.js dev server renders a styled placeholder dashboard shell.
- No secret values are committed anywhere in the repo.

---

### Phase 2 — Review Collection

**Docs first:** `workflow.md` (ingestion section)

**Tasks**

1. Define a `BaseCollector` abstract class with `fetch(config) -> list[RawReview]` so new sources are drop-in.
2. Implement the Play Store collector using `google-play-scraper`, paginating by app ID, language, and country, with a configurable review cap.
3. Implement the App Store collector using the public RSS reviews endpoint plus `app-store-scraper`.
4. Implement CSV and JSON collectors with column mapping and schema validation, so exported Reddit, Quora, X, or YouTube data can be loaded without new code.
5. Implement manual upload: `POST /api/reviews/upload` accepting a file, and `POST /api/reviews/manual` accepting pasted text.
6. Persist raw payloads before any transformation, so preprocessing can be re-run without re-scraping.
7. Add a `runs` record per ingestion with counts fetched, stored, and skipped.
8. Ship a sample dataset of roughly 500 Blinkit reviews in `backend/data/` so the pipeline is demoable offline.

**Acceptance criteria**

- At least 1,000 real Play Store and App Store reviews ingest end to end.
- Re-running the same ingestion adds zero duplicate rows.
- A malformed CSV produces a clear 422 with per-row errors rather than a 500.
- Adding a new source requires only a new collector file plus registry entry.

---

### Phase 3 — Preprocessing and Embeddings

**Docs first:** `review-analysis.md` (cleaning rules)

**Tasks**

1. Cleaning: strip HTML and control characters, collapse whitespace, normalise Unicode (NFKC), preserve emoji as sentiment signal rather than deleting them.
2. Spam and noise filters: rating-only reviews with no text, single-token reviews, repeated-character strings, URL-heavy promotional text, and near-identical bulk postings.
3. Deduplication in two passes — exact `SHA-256` hash of normalised text, then near-duplicate detection via MinHash or cosine similarity above a 0.95 threshold.
4. Language detection with `langdetect` or `fasttext`; store the ISO code and a confidence value.
5. Translation of non-English reviews to English through Groq, preserving the original text alongside the translation. Hinglish and other transliterated text is routed to a dedicated prompt rather than a generic translator.
6. Tokenisation and length statistics; flag reviews that exceed the model context budget for chunking.
7. Batch embedding generation with `all-MiniLM-L6-v2`, written to ChromaDB with review ID metadata.
8. Idempotent pipeline runner: `POST /api/pipeline/preprocess` processes only rows not yet at the current preprocessing version.

**Acceptance criteria**

- Ten thousand reviews preprocess in under five minutes on a laptop.
- Duplicate rate after processing is under one percent on a manually spot-checked sample.
- Non-English reviews carry both original and translated text.
- Re-running preprocessing is a no-op when nothing has changed.

---

### Phase 4 — LLM Analysis, Clustering, and Insights

**Docs first:** `review-analysis.md` (analysis and scoring), prompt specifications

This is the analytical core of the project and deserves the largest share of the schedule.

**Tasks**

1. Build the Groq `LLMClient`: async batching, exponential backoff on 429 and 5xx, token accounting, response caching keyed on prompt hash plus input hash, and a hard per-run cost ceiling.
2. Enforce structured output — every analysis prompt returns JSON validated against a Pydantic schema, with one repair retry before the row is marked `analysis_failed`. Malformed output is never silently coerced.
3. Per-review extraction in a single consolidated call to limit cost: sentiment (positive / neutral / negative with intensity), emotion, complaint category, motivation, unmet need, job-to-be-done, shopping behaviour, and inferred customer segment.
4. Discovery-specific extraction, which is what separates this project from a generic review analyser: does the review mention a category beyond groceries, does it name a discovery barrier (awareness, trust, price, search, quality doubt, habit), and does it express latent cross-category intent.
5. Clustering: reduce embeddings with UMAP, cluster with HDBSCAN, then have the LLM label each cluster from its ten most representative reviews. Map clusters onto the taxonomy from the brief — Category Discovery, Shopping Habit, Price, Search, Recommendations, Trust, Delivery, Availability, Subscription, Coupons.
6. Insight generator producing every field the brief requires: problem, evidence, frequency, example reviews, customer segment, business impact, potential opportunity, and confidence score.
7. Confidence scoring as a transparent, explainable formula rather than an LLM guess — a weighted combination of supporting review volume, cross-source agreement, cluster coherence, sentiment consistency, and recency, with the component breakdown stored alongside the total.
8. Insight ranking that combines confidence with estimated business impact on the north star metric.
9. Cross-source triangulation labelling each insight consistent, contradicting, weak, or high confidence.

**Prompt management**

Prompts live in versioned files under `backend/app/prompts/` as `<name>.v<N>.txt`, never inline in application code. Each prompt file carries its intended model, expected JSON schema, and a golden-set example. Changing a prompt means adding a new version, not editing history.

**Acceptance criteria**

- One thousand reviews analyse end to end with a failure rate under two percent.
- Clustering yields between eight and twenty coherent themes on the sample dataset, manually judged sensible.
- At least fifteen insights are generated, each with all eight required fields populated.
- Every insight traces back to specific review IDs; nothing is unsourced.
- A blind manual review of ten insights finds no fabricated evidence.

---

### Phase 5 — Research Repository and Validation

**Docs first:** `research-plan.md`, `interview-guide.md`, `survey-plan.md`, `problem-definition.md`

**Tasks**

1. Interview upload accepting transcripts as text, CSV, or plain files, with participant segment metadata.
2. LLM-assisted interview coding: extract pain points, jobs-to-be-done, discovery barriers, and quotes, always with a pointer back to the source transcript span.
3. Survey ingestion with per-question aggregation and segment breakdowns.
4. Affinity mapping: group interview and survey findings into clusters that share the theme taxonomy from Phase 4, so AI and human findings are directly comparable.
5. Triangulation engine comparing each AI insight against interview and survey evidence, classifying it validated, rejected, partially supported, or new discovery — where "new discovery" means something interviews surfaced that reviews never did.
6. Opportunity assessment scoring each validated problem on reach, severity, north star impact, and implementation effort.
7. Generate `problem-definition.md` — the sharpened, evidence-backed problem statement that drives MVP design.
8. Write `interview-guide.md` with a discussion guide of roughly twelve questions targeting discovery barriers, and `survey-plan.md` with the sampling approach and instrument.

**Acceptance criteria**

- Notes from at least five interviews and one survey are stored and coded.
- Every AI insight carries an explicit validation status with cited human evidence.
- At least one assumption is genuinely rejected by interview data, which demonstrates the loop is real rather than confirmatory.
- The top three opportunities are ranked with visible scoring rationale.

---

### Phase 6 — AI-Native MVP, Deployment, and Testing

**Docs first:** `mvp-design.md`, `deployment-plan.md`, `edge-cases.md`

**MVP selection**

The MVP is chosen from the ranked opportunities in Phase 5, not decided up front — that ordering is the point of the project. The default candidate, pending validation, is an **AI Smart Basket Expansion** agent that suggests one adjacent-category item per order with a plain-language reason grounded in a real discovery barrier, since it attacks the north star metric directly at the moment of purchase.

**Tasks**

1. Recommendation engine: given a basket and a customer segment, return adjacent-category suggestions, each with a reason string traceable to an insight ID.
2. Barrier-aware messaging — if the dominant barrier for that segment and category is trust, the copy leads with ratings and returns; if it is awareness, it leads with the use case. This is where research findings become product behaviour.
3. MVP API endpoints plus an evaluation harness measuring suggestion relevance on held-out baskets.
4. Dashboard build-out covering every panel in the brief: review upload, sources, statistics, theme distribution, sentiment charts, opportunity dashboard, customer segments, insight cards, interview repository, survey repository, problem statement, AI recommendations, and MVP demo.
5. Frontend polish: loading skeletons, empty states, error boundaries, Framer Motion transitions, responsive breakpoints, keyboard navigation, and ARIA labelling for accessibility compliance.
6. Streamlit variant for the Case 1 single-service deployment path.
7. Deployment: frontend to Vercel, backend to Railway or Render, database and vectors to Supabase, with environment variables, secret handling, structured production logging, health checks, a GitHub Actions pipeline, and a documented rollback path.
8. Full test suite plus a manual testing checklist.
9. Presentation assets: architecture diagram, workflow diagram, and a demo script.

**Acceptance criteria**

- The deployed public URL loads and runs a full demo on seeded data.
- A cold visitor can upload reviews and reach generated insights without reading any documentation.
- Lighthouse accessibility score is 90 or above.
- CI runs tests on every push and blocks merges on failure.
- A rollback to the previous release is demonstrated once.

---

## 6. Edge Cases to Handle Throughout

These are not deferred to a final hardening pass; each phase handles the cases it introduces, and all of them are documented in `edge-cases.md`.

| Case | Handling |
|------|----------|
| Empty or whitespace-only review | Filtered at preprocessing, counted in run stats, never sent to the LLM |
| Duplicate reviews | Exact hash plus near-duplicate similarity pass |
| Unsupported or transliterated language | Translate via Groq; below a confidence threshold, flag for manual review instead of guessing |
| Hallucinated insights | Every insight must cite review IDs; uncitable claims are dropped, not softened |
| LLM failure or timeout | Retry with backoff, then mark the row failed and continue the batch |
| Missing fields in output | Pydantic validation, one repair retry, then quarantine |
| Corrupted CSV | Row-level validation returning a per-row error report |
| Low-confidence insights | Retained but visually separated in the dashboard, never mixed into headline findings |
| Conflicting themes | Surfaced explicitly as contradictions rather than averaged away |
| API rate limits | Client-side throttling, queueing, and cost ceilings per run |
| Cold start with no data | Seeded sample dataset and clear empty states |

---

## 7. Testing Strategy

| Level | Coverage |
|-------|----------|
| Unit | Cleaning functions, dedupe hashing, confidence formula, collector parsers |
| Integration | Ingest → preprocess → embed → analyse → insight, on a fixed fixture set |
| Prompt evaluation | Golden set of roughly fifty hand-labelled reviews; prompt changes must not regress agreement |
| LLM evaluation | Schema validity rate, hallucination spot-checks, cost and latency per run |
| Performance | Ten thousand review pipeline timing, endpoint p95 latency |
| Edge case | One test per row in the table above |
| Research validation | AI insights versus human interview findings, tracked as an agreement rate |

The prompt golden set matters more than raw code coverage here: it is the only guard against a prompt edit quietly degrading every insight in the system.

---

## 8. Sequencing and Effort

Phases are strictly sequential except for frontend scaffolding, which can proceed in parallel from Phase 2 onward against mocked API responses.

| Phase | Focus | Relative effort |
|-------|-------|-----------------|
| 1 | Project setup | 10% |
| 2 | Review collection | 15% |
| 3 | Preprocessing and embeddings | 15% |
| 4 | LLM analysis and insights | 30% |
| 5 | Research and validation | 15% |
| 6 | MVP, deployment, testing | 15% |

Operational detail, calendar guidance, parallel frontend track, and automated gates: **[sequencing-and-effort.md](./sequencing-and-effort.md)**. API: `GET /api/project/sequencing`, `GET /api/project/phases`. CLI: `backend/scripts/check_phase_gates.py`.

---

## 9. Key Risks

Operational detail, verification commands, and code pointers: **[key-risks.md](./key-risks.md)**. API: `GET /api/project/risks`. CLI: `python scripts/check_phase_gates.py --risks`.

| Risk | Mitigation |
|------|-----------|
| Reviews rarely discuss category discovery directly, so insights stay generic | Add discovery-specific extraction in Phase 4 and treat interviews as the primary source for barrier depth |
| LLM invents plausible-sounding insights | Mandatory review ID citations; uncitable insights are dropped |
| Scraper breakage or rate limiting | CSV and JSON fallback paths plus a committed sample dataset keep the demo alive |
| Prompt drift degrading quality silently | Versioned prompts and a golden evaluation set |
| Cost overrun on large batches | Consolidated per-review calls, response caching, per-run cost ceiling |
| Scope creep across fourteen documents | Documentation-first order and per-phase acceptance gates |

---

## 10. Implementation Prompts

Copy-paste prompts, docs-first checklist, and verification: **[implementation-prompts.md](./implementation-prompts.md)**. API: `GET /api/project/implementation-prompts` (optional `?phase=N`, `?validate=true`). CLI: `python scripts/check_phase_gates.py --prompts`.

Sequential prompts to drive the build, one per phase:

1. **Implement Phase 1** — repository scaffold, config, data models, migrations, logging, error handling, health endpoint.
2. **Implement Phase 2** — collector interface plus Play Store, App Store, CSV, JSON, and manual upload sources with run tracking.
3. **Implement Phase 3** — cleaning, spam filtering, deduplication, language detection, translation, tokenisation, embeddings.
4. **Implement Phase 4** — Groq client, versioned prompts, per-review analysis, clustering, insight generation, confidence scoring, ranking.
5. **Implement Phase 5** — interview and survey repositories, affinity mapping, triangulation, opportunity assessment, problem definition.
6. **Implement Phase 6** — MVP recommendation engine, full dashboard, deployment, and test suite.

Each prompt assumes the corresponding `docs/` file already exists and is current.
