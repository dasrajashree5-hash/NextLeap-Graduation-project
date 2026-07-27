"""Exact and near-duplicate detection."""

import hashlib
import re
from typing import Dict, List, Optional, Set, Tuple

from datasketch import MinHash, MinHashLSH

_SHINGLE_WORDS = 3
_NUM_PERM = 128
_NEAR_THRESHOLD = 0.95


def normalized_hash(text: str) -> str:
    normalized = re.sub(r"\s+", " ", (text or "").strip().lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _shingles(text: str) -> Set[str]:
    words = text.lower().split()
    if len(words) <= _SHINGLE_WORDS:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i : i + _SHINGLE_WORDS]) for i in range(len(words) - _SHINGLE_WORDS + 1)}


def minhash_signature(text: str) -> MinHash:
    mh = MinHash(num_perm=_NUM_PERM)
    for shingle in _shingles(text):
        mh.update(shingle.encode("utf-8"))
    return mh


class DedupeIndex:
    """Tracks exact hashes and near-duplicates via MinHash LSH."""

    def __init__(self) -> None:
        self.exact_hashes: Dict[str, int] = {}
        self.lsh = MinHashLSH(threshold=_NEAR_THRESHOLD, num_perm=_NUM_PERM)
        self.canonical_ids: Dict[str, int] = {}

    def seed(self, review_id: int, clean_text: str, dedupe_hash: str) -> None:
        if dedupe_hash and dedupe_hash not in self.exact_hashes:
            self.exact_hashes[dedupe_hash] = review_id
        key = f"r{review_id}"
        if key not in self.canonical_ids:
            sig = minhash_signature(clean_text)
            self.lsh.insert(key, sig)
            self.canonical_ids[key] = review_id

    def check(self, clean_text: str, dedupe_hash: str) -> Tuple[bool, Optional[int], str]:
        if dedupe_hash in self.exact_hashes:
            return True, self.exact_hashes[dedupe_hash], "exact"

        sig = minhash_signature(clean_text)
        matches = self.lsh.query(sig)
        if matches:
            canonical_key = sorted(matches)[0]
            return True, self.canonical_ids.get(canonical_key), "near"

        return False, None, dedupe_hash

    def register(self, review_id: int, clean_text: str, dedupe_hash: str) -> None:
        self.exact_hashes.setdefault(dedupe_hash, review_id)
        key = f"r{review_id}"
        if key not in self.canonical_ids:
            self.lsh.insert(key, minhash_signature(clean_text))
            self.canonical_ids[key] = review_id
