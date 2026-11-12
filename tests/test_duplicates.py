import pandas as pd
import pytest

from open_finance_toolkit import (
    MissingColumnsError,
    find_duplicates,
    mark_duplicates,
    remove_duplicates,
)


@pytest.fixture
def data():
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(
                ["2026-10-06", "2026-10-06 14:30", "2026-10-06", "2026-10-07"],
                format="mixed",
            ),
            "Type": ["Expense"] * 4,
            "Category": ["Shopping"] * 4,
            "Amount": [1299.0, 1299.001, 500.0, 1299.0],
            "Description": ["UPI-AMAZON", "  upi-amazon ", "UPI-AMAZON", "UPI-AMAZON"],
        }
    )


def test_mark_flags_later_copies(data):
    assert mark_duplicates(data)["IsDuplicate"].tolist() == [False, True, False, False]


def test_comparison_ignores_case_spaces_time_and_tiny_rounding(data):
    assert len(find_duplicates(data)) == 1


def test_keep_last_and_keep_false(data):
    assert mark_duplicates(data, keep="last")["IsDuplicate"].tolist() == [True, False, False, False]
    assert mark_duplicates(data, keep=False)["IsDuplicate"].tolist() == [True, True, False, False]


def test_remove_duplicates_resets_index(data):
    result = remove_duplicates(data)
    assert len(result) == 3
    assert result.index.tolist() == [0, 1, 2]
    assert "IsDuplicate" not in result.columns


def test_custom_subset(data):
    flagged = mark_duplicates(data, subset=["Amount"])
    assert flagged["IsDuplicate"].sum() == 2  # 1299.0 appears twice after rounding, plus 1299.001


def test_input_is_not_modified(data):
    before = data.copy()
    mark_duplicates(data)
    pd.testing.assert_frame_equal(data, before)


def test_unknown_subset_column(data):
    with pytest.raises(MissingColumnsError, match="Nope"):
        mark_duplicates(data, subset=["Nope"])


def test_no_comparable_columns():
    with pytest.raises(MissingColumnsError):
        mark_duplicates(pd.DataFrame({"X": [1]}))
