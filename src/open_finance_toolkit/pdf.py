"""Read bank statement PDFs (experimental).

Reading PDFs needs the optional ``pdfplumber`` package::

    pip install "open-finance-toolkit[pdf]"

Only text-based statements work. A scanned or photographed statement is just
a picture, and reading it would need OCR, which this library does not do.

At the moment only the HDFC Bank statement layout is understood. A PDF
statement is a page of positioned text, not a table, so the reader works out
the columns from the position of the header words and then reads each row
from the text that lines up under them.
"""

from __future__ import annotations

import os
import re
from typing import IO, Dict, List, Optional, Union

import pandas as pd

from .exceptions import (
    FileReadError,
    MissingColumnsError,
    MissingDependencyError,
    NoValidTransactionsError,
)
from .formats import normalize_header
from .importer import clean_transactions

Source = Union[str, "os.PathLike[str]", bytes, IO]

#: Column names, in the order they appear on an HDFC statement.
HDFC_COLUMNS = [
    "Date",
    "Narration",
    "Chq./Ref.No.",
    "Value Dt",
    "Withdrawal Amt.",
    "Deposit Amt.",
    "Closing Balance",
]

_HEADER_KEYS = {
    "date": "Date",
    "narration": "Narration",
    "chqrefno": "Chq./Ref.No.",
    "valuedt": "Value Dt",
    "withdrawalamt": "Withdrawal Amt.",
    "depositamt": "Deposit Amt.",
    "closingbalance": "Closing Balance",
}

_DATE = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
_END_OF_TABLE = "statement summary"

#: Words on one printed line can differ in height by a point or two.
_LINE_TOLERANCE = 3
#: A wrapped narration line sits close under its row. Anything further away
#: is something else on the page (a footer, a note) and is ignored.
_MAX_WRAP_GAP = 24


def load_pdf_transactions(
    source: Source, *, password: Optional[str] = None, dayfirst: bool = True
) -> pd.DataFrame:
    """Read a text-based HDFC Bank statement PDF and return clean transactions.

    The result is the same table that ``load_transactions`` returns for a
    CSV: ``Date``, ``Type``, ``Category``, ``Amount`` and ``Description``.

    ``source`` can be a file path, raw ``bytes`` or an open file. If the PDF
    is protected, pass its ``password``.

    This is **experimental**: it has been built against one statement style,
    so please report statements it cannot read.

    Raises ``MissingDependencyError`` if ``pdfplumber`` is not installed,
    ``FileReadError`` if the file cannot be opened (including a missing or
    wrong password), and ``MissingColumnsError`` if no HDFC-style table is
    found.
    """
    table = read_pdf_table(source, password=password)
    cleaned = clean_transactions(table, layout="hdfc", dayfirst=dayfirst)
    cleaned.attrs["source"] = "pdf"
    return cleaned


def read_pdf_table(source: Source, *, password: Optional[str] = None) -> pd.DataFrame:
    """Return the raw rows of the statement table as text, before cleaning."""
    pdfplumber = _import_pdfplumber()

    file = _as_file(source)  # raises its own clear errors, so keep it outside the try
    try:
        document = pdfplumber.open(file, password=password)
    except Exception as exc:  # pdfminer raises several unrelated error types
        raise FileReadError(_open_error_message(exc)) from exc

    with document:
        pages = [page.extract_words() for page in document.pages]

    rows = _extract_rows(pages)
    if not rows:
        raise NoValidTransactionsError(
            "No transactions found in this PDF. It may be a scanned image, "
            "which this library cannot read."
        )
    return pd.DataFrame(rows, columns=HDFC_COLUMNS)


def _import_pdfplumber():
    try:
        import pdfplumber
    except ImportError as exc:
        raise MissingDependencyError(
            "Reading PDFs needs the optional 'pdfplumber' package. "
            'Install it with: pip install "open-finance-toolkit[pdf]"'
        ) from exc
    return pdfplumber


def _as_file(source: Source):
    if isinstance(source, (bytes, bytearray)):
        import io

        return io.BytesIO(bytes(source))
    if isinstance(source, (str, os.PathLike)):
        if not os.path.exists(source):
            raise FileReadError(f"Could not open '{source}': file not found")
        return source
    if hasattr(source, "read"):
        if hasattr(source, "seek"):
            source.seek(0)
        return source
    raise TypeError(
        f"source must be a file path, bytes, or an open file, not {type(source).__name__}"
    )


def _open_error_message(exc: Exception) -> str:
    name = type(exc).__name__
    if "Password" in name:
        return "This PDF is password protected. Pass the password with password=..."
    return "Unable to read this PDF. Please check that it is a valid statement."


