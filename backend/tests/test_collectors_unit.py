"""Collector parser unit tests."""

import json

import pytest

from app.collectors.csv_collector import CsvReviewCollector
from app.collectors.json_collector import JsonReviewCollector
from app.core.errors import ValidationError


def test_csv_maps_review_column_alias():
    collector = CsvReviewCollector()
    body = b"review,rating\nFast delivery,5\n"
    reviews, errors = collector.parse(body)
    assert len(reviews) == 1
    assert reviews[0].text == "Fast delivery"
    assert reviews[0].rating == 5.0
    assert not errors


def test_csv_row_errors_partial_success():
    collector = CsvReviewCollector()
    body = b"text,rating\nGood app,5\n,not_a_number\n"
    reviews, errors = collector.parse(body)
    assert len(reviews) == 1
    assert len(errors) == 1
    assert errors[0]["row"] == 3


def test_csv_all_invalid_raises():
    collector = CsvReviewCollector()
    body = b"text,rating\n,5\n"
    with pytest.raises(ValidationError) as exc:
        collector.parse(body)
    assert exc.value.details


def test_json_array_root():
    collector = JsonReviewCollector()
    payload = [{"text": "Love Blinkit", "rating": 4}]
    reviews, errors = collector.parse(json.dumps(payload).encode())
    assert len(reviews) == 1
    assert not errors


def test_json_object_reviews_key():
    collector = JsonReviewCollector()
    payload = {"reviews": [{"body": "Search is slow", "rating": 2}]}
    reviews, _ = collector.parse(json.dumps(payload).encode())
    assert reviews[0].text == "Search is slow"
    assert reviews[0].rating == 2.0


def test_json_invalid_root():
    collector = JsonReviewCollector()
    with pytest.raises(ValidationError):
        collector.parse(b'"just a string"')
