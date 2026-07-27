"""LLM output validation metrics (offline)."""

import json

from app.llm.json_utils import extract_json_text, parse_json, validate_model
from app.schemas.analysis import InsightListOutput, ReviewAnalysisOutput


def test_schema_validity_rate_on_samples():
    samples = [
        {
            "sentiment": "negative",
            "sentiment_intensity": 0.8,
            "emotion": "anger",
            "complaint_category": "Delivery",
            "motivation": None,
            "unmet_need": "speed",
            "jtbd": "get groceries fast",
            "shopping_behaviour": "urgent",
            "customer_segment": "student",
            "discovery": {
                "mentions_non_grocery_category": False,
                "named_categories": [],
                "discovery_barriers": ["delivery"],
                "latent_cross_category_intent": False,
                "cross_category_detail": None,
            },
        }
    ]
    valid = 0
    for item in samples:
        validate_model(json.dumps(item), ReviewAnalysisOutput)
        valid += 1
    assert valid / len(samples) == 1.0


def test_insight_list_schema():
    payload = {
        "insights": [
            {
                "problem": "Users struggle to discover non-grocery categories",
                "evidence": "Multiple reviews mention unawareness",
                "frequency": 3,
                "example_review_ids": [1, 2, 3],
                "customer_segment": "urban",
                "business_impact": "category discovery",
                "opportunity": "surface adjacent categories",
                "confidence_score": 0.7,
            }
        ]
    }
    model = validate_model(json.dumps(payload), InsightListOutput)
    assert len(model.insights) == 1


def test_markdown_wrapped_json_parses():
    inner = {"insights": []}
    raw = f"Sure:\n```json\n{json.dumps(inner)}\n```"
    parsed = parse_json(raw)
    assert parsed == inner
    assert extract_json_text(raw).startswith("{")
