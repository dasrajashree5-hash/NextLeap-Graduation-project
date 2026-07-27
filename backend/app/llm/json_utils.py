"""JSON extraction and validation helpers."""

from __future__ import annotations

import json
import re
from typing import Any, Callable, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)


def extract_json_text(raw: str) -> str:
    text = raw.strip()
    match = _FENCE.search(text)
    if match:
        return match.group(1).strip()
    start = text.find("{")
    start_arr = text.find("[")
    if start_arr != -1 and (start == -1 or start_arr < start):
        start = start_arr
    if start == -1:
        return text
    return text[start:].strip()


def parse_json(raw: str) -> Any:
    return json.loads(extract_json_text(raw))


def validate_model(raw: str, model: Type[T]) -> T:
    data = parse_json(raw)
    return model.model_validate(data)


def validate_with_repair(
    raw: str,
    model: Type[T],
    repair_fn: Optional[Callable[[str, str], str]] = None,
) -> tuple[Optional[T], Optional[str]]:
    """Returns (instance, error_message). One repair attempt via repair_fn."""
    try:
        return validate_model(raw, model), None
    except (json.JSONDecodeError, ValidationError) as first_err:
        if repair_fn is None:
            return None, str(first_err)
        try:
            repaired = repair_fn(raw, str(first_err))
            return validate_model(repaired, model), None
        except Exception as second_err:  # noqa: BLE001
            return None, str(second_err)
