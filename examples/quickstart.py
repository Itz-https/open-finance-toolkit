"""A five-minute tour of Open Finance Toolkit.

Run from the project folder after installing the package:

    python examples/quickstart.py
"""

from pathlib import Path

from open_finance_toolkit import (
    categorize,
    find_duplicates,
    load_transactions,
    spending_by_category,
    summarize,
    totals,
)

here = Path(__file__).parent

# 1. Read a bank-style statement. The layout is detected automatically and
#    the lines above the table (account details) are skipped.
transactions = load_transactions(here / "sample_debit_credit.csv")
print(f"Layout detected: {transactions.attrs['layout']}")

# 2. Fill in categories from the Description column.
transactions = categorize(transactions, rules={"Subscriptions": ["netflix"]})

# 3. Check for duplicates (flagged, never deleted automatically).
print("\nPossible duplicates:")
print(find_duplicates(transactions)[["Date", "Amount", "Description"]].to_string(index=False))

# 4. Headline numbers.
summary = totals(transactions)
print(f"\nIncome:       {summary.income:>12,.2f}")
print(f"Expenses:     {summary.expenses:>12,.2f}")
print(f"Savings:      {summary.savings:>12,.2f}")
print(f"Savings rate: {summary.savings_rate:>11.1f}%")

# 5. Breakdowns.
print("\nBy month:")
print(summarize(transactions, by="month").to_string(index=False))
print("\nTop spending categories:")
print(spending_by_category(transactions, top=3).to_string(index=False))
