"""Groq LLM implementation with backoff, caching, and cost tracking."""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any, Dict, List, Optional

import httpx

from app.config import Settings
from app.llm.cache import ResponseCache
from app.llm.client import LLMClient, LLMRunBudget, LLMUsage
from app.llm.prompts import load_prompt  # re-export for translation module

logger = logging.getLogger(__name__)

# Rough Groq llama-3.3-70b pricing (USD per 1M tokens) for budgeting
_INPUT_COST_PER_M = 0.59
_OUTPUT_COST_PER_M = 0.79


def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    return (prompt_tokens / 1_000_000) * _INPUT_COST_PER_M + (
        completion_tokens / 1_000_000
    ) * _OUTPUT_COST_PER_M


class GroqLLMClient(LLMClient):
    def __init__(
        self,
        settings: Settings,
        *,
        budget: Optional[LLMRunBudget] = None,
        cache: Optional[ResponseCache] = None,
        max_concurrency: int = 4,
    ):
        self.settings = settings
        self.api_key = settings.groq_api_key
        self.base_url = settings.groq_base_url.rstrip("/")
        self.default_model = settings.groq_analysis_model
        self._budget = budget or LLMRunBudget(ceiling_usd=settings.llm_run_cost_ceiling_usd)
        self._cache = cache or ResponseCache()
        self._semaphore = asyncio.Semaphore(max_concurrency)

    @property
    def budget(self) -> LLMRunBudget:
        return self._budget

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _usage_from_response(self, data: Dict[str, Any]) -> LLMUsage:
        usage = data.get("usage") or {}
        pt = int(usage.get("prompt_tokens") or 0)
        ct = int(usage.get("completion_tokens") or 0)
        tt = int(usage.get("total_tokens") or pt + ct)
        cost = estimate_cost(pt, ct)
        return LLMUsage(
            prompt_tokens=pt,
            completion_tokens=ct,
            total_tokens=tt,
            estimated_cost_usd=cost,
        )

    async def _post_with_retry(
        self,
        payload: Dict[str, Any],
        *,
        max_attempts: int = 5,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        delay = 1.0
        last_exc: Optional[Exception] = None
        async with httpx.AsyncClient(timeout=120.0) as client:
            for attempt in range(max_attempts):
                try:
                    response = await client.post(
                        url, headers=self._headers(), json=payload
                    )
                    if response.status_code in (429, 500, 502, 503, 504):
                        raise httpx.HTTPStatusError(
                            "retryable",
                            request=response.request,
                            response=response,
                        )
                    response.raise_for_status()
                    return response.json()
                except (httpx.HTTPStatusError, httpx.TransportError) as exc:
                    last_exc = exc
                    status = getattr(getattr(exc, "response", None), "status_code", None)
                    if status not in (429, 500, 502, 503, 504, None) and attempt == 0:
                        raise
                    if attempt == max_attempts - 1:
                        break
                    sleep_for = delay + random.uniform(0, 0.5)
                    logger.warning(
                        "Groq request retry attempt=%s status=%s sleep=%.1f",
                        attempt + 1,
                        status,
                        sleep_for,
                    )
                    await asyncio.sleep(sleep_for)
                    delay = min(delay * 2, 30.0)
        assert last_exc is not None
        raise last_exc

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
        ph = prompt_hash or "default"
        ih = ResponseCache.hash_input(cache_key or prompt)
        cached = self._cache.get(ph, ih)
        if cached is not None:
            return cached

        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with self._semaphore:
            data = await self._post_with_retry(payload)

        usage = self._usage_from_response(data)
        self._budget.charge(usage.estimated_cost_usd, usage)

        choices = data.get("choices") or []
        content = ""
        if choices:
            content = (choices[0].get("message") or {}).get("content") or ""
        self._cache.set(ph, ih, content)
        return content

    def complete_sync(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.1,
    ) -> str:
        return asyncio.run(
            self.complete(
                prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        )

    async def complete_batch(
        self,
        prompts: List[str],
        *,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        prompt_hash: Optional[str] = None,
    ) -> List[str]:
        tasks = [
            self.complete(
                p,
                model=model,
                max_tokens=max_tokens,
                cache_key=p,
                prompt_hash=prompt_hash,
            )
            for p in prompts
        ]
        return await asyncio.gather(*tasks)


class GroqClient:
    """Backward-compatible sync client used by Phase 3 translation."""

    def __init__(self, settings: Settings):
        self._inner = GroqLLMClient(settings)
        self.settings = settings
        self.api_key = settings.groq_api_key
        self.base_url = settings.groq_base_url.rstrip("/")
        self.model = settings.groq_translation_model

    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        return self._inner.complete_sync(
            prompt, model=self.model, max_tokens=max_tokens
        )
