# Multi-source scraping pipeline

A small Python pipeline that collects the public practice data from [Books to Scrape](https://books.toscrape.com/) and [Quotes to Scrape](https://quotes.toscrape.com/), normalizes it, validates it, removes duplicates, and writes one CSV plus a JSON summary.

## Setup and run

Use Python 3.10 or newer. From this directory:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Run the unit tests with `python -m unittest discover -s tests -v`. The first run creates `output/` and `logs/`.

Dependencies are listed in `requirements.txt`: Requests handles HTTP and retries; Beautiful Soup parses the returned HTML. No browser automation or external service credentials are needed.

## Source observations

- Books to Scrape presents book cards as `article.product_pod`. The site links category listing pages in its sidebar; each category page provides product title, product URL, price, stock status, and a star-rating class. Its `li.next a` link gives the next page. Category listings provide the category without making a separate request for each product detail page.
- Quotes to Scrape presents entries in `.quote` elements with `.text`, `.author`, and `.tags .tag` children. The author’s `about` link is available, but quote records have no individual page URL. The containing page URL is therefore retained as `source_url`. Pagination is provided by `li.next a`.
- The data sites are explicitly intended for scraping practice. The scraper uses ordinary GET requests and does not attempt authentication or access-control workarounds.

## Data model

The CSV contains `source`, `source_url`, `name_or_title`, `category`, `price`, `rating`, `author`, `author_url`, `tags`, `description`, `availability`, and `scraped_at`. Fields absent from a source remain empty. `tags` is stored as a pipe-separated string in CSV. Book prices are numeric GBP amounts as displayed by the source; book ratings are integers from 1 to 5. Quotes use the quote text as `name_or_title`, set category to `Quote`, and leave price/rating empty. Quote author names and their public `about` URLs are retained; author biography pages are not fetched.

## Cleaning, validation, and duplicates

Whitespace is collapsed and trimmed, URLs are restricted to HTTP(S), and prices/ratings are converted to numbers where possible. Validation requires a recognized source, non-empty title/text, a valid-looking source URL, a non-negative numeric price when present, and a rating from 1 through 5 when present. Invalid rows are rejected and counted; missing optional source-specific values remain empty.

Duplicate keys are source-specific and case-insensitive. Books use their normalized product URL (falling back to normalized title if the URL is absent). Quotes use normalized quote text plus normalized author; Unicode compatibility forms, whitespace, casing, and punctuation are normalized for comparison. The first occurrence is retained and subsequent matches are removed. Keeping the source in the key prevents unrelated records from different sites being collapsed.

## Outputs and failure behavior

- `output/final_dataset.csv`: consolidated validated, deduplicated records.
- `output/summary_report.json`: per-source collected counts, validated counts, rejection reasons, duplicates removed, final count, and execution duration.
- `logs/scraper.log`: progress and recoverable page/record failures.

HTTP requests have connect/read timeouts, retries for common transient errors and rate limiting, and a short pause between pages. A failed page ends that source’s current page sequence; the other categories/pages and the other source continue where possible. A complete source-level exception is logged and does not prevent the other source from running.

## Processing details

Cleaning collapses whitespace, trims text, standardizes missing optional fields as empty CSV values, normalizes valid HTTP(S) URLs, and converts prices and ratings to numeric values. Validation checks recognized sources, required title/text and source URL, valid-looking optional author URLs, non-negative numeric prices, and ratings from 1 to 5. Rejected records and validation reasons are counted in the summary and logged.

Pagination follows each page's `li.next a` link until it is absent. Book category pages are discovered from the site's category sidebar; the scraper visits each category's available pages instead of relying on a fixed page count. Both source parsers are isolated in their own modules while shared fetching and retries live in `scrapers/common.py`.

## Assumptions and limitations

- These two websites are public scraping-practice fixtures; the scraper makes ordinary GET requests only and does not interact with login pages or bypass access controls.
- A quote's containing page is its `source_url` because the site does not provide a unique quote URL. The author's public profile/about URL is stored separately.
- Book category listings can repeat a book if the source associates it with multiple categories. URL-based deduplication retains one copy, including the first category encountered.
- The scraper depends on current HTML selectors and follows available `Next` links. A material site redesign may require selector updates.
- Page failures are logged and the failed page sequence stops; already collected records and the other source still proceed.

## AI usage summary

GitHub Copilot assisted with initial code structure, parser and processing tests, and documentation. The detailed tool use, representative prompts, review corrections, and verification notes are recorded in [AI_USAGE.md](AI_USAGE.md).