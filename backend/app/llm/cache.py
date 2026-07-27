"""In-memory LLM response cache (prompt hash + input hash)."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional


class ResponseCache:
    def __init__(self) -> None:
        self._store: Dict[str, str] = {}

    @staticmethod
    def key(prompt_hash: str, input_hash: str) -> str:
        return f"{prompt_hash}:{input_hash}"

    @staticmethod
    def hash_input(payload: Any) -> str:
        if isinstance(payload, str):
            data = payload
        else:
            data = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def get(self, prompt_hash: str, input_hash: str) -> Optional[str]:
        return self._store.get(self.key(prompt_hash, input_hash))

    def set(self, prompt_hash: str, input_hash: str, response: str) -> None:
        self._store[self.key(prompt_hash, input_hash)] = response

    def clear(self) -> None:
        self._store.clear()
