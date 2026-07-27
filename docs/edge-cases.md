# Edge Cases

Cross-phase handling reference (from implementation plan). Each row maps to code or UX behavior in the repo.

| Case | Handling | Where |
|------|----------|--------|
| Empty or whitespace-only review | Filtered at preprocessing; counted in run stats | `preprocessing/spam.py`, pipeline |
| Duplicate reviews | Exact hash + near-duplicate pass | `preprocessing/dedupe.py` |
| Unsupported / transliterated language | Groq translation; low confidence flagged | `preprocessing/translate.py` |
| Hallucinated insights | Require `example_review_ids`; drop uncitable | `insights/generator.py` |
| LLM failure / timeout | Retry + mark `analysis_failed` | `llm/groq_client.py` |
| Missing LLM JSON fields | Pydantic + one repair retry | `llm/json_utils.py` |
| Corrupted CSV | Row-level 422 with details | `collectors/csv_collector.py` |
| Low-confidence insights | Shown with badge in dashboard | `Dashboard` insights panel |
| Conflicting themes | Triangulation `rejected` / notes | `research/triangulation.py` |
| API rate limits | Throttle, cache, cost ceiling | `llm/groq_client.py` |
| Cold start (no data) | Sample CSV + research seed + empty states | `data/sample_blinkit_reviews.csv`, UI |
| No insights for MVP | `503` on recommend; status `ready: false` | `api/routes/mvp.py` |
| Basket with no category match | Default `Grocery`; adjacency still applies | `mvp/catalog.py` |
| MVP eval without insights | `422` with clear message | `mvp/evaluation.py` |
| Backend unreachable (frontend) | Error banner + retry | `frontend` dashboard |
| Rejected insight for copy | Engine deprioritizes in scoring | `mvp/engine.py` |

---

## Demo / production notes

- **SQLite file** in repo is for local demo only; production uses Postgres.
- **Groq key missing:** health shows `not_configured`; analysis endpoints fail gracefully.
- **Large uploads:** use `limit` on pipeline endpoints to avoid timeouts on free tiers.
