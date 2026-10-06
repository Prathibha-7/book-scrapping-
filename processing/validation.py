"""Basic validation for normalized pipeline records."""

from __future__ import annotations

import math
from urllib.parse import urlsplit
from typing import Any


def validate_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not record.get("source"):
        errors.append("missing source")
    if record.get("source") not in {"Books to Scrape", "Quotes to Scrape"}:
        errors.append("unrecognized source")
    if not record.get("name_or_title"):
        errors.append("missing name_or_title")

    url = record.get("source_url")
    if not url:
        errors.append("missing source_url")
    else:
        parts = urlsplit(url)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            errors.append("invalid source_url")

    author_url = record.get("author_url")
    if author_url:
        parts = urlsplit(author_url)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            errors.append("invalid author_url")

    price = record.get("price")
    if price is not None:
        if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price < 0:
            errors.append("invalid price")

    rating = record.get("rating")
    if rating is not None:
        if isinstance(rating, bool) or not isinstance(rating, (int, float)) or not math.isfinite(rating) or not 1 <= rating <= 5:
            errors.append("rating outside expected range 1-5")
    return errors