"""Normalize parsed source records into a consistent output shape."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit

SCHEMA_FIELDS = (
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "author_url",
    "tags",
    "description",
    "availability",
    "scraped_at",
)


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None


def normalize_url(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    parts = urlsplit(text)
    if parts.scheme.lower() not in {"http", "https"} or not parts.netloc:
        return None
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, parts.query, ""))


def clean_record(raw: dict[str, Any]) -> dict[str, Any]:
    record = {field: raw.get(field) for field in SCHEMA_FIELDS}
    for field in ("source", "name_or_title", "category", "author", "description", "availability", "scraped_at"):
        record[field] = clean_text(record[field])
    record["source_url"] = normalize_url(record["source_url"])
    record["author_url"] = normalize_url(record["author_url"])
    record["tags"] = [cleaned for item in (record["tags"] or []) if (cleaned := clean_text(item))]

    price = record["price"]
    if price is not None:
        try:
            record["price"] = float(price)
        except (TypeError, ValueError):
            record["price"] = price

    rating = record["rating"]
    if rating is not None:
        try:
            number = float(rating)
            record["rating"] = int(number) if number.is_integer() else number
        except (TypeError, ValueError):
            record["rating"] = rating
    return record