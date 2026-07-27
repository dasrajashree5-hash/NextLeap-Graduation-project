"""Performance smoke tests (excluded from default CI)."""

import time
import uuid

import pytest

from app.preprocessing.clean import clean_text
from app.preprocessing.dedupe import DedupeIndex, normalized_hash


@pytest.mark.slow
def test_cleaning_throughput_ten_thousand_reviews():
    sample = "Blinkit delivery was quick and vegetables were fresh today."
    start = time.perf_counter()
    index = DedupeIndex()
    for i in range(10_000):
        text = f"{sample} #{i}"
        cleaned = clean_text(text)
        h = normalized_hash(cleaned)
        index.check(cleaned, h)
    elapsed = time.perf_counter() - start
    assert elapsed < 300, f"clean+dedupe 10k took {elapsed:.1f}s"


@pytest.mark.slow
def test_health_endpoint_p95(client):
    latencies = []
    for _ in range(30):
        start = time.perf_counter()
        resp = client.get("/api/health")
        latencies.append(time.perf_counter() - start)
        assert resp.status_code == 200
    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95) - 1]
    assert p95 < 2.0, f"p95 health latency {p95:.3f}s"


@pytest.mark.slow
def test_bulk_manual_ingest_timing(client):
    reviews = [
        {"text": f"Performance ingest review number {i}", "external_id": f"perf-{uuid.uuid4().hex}"}
        for i in range(200)
    ]
    start = time.perf_counter()
    resp = client.post(
        "/api/reviews/manual",
        json={"source_name": f"perf_{uuid.uuid4().hex[:8]}", "reviews": reviews},
    )
    elapsed = time.perf_counter() - start
    assert resp.status_code == 200
    assert resp.json()["stats"]["stored"] == 200
    assert elapsed < 60, f"200-review ingest took {elapsed:.1f}s"
