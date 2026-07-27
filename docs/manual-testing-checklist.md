# Manual Testing Checklist

Use before demos and after deploys.

## Backend

- [ ] `GET /api/health` — database ok
- [ ] `GET /api/reviews/stats` — counts look reasonable
- [ ] Upload sample CSV via `/api/reviews/upload`
- [ ] `POST /api/research/seed?code=true` — interviews + surveys
- [ ] `GET /api/insights` — at least one insight with review IDs
- [ ] `POST /api/mvp/recommend` — suggestion + message + `insight_id`
- [ ] `POST /api/mvp/evaluate` — pass rate reported

## Frontend dashboard

- [ ] Overview shows live health and stats
- [ ] Paste manual reviews and submit
- [ ] Insights tab lists cards; low confidence visually distinct
- [ ] Research tab: opportunities + seed
- [ ] MVP demo: preset basket → recommend → insight cited
- [ ] Problem statement tab loads markdown
- [ ] Keyboard: tab through nav and primary buttons
- [ ] Mobile width: sidebar collapses / content readable

## Streamlit (Case 1)

- [ ] App starts with `API_BASE_URL` set
- [ ] MVP recommend flow matches API

## CI

- [ ] GitHub Actions green on latest `main` (backend `pytest -m "not slow and not live_llm"`, frontend Vitest + Playwright)

See [testing-strategy.md](./testing-strategy.md) for full coverage map.
