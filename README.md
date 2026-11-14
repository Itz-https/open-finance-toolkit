# Open Finance Toolkit

Clean, categorise and summarise bank transaction CSVs in Python, with a focus on Indian bank statement formats.

[![PyPI](https://img.shields.io/pypi/v/open-finance-toolkit.svg)](https://pypi.org/project/open-finance-toolkit/)
[![CI](https://github.com/Itz-https/open-finance-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/Itz-https/open-finance-toolkit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> **Status: alpha (v0.1).** The core works and is tested, but the bank layouts for HDFC, SBI, ICICI and Axis are built from commonly seen column headers and have **not yet been checked against real statements**. If you have a statement from any bank, you can help. See [Contributing](#contributing).

## Why this exists

Every bank exports transactions slightly differently. Some put account details above the table. Some use separate Debit and Credit columns, others one signed Amount column. Dates may be `03/04/2026` or `2026-04-03`, and amounts look like `1,25,000.50`. Every developer who builds a budgeting tool ends up rewriting the same cleaning code.

Open Finance Toolkit does that part once, so you can focus on your app.

- Reads messy statement CSVs and returns one clean, standard table
- Reads HDFC statement PDFs too (experimental, optional `[pdf]` extra)
- Detects the layout automatically and skips lines above the table
- Categorises transactions with simple rules you can read and extend
- Flags duplicate transactions without deleting anything behind your back
- Calculates income, expenses, savings and savings rate
- Summarises by month or year
- Runs entirely on your computer. No network calls, no accounts, no tracking.

## Install

```bash
pip install open-finance-toolkit
```

Requires Python 3.9 or newer. The only dependency is `pandas`.

To also run the demo dashboard, install the optional extra: `pip install "open-finance-toolkit[dashboard]"`.

## Quick start

```python
from open_finance_toolkit import load_transactions, categorize, summarize, totals

transactions = load_transactions("statement.csv")   # any supported layout
transactions = categorize(transactions)             # fill in categories

print(totals(transactions))
print(summarize(transactions, by="month"))
```

Example output from the included fictional statement:

```text
Income:          85,312.00
Expenses:        32,567.50
Savings:         52,744.50
Savings rate:        61.8%

 Period  Income  Expenses  Savings  SavingsRate
2026-10 85312.0   32567.5  52744.5    61.825417
```

Run the full tour with `python examples/quickstart.py`.

### Command line

```bash
open-finance-toolkit summary statement.csv --by month
open-finance-toolkit categories statement.csv
```

## What you get back

`load_transactions` returns a pandas DataFrame with the same columns no matter which bank the file came from:

| Column | Meaning |
|---|---|
| `Date` | Transaction date (datetime) |
| `Type` | `Income` or `Expense` |
| `Category` | Category, or `Uncategorised` until you call `categorize` |
| `Amount` | Always positive |
| `Description` | The bank's narration text |

## Supported layouts

| Layout | Status |
|---|---|
| `standard`: Date, Type, Category, Amount | Verified (the original dashboard format) |
| `generic-debit-credit`: any file with separate Debit and Credit columns | Works on test data, not yet on real statements |
| `generic-signed`: any file with one signed Amount column | Works on test data, not yet on real statements |
| `hdfc`, `sbi`, `icici`, `axis` | **Unverified.** Based on commonly seen headers |
| HDFC statement **PDF** (`load_pdf_transactions`) | **Experimental.** Needs `pip install "open-finance-toolkit[pdf]"`. Checked against one statement style |

Anything the named layouts miss usually still loads through the generic ones. Details and how to add a bank are in [docs/adding-a-bank-format.md](docs/adding-a-bank-format.md).

## Documentation

- [Website](https://itz-https.github.io/open-finance-toolkit/): overview, supported banks and how to help
- [Live dashboard](https://open-finance-toolkit-ryrgetx4uzgmsftogm6kan.streamlit.app): upload a CSV or HDFC PDF (use fictional data)
- [Usage guide](docs/usage.md): every function with examples
- [Adding a bank format](docs/adding-a-bank-format.md)
- [Roadmap](docs/roadmap.md)
- [Publishing to PyPI](docs/publishing-to-pypi.md) (for maintainers)
- [Changelog](CHANGELOG.md)

## The demo dashboard

The original Streamlit dashboard lives in [`examples/dashboard`](examples/dashboard) as a demo of what you can build on top of the library.

## Contributing

Contributions of every size are welcome, including fixing a typo. The most valuable thing you can do is **verify or add a bank format**: open a [bank format request](https://github.com/Itz-https/open-finance-toolkit/issues/new?template=bank_format_request.yml) with the column headers of your statement (never the real transactions). Read [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## Privacy

Never post real statements, account numbers or personal details in issues or pull requests. The test data in this repository is entirely fictional.

## License

[MIT](LICENSE)
