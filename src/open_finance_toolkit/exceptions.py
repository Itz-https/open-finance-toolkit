"""Errors raised by Open Finance Toolkit.

Every error the library raises on purpose inherits from ``OpenFinanceError``,
so applications can catch just one class::

    try:
        df = load_transactions("statement.csv")
    except OpenFinanceError as error:
        print(f"Could not read the file: {error}")
"""

from __future__ import annotations

from typing import List, Optional


class OpenFinanceError(Exception):
    """Base class for all errors raised on purpose by this library."""


class EmptyFileError(OpenFinanceError):
    """The file contains no data at all."""


class FileReadError(OpenFinanceError):
    """The file could not be opened or is not a readable CSV."""


class MissingColumnsError(OpenFinanceError):
    """The columns needed for the requested operation were not found.

    ``detected`` lists the column names that were actually found, which is
    handy for showing a helpful message to the user.
    """

    def __init__(self, message: str, detected: Optional[List[str]] = None) -> None:
        super().__init__(message)
        self.detected: List[str] = list(detected or [])


class NoValidTransactionsError(OpenFinanceError):
    """The file was read, but no valid transaction rows were left."""


class MissingDependencyError(OpenFinanceError):
    """An optional package needed for this feature is not installed.

    For example, reading PDFs needs ``pip install "open-finance-toolkit[pdf]"``.
    """
