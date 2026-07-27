"""Whitespace token stats."""

from typing import Tuple


def tokenize_stats(text: str, max_context_tokens: int) -> Tuple[int, bool]:
    tokens = (text or "").split()
    count = len(tokens)
    needs_chunking = count > max_context_tokens or len(text or "") > 2000
    return count, needs_chunking
