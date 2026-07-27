"""Preprocessing unit tests."""

from app.preprocessing.clean import clean_text
from app.preprocessing.dedupe import DedupeIndex, normalized_hash
from app.preprocessing.spam import is_spam


def test_clean_strips_html_and_normalizes():
    raw = "<b>Great</b>   app!!!\r\n"
    assert clean_text(raw) == "Great app!!!"


def test_spam_single_token():
    flag, reason = is_spam("ok")
    assert flag is True
    assert reason == "single_token"


def test_exact_dedupe():
    index = DedupeIndex()
    text = "Blinkit delivery is fast"
    h = normalized_hash(text)
    index.register(1, text, h)
    is_dup, canonical, _ = index.check(text, h)
    assert is_dup is True
    assert canonical == 1
