import pandas as pd
import pytest

from open_finance_toolkit import (
    MissingColumnsError,
    load_transactions,
    spending_by_category,
    summarize,
    totals,
)

# The exact sample data the original Streamlit dashboard shipped with.
DASHBOARD_SAMPLE = pd.DataFrame(
    {
        "Date": pd.to_datetime(
            ["2026-11-01", "2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06"]
        ),
        "Type": ["Income", "Expense", "Expense", "Expense", "Income", "Expense"],
        "Category": ["Salary", "Food", "Travel", "Shopping", "Freelance", "Bills"],
        "Amount": [25000.0, 3500.0, 2000.0, 4500.0, 5000.0, 1500.0],
    }
)


def test_totals_match_the_original_dashboard_maths():
    result = totals(DASHBOARD_SAMPLE)
    assert result.income == 30000
    assert result.expenses == 11500
    assert result.savings == 18500
    assert result.savings_rate == pytest.approx(18500 / 30000 * 100)


def test_savings_rate_is_zero_without_income():
    expenses_only = DASHBOARD_SAMPLE[DASHBOARD_SAMPLE["Type"] == "Expense"]
    result = totals(expenses_only)
    assert result.income == 0
    assert result.savings == -11500
    assert result.savings_rate == 0.0


def test_monthly_summary():
    data = pd.concat(
        [
            DASHBOARD_SAMPLE,
            DASHBOARD_SAMPLE.assign(Date=DASHBOARD_SAMPLE["Date"] - pd.DateOffset(months=1)),
        ]
    )
    result = summarize(data, by="month")
    assert result["Period"].tolist() == ["2026-10", "2026-11"]
    assert result["Income"].tolist() == [30000, 30000]
    assert result["Expenses"].tolist() == [11500, 11500]
    assert result["Savings"].tolist() == [18500, 18500]
    assert result["SavingsRate"].iloc[0] == pytest.approx(61.6667, abs=1e-3)


def test_yearly_summary_and_chronological_order():
    data = pd.concat(
        [
            DASHBOARD_SAMPLE,
            DASHBOARD_SAMPLE.assign(Date=DASHBOARD_SAMPLE["Date"] - pd.DateOffset(years=1)),
        ]
    )
    result = summarize(data, by="year")
    assert result["Period"].tolist() == ["2025", "2026"]


def test_period_with_only_expenses_has_zero_rate_and_income():
    data = DASHBOARD_SAMPLE[DASHBOARD_SAMPLE["Type"] == "Expense"]
    result = summarize(data)
    assert result.loc[0, "Income"] == 0
    assert result.loc[0, "SavingsRate"] == 0.0


def test_summarize_rejects_bad_period():
    with pytest.raises(ValueError):
        summarize(DASHBOARD_SAMPLE, by="week")


def test_spending_by_category():
    result = spending_by_category(DASHBOARD_SAMPLE)
    assert result["Category"].tolist() == ["Shopping", "Food", "Travel", "Bills"]
    assert result["Amount"].tolist() == [4500, 3500, 2000, 1500]
    assert result["Share"].sum() == pytest.approx(100)
    assert len(spending_by_category(DASHBOARD_SAMPLE, top=2)) == 2


def test_spending_by_category_with_no_expenses():
    income_only = DASHBOARD_SAMPLE[DASHBOARD_SAMPLE["Type"] == "Income"]
    assert spending_by_category(income_only).empty


def test_requires_standard_columns():
    with pytest.raises(MissingColumnsError):
        totals(pd.DataFrame({"x": [1]}))


def test_end_to_end_with_the_example_file():
    from pathlib import Path

    path = Path(__file__).resolve().parent.parent / "examples" / "sample_transactions.csv"
    data = load_transactions(path)
    result = totals(data[data["Date"].dt.strftime("%Y-%m") == "2026-11"])
    assert result.income == 30000
    assert result.expenses == 11500
