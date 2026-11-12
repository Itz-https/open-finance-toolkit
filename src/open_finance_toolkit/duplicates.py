"""Find and remove duplicate transactions.

Duplicates usually appear when two statements overlap (for example, you
download January and then "last 45 days") or when a file is imported twice.

Be careful: two real purchases can look identical, such as two ₹40 teas from
the same stall on the same day. That is why ``mark_duplicates`` and
``find_duplicates`` only *flag* rows. Nothing is deleted unless you call
``remove_duplicates``.
"""

from __future__ import annotations

from typing import Optional, Sequence, Union

import pandas as pd

from .exceptions import MissingColumnsError

DEFAULT_SUBSET = ("Date", "Type", "Amount", "Description")

Keep = Union[str, bool]


def mark_duplicates(
    transactions: pd.DataFrame,
    subset: Optional[Sequence[str]] = None,
    *,
    keep: Keep = "first",
) -> pd.DataFrame:
    """Return a copy with an ``IsDuplicate`` column (``True``/``False``).

    Rows are duplicates when every column in ``subset`` matches. The default
    subset is ``Date``, ``Type``, ``Amount`` and ``Description`` (whichever
    exist). Comparison ignores case and extra spaces in text, ignores the
    time of day in dates, and rounds amounts to 2 decimals.

    ``keep`` works like pandas: ``"first"`` leaves the first copy unflagged,
    ``"last"`` leaves the last, and ``False`` flags every copy.
    """
    columns = _resolve_subset(transactions, subset)
    key = pd.DataFrame(index=transactions.index)
    for column in columns:
        key[column] = _comparable(transactions[column])
    marked = transactions.copy()
    marked["IsDuplicate"] = key.duplicated(keep=keep)
    return marked


def find_duplicates(
    transactions: pd.DataFrame,
    subset: Optional[Sequence[str]] = None,
    *,
    keep: Keep = "first",
) -> pd.DataFrame:
    """Return only the rows flagged as duplicates (see ``mark_duplicates``)."""
    marked = mark_duplicates(transactions, subset, keep=keep)
    return marked[marked["IsDuplicate"]].drop(columns="IsDuplicate")


def remove_duplicates(
    transactions: pd.DataFrame,
    subset: Optional[Sequence[str]] = None,
    *,
    keep: Keep = "first",
) -> pd.DataFrame:
    """Return a copy without the rows flagged as duplicates."""
    marked = mark_duplicates(transactions, subset, keep=keep)
    kept = marked[~marked["IsDuplicate"]].drop(columns="IsDuplicate")
    return kept.reset_index(drop=True)


def _resolve_subset(transactions: pd.DataFrame, subset: Optional[Sequence[str]]) -> Sequence[str]:
    if subset is None:
        columns = [c for c in DEFAULT_SUBSET if c in transactions.columns]
        if not columns:
            raise MissingColumnsError(
                "Could not find any of Date, Type, Amount or Description "
                "to compare. Pass subset=[...] to choose columns.",
                detected=[str(c) for c in transactions.columns],
            )
        return columns
    missing = [c for c in subset if c not in transactions.columns]
    if missing:
        raise MissingColumnsError(
            f"Columns not found: {', '.join(missing)}",
            detected=[str(c) for c in transactions.columns],
        )
    return list(subset)


def _comparable(values: pd.Series) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(values):
        return values.dt.normalize()
    if pd.api.types.is_numeric_dtype(values):
        return values.round(2)
    return values.astype(str).str.casefold().str.split().str.join(" ")
