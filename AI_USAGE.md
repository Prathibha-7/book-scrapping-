# AI Usage

## Tool and use

- **Tool:** GitHub Copilot in VS Code.
- **Used for:** Interpreting the assignment, proposing the shared record model and page traversal, drafting both source parsers and the processing pipeline, generating focused tests, and drafting project documentation.

## Representative prompts

- “Build a Python-based web scraping and data-processing pipeline that collects information from Books to Scrape and Quotes to Scrape, handles pagination, cleans and validates records, deduplicates them, and produces a consolidated CSV and summary.”
- “Include an AI_USAGE.md with the tools used, representative prompts, AI-assisted parts, review changes, issues found, and verification; make the README cover the full assignment checklist and package a ZIP deliverable.”

## AI-assisted parts

AI assistance contributed to the initial structure and code in `main.py`, `scrapers/`, `processing/`, and `tests/`, plus the first drafts of `README.md` and this file. The candidate remains responsible for understanding and reviewing the submitted implementation.

## Review and corrections

- The first AI_USAGE draft did not meet the assignment's required level of detail; it was expanded to include prompts, scope, review notes, and verification.
- The quote parser initially extracted each author's profile URL, but the first shared schema discarded that field. `author_url` was added to cleaning, validation, CSV output, and tests.
- The implementation uses category listings and product URLs for book records, and containing page URLs for quote records because quotes do not have individual URLs. The README documents these choices and duplicate behavior across categories.
- No authentication, CAPTCHA, robots restriction, access control, credentials, or secrets are used. The provided sites are the only scrape targets.

## Testing and verification

- Ran `python -m unittest discover -s tests -v`; all tests passed, covering source parsing, cleaning, validation, quote/book duplicate keys, and normalized duplicate detection.
- Ran `python main.py` against both public practice sites. The verified run collected 1,000 books and 100 quotes, rejected 0 records, removed 0 duplicates, and wrote 1,100 final records.
- After adding `author_url` to the schema and aligning book records with the shared fields, tests passed again and `output/final_dataset.csv` plus `output/summary_report.json` were regenerated.