"""Scrape books from category listings on Books to Scrape."""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from typing import Any

import requests
from bs4 import BeautifulSoup

from scrapers.common import absolute_url, fetch_soup, iter_pages, make_session

START_URL = "https://books.toscrape.com/"
SOURCE = "Books to Scrape"
RATING_VALUES = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
LOGGER = logging.getLogger(__name__)


def _category_links(soup: BeautifulSoup) -> list[tuple[str, str]]:
    categories: list[tuple[str, str]] = []
    for link in soup.select(".side_categories ul li ul li a"):
        href = link.get("href")
        if href:
            categories.append((link.get_text(" ", strip=True), href))
    return categories


def _parse_book(article: BeautifulSoup, page_url: str, category: str) -> dict[str, Any] | None:
    title_link = article.select_one("h3 a")
    price_node = article.select_one(".price_color")
    availability_node = article.select_one(".availability")
    if not title_link or not title_link.get("href"):
        LOGGER.warning("Skipping a product card missing its title or URL on %s", page_url)
        return None

    title = title_link.get("title") or title_link.get_text(" ", strip=True)
    price_text = price_node.get_text(" ", strip=True) if price_node else ""
    amount = re.sub(r"[^0-9.]", "", price_text)
    try:
        price = float(amount) if amount else None
    except ValueError:
        LOGGER.warning("Invalid book price %r on %s", price_text, page_url)
        price = None

    rating_node = article.select_one(".star-rating")
    rating = None
    if rating_node:
        rating = next(
            (RATING_VALUES[class_name] for class_name in rating_node.get("class", []) if class_name in RATING_VALUES),
            None,
        )

    return {
        "source": SOURCE,
        "source_url": absolute_url(page_url, title_link.get("href")),
        "name_or_title": title,
        "category": category or None,
        "price": price,
        "rating": rating,
        "author": None,
        "author_url": None,
        "tags": [],
        "description": None,
        "availability": availability_node.get_text(" ", strip=True) if availability_node else None,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def scrape_books() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    session = make_session()
    try:
        try:
            home = fetch_soup(session, START_URL)
            categories = _category_links(home)
        except requests.RequestException:
            LOGGER.exception("Could not load Books to Scrape category index; falling back to catalogue")
            categories = []

        targets = [(name, absolute_url(START_URL, href)) for name, href in categories]
        if not targets:
            targets = [("", START_URL)]

        for target_index, (category, first_url) in enumerate(targets):
            if target_index:
                time.sleep(0.15)
            if not first_url:
                continue
            for page_url, soup in iter_pages(session, first_url, "li.next a", LOGGER):
                product_cards = soup.select("article.product_pod")
                if not product_cards:
                    LOGGER.warning("No product cards found on %s", page_url)
                for card in product_cards:
                    record = _parse_book(card, page_url, category)
                    if record:
                        records.append(record)
    finally:
        session.close()
    return records