"""Versioned prompt loading with optional YAML front matter."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"

_FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass(frozen=True)
class PromptSpec:
    name: str
    version: str
    body: str
    model: Optional[str]
    schema_name: Optional[str]
    meta: Dict[str, Any]

    @property
    def version_tag(self) -> str:
        return f"{self.name}.{self.version}"

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.body.encode("utf-8")).hexdigest()[:16]


def _parse_filename(filename: str) -> tuple[str, str]:
    # review_analysis.v1.txt -> (review_analysis, v1)
    stem = filename.replace(".txt", "")
    if ".v" not in stem:
        return stem, "v1"
    name, ver = stem.rsplit(".v", 1)
    return name, f"v{ver}"


def load_prompt(filename: str) -> str:
    """Return prompt body only (backward compatible with Phase 3)."""
    return load_prompt_spec(filename).body


def render_prompt(template: str, **values: Any) -> str:
    """Substitute {name} placeholders without treating literal JSON braces as fields."""
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{" + key + "}", str(value))
    return rendered


def load_prompt_spec(filename: str) -> PromptSpec:
    path = PROMPTS_DIR / filename
    raw = path.read_text(encoding="utf-8")
    meta: Dict[str, Any] = {}
    body = raw
    match = _FRONT_MATTER.match(raw)
    if match:
        meta = yaml.safe_load(match.group(1)) or {}
        body = raw[match.end() :]
    name, version = _parse_filename(path.name)
    return PromptSpec(
        name=name,
        version=version,
        body=body.strip(),
        model=meta.get("model"),
        schema_name=meta.get("schema"),
        meta=meta,
    )
