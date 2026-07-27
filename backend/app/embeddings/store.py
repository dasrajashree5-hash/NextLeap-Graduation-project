"""ChromaDB vector store adapter."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import Settings

COLLECTION_NAME = "blinkit_reviews"


class VectorStore:
    def __init__(self, settings: Settings):
        persist = settings.chroma_persist_dir
        if not persist.is_absolute():
            persist = Path.cwd() / persist
        persist.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(persist),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(
        self,
        review_ids: List[int],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        if not review_ids:
            return
        ids = [str(rid) for rid in review_ids]
        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def vector_ref(self, review_id: int) -> str:
        return f"chroma:{COLLECTION_NAME}:{review_id}"

    def count(self) -> int:
        return self._collection.count()

    def get_embeddings(self, review_ids: List[int]) -> Dict[int, List[float]]:
        if not review_ids:
            return {}
        ids = [str(rid) for rid in review_ids]
        result = self._collection.get(ids=ids, include=["embeddings"])
        out: Dict[int, List[float]] = {}
        for rid_str, emb in zip(result.get("ids") or [], result.get("embeddings") or []):
            if emb is not None:
                out[int(rid_str)] = list(emb)
        return out

    def all_review_ids(self) -> List[int]:
        result = self._collection.get(include=[])
        ids = result.get("ids") or []
        return [int(i) for i in ids]
