"""Read a transactions CSV and turn it into a clean, standard table."""

from __future__ import annotations

import csv
import io
import os
from typing import IO, Union

import pandas as pd

from .exceptions import (
    EmptyFileError,
    FileReadError,
    MissingColumnsError,
    NoValidTransactionsError,
)
from .formats import normalize_header, resolve_layout
from .parsing import parse_amount, parse_dates
from .schema import EXPENSE, INCOME, OUTPUT_COLUMNS, UNCATEGORISED

#: Bank statements often start with a few lines of account details before the
#: real table. We look this far down for the header row.
MAX_PREAMBLE_LINES = 60

Source = Union[str, "os.PathLike[str]", bytes, IO]


def load_transactions(
    source: Source, *, layout: str = "auto", dayfirst: bool = True
) -> pd.DataFrame:
    """Read a CSV file and return clean transactions.

    ``source`` can be a file path, raw ``bytes``, or an open file (including
    a Streamlit ``UploadedFile``). A plain ``str`` is always treated as a path.

    The result has the columns ``Date``, ``Type`` (``Income`` or ``Expense``),
    ``Category``, ``Amount`` (always positive) and ``Description``.

    ``layout="auto"`` detects the statement format. Pass a layout name (see
    ``open_finance_toolkit.LAYOUTS``) to force one. ``dayfirst`` controls how
    ambiguous dates such as ``03/04/2026`` are read; ISO dates
    (``2026-04-03``) are always read year-first.

    Raises a subclass of ``OpenFinanceError`` if the file is empty, unreadable,
    has unrecognised columns, or contains no valid transactions.
    """
    text = _decode(_read_bytes(source)).replace("\r\n", "\n").replace("\r", "\n")
    if not text.strip():
        raise EmptyFileError("Your CSV file is empty. Please upload a file with data.")

    lines = text.split("\n")
    header_line = _find_header_line(lines, layout)

    try:
        table = pd.read_csv(
            io.StringIO(text),
            skiprows=header_line or 0,
            dtype=str,
            keep_default_na=False,
            skipinitialspace=True,
            on_bad_lines="skip",
        )
    except pd.errors.EmptyDataError as exc:
        raise EmptyFileError("Your CSV file is empty. Please upload a file with data.") from exc
    except (pd.errors.ParserError, ValueError) as exc:
        raise FileReadError("Unable to read this CSV. Please check its format.") from exc

    return clean_transactions(table, layout=layout, dayfirst=dayfirst)


def clean_transactions(
    table: pd.DataFrame, *, layout: str = "auto", dayfirst: bool = True
) -> pd.DataFrame:
    """Clean a DataFrame of raw statement rows into standard transactions.

    Use this when you already have a DataFrame. ``load_transactions`` calls it
    after reading the file. Rows with an unreadable date or amount, an unknown
    type, or a zero amount are dropped; how many is stored in
    ``result.attrs["dropped_rows"]``, and the layout used in
    ``result.attrs["layout"]``.
    """
    columns = {}
    for original in table.columns:
        columns.setdefault(normalize_header(original), str(original))

    found = resolve_layout(columns, layout)
    if found is None:
        raise MissingColumnsError(
            "CSV must contain Date, Type, Category and Amount columns "
            "(or a Date column with Debit and Credit columns, "
            "or a Date column with one signed Amount column).",
            detected=[str(c) for c in table.columns],
        )
    chosen, mapping = found
    table = table.rename(columns=lambda c: str(c))

    dates = parse_dates(table[mapping["date"]], dayfirst=dayfirst)
    if "description" in mapping:
        description = table[mapping["description"]].astype(str).str.strip()
    else:
        description = pd.Series("", index=table.index)

    if chosen.kind == "typed":
        kind = table[mapping["txn_type"]].astype(str).str.strip().str.title()
        category = table[mapping["category"]].astype(str).str.strip()
        category = category.where(category != "", UNCATEGORISED)
        amount = parse_amount(table[mapping["amount"]])
        valid = kind.isin([INCOME, EXPENSE]) & (amount >= 0)
    else:
        if chosen.kind == "debit_credit":
            money_out = parse_amount(table[mapping["debit"]]).fillna(0).abs()
            money_in = parse_amount(table[mapping["credit"]]).fillna(0).abs()
            net = money_in - money_out
        else:
            net = parse_amount(table[mapping["amount"]])
        kind = pd.Series(INCOME, index=table.index).where(net > 0, EXPENSE)
        amount = net.abs()
        category = pd.Series(UNCATEGORISED, index=table.index)
        valid = net.notna() & (net != 0)

    result = pd.DataFrame(
        {
            "Date": dates,
            "Type": kind,
            "Category": category,
            "Amount": amount.astype(float),
            "Description": description,
        }
    )
    keep = valid & dates.notna() & result["Amount"].notna()
    cleaned = result[keep].reset_index(drop=True)[OUTPUT_COLUMNS]

    if cleaned.empty:
        raise NoValidTransactionsError("No valid transactions found. Please check your CSV.")

    cleaned.attrs["layout"] = chosen.name
    cleaned.attrs["dropped_rows"] = int(len(result) - len(cleaned))
    return cleaned


def _read_bytes(source: Source) -> bytes:
    if isinstance(source, (bytes, bytearray)):
        return bytes(source)
    if isinstance(source, (str, os.PathLike)):
        try:
            with open(source, "rb") as handle:
                return handle.read()
        except OSError as exc:
            raise FileReadError(f"Could not open '{source}': {exc.strerror or exc}") from exc
    if hasattr(source, "read"):
        data = source.read()
        if hasattr(source, "seek"):
            try:
                source.seek(0)  # let the caller read the same file again
            except (OSError, ValueError):
                pass
        return data.encode("utf-8") if isinstance(data, str) else bytes(data)
    raise TypeError(
        f"source must be a file path, bytes, or an open file, not {type(source).__name__}"
    )


def _decode(data: bytes) -> str:
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1")


def _find_header_line(lines: list, layout: str) -> int:
    """Index of the first line that looks like a header row, or 0."""
    for index, line in enumerate(lines[:MAX_PREAMBLE_LINES]):
        if not line.strip():
            continue
        try:
            cells = next(csv.reader([line]))
        except (csv.Error, StopIteration):
            continue
        columns = {}
        for cell in cells:
            columns.setdefault(normalize_header(cell), cell)
        if resolve_layout(columns, layout) is not None:
            return index
    return 0
