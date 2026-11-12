"""Totals and monthly or yearly summaries.

The maths is the same as the original dashboard:

* savings = income - expenses
* savings rate = savings / income x 100, or 0 when there is no income
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from .exceptions import MissingColumnsError
from .schema import EXPENSE, INCOME

_PERIOD_FORMATS = {"month": "%Y-%m", "year": "%Y"}


@dataclass(frozen=True)
class Totals:
    """Headline numbers for a set of transactions."""

    income: float
    expenses: float
    savings: float
    savings_rate: float  # percent of income, 0.0 when income is 0


def totals(transactions: pd.DataFrame) -> Totals:
    """Add up income, expenses, savings and savings rate."""
    _require(transactions, "Type", "Amount")
    income = float(transactions.loc[transactions["Type"] == INCOME, "Amount"].sum())
    expenses = float(transactions.loc[transactions["Type"] == EXPENSE, "Amount"].sum())
    savings = income - expenses
    rate = (savings / income * 100) if income > 0 else 0.0
    return Totals(income=income, expenses=expenses, savings=savings, savings_rate=rate)


def summarize(transactions: pd.DataFrame, by: str = "month") -> pd.DataFrame:
    """Summarise transactions by month or year.

    Returns one row per period, oldest first, with the columns ``Period``
    (``"2026-11"`` for months, ``"2026"`` for years), ``Income``,
    ``Expenses``, ``Savings`` and ``SavingsRate`` (percent).
    """
    if by not in _PERIOD_FORMATS:
        raise ValueError("by must be 'month' or 'year'")
    _require(transactions, "Date", "Type", "Amount")

    period = transactions["Date"].dt.strftime(_PERIOD_FORMATS[by]).rename("Period")
    table = (
        transactions.assign(Period=period)
        .pivot_table(
            index="Period",
            columns="Type",
            values="Amount",
            aggfunc="sum",
            fill_value=0,
        )
        .reindex(columns=[INCOME, EXPENSE], fill_value=0)
        .sort_index()
    )
    table = table.rename(columns={EXPENSE: "Expenses", INCOME: "Income"})
    table["Savings"] = table["Income"] - table["Expenses"]
    rate = table["Savings"] / table["Income"] * 100
    table["SavingsRate"] = rate.where(table["Income"] > 0, 0.0)
    table.columns.name = None
    return table.reset_index().astype(
        {"Income": float, "Expenses": float, "Savings": float, "SavingsRate": float}
    )


def spending_by_category(transactions: pd.DataFrame, top: Optional[int] = None) -> pd.DataFrame:
    """Expenses added up per category, biggest first.

    Columns: ``Category``, ``Amount`` and ``Share`` (percent of all expenses).
    Pass ``top=5`` to keep only the five biggest categories.
    """
    _require(transactions, "Type", "Category", "Amount")
    spending = (
        transactions[transactions["Type"] == EXPENSE]
        .groupby("Category", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False, kind="stable")
        .reset_index(drop=True)
    )
    total = spending["Amount"].sum()
    spending["Share"] = (spending["Amount"] / total * 100) if total > 0 else 0.0
    return spending.head(top) if top is not None else spending


def _require(transactions: pd.DataFrame, *columns: str) -> None:
    missing = [c for c in columns if c not in transactions.columns]
    if missing:
        raise MissingColumnsError(
            f"Columns not found: {', '.join(missing)}. "
            "Use load_transactions() to create a standard table.",
            detected=[str(c) for c in transactions.columns],
        )
