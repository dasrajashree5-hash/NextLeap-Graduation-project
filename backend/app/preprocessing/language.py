"""Language detection."""

import re
from typing import Optional, Tuple

from langdetect import DetectorFactory, LangDetectException, detect_langs

DetectorFactory.seed = 0

_INDIC_RE = re.compile(r"[\u0900-\u097F]")
_LATIN_RE = re.compile(r"[A-Za-z]")


def detect_language(text: str) -> Tuple[str, float]:
    if not text or len(text.strip()) < 10:
        return "unknown", 0.0
    try:
        candidates = detect_langs(text)
        if not candidates:
            return "unknown", 0.0
        top = candidates[0]
        return top.lang, float(top.prob)
    except LangDetectException:
        return "unknown", 0.0


def is_hinglish(text: str, lang: str) -> bool:
    has_indic = bool(_INDIC_RE.search(text))
    has_latin = bool(_LATIN_RE.search(text))
    if has_indic and has_latin:
        return True
    if lang == "hi" and has_latin and not has_indic:
        return True
    return False
