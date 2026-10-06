"""Shared HTTP helpers used by source scrapers."""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENT = "PracticeDataPipeline/1.0 (educational scraping; contact: local assignment)"
REQUEST_DELAY_SECONDS = 0.15


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    retry = Retry(
        total=3,
        connect=3,
        read=2,
        status=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch_soup(session: requests.Session, url: str) -> BeautifulSoup:
    response = session.get(url, timeout=(5, 20))
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def iter_pages(
    session: requests.Session,
    first_url: str,
    next_selector: str,
    logger: logging.Logger,
) -> Iterator[tuple[str, BeautifulSoup]]:
    current_url = first_url
    visited: set[str] = set()
    while current_url and current_url not in visited:
        visited.add(current_url)
        try:
            soup = fetch_soup(session, current_url)
        except requests.RequestException:
            logger.exception("Failed to fetch page %s; stopping this page sequence", current_url)
            return
        yield current_url, soup
        next_link = soup.select_one(next_selector)
        href = next_link.get("href") if next_link else None
        current_url = urljoin(current_url, href) if href else ""
        if current_url:
            time.sleep(REQUEST_DELAY_SECONDS)


def absolute_url(page_url: str, href: str | None) -> str | None:
    if not href:
        return None
    return urljoin(page_url, href.strip())