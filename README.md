# Blinkit Discovery Engine

AI-powered customer discovery research platform for Blinkit's Growth Team (NextLeap graduation project).

## Phase 1 status

- FastAPI backend with full relational schema (Alembic)
- Structured JSON logging and global error handling
- `GET /api/health` — database, Chroma path, Groq reachability
- Next.js dashboard shell (Tailwind)
- Docs: [`docs/context.md`](docs/context.md), [`docs/architecture.md`](docs/architecture.md)

## Phase 2 status

- Collectors: Play Store, App Store (RSS), CSV, JSON, manual
- Ingestion API under `/api/reviews/*` with dedupe and `runs` stats
- Offline sample: [`backend/data/sample_blinkit_reviews.csv`](backend/data/sample_blinkit_reviews.csv)
- Workflow: [`docs/workflow.md`](docs/workflow.md)

## Phase 3 status

- Preprocessing pipeline: clean, spam, dedupe, language, Groq translation
- Embeddings: `all-MiniLM-L6-v2` → ChromaDB
- `POST /api/pipeline/preprocess`, `GET /api/pipeline/status`
- Rules: [`docs/review-analysis.md`](docs/review-analysis.md)

## Quick start (backend)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env       # optional: set GROQ_API_KEY
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- API docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/api/health  

### Ingest reviews (Phase 2)

```bash
# Offline sample (~500 rows)
curl -X POST "http://127.0.0.1:8000/api/reviews/upload" \
  -F format=csv -F source_name="Blinkit sample" \
  -F file=@data/sample_blinkit_reviews.csv

# Live stores (requires network)
curl -X POST http://127.0.0.1:8000/api/reviews/ingest/play-store \
  -H "Content-Type: application/json" \
  -d '{"max_reviews": 1000}'

curl -X POST http://127.0.0.1:8000/api/reviews/ingest/app-store \
  -H "Content-Type: application/json" \
  -d '{"max_reviews": 500}'

curl http://127.0.0.1:8000/api/reviews/stats
```

Refresh sample file from stores:

```bash
python scripts/fetch_sample_reviews.py
```

### Preprocess and embed (Phase 3)

```bash
curl http://127.0.0.1:8000/api/pipeline/status
curl -X POST http://127.0.0.1:8000/api/pipeline/preprocess \
  -H "Content-Type: application/json" \
  -d '{"limit": 500, "skip_translation": false}'
```

## Phase 6c — Dashboard, Streamlit, deployment

- Next.js dashboard wired to live APIs (overview, reviews, insights, research, MVP demo, problem statement)
- Streamlit app: [`streamlit_app/app.py`](streamlit_app/app.py)
- Docs: [`docs/deployment-plan.md`](docs/deployment-plan.md), [`docs/edge-cases.md`](docs/edge-cases.md), [`docs/manual-testing-checklist.md`](docs/manual-testing-checklist.md)
- CI: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

## Quick start (frontend)

Requires Node.js 18+.

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

### Deploy frontend on Netlify

1. Push the repo to GitHub and import it in Netlify.
2. Add env var `NEXT_PUBLIC_API_URL` pointing at your deployed FastAPI URL.
3. Add that Netlify URL to backend `CORS_ORIGINS`.
4. See [`docs/deployment-plan.md`](docs/deployment-plan.md) and root [`netlify.toml`](netlify.toml).

The backend is **not** deployed on Netlify — use Railway, Render, or Docker per the deployment plan.

## Docker (Postgres + backend)

```bash
export GROQ_API_KEY=your_key   # optional
docker compose up --build
```

## Tests

```bash
cd backend && pytest
```

## Documentation-first workflow

Update docs in `docs/` before implementing each phase. See [`docs/implementation-plan.md`](docs/implementation-plan.md) and [`docs/sequencing-and-effort.md`](docs/sequencing-and-effort.md) for phase order, effort budget, and gates.

### Phase progress

```bash
cd backend
python scripts/check_phase_gates.py --through 6
python scripts/check_phase_gates.py --risks --fail-on-incomplete
python scripts/check_phase_gates.py --prompts --fail-on-incomplete
curl http://127.0.0.1:8000/api/project/sequencing
curl http://127.0.0.1:8000/api/project/risks
curl http://127.0.0.1:8000/api/project/implementation-prompts
```

## License

MIT — see [LICENSE](LICENSE).
