"""Key risk mitigation checks (implementation plan §9)."""

from app.db.session import SessionLocal
from app.services.key_risks import KEY_RISKS, evaluate_key_risks


def test_key_risk_register_has_six_items():
    assert len(KEY_RISKS) == 6
    ids = {r.risk_id for r in KEY_RISKS}
    assert "llm_hallucination" in ids
    assert "prompt_drift" in ids


def test_evaluate_key_risks_all_mitigated():
    db = SessionLocal()
    try:
        report = evaluate_key_risks(db)
    finally:
        db.close()
    assert report["total_risks"] == 6
    assert report["mitigated_count"] == 6
    assert report["all_mitigated"] is True
    assert len(report["risks"]) == 6
    for item in report["risks"]:
        assert item["mitigated"] is True
        assert all(c["passed"] for c in item["checks"])


def test_risks_endpoint(client):
    resp = client.get("/api/project/risks")
    assert resp.status_code == 200
    body = resp.json()
    assert body["all_mitigated"] is True
    assert body["total_risks"] == 6
