"""Shared pytest fixtures."""

from __future__ import annotations

import uuid
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import create_app

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
GOLDEN_DIR = FIXTURES_DIR / "prompt_golden"


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_embeddings(monkeypatch):
    """Avoid loading sentence-transformers during pipeline tests."""

    monkeypatch.setattr(
        "app.services.pipeline.encode_texts",
        lambda texts, batch_size=64: np.zeros((len(texts), 384), dtype=np.float32),
    )
    monkeypatch.setattr(
        "app.services.pipeline.VectorStore",
        lambda settings: type(
            "MockVectorStore",
            (),
            {
                "upsert": lambda *a, **k: None,
                "vector_ref": lambda self, rid: f"mock:{rid}",
                "count": lambda self: 0,
            },
        )(),
    )


def ingest_manual(client: TestClient, text: str, *, prefix: str = "t") -> str:
    ext = f"{prefix}-{uuid.uuid4().hex}"
    client.post(
        "/api/reviews/manual",
        json={
            "source_name": f"fixture_{uuid.uuid4().hex[:8]}",
            "reviews": [{"text": text, "external_id": ext}],
        },
    )
    return ext
