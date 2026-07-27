# Testing Strategy

Companion to [implementation-plan.md](./implementation-plan.md) §7. Defines how quality is enforced across the Blinkit Discovery Engine.

## Tooling

| Layer | Tool | Location |
|-------|------|----------|
| Backend unit / integration | **pytest** | `backend/tests/` |
| Prompt regression | Golden set + agreement scorer | `backend/tests/fixtures/prompt_golden/` |
| Frontend components / lib | **Vitest** | `frontend/**/*.test.ts` |
| End-to-end smoke | **Playwright** | `frontend/e2e/` |
| Manual QA | Checklist | [manual-testing-checklist.md](./manual-testing-checklist.md) |
| CI | GitHub Actions | `.github/workflows/ci.yml` |

## Test levels

### Unit

- **Preprocessing:** `clean_text`, spam heuristics, exact/near dedupe (`test_preprocess_unit.py`, `test_edge_cases.py`).
- **Collectors:** CSV/JSON parsers and row errors (`test_collectors_unit.py`, `test_reviews.py`).
- **Scoring:** Confidence formula components and ranking (`test_confidence_unit.py`, `test_analysis.py`).
- **LLM helpers:** JSON extraction and Pydantic validation (`test_llm_eval.py`).

### Integration

Fixed fixture CSV under `backend/tests/fixtures/prompt_golden/integration_reviews.csv` drives:

**ingest → preprocess → analyze (mocked LLM) → insight citation rules**

See `test_integration_pipeline.py`.

### Prompt evaluation

Roughly **50 hand-labelled reviews** live in `review_golden_set.json`. Each row includes:

- `expected` — human labels for regression (sentiment, barriers, discovery flags).
- `baseline_output` — last accepted model-shaped JSON (schema guard + agreement floor).

CI runs `test_prompt_golden.py` (no live Groq). Optional local job with `GROQ_API_KEY`:

```bash
cd backend
pytest tests/test_prompt_golden.py -m live_llm -v
```

Agreement uses weighted field match (`app/testing/prompt_agreement.py`). **Prompt file changes must not drop agreement below the configured floor** (see `MIN_GOLDEN_AGREEMENT` in tests).

### LLM evaluation

Without calling Groq in CI:

- Schema validity rate on golden `baseline_output` payloads.
- Repair-path behaviour on fenced / malformed JSON samples.
- Hallucination guard: insights without valid review IDs are dropped (`test_insights_citation.py`).

With API key (`-m live_llm`): spot-check latency and token budget on a 3-review sample.

### Performance

- `test_performance.py` — batch preprocess timing (marked `@pytest.mark.slow`).
- Default CI excludes slow tests (`pytest -m "not slow"`).
- Nightly or manual: `pytest -m slow` for 10k-review budget check on capable hardware.

### Edge cases

One automated test per row in [edge-cases.md](./edge-cases.md) where behaviour is deterministic (`test_edge_cases.py`).

### Research validation

After triangulation, **agreement rate** = share of insights in `validated` or `partially_supported` vs `rejected` (`app/research/metrics.py`, `test_research_agreement.py`).

## Running tests

```bash
# Backend (default CI profile)
cd backend
alembic upgrade head
pytest -m "not slow and not live_llm" -q

# Full backend including slow performance
pytest -q

# Frontend
cd frontend
npm test
npm run test:e2e
```

## CI policy

- Every push/PR: backend pytest (excluding `slow` and `live_llm`), frontend lint + build, Vitest unit tests.
- Playwright smoke runs in CI against `next start` (static shell; API may be unreachable — empty states must render).
