"""Open Finance Toolkit: clean, categorise and summarise bank transactions.

Quick example::

    from open_finance_toolkit import load_transactions, categorize, summarize

    transactions = categorize(load_transactions("statement.csv"))
    print(summarize(transactions, by="month"))
"""

__version__ = "0.1.0"

from .categorize import (
    DEFAULT_EXPENSE_RULES,
    DEFAULT_INCOME_RULES,
    categorize,
)
from .duplicates import find_duplicates, mark_duplicates, remove_duplicates
from .exceptions import (
    EmptyFileError,
    FileReadError,
    MissingColumnsError,
    NoValidTransactionsError,
    OpenFinanceError,
)
from .formats import LAYOUTS, Layout
from .importer import clean_transactions, load_transactions
from .summary import Totals, spending_by_category, summarize, totals

__all__ = [
    "__version__",
    "load_transactions",
    "clean_transactions",
    "categorize",
    "DEFAULT_INCOME_RULES",
    "DEFAULT_EXPENSE_RULES",
    "mark_duplicates",
    "find_duplicates",
    "remove_duplicates",
    "totals",
    "summarize",
    "spending_by_category",
    "Totals",
    "LAYOUTS",
    "Layout",
    "OpenFinanceError",
    "EmptyFileError",
    "FileReadError",
    "MissingColumnsError",
    "NoValidTransactionsError",
]
