"""Small, well-tested helpers for turning messy text into dates and numbers."""

from __future__ import annotations

import re

import pandas as pd

_CURRENCY = re.compile(r"(?i)₹|\brs\.?|\binr\b")


def parse_dates(values: pd.Series, *, dayfirst: bool = True) -> pd.Series:
    """Convert text dates to datetimes. Unreadable values become ``NaT``.

    Dates written the international way (``2026-11-01``) are always read as
    year-month-day. Everything else (``01/11/2026``, ``1 Nov 2026``) is read
    with ``dayfirst``, which defaults to ``True`` because that is how Indian
    bank statements write dates.

    Reading ISO dates first matters: forcing ``dayfirst=True`` on
    ``2026-11-01`` would wrongly give 11 January.
    """
    text = values.astype(str).str.strip()
    iso = pd.to_datetime(text, format="ISO8601", errors="coerce")
    leftover = text.where(iso.isna())
    fallback = pd.to_datetime(leftover, format="mixed", dayfirst=dayfirst, errors="coerce")
    return iso.fillna(fallback)


def parse_amount(values: pd.Series) -> pd.Series:
    """Convert text amounts to numbers. Unreadable values become ``NaN``.

    Understands thousands separators (``1,25,000.50``), currency marks
    (``₹``, ``Rs.``, ``INR``) and accounting negatives (``(500.00)``).
    """
    text = values.astype(str).str.strip()
    text = text.str.replace(_CURRENCY, "", regex=True)
    text = text.str.replace(",", "", regex=False).str.strip()
    negative = text.str.match(r"^\(.*\)$")
    number = pd.to_numeric(text.str.strip("()").str.strip(), errors="coerce")
    return number.where(~negative, -number)
