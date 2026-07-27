"""Phase sequencing and gate API tests."""

from app.core.phases import PHASES, total_effort_pct


def test_effort_percentages_sum_to_100():
    assert abs(total_effort_pct() - 100.0) < 0.01


def test_phases_strict_dependencies():
    for p in PHASES:
        if p.number == 1:
            assert p.depends_on == ()
        else:
            assert p.depends_on == (p.number - 1,)


def test_sequencing_endpoint(client):
    resp = client.get("/api/project/sequencing")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_effort_pct"] == 100.0
    assert len(body["phases"]) == 6
    assert body["phases"][3]["effort_pct"] == 30.0


def test_phases_gates_endpoint(client):
    resp = client.get("/api/project/phases?through=6")
    assert resp.status_code == 200
    body = resp.json()
    assert body["recommended_current_phase"] >= 1
    assert len(body["phases"]) == 6
    phase1 = body["phases"][0]
    assert phase1["phase"] == 1
    assert any(g["gate_id"] == "p1_health_database" for g in phase1["gates"])
