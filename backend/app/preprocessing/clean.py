"""Text cleaning utilities."""

import re
import unicodedata
from html import unescape
from xml.etree import ElementTree

_CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]")
_WHITESPACE_RE = re.compile(r"\s+")


def strip_html(text: str) -> str:
    if "<" not in text:
        return text
    try:
        wrapped = f"<root>{text}</root>"
        root = ElementTree.fromstring(wrapped)
        return "".join(root.itertext())
    except ElementTree.ParseError:
        return re.sub(r"<[^>]+>", " ", text)


def clean_text(raw: str) -> str:
    text = unescape(raw or "")
    text = strip_html(text)
    text = _CONTROL_RE.sub(" ", text)
    text = unicodedata.normalize("NFKC", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text
