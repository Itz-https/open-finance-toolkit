import pandas as pd
import pytest

from open_finance_toolkit import MissingColumnsError, categorize


def frame(rows):
    return pd.DataFrame(rows, columns=["Type", "Category", "Description"]).assign(
        Date=pd.Timestamp("2026-11-01"), Amount=100.0
    )


def test_default_rules_for_common_indian_merchants():
    df = frame(
        [
            ("Expense", "Uncategorised", "UPI-SWIGGY-ORDER 123"),
            ("Expense", "Uncategorised", "UPI/ZOMATO/998877"),
            ("Expense", "Uncategorised", "UBER INDIA SYSTEMS"),
            ("Expense", "Uncategorised", "IRCTC TICKET"),
            ("Expense", "Uncategorised", "AMAZON PAY INDIA"),
            ("Expense", "Uncategorised", "BESCOM ELECTRICITY"),
            ("Expense", "Uncategorised", "ATM CASH WDL"),
            ("Income", "Uncategorised", "NEFT-ACME-SALARY OCT"),
            ("Income", "Uncategorised", "INT.PD:01-07-2026"),
        ]
    )
    result = categorize(df)["Category"].tolist()
    assert result == [
        "Food",
        "Food",
        "Transport",
        "Travel",
        "Shopping",
        "Bills & Utilities",
        "Cash Withdrawal",
        "Salary",
        "Interest",
    ]


def test_unmatched_rows_stay_uncategorised():
    df = frame([("Expense", "Uncategorised", "SOMETHING UNKNOWN")])
    assert categorize(df).loc[0, "Category"] == "Uncategorised"


def test_keywords_match_word_starts_not_the_middle_of_words():
    df = frame([("Expense", "Uncategorised", "HUBERT STORES")])  # contains "uber"
    assert categorize(df).loc[0, "Category"] == "Uncategorised"


def test_income_and_expense_rules_are_separate():
    # "interest" is an income rule, so a loan interest debit must not match it.
    df = frame([("Expense", "Uncategorised", "LOAN INTEREST DEBIT")])
    assert categorize(df).loc[0, "Category"] == "Loans & EMI"


def test_user_rules_win_over_defaults():
    df = frame([("Expense", "Uncategorised", "SWIGGY INSTAMART")])
    result = categorize(df, {"Groceries": ["swiggy instamart"]})
    assert result.loc[0, "Category"] == "Groceries"


def test_existing_categories_are_kept_unless_overwrite():
    df = frame([("Expense", "My Own Label", "SWIGGY")])
    assert categorize(df).loc[0, "Category"] == "My Own Label"
    assert categorize(df, overwrite=True).loc[0, "Category"] == "Food"


def test_blank_category_is_filled():
    df = frame([("Expense", "", "ZOMATO")])
    assert categorize(df).loc[0, "Category"] == "Food"


def test_can_turn_off_defaults_and_set_default_label():
    df = frame([("Expense", "Uncategorised", "SWIGGY")])
    result = categorize(df, use_defaults=False, default="Other")
    assert result.loc[0, "Category"] == "Other"


def test_does_not_change_the_input_frame():
    df = frame([("Expense", "Uncategorised", "SWIGGY")])
    categorize(df)
    assert df.loc[0, "Category"] == "Uncategorised"


def test_string_instead_of_list_is_accepted():
    df = frame([("Expense", "Uncategorised", "VET CLINIC")])
    assert categorize(df, {"Pets": "vet clinic"}).loc[0, "Category"] == "Pets"


def test_requires_description_column():
    with pytest.raises(MissingColumnsError, match="Description"):
        categorize(pd.DataFrame({"Type": ["Expense"], "Category": ["x"]}))
