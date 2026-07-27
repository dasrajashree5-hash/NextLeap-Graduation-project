"""Spam and low-quality review detection."""

import re
from typing import Optional, Tuple

_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)
_PROMO_KEYWORDS = (
    "subscribe",
    "follow me",
    "click here",
    "discount code",
    "promo code",
    "free gift",
    "whatsapp",
    "telegram",
    "earn money",
)

_TOKEN_RE = re.compile(r"[A-Za-z\u0900-\u097F]+")


def is_spam(clean: str) -> Tuple[bool, Optional[str]]:
    if not clean or not clean.strip():
        return True, "empty"

    tokens = clean.split()
    alpha_tokens = _TOKEN_RE.findall(clean)

    if len(alpha_tokens) == 0:
        return True, "rating_only"

    if len(tokens) == 1 and len(tokens[0]) < 8:
        return True, "single_token"

    if len(clean) >= 10:
        char_counts = {}
        for ch in clean:
            if not ch.isspace():
                char_counts[ch] = char_counts.get(ch, 0) + 1
        if char_counts:
            dominant = max(char_counts.values())
            if dominant / max(len(clean.replace(" ", "")), 1) > 0.6:
                return True, "repeated_characters"

    url_count = len(_URL_RE.findall(clean))
    if url_count and url_count / max(len(tokens), 1) > 0.3:
        return True, "url_heavy"

    lower = clean.lower()
    promo_hits = sum(1 for kw in _PROMO_KEYWORDS if kw in lower)
    if promo_hits >= 3:
        return True, "promotional"

    return False, None
