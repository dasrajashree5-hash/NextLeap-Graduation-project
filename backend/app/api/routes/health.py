"""Health checks for dependencies."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import Settings


def check_database(db: Session) -> Tuple[str, Optional[str]]:
    try:
        db.execute(text("SELECT 1"))
        return "ok", None
    except Exception as exc:  # noqa: BLE001
        return "error", str(exc)


def check_vector_store(settings: Settings) -> Tuple[str, Optional[str]]:
    try:
        if settings.vector_store.lower() != "chroma":
            return "ok", None
        path: Path = settings.chroma_persist_dir
        if not path.is_absolute():
            path = Path.cwd() / path
        path.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            return "error", "chroma directory missing"
        return "ok", None
    except Exception as exc:  # noqa: BLE001
        return "error", str(exc)


async def check_groq(settings: Settings) -> Tuple[str, Optional[str]]:
    if not settings.groq_api_key:
        return "not_configured", "GROQ_API_KEY not set"
    url = f"{settings.groq_base_url.rstrip('/')}/models"
    headers = {"Authorization": f"Bearer {settings.groq_api_key}"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return "ok", None
        return "error", f"HTTP {response.status_code}"
    except Exception as exc:  # noqa: BLE001
        return "error", str(exc)
