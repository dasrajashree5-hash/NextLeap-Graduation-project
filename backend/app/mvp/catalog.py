"""Blinkit-style demo catalog for basket expansion (offline-friendly)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class CatalogProduct:
    product_id: str
    name: str
    category: str
    rating: float
    price_inr: int
    review_count: int


# Category slugs used in adjacency graph
CATEGORIES = [
    "Grocery",
    "Dairy",
    "Snacks",
    "Fruits & Vegetables",
    "Beverages",
    "Personal Care",
    "Baby Care",
    "Pet Care",
    "Household",
    "Health & Nutrition",
    "Electronics",
]

# Keyword → category for inferring basket contents from free-text item names
_CATEGORY_KEYWORDS: Dict[str, str] = {
    "milk": "Dairy",
    "curd": "Dairy",
    "butter": "Dairy",
    "cheese": "Dairy",
    "bread": "Grocery",
    "rice": "Grocery",
    "atta": "Grocery",
    "dal": "Grocery",
    "oil": "Grocery",
    "chips": "Snacks",
    "biscuit": "Snacks",
    "namkeen": "Snacks",
    "chocolate": "Snacks",
    "apple": "Fruits & Vegetables",
    "banana": "Fruits & Vegetables",
    "onion": "Fruits & Vegetables",
    "tomato": "Fruits & Vegetables",
    "cola": "Beverages",
    "juice": "Beverages",
    "tea": "Beverages",
    "coffee": "Beverages",
    "shampoo": "Personal Care",
    "soap": "Personal Care",
    "toothpaste": "Personal Care",
    "diaper": "Baby Care",
    "wipes": "Baby Care",
    "formula": "Baby Care",
    "dog": "Pet Care",
    "cat": "Pet Care",
    "pet": "Pet Care",
    "detergent": "Household",
    "cleaner": "Household",
    "protein": "Health & Nutrition",
    "vitamin": "Health & Nutrition",
    "charger": "Electronics",
    "cable": "Electronics",
}

PRODUCTS: List[CatalogProduct] = [
    CatalogProduct("sku-d001", "Amul Taaza Milk 1L", "Dairy", 4.7, 57, 12000),
    CatalogProduct("sku-g001", "Britannia Brown Bread", "Grocery", 4.5, 45, 8000),
    CatalogProduct("sku-s001", "Lay's Classic Salted 52g", "Snacks", 4.4, 20, 15000),
    CatalogProduct("sku-pc001", "Dove Intense Repair Shampoo 180ml", "Personal Care", 4.6, 249, 3200),
    CatalogProduct("sku-bc001", "Pampers Baby Dry Diapers M (22)", "Baby Care", 4.5, 599, 2100),
    CatalogProduct("sku-pet001", "Pedigree Adult Chicken Treats 70g", "Pet Care", 4.4, 99, 980),
    CatalogProduct("sku-hn001", "MuscleBlaze Whey 1kg", "Health & Nutrition", 4.3, 2499, 450),
    CatalogProduct("sku-hh001", "Surf Excel Matic Liquid 1L", "Household", 4.6, 320, 5600),
    CatalogProduct("sku-bev001", "Real Fruit Power Orange 1L", "Beverages", 4.5, 110, 4100),
    CatalogProduct("sku-el001", "boAt Type-C Cable 1m", "Electronics", 4.2, 199, 12000),
    CatalogProduct("sku-pc002", "Colgate MaxFresh Toothpaste 150g", "Personal Care", 4.7, 89, 22000),
    CatalogProduct("sku-pet002", "Whiskas Temptations Cat Treats 35g", "Pet Care", 4.5, 75, 640),
]


def infer_category(item_name: str, explicit: Optional[str] = None) -> Optional[str]:
    if explicit and explicit in CATEGORIES:
        return explicit
    lowered = item_name.lower()
    for keyword, category in _CATEGORY_KEYWORDS.items():
        if keyword in lowered:
            return category
    return None


def categories_in_basket(
    items: List[Tuple[str, Optional[str]]],
) -> List[str]:
    found: List[str] = []
    seen = set()
    for name, cat in items:
        resolved = infer_category(name, cat)
        if resolved and resolved not in seen:
            seen.add(resolved)
            found.append(resolved)
    return found


def products_for_category(category: str) -> List[CatalogProduct]:
    return [p for p in PRODUCTS if p.category == category]
