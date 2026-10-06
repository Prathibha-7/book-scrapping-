"""Run the Books to Scrape and Quotes to Scrape data pipeline."""

from __future__ import annotations

import csv
import json
import logging
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from processing.cleaning import clean_record
from processing.deduplication import deduplicate_records
from processing.validation import validate_record
from scrapers.books_scraper import scrape_books
from scrapers.quotes_scraper import scrape_quotes

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
CSV_FIELDS = [
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
]


def configure_logging() -> None:
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_DIR / "scraper.log", encoding="utf-8"),
        ],
    )


def write_outputs(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    with (OUTPUT_DIR / "final_dataset.csv").open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for record in records:
            row = record.copy()
            row["tags"] = "|".join(row["tags"] or [])
            writer.writerow(row)

    with (OUTPUT_DIR / "summary_report.json").open("w", encoding="utf-8") as json_file:
        json.dump(summary, json_file, indent=2, ensure_ascii=False)


def run_pipeline() -> dict[str, Any]:
    started = time.monotonic()
    logger = logging.getLogger("pipeline")
    scrapers = {
        "Books to Scrape": scrape_books,
        "Quotes to Scrape": scrape_quotes,
    }
    collected: list[dict[str, Any]] = []
    collected_by_source: Counter[str] = Counter()
    for source, scraper in scrapers.items():
        try:
            source_records = scraper()
            collected.extend(source_records)
            collected_by_source[source] = len(source_records)
            logger.info("Collected %d records from %s", len(source_records), source)
        except Exception:
            logger.exception("Scraper failed for %s; continuing with remaining sources", source)
            collected_by_source[source] = 0

    cleaned: list[dict[str, Any]] = []
    rejected = 0
    rejection_reasons: Counter[str] = Counter()
    for raw_record in collected:
        try:
            record = clean_record(raw_record)
            errors = validate_record(record)
            if errors:
                rejected += 1
                rejection_reasons.update(errors)
                logging.getLogger("pipeline").warning(
                    "Rejected record from %s: %s",
                    record.get("source", "unknown"),
                    ", ".join(errors),
                )
                continue
            cleaned.append(record)
        except (TypeError, ValueError) as error:
            rejected += 1
            rejection_reasons[str(error)] += 1
            logging.getLogger("pipeline").exception("Could not process a collected record")

    final_records, duplicate_count = deduplicate_records(cleaned)
    cleaned_by_source = Counter(record["source"] for record in cleaned)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "execution_seconds": round(time.monotonic() - started, 3),
        "records_collected": dict(collected_by_source),
        "records_collected_total": len(collected),
        "records_after_cleaning_and_validation": dict(cleaned_by_source),
        "records_rejected": rejected,
        "validation_rejection_reasons": dict(rejection_reasons),
        "duplicates_detected_and_removed": duplicate_count,
        "final_record_count": len(final_records),
    }
    write_outputs(final_records, summary)
    logger.info("Wrote %d final records; removed %d duplicates", len(final_records), duplicate_count)
    return summary


if __name__ == "__main__":
    configure_logging()
    run_pipeline()