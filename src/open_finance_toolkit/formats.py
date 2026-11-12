"""Statement layouts: which column headers mean what.

A *layout* describes how a CSV names its columns. Open Finance Toolkit tries
each layout in ``LAYOUTS`` in order and uses the first one whose required
columns are all present.

Adding support for a new bank usually means adding one ``Layout`` entry to
this file. See ``docs/adding-a-bank-format.md``.

Headers are compared after normalising them: lower-case, with every
character that is not a letter or digit removed. ``"Withdrawal Amt."`` and
``"withdrawal amt"`` both become ``"withdrawalamt"``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Tuple


def normalize_header(value: object) -> str:
    """Lower-case a header and strip everything except letters and digits."""
    return re.sub(r"[^a-z0-9]", "", str(value).replace("﻿", "").lower())


@dataclass(frozen=True)
class Layout:
    """How one kind of CSV names its columns.

    ``kind`` decides how amounts are read:

    * ``"typed"``: a ``Type`` column says Income or Expense, and ``Amount`` is
      always positive. This is the format the original dashboard used.
    * ``"debit_credit"``: separate Debit (money out) and Credit (money in)
      columns, as most Indian bank statements have.
    * ``"signed"``: one ``Amount`` column where negative means money out.

    ``verified`` is ``True`` only when the layout has been checked against a
    real statement. Unverified layouts are best-effort guesses based on
    commonly seen headers. Please help verify them (see CONTRIBUTING.md).
    """

    name: str
    label: str
    kind: str
    date: Tuple[str, ...]
    description: Tuple[str, ...] = ()
    amount: Tuple[str, ...] = ()
    txn_type: Tuple[str, ...] = ()
    category: Tuple[str, ...] = ()
    debit: Tuple[str, ...] = ()
    credit: Tuple[str, ...] = ()
    verified: bool = False

    def match(self, columns: Mapping[str, str]) -> Optional[Dict[str, str]]:
        """Return ``{field: original column name}`` if this layout fits.

        ``columns`` maps normalised header to original header. Returns
        ``None`` when a required column is missing.
        """
        fields = {
            "date": self.date,
            "description": self.description,
            "amount": self.amount,
            "txn_type": self.txn_type,
            "category": self.category,
            "debit": self.debit,
            "credit": self.credit,
        }
        required = {
            "typed": ("date", "txn_type", "category", "amount"),
            "debit_credit": ("date", "debit", "credit"),
            "signed": ("date", "amount"),
        }[self.kind]

        mapping: Dict[str, str] = {}
        for field, aliases in fields.items():
            found = next((columns[a] for a in aliases if a in columns), None)
            if found is None:
                if field in required:
                    return None
                continue
            mapping[field] = found
        return mapping


_GENERIC_DATES = (
    "date",
    "transactiondate",
    "txndate",
    "trandate",
    "postingdate",
    "valuedate",
    "valuedt",
)
_GENERIC_DESCRIPTIONS = (
    "description",
    "narration",
    "particulars",
    "transactionremarks",
    "remarks",
    "details",
    "notes",
    "note",
)

#: Layouts are tried top to bottom; the first match wins.
LAYOUTS: Tuple[Layout, ...] = (
    Layout(
        name="standard",
        label="Date, Type, Category, Amount (the original dashboard format)",
        kind="typed",
        date=("date",),
        txn_type=("type",),
        category=("category",),
        amount=("amount",),
        description=_GENERIC_DESCRIPTIONS,
        verified=True,
    ),
    # Bank layouts below are based on commonly seen headers and have NOT yet
    # been verified against real statements. They are flagged on purpose.
    Layout(
        name="hdfc",
        label="HDFC Bank (unverified)",
        kind="debit_credit",
        date=("date",),
        description=("narration",),
        debit=("withdrawalamt",),
        credit=("depositamt",),
    ),
    Layout(
        name="sbi",
        label="State Bank of India (unverified)",
        kind="debit_credit",
        date=("txndate",),
        description=("description",),
        debit=("debit",),
        credit=("credit",),
    ),
    Layout(
        name="icici",
        label="ICICI Bank (unverified)",
        kind="debit_credit",
        date=("transactiondate",),
        description=("transactionremarks",),
        debit=("withdrawalamountinr",),
        credit=("depositamountinr",),
    ),
    Layout(
        name="axis",
        label="Axis Bank (unverified)",
        kind="debit_credit",
        date=("trandate",),
        description=("particulars",),
        debit=("dr",),
        credit=("cr",),
    ),
    Layout(
        name="generic-debit-credit",
        label="Any CSV with separate Debit and Credit columns",
        kind="debit_credit",
        date=_GENERIC_DATES,
        description=_GENERIC_DESCRIPTIONS,
        debit=(
            "debit",
            "debitamount",
            "withdrawal",
            "withdrawalamt",
            "withdrawalamount",
            "withdrawalamountinr",
            "dr",
            "paidout",
        ),
        credit=(
            "credit",
            "creditamount",
            "deposit",
            "depositamt",
            "depositamount",
            "depositamountinr",
            "cr",
            "paidin",
        ),
    ),
    Layout(
        name="generic-signed",
        label="Any CSV with one signed Amount column (negative = money out)",
        kind="signed",
        date=_GENERIC_DATES,
        description=_GENERIC_DESCRIPTIONS,
        amount=("amount", "transactionamount", "amt"),
    ),
)


def resolve_layout(
    columns: Mapping[str, str], name: str = "auto"
) -> Optional[Tuple[Layout, Dict[str, str]]]:
    """Find the layout that fits ``columns``.

    ``columns`` maps normalised header to original header. With
    ``name="auto"`` every layout is tried in order. Otherwise only the named
    layout is tried. Returns ``None`` when nothing fits.
    """
    if name == "auto":
        candidates: Tuple[Layout, ...] = LAYOUTS
    else:
        by_name = {layout.name: layout for layout in LAYOUTS}
        if name not in by_name:
            known = ", ".join(["auto"] + list(by_name))
            raise ValueError(f"Unknown layout {name!r}. Choose one of: {known}")
        candidates = (by_name[name],)

    for layout in candidates:
        mapping = layout.match(columns)
        if mapping is not None:
            return layout, mapping
    return None
