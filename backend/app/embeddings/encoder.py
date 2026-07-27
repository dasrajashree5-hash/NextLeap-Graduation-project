"""Sentence-transformer encoding."""

from functools import lru_cache
from typing import List, Optional

import numpy as np

_encoder = None


@lru_cache
def _get_model_name() -> str:
    from app.config import get_settings

    return get_settings().embedding_model


def get_encoder():
    global _encoder
    if _encoder is None:
        from sentence_transformers import SentenceTransformer

        _encoder = SentenceTransformer(_get_model_name())
    return _encoder


def encode_texts(texts: List[str], batch_size: int = 64) -> np.ndarray:
    if not texts:
        return np.zeros((0, 384), dtype=np.float32)
    model = get_encoder()
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return vectors.astype(np.float32)


def embedding_dimension() -> int:
    model = get_encoder()
    return int(model.get_sentence_embedding_dimension())
