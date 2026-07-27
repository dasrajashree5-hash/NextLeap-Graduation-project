# Implementation Prompts

**Project:** AI-Powered Product Discovery Engine for Blinkit  
**Source:** [implementation-plan.md](./implementation-plan.md) §10

Sequential prompts to drive the build, **one per phase**. Use them in Cursor (or any agent) after the phase’s **docs-first** files are written and current.

---

## Policy

Each prompt assumes the listed `docs/` files exist and match what you are about to build. Do not skip the documentation step for that phase.

---

## Prompts

### Phase 1 — Project setup

**Docs first:** `context.md`, `architecture.md`, `implementation-plan.md`

```
@docs/implementation-plan.md Implement Phase 1 — repository scaffold, config, data models, migrations, logging, error handling, health endpoint.
```

**Scope:** Initialise repo structure, Pydantic settings, SQLAlchemy models + Alembic, structured logging and errors, `GET /health`, Docker Compose for Postgres/backend.

---

### Phase 2 — Review collection

**Docs first:** `workflow.md`

```
@docs/implementation-plan.md Implement Phase 2 — collector interface plus Play Store, App Store, CSV, JSON, and manual upload sources with run tracking.
```

**Scope:** `BaseCollector`, store scrapers, file ingest with row-level validation, manual upload API, `runs` records, offline sample corpus.

---

### Phase 3 — Preprocessing and embeddings

**Docs first:** `review-analysis.md` (cleaning rules)

```
@docs/implementation-plan.md Implement Phase 3 — cleaning, spam filtering, deduplication, language detection, translation, tokenisation, embeddings.
```

**Scope:** Idempotent preprocess pipeline, ChromaDB embeddings, Groq translation for non-English text, `POST /api/pipeline/preprocess`.

---

### Phase 4 — LLM analysis and insights

**Docs first:** `review-analysis.md` (analysis and prompts)

```
@docs/implementation-plan.md Implement Phase 4 — Groq client, versioned prompts, per-review analysis, clustering, insight generation, confidence scoring, ranking.
```

**Scope:** `LLMClient`, versioned prompts under `app/prompts/`, UMAP + HDBSCAN, insight generator with citation enforcement and confidence formula.

---

### Phase 5 — Research and validation

**Docs first:** `research-plan.md`, `interview-guide.md`, `survey-plan.md`, `problem-definition.md`

```
@docs/implementation-plan.md Implement Phase 5 — interview and survey repositories, affinity mapping, triangulation, opportunity assessment, problem definition.
```

**Scope:** Interview/survey ingest, LLM coding with transcript spans, triangulation vs AI insights, ranked opportunities, generated problem definition doc.

---

### Phase 6 — MVP, deployment, and testing

**Docs first:** `mvp-design.md`, `deployment-plan.md`, `edge-cases.md`, `testing-strategy.md`

```
@docs/implementation-plan.md Implement Phase 6 — MVP recommendation engine, full dashboard, deployment, and test suite.
```

**Scope:** Smart Basket Expansion API, Next.js dashboard panels, Streamlit Case 1 app, CI, deployment docs, manual testing checklist.

---

## Verification

### API

```bash
curl http://127.0.0.1:8000/api/project/implementation-prompts
curl "http://127.0.0.1:8000/api/project/implementation-prompts?phase=4"
```

### CLI

```bash
cd backend
python scripts/check_phase_gates.py --prompts
python scripts/check_phase_gates.py --prompts --fail-on-incomplete
```

### Tests

```bash
cd backend && pytest tests/test_implementation_prompts.py -q
```

---

## Related

- Phase gates: [sequencing-and-effort.md](./sequencing-and-effort.md)  
- Key risks: [key-risks.md](./key-risks.md)  
- Acceptance detail: [implementation-plan.md](./implementation-plan.md) §5
