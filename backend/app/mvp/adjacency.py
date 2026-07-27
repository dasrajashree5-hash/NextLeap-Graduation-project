"""Cross-category adjacency for smart basket expansion."""

from __future__ import annotations

from typing import Dict, List, Set

# Undirected adjacency — discovery expansion edges (non-grocery emphasis)
_ADJACENCY: Dict[str, Set[str]] = {
    "Grocery": {"Snacks", "Beverages", "Personal Care", "Household", "Pet Care", "Baby Care"},
    "Dairy": {"Beverages", "Snacks", "Baby Care", "Health & Nutrition"},
    "Snacks": {"Beverages", "Personal Care", "Pet Care"},
    "Fruits & Vegetables": {"Beverages", "Health & Nutrition", "Household"},
    "Beverages": {"Snacks", "Grocery"},
    "Personal Care": {"Health & Nutrition", "Baby Care"},
    "Baby Care": {"Personal Care", "Household", "Grocery"},
    "Pet Care": {"Snacks", "Grocery", "Household"},
    "Household": {"Personal Care", "Grocery"},
    "Health & Nutrition": {"Personal Care", "Beverages", "Fruits & Vegetables"},
    "Electronics": {"Grocery", "Household"},
}

# Prefer suggesting these when basket is grocery-heavy (north star)
_DISCOVERY_PRIORITY = [
    "Pet Care",
    "Baby Care",
    "Personal Care",
    "Health & Nutrition",
    "Electronics",
    "Household",
    "Beverages",
    "Snacks",
]


def adjacent_categories(basket_categories: List[str]) -> List[str]:
    """Adjacent categories not already in the basket, discovery-priority ordered."""
    in_basket = set(basket_categories)
    candidates: Set[str] = set()
    for cat in basket_categories:
        for adj in _ADJACENCY.get(cat, set()):
            if adj not in in_basket:
                candidates.add(adj)

    ordered: List[str] = []
    for pref in _DISCOVERY_PRIORITY:
        if pref in candidates:
            ordered.append(pref)
    for c in sorted(candidates):
        if c not in ordered:
            ordered.append(c)
    return ordered
