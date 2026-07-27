"""Application configuration."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_database_url(url: str) -> str:
    """Railway/Render often provide postgres:// or postgresql:// without a driver."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(
        default="sqlite:///./data/discovery.db",
        alias="DATABASE_URL",
    )

    vector_store: str = Field(default="chroma", alias="VECTOR_STORE")
    chroma_persist_dir: Path = Field(
        default=Path("./data/chroma"),
        alias="CHROMA_PERSIST_DIR",
    )

    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    groq_base_url: str = Field(
        default="https://api.groq.com/openai/v1",
        alias="GROQ_BASE_URL",
    )

    api_prefix: str = "/api"

    preprocessing_version: str = Field(default="1.0.0", alias="PREPROCESSING_VERSION")
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL",
    )
    groq_translation_model: str = Field(
        default="llama-3.3-70b-versatile",
        alias="GROQ_TRANSLATION_MODEL",
    )
    groq_analysis_model: str = Field(
        default="llama-3.3-70b-versatile",
        alias="GROQ_ANALYSIS_MODEL",
    )
    analysis_version: str = Field(default="1.0.0", alias="ANALYSIS_VERSION")
    llm_run_cost_ceiling_usd: float = Field(
        default=25.0,
        alias="LLM_RUN_COST_CEILING_USD",
    )
    llm_max_concurrency: int = Field(default=4, alias="LLM_MAX_CONCURRENCY")
    analyze_batch_size: int = Field(default=50, alias="ANALYZE_BATCH_SIZE")
    preprocess_batch_size: int = Field(default=256, alias="PREPROCESS_BATCH_SIZE")
    max_context_tokens: int = Field(default=400, alias="MAX_CONTEXT_TOKENS")
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ORIGINS",
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> object:
        if isinstance(value, str):
            return _normalize_database_url(value)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