def _extract_rows(pages: List[list]) -> List[List[str]]:
    """Turn the positioned words of every page into table rows."""
    columns = _find_columns(pages)
    rows: List[List[str]] = []
    current: Optional[Dict[str, str]] = None
    last_top = 0.0

    for page_index, words in enumerate(pages):
        started = page_index > 0  # on page 1, ignore everything above the header
        # A wrapped line is only joined to a row on the same page. The top of
        # a later page holds a page number and branch details, not narration.
        last_top = float("-inf")
        for line in _group_lines(words):
            top = line[0]["top"]
            text = " ".join(w["text"] for w in line).lower()

            if not started:
                if top > columns["header_top"] + _LINE_TOLERANCE:
                    started = True
                else:
                    continue

            if _END_OF_TABLE in text:
                return _finish(rows, current)

            cells = _assign_cells(line, columns)
            if _DATE.match(cells["Date"]):
                if current is not None:
                    rows.append(_as_row(current))
                current = cells
                last_top = top
            elif current is not None and cells["Narration"] and top - last_top <= _MAX_WRAP_GAP:
                current["Narration"] = (current["Narration"] + " " + cells["Narration"]).strip()
                last_top = top

    return _finish(rows, current)


def _finish(rows: List[List[str]], current: Optional[Dict[str, str]]) -> List[List[str]]:
    if current is not None:
        rows.append(_as_row(current))
    return rows


def _as_row(cells: Dict[str, str]) -> List[str]:
    return [cells[name] for name in HDFC_COLUMNS]


def _group_lines(words: list) -> List[list]:
    """Group words into printed lines, top to bottom, each left to right."""
    lines: List[list] = []
    for word in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if lines and abs(word["top"] - lines[-1][0]["top"]) <= _LINE_TOLERANCE:
            lines[-1].append(word)
        else:
            lines.append([word])
    return [sorted(line, key=lambda w: w["x0"]) for line in lines]


def _find_columns(pages: List[list]) -> dict:
    """Locate the header row and work out where each column sits.

    Only the first page has a header row, so its positions are used for every
    page. Text columns are matched on their left edge and number columns on
    their right edge, because numbers are right-aligned.
    """
    for words in pages[:1]:
        for line in _group_lines(words):
            found = _header_cells(line)
            if len(found) == len(HDFC_COLUMNS):
                return _boundaries(found, line[0]["top"], words)
    raise MissingColumnsError(
        "Could not find an HDFC statement table (Date, Narration, Withdrawal Amt., "
        "Deposit Amt., Closing Balance) in this PDF.",
        detected=[],
    )


def _header_cells(line: list) -> dict:
    """Find the header names on a line, as ``{name: {"x0": .., "x1": ..}}``.

    A header such as "Withdrawal Amt." may come out of the PDF as one word or
    as two, depending on how the bank's software wrote the spaces. So up to
    three neighbouring words are joined before looking the name up.
    """
    found = {}
    index = 0
    while index < len(line):
        for size in (3, 2, 1):
            group = line[index : index + size]
            if len(group) < size:
                continue
            name = _HEADER_KEYS.get(normalize_header("".join(w["text"] for w in group)))
            if name:
                found[name] = {"x0": group[0]["x0"], "x1": group[-1]["x1"]}
                index += size
                break
        else:
            index += 1
    return found


def _boundaries(found: dict, header_top: float, words: list) -> dict:
    # A header such as "Narration" is centred over its column, but the text
    # under it starts at the left, much further over. So the edge of the Date
    # column comes from where the dates actually end, not from the header.
    date_ends = [
        w["x1"]
        for w in words
        if w["top"] > header_top + _LINE_TOLERANCE
        and w["x0"] < found["Narration"]["x0"]
        and _DATE.match(w["text"])
    ]
    if not date_ends:
        raise NoValidTransactionsError(
            "No transactions found in this PDF. It may be a scanned image, "
            "which this library cannot read."
        )
    # Numbers are right-aligned, so split the number columns halfway between
    # the right edges of neighbouring headers.
    value_right = found["Value Dt"]["x1"]
    withdrawal_right = found["Withdrawal Amt."]["x1"]
    deposit_right = found["Deposit Amt."]["x1"]
    closing_right = found["Closing Balance"]["x1"]
    return {
        "header_top": header_top,
        "date_limit": max(date_ends) + 3,
        "chq_left": found["Chq./Ref.No."]["x0"] - 10,
        "value_left": found["Value Dt"]["x0"] - 5,
        "withdrawal_from": (value_right + withdrawal_right) / 2,
        "deposit_from": (withdrawal_right + deposit_right) / 2,
        "closing_from": (deposit_right + closing_right) / 2,
    }


def _assign_cells(line: list, columns: dict) -> Dict[str, str]:
    cells: Dict[str, List[str]] = {name: [] for name in HDFC_COLUMNS}
    for word in line:
        left, right = word["x0"], word["x1"]
        if left < columns["date_limit"]:
            name = "Date"
        elif left < columns["chq_left"]:
            name = "Narration"
        elif left < columns["value_left"]:
            name = "Chq./Ref.No."
        elif right <= columns["withdrawal_from"]:
            name = "Value Dt"
        elif right <= columns["deposit_from"]:
            name = "Withdrawal Amt."
        elif right <= columns["closing_from"]:
            name = "Deposit Amt."
        else:
            name = "Closing Balance"
        cells[name].append(word["text"])
    return {name: " ".join(parts).strip() for name, parts in cells.items()}
