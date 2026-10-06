"""Remove normalized duplicate books and quotes while preserving first occurrence."""

from __future__ import annotations

import re
import unicodedata
from typing import Any


def _key_text(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return " ".join(text.split())


def duplicate_key(record: dict[str, Any]) -> tuple[str, ...]:
    source = _key_text(record.get("source"))
    if source == "books to scrape":
        url = _key_text(record.get("source_url"))
        if url:
            return source, url.rstrip("/")
        return source, _key_text(record.get("name_or_title"))

    quote = re.sub(r"[^\w\s]", " ", _key_text(record.get("name_or_title")), flags=re.UNICODE)
    quote = " ".join(quote.split())
    return source, quote, _key_text(record.get("author"))


def deduplicate_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    unique: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    duplicate_count = 0
    for record in records:
        key = duplicate_key(record)
        if key in seen:
            duplicate_count += 1
            continue
        seen.add(key)
        unique.append(record)
    return unique, duplicate_count