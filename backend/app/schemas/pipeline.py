"""Pipeline API schemas."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PreprocessRequest(BaseModel):
    limit: int = Field(default=500, ge=1, le=10000)
    force: bool = False
    skip_translation: bool = False
    skip_embeddings: bool = False


class PreprocessResponse(BaseModel):
    run_id: int
    stats: Dict[str, Any]


class PipelineStatusResponse(BaseModel):
    preprocessing_version: str
    total_reviews: int
    pending: int
    embedded: int
    chroma_vectors: Optional[int] = None
