"""Scrape quote records from Quotes to Scrape."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from bs4 import BeautifulSoup

from scrapers.common import absolute_url, iter_pages, make_session

START_URL = "https://quotes.toscrape.com/"
SOURCE = "Quotes to Scrape"
LOGGER = logging.getLogger(__name__)


def _parse_quote(quote: BeautifulSoup, page_url: str) -> dict[str, Any] | None:
    text_node = quote.select_one(".text")
    author_node = quote.select_one(".author")
    if not text_node or not author_node:
        LOGGER.warning("Skipping an incomplete quote record on %s", page_url)
        return None

    author_link = quote.select_one(".author + a")
    author_url = absolute_url(page_url, author_link.get("href")) if author_link else None
    tags = [tag.get_text(" ", strip=True) for tag in quote.select(".tags .tag")]
    return {
        "source": SOURCE,
        "source_url": page_url,
        "name_or_title": text_node.get_text(" ", strip=True),
        "category": "Quote",
        "price": None,
        "rating": None,
        "author": author_node.get_text(" ", strip=True),
        "tags": tags,
        "description": None,
        "availability": None,
        "author_url": author_url,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def scrape_quotes() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    session = make_session()
    try:
        for page_url, soup in iter_pages(session, START_URL, "li.next a", LOGGER):
            quote_cards = soup.select(".quote")
            if not quote_cards:
                LOGGER.warning("No quote records found on %s", page_url)
            for card in quote_cards:
                record = _parse_quote(card, page_url)
                if record:
                    records.append(record)
    finally:
        session.close()
    return records