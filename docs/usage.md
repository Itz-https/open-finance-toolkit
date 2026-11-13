# Usage guide

Everything below uses fictional data. Every function takes and returns a normal pandas DataFrame, so you can mix it freely with your own pandas code.

```python
from open_finance_toolkit import (
    load_transactions, clean_transactions, categorize,
    mark_duplicates, find_duplicates, remove_duplicates,
    totals, summarize, spending_by_category,
)
```

## Loading a file

```python
transactions = load_transactions("statement.csv")
```

`source` can be a file path (`str` or `pathlib.Path`), raw `bytes`, or an open file. That includes the object Streamlit gives you from `st.file_uploader`. A plain string is always treated as a path.

The result always has the columns `Date`, `Type`, `Category`, `Amount` and `Description`.

- `Type` is `Income` or `Expense`.
- `Amount` is always positive.
- `Category` is `Uncategorised` unless the file already had one.

Extra facts about the load are stored in `transactions.attrs`:

```python
transactions.attrs["layout"]        # e.g. "hdfc" or "generic-signed"
transactions.attrs["dropped_rows"]  # rows skipped (bad date, zero amount, footer lines)
```

### Dates

Dates like `2026-11-01` are always read year-month-day. Other formats, such as `03/04/2026`, are read **day first** by default because that is how Indian banks write them. For month-first files:

```python
load_transactions("us_bank.csv", dayfirst=False)
```

### Forcing a layout

Detection is automatic. To insist on one layout:

```python
from open_finance_toolkit import LAYOUTS
print([layout.name for layout in LAYOUTS])
load_transactions("statement.csv", layout="sbi")
```

### Already have a DataFrame?

```python
clean = clean_transactions(raw_dataframe)
```

### Errors

Every error the library raises on purpose inherits from `OpenFinanceError`:

```python
from open_finance_toolkit import OpenFinanceError, MissingColumnsError

try:
    transactions = load_transactions(uploaded)
except MissingColumnsError as error:
    print("Columns we found:", error.detected)
except OpenFinanceError as error:
    print(error)
```

| Error | When |
|---|---|
| `EmptyFileError` | The file has no content |
| `FileReadError` | The file can't be opened or parsed |
| `MissingColumnsError` | No layout fits. `.detected` lists the columns found |
| `NoValidTransactionsError` | Columns fit but every row was invalid, or no transactions were found in a PDF |
| `MissingDependencyError` | An optional package is missing, for example `pdfplumber` for PDFs |

## Reading a PDF statement (experimental)

Some banks only give you a PDF. Install the optional extra and use `load_pdf_transactions`:

```bash
pip install "open-finance-toolkit[pdf]"
```

```python
from open_finance_toolkit import load_pdf_transactions

transactions = load_pdf_transactions("hdfc_statement.pdf")
# Password protected? Pass it in: load_pdf_transactions("file.pdf", password="...")
```

You get the same table as `load_transactions`, so `categorize`, `summarize` and the rest work unchanged.

What to know:

- **Only HDFC Bank statements** are supported for now, and the reader has been checked against one statement style. Please report statements it can't read.
- **Text PDFs only.** A scanned or photographed statement is a picture, and reading it needs OCR, which this library does not do.
- **Check the result.** A statement's closing balance should equal opening balance plus income minus expenses. If your totals disagree with the bank's, please open an issue.
- The base install stays light: `pdfplumber` is only needed if you use PDFs. Without it you get a `MissingDependencyError` that tells you the install command.

## Categorising

```python
transactions = categorize(transactions)
```

Categories come from keywords in `Description`. For example, `UPI-SWIGGY-ORDER 123` becomes `Food`. Matching ignores case and looks for keywords at the **start of a word**, so `uber` matches `UBER INDIA` but not `HUBERT`.

Add your own rules. They are checked first:

```python
rules = {
    "Pets": ["petco", "vet clinic"],
    "Gym": ["cult.fit", "gold's gym"],
}
transactions = categorize(transactions, rules)
```

Options:

| Option | Default | Meaning |
|---|---|---|
| `overwrite` | `False` | `True` re-categorises every row, not only `Uncategorised` ones |
| `use_defaults` | `True` | `False` uses only your rules |
| `default` | `"Uncategorised"` | Label for rows that match nothing |

The built-in rules are in `DEFAULT_INCOME_RULES` and `DEFAULT_EXPENSE_RULES`. They are intentionally small, so please send additions as pull requests.

## Duplicates

Overlapping statements often repeat transactions.

```python
find_duplicates(transactions)      # only the repeated rows
mark_duplicates(transactions)      # adds an IsDuplicate True/False column
clean = remove_duplicates(transactions)
```

Rows are duplicates when `Date`, `Type`, `Amount` and `Description` all match. Case, extra spaces and time of day are ignored. Pass `subset=[...]` to compare different columns, and `keep="last"` or `keep=False` to choose which copy is left unflagged.

**Be careful.** Two real purchases can look identical, such as two ₹40 teas on the same day. Look at what `find_duplicates` returns before you remove anything.

## Totals and summaries

```python
result = totals(transactions)
result.income, result.expenses, result.savings, result.savings_rate
```

Savings is `income - expenses`. Savings rate is `savings / income * 100`, or `0` when there is no income.

```python
summarize(transactions, by="month")   # or by="year"
```

Returns one row per period, oldest first: `Period` (`"2026-11"` or `"2026"`), `Income`, `Expenses`, `Savings`, `SavingsRate`.

```python
spending_by_category(transactions, top=5)
```

Returns `Category`, `Amount` and `Share` (percent of all expenses), biggest first.

## Command line

```bash
open-finance-toolkit summary statement.csv --by year
open-finance-toolkit categories statement.csv
open-finance-toolkit summary hdfc_statement.pdf   # needs the [pdf] extra
```

Useful flags: `--layout NAME`, `--no-dayfirst`, `--remove-duplicates`.

## Using it with Streamlit

```python
import streamlit as st
from open_finance_toolkit import load_transactions, OpenFinanceError

uploaded = st.file_uploader("Upload a CSV", type=["csv"])
if uploaded:
    try:
        transactions = load_transactions(uploaded)
    except OpenFinanceError as error:
        st.error(str(error))
        st.stop()
```
