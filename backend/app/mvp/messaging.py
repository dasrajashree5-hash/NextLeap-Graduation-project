"""Barrier-aware suggestion copy grounded in insight evidence."""

from __future__ import annotations

from typing import Optional

from app.models import Insight
from app.mvp.catalog import CatalogProduct


def _snippet(insight: Optional[Insight], max_len: int = 120) -> str:
    if not insight:
        return "customers like you expanded their basket"
    text = (insight.evidence or insight.problem or "").strip()
    if len(text) > max_len:
        return text[: max_len - 3].rsplit(" ", 1)[0] + "..."
    return text


def compose_message(
    *,
    product: CatalogProduct,
    dominant_barrier: str,
    adjacent_to: str,
    insight: Optional[Insight],
) -> str:
    snippet = _snippet(insight)
    name = product.name
    rating = product.rating
    reviews = product.review_count
    price = product.price_inr

    if dominant_barrier == "trust":
        return (
            f"{name} is rated {rating}/5 from {reviews:,}+ reviews — "
            f"shoppers who buy {adjacent_to} often add this when trying {product.category}. "
            f"Research: {snippet}"
        )
    if dominant_barrier == "awareness":
        return (
            f"Complete your {adjacent_to} run — {name} is a simple way to try {product.category} "
            f"without browsing the full store. {snippet}"
        )
    if dominant_barrier == "price":
        return (
            f"Add {name} for ₹{price} — often bought with {adjacent_to} staples. "
            f"{snippet}"
        )
    if dominant_barrier == "search":
        return (
            f"Easy add-on next to your {adjacent_to} items: {name}. "
            f"No extra search needed. {snippet}"
        )
    if dominant_barrier == "quality_doubt":
        return (
            f"{name} — {rating}/5 from verified buyers; popular with {product.category} first-timers. "
            f"{snippet}"
        )
    # habit (default)
    return (
        f"Pairs with what's in your cart: {name} complements your {adjacent_to} picks. "
        f"{snippet}"
    )
