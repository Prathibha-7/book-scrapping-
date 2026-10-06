import unittest

from bs4 import BeautifulSoup

from processing.cleaning import clean_record
from scrapers.books_scraper import _parse_book
from scrapers.quotes_scraper import _parse_quote


class ScraperParserTests(unittest.TestCase):
    def test_book_card_fields(self):
        html = """
        <article class="product_pod">
          <p class="star-rating Three"></p>
          <h3><a href="book.html" title=" A Book ">A Book</a></h3>
          <p class="price_color">£12.50</p>
          <p class="availability"> In stock </p>
        </article>
        """
        book = _parse_book(BeautifulSoup(html, "html.parser").article, "https://example.test/category/", "Fiction")
        self.assertEqual(book["name_or_title"], " A Book ")
        self.assertEqual(book["source_url"], "https://example.test/category/book.html")
        self.assertEqual(book["price"], 12.5)
        self.assertEqual(book["rating"], 3)
        self.assertEqual(book["category"], "Fiction")

    def test_quote_fields_and_author_link(self):
        html = """
        <div class="quote">
          <span class="text">“ A quote ”</span>
          <small class="author">Ada Lovelace</small>
          <a href="/author/Ada-Lovelace">(about)</a>
          <div class="tags"><a class="tag"> math </a></div>
        </div>
        """
        quote = _parse_quote(BeautifulSoup(html, "html.parser").div, "https://quotes.toscrape.com/page/1/")
        self.assertEqual(quote["name_or_title"], "“ A quote ”")
        self.assertEqual(quote["author"], "Ada Lovelace")
        self.assertEqual(quote["tags"], ["math"])
        self.assertEqual(quote["author_url"], "https://quotes.toscrape.com/author/Ada-Lovelace")
        self.assertEqual(clean_record(quote)["author_url"], "https://quotes.toscrape.com/author/Ada-Lovelace")


if __name__ == "__main__":
    unittest.main()