"""The standard shape of a cleaned transactions table."""

from __future__ import annotations

#: Columns present in every DataFrame returned by ``load_transactions``.
OUTPUT_COLUMNS = ["Date", "Type", "Category", "Amount", "Description"]

#: Allowed values in the ``Type`` column.
INCOME = "Income"
EXPENSE = "Expense"

#: Category given to transactions that have not been categorised yet.
UNCATEGORISED = "Uncategorised"
