# Key Risks and Mitigations

**Project:** AI-Powered Product Discovery Engine for Blinkit  
**Source:** [implementation-plan.md](./implementation-plan.md) §9

Each risk has **code-level mitigations** and **automated checks** you can run without a live Groq key or store scrapers.

---

## Risk register

| ID | Risk | Mitigation | Where it lives |
|----|------|------------|----------------|
| `generic_discovery_insights` | Reviews rarely mention category discovery | Discovery fields in review analysis; interviews prioritized for barrier depth | `prompts/review_analysis.v1.txt`, `mvp/barriers.py`, `research/coding.py` |
| `llm_hallucination` | LLM invents plausible insights | Mandatory review IDs; drop uncitable drafts | `insights/citations.py`, `insights/generator.py` |
| `scraper_breakage` | Play/App Store scrapers break or rate-limit | CSV/JSON/manual upload + sample corpus | `collectors/*`, `data/sample_blinkit_reviews.csv` |
| `prompt_drift` | Prompt edits silently degrade quality | Versioned prompts + ≥50-row golden set | `prompts/*.v*.txt`, `tests/test_prompt_golden.py` |
| `cost_overrun` | Large batches exhaust LLM budget | One analysis call per review, cache, run ceiling | `llm/groq_client.py`, `LLM_RUN_COST_CEILING_USD` |
| `scope_creep` | Fourteen docs and six phases sprawl | Docs-first list per phase + automated gates | `docs/*`, `services/phase_gates.py` |

---

## Verification

### API

```bash
curl http://127.0.0.1:8000/api/project/risks
```

Returns each risk, its checks, and `mitigated` / `all_mitigated`.

### CLI

```bash
cd backend
python scripts/check_phase_gates.py --risks
python scripts/check_phase_gates.py --risks --fail-on-incomplete
```

`--fail-on-incomplete` exits non-zero if any mitigation check fails (CI-friendly).

### Tests

```bash
cd backend && pytest tests/test_key_risks.py -q
```

---

## Operational notes

- **Discovery depth:** When review text is generic, triangulation and MVP copy should lean on interview-coded `discovery_barriers` before review aggregates.
- **Hallucinations:** Never persist an insight without at least one valid `example_review_id` from the theme’s review set.
- **Demo without scrapers:** Load `backend/data/sample_blinkit_reviews.csv` via the CSV collector or upload API.
- **Prompt changes:** Add `name.vN.txt`; do not edit prior versions. Run golden tests before merging.
- **Cost:** Raise `LLM_RUN_COST_CEILING_USD` only deliberately; batches stop when the ceiling is hit.
