"""LLM client interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class LLMUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


@dataclass
class LLMRunBudget:
    ceiling_usd: float
    spent_usd: float = 0.0
    usage: LLMUsage = field(default_factory=LLMUsage)

    def charge(self, cost: float, usage: LLMUsage) -> None:
        self.spent_usd += cost
        self.usage.prompt_tokens += usage.prompt_tokens
        self.usage.completion_tokens += usage.completion_tokens
        self.usage.total_tokens += usage.total_tokens
        self.usage.estimated_cost_usd += cost
        if self.spent_usd > self.ceiling_usd:
            raise RuntimeError(
                f"LLM run cost ceiling exceeded ({self.spent_usd:.4f} > {self.ceiling_usd:.4f} USD)"
            )


class LLMClient(ABC):
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.1,
        cache_key: Optional[str] = None,
        prompt_hash: Optional[str] = None,
    ) -> str:
        ...

    @abstractmethod
    def complete_sync(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.1,
    ) -> str:
        ...

    @property
    @abstractmethod
    def budget(self) -> LLMRunBudget:
        ...
