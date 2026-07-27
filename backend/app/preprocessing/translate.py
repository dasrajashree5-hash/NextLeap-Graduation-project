"""Groq-powered translation."""

from app.config import Settings
from app.llm.groq_client import GroqClient, load_prompt
from app.preprocessing.language import is_hinglish


def translate_review(text: str, language: str, settings: Settings) -> str:
    if language in ("en", "unknown"):
        return text
    client = GroqClient(settings)
    if is_hinglish(text, language):
        template = load_prompt("hinglish_translate.v1.txt")
    else:
        template = load_prompt("translate.v1.txt")
    prompt = template.format(text=text)
    translated = client.complete(prompt).strip()
    return translated or text
