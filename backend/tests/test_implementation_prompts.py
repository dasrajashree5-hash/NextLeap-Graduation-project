"""Implementation prompts (plan §10)."""

from app.core.implementation_prompts import (
    IMPLEMENTATION_PROMPTS,
    evaluate_implementation_prompts,
    get_implementation_prompt,
    implementation_prompts_summary,
)
from app.core.phases import PHASES


def test_six_sequential_prompts():
    assert len(IMPLEMENTATION_PROMPTS) == 6
    assert [p.phase for p in IMPLEMENTATION_PROMPTS] == list(range(1, 7))


def test_prompts_align_with_phase_specs():
    for prompt in IMPLEMENTATION_PROMPTS:
        spec = next(p for p in PHASES if p.number == prompt.phase)
        assert prompt.slug == spec.slug
        assert prompt.docs_first == spec.docs_first


def test_get_implementation_prompt():
    p4 = get_implementation_prompt(4)
    assert p4 is not None
    assert "Phase 4" in p4.cursor_prompt
    assert get_implementation_prompt(99) is None


def test_implementation_prompts_summary():
    body = implementation_prompts_summary()
    assert body["total"] == 6
    assert len(body["prompts"]) == 6
    assert "docs-first" in body["policy"].lower()


def test_evaluate_implementation_prompts_complete():
    report = evaluate_implementation_prompts()
    assert report["complete"] is True
    assert all(c["passed"] for c in report["checks"])


def test_implementation_prompts_api_list(client):
    resp = client.get("/api/project/implementation-prompts")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 6
    assert body["prompts"][0]["phase"] == 1


def test_implementation_prompts_api_single_phase(client):
    resp = client.get("/api/project/implementation-prompts?phase=3")
    assert resp.status_code == 200
    body = resp.json()
    assert body["phase"] == 3
    assert body["slug"] == "preprocess"


def test_implementation_prompts_api_invalid_phase_query(client):
    resp = client.get("/api/project/implementation-prompts?phase=10")
    assert resp.status_code == 422
