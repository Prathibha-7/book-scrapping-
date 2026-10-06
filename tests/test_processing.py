import unittest

from processing.cleaning import clean_record
from processing.deduplication import deduplicate_records
from processing.validation import validate_record


def record(**overrides):
    values = {
        "source": "Quotes to Scrape",
        "source_url": "https://quotes.toscrape.com/page/1/",
        "name_or_title": "  Be   curious! ",
        "category": "Quote",
        "price": None,
        "rating": None,
        "author": "Ada Lovelace",
        "tags": [" math ", ""],
        "description": None,
        "availability": None,
        "scraped_at": "2026-01-01T00:00:00+00:00",
    }
    values.update(overrides)
    return values


class ProcessingTests(unittest.TestCase):
    def test_cleaning_normalizes_values_and_schema(self):
        cleaned = clean_record(record())
        self.assertEqual(cleaned["name_or_title"], "Be curious!")
        self.assertEqual(cleaned["tags"], ["math"])
        self.assertEqual(set(cleaned), {
            "source", "source_url", "name_or_title", "category", "price", "rating",
            "author", "author_url", "tags", "description", "availability", "scraped_at",
        })

    def test_validation_rejects_bad_price_and_rating(self):
        cleaned = clean_record(record(source="Books to Scrape", price="bad", rating=6))
        self.assertIn("invalid price", validate_record(cleaned))
        self.assertIn("rating outside expected range 1-5", validate_record(cleaned))

    def test_deduplication_ignores_case_spacing_and_quote_punctuation(self):
        first = clean_record(record())
        second = clean_record(record(name_or_title="be curious", author=" ADA   LOVELACE "))
        unique, duplicate_count = deduplicate_records([first, second])
        self.assertEqual(len(unique), 1)
        self.assertEqual(duplicate_count, 1)

    def test_book_deduplication_uses_normalized_url(self):
        first = clean_record(record(
            source="Books to Scrape",
            source_url="https://books.toscrape.com/catalogue/a-book_1/index.html",
            name_or_title="A Book",
            author=None,
            category="Fiction",
            price=10.0,
            rating=3,
        ))
        second = clean_record(record(
            source="Books to Scrape",
            source_url="HTTPS://Books.toscrape.com/catalogue/a-book_1/index.html",
            name_or_title="A Book (Travel)",
            author=None,
            category="Travel",
            price=10.0,
            rating=3,
        ))
        unique, duplicate_count = deduplicate_records([first, second])
        self.assertEqual(len(unique), 1)
        self.assertEqual(duplicate_count, 1)
        self.assertEqual(unique[0]["category"], "Fiction")


if __name__ == "__main__":
    unittest.main()