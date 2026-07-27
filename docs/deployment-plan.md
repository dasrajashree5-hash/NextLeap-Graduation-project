# Deployment Plan

**Project:** Blinkit Discovery Engine  
**Phase:** 6c — Case 2 (split stack) primary; Case 1 (Streamlit) secondary

---

## Architecture (production)

| Component | Platform | Notes |
|-----------|----------|--------|
| Frontend | **Vercel** or **Netlify** | Next.js 14, `NEXT_PUBLIC_API_URL` |
| Backend | **Railway** or **Render** | `uvicorn app.main:app`, health probe `/api/health` |
| Relational DB | **Supabase Postgres** | `DATABASE_URL=postgresql+psycopg://...` |
| Vectors | **Supabase pgvector** or Chroma on volume | Set `VECTOR_STORE` per env |
| Secrets | Platform env vars | Never commit `.env` |

---

## Environment variables

Copy [`.env.example`](../.env.example) per service.

| Variable | Backend | Frontend |
|----------|---------|----------|
| `DATABASE_URL` | Required | — |
| `GROQ_API_KEY` | Required for LLM paths | — |
| `CHROMA_PERSIST_DIR` / vector config | Required | — |
| `ENVIRONMENT` | `production` | — |
| `NEXT_PUBLIC_API_URL` | — | e.g. `https://api.example.com` |

Backend CORS: `CORS_ORIGINS` (comma-separated) plus `CORS_ORIGIN_REGEX` for Netlify deploy previews.
Defaults already allow localhost and `https://graduationprojectblinkitnextleap.netlify.app`; override both
when the frontend moves to a different domain.

**Verifying live env vars:** `GET /api/health` echoes `environment`. If it reports `development` on Railway,
no service variables are set, which also means `CORS_ORIGINS` and `DATABASE_URL` are falling back to defaults.

---

## Backend deploy (Railway / Render)

1. **Root directory:** `backend/` (must match `backend/railway.toml` and `backend/Dockerfile`).
2. **Start command:** leave empty in the Railway UI so the image runs `scripts/start.sh` (migrations + uvicorn on `$PORT`).  
   If you override it, use a **shell** so `PORT` expands, e.g. `sh scripts/start.sh` — never bare `uvicorn ... --port $PORT` (uvicorn receives the literal `$PORT` and the container crash-loops).
3. **Health check path:** `/api/health`
4. **Required env vars on the backend service:**

   | Variable | Required | Notes |
   |----------|----------|--------|
   | `DATABASE_URL` | **Yes (production)** | Attach Railway Postgres or paste URL; `postgres://` / `postgresql://` are auto-normalized to `postgresql+psycopg://` |
   | `ENVIRONMENT` | Recommended | `production` |
   | `GROQ_API_KEY` | Optional | LLM pipelines; health may show `not_configured` without it |
   | `CORS_ORIGINS` | Recommended | Defaults include the Netlify site; set explicitly if the domain changes |
   | `CORS_ORIGIN_REGEX` | Optional | Netlify deploy previews (`https://<hash>--<site>.netlify.app`) |
   | `CHROMA_PERSIST_DIR` | Optional | Default `./data/chroma`; use a volume for persistence |

   A fresh deploy starts with an **empty database**, so `/api/themes` and `/api/insights` return `[]`.
   Seed demo data with `POST /api/research/seed?code=true`, then run the analysis pipeline.

5. **Public URL:** Service → **Settings → Networking → Generate domain**. Without a domain, the service is not reachable from the internet.
6. Persistent volume (optional): mount `data/` for SQLite demo; use Postgres for production.

**Smoke URLs after deploy** (replace host):

- `GET https://<host>/api/health`
- `GET https://<host>/api/themes` (may be `[]` until pipeline runs)
- `GET https://<host>/api/insights?limit=12`
- Legacy redirects: `/themes` → `/api/themes`, `/insights` → `/api/insights`

---

## Frontend deploy (Vercel)

1. Root directory: `frontend/`
2. Build: `npm run build`
3. Env: `NEXT_PUBLIC_API_URL=https://<backend-host>`
4. No server-side secrets in the frontend bundle.

---

## Frontend deploy (Netlify)

1. Connect the GitHub repo in [Netlify](https://app.netlify.com).
2. Netlify reads [`netlify.toml`](../netlify.toml): base directory `frontend`, Next.js plugin.
3. **Site configuration → Environment variables:**  
   `NEXT_PUBLIC_API_URL` = `https://<backend-host>` (no trailing slash).
4. On the **backend**, set `CORS_ORIGINS` to include your Netlify URL, e.g.  
   `https://your-site.netlify.app` (comma-separated if multiple origins).
5. Deploy. Smoke-test: home loads, **Discover** / **Cart** call the API without CORS errors.

Same split as Vercel: Netlify hosts the UI only; FastAPI + DB stay on Railway/Render/Supabase.

---

## Case 1 — Streamlit single service

```bash
cd streamlit_app
pip install -r requirements.txt
export API_BASE_URL=http://127.0.0.1:8000
streamlit run app.py
```

Deploy Streamlit on Railway with the same `API_BASE_URL` pointing at the co-located or remote FastAPI service.

---

## CI (GitHub Actions)

Workflow [`.github/workflows/ci.yml`](../.github/workflows/ci.yml):

- Backend: Alembic migrate + `pytest` on push/PR
- Frontend: `npm run build` + `npm run lint`

Merges should stay green before release.

---

## Rollback

1. **Frontend (Vercel):** Deployments → previous deployment → Promote to Production.
2. **Backend (Railway/Render):** Redeploy prior image/commit from deployment history.
3. **Database:** Alembic downgrade one revision only with a backup; prefer forward-fix migrations.

Document the rollback commit SHA after each production promote.

---

## Post-deploy smoke test

1. `GET /api/health` → `status: ok`
2. `GET /api/reviews/stats` → `total_reviews > 0` (seeded demo)
3. `GET /api/mvp/status` → `ready: true`
4. `POST /api/mvp/recommend` with sample basket → suggestion + `insight_id`
5. Open Vercel URL → dashboard loads, MVP demo returns a suggestion

See [manual-testing-checklist.md](./manual-testing-checklist.md).
