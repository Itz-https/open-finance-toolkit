# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- The demo dashboard accepts HDFC statement PDFs (with an optional password box), using `load_pdf_transactions`.
- A dark theme file, `.streamlit/config.toml`, so the dashboard's inputs match its dark design.

## [0.2.0] - 2026-11-13

### Added
- `load_pdf_transactions` reads text-based HDFC Bank statement PDFs (experimental). It needs the optional extra `pip install "open-finance-toolkit[pdf]"`; the base install still needs only pandas.
- `MissingDependencyError`, raised when an optional package is not installed.
- The command line tool accepts a `.pdf` file.
- A fake-data HDFC PDF for tests, with the script that generates it (`tests/data/make_fake_hdfc_pdf.py`).

## [0.1.0] - 2026-11-12

First release as a reusable library. It grew out of the Personal Finance
Analytics dashboard.

### Added
- `load_transactions` and `clean_transactions` to read and standardise CSVs, with automatic layout detection and skipping of lines above the table.
- Layouts: `standard`, `generic-debit-credit`, `generic-signed`, and unverified `hdfc`, `sbi`, `icici`, `axis`.
- `categorize`, a keyword-based categoriser with built-in rules and support for your own.
- `mark_duplicates`, `find_duplicates`, `remove_duplicates`.
- `totals`, `summarize` (by month or year) and `spending_by_category`.
- A command-line tool: `open-finance-toolkit summary` and `open-finance-toolkit categories`.
- Tests, continuous integration, contribution guidelines and issue templates.

### Changed
- The Streamlit dashboard moved to `examples/dashboard/` and is otherwise unchanged.

### Fixed
- ISO dates such as `2026-11-01` are no longer read day-first (which turned them into 11 January). This fix is in the library. The demo dashboard still has the old behaviour.
- A blank category now becomes `Uncategorised` instead of the text `nan`.
