# Streamlit single-service path (Case 1)

Requires a running FastAPI backend (local or deployed).

```bash
cd backend && uvicorn app.main:app --port 8000
cd streamlit_app
pip install -r requirements.txt
export API_BASE_URL=http://127.0.0.1:8000
streamlit run app.py
```

See [`docs/deployment-plan.md`](../docs/deployment-plan.md).
