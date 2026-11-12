"""Rule-based transaction categorisation.

Categorisation works by looking for keywords in the ``Description`` column.
It is deliberately simple and predictable: no machine learning, no network
calls, and you can read every rule. Add your own rules for your own merchants.
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import pandas as pd

from .exceptions import MissingColumnsError
from .schema import EXPENSE, INCOME, UNCATEGORISED

Rules = Mapping[str, Iterable[str]]

#: Keywords for money coming in. Order matters: the first category that
#: matches wins.
DEFAULT_INCOME_RULES: Dict[str, Tuple[str, ...]] = {
    "Salary": ("salary", "payroll", "sal credit"),
    "Interest": ("interest", "int.pd", "int pd", "int.credit"),
    "Dividends": ("dividend",),
    "Refunds": ("refund", "reversal", "cashback"),
}

#: Keywords for money going out. Order matters: the first match wins.
DEFAULT_EXPENSE_RULES: Dict[str, Tuple[str, ...]] = {
    "Rent": ("house rent", "rent payment", "landlord", "rent"),
    "Loans & EMI": ("emi", "loan repayment", "loan", "home loan"),
    "Food": (
        "swiggy",
        "zomato",
        "restaurant",
        "cafe",
        "starbucks",
        "dominos",
        "mcdonald",
        "kfc",
        "pizza",
        "bakery",
    ),
    "Groceries": (
        "bigbasket",
        "blinkit",
        "zepto",
        "dmart",
        "grocery",
        "supermarket",
        "reliance fresh",
    ),
    "Transport": (
        "uber",
        "ola cabs",
        "olacabs",
        "rapido",
        "metro",
        "petrol",
        "fuel",
        "fastag",
        "indian oil",
        "bpcl",
        "hpcl",
    ),
    "Travel": (
        "irctc",
        "redbus",
        "makemytrip",
        "goibibo",
        "indigo",
        "air india",
        "vistara",
        "airbnb",
        "oyo",
    ),
    "Shopping": (
        "amazon",
        "flipkart",
        "myntra",
        "ajio",
        "meesho",
        "nykaa",
        "decathlon",
        "shoppers stop",
    ),
    "Bills & Utilities": (
        "electricity",
        "bescom",
        "water bill",
        "gas bill",
        "broadband",
        "recharge",
        "airtel",
        "jio",
        "bsnl",
        "vodafone",
        "tata play",
        "act fibernet",
        "dth",
    ),
    "Entertainment": (
        "netflix",
        "spotify",
        "hotstar",
        "prime video",
        "youtube",
        "bookmyshow",
        "pvr",
        "inox",
        "sonyliv",
        "zee5",
    ),
    "Health": (
        "pharmacy",
        "apollo",
        "medplus",
        "pharmeasy",
        "1mg",
        "hospital",
        "clinic",
        "diagnostic",
    ),
    "Education": (
        "udemy",
        "coursera",
        "tuition",
        "school fee",
        "college fee",
        "exam fee",
    ),
    "Investments": (
        "zerodha",
        "groww",
        "upstox",
        "mutual fund",
        "sip",
        "nps",
        "ppf",
    ),
    "Insurance": ("insurance", "lic of india", "lic premium"),
    "Cash Withdrawal": ("atm", "cash wdl", "cash withdrawal", "nfs"),
}


def categorize(
    transactions: pd.DataFrame,
    rules: Optional[Rules] = None,
    *,
    overwrite: bool = False,
    use_defaults: bool = True,
    default: str = UNCATEGORISED,
) -> pd.DataFrame:
    """Return a copy of ``transactions`` with categories filled in.

    ``rules`` maps a category name to a list of keywords, for example
    ``{"Pets": ["petco", "vet clinic"]}``. Your rules are checked first, for
    both income and expenses, then the built-in rules for the row's type.
    Matching ignores upper/lower case and looks for the keyword at the start
    of a word, so ``"uber"`` matches ``"UPI-UBER INDIA"`` but not ``"hubert"``.

    By default only rows that are still ``Uncategorised`` (or blank) are
    changed. Pass ``overwrite=True`` to re-categorise every row. Rows that
    match nothing get ``default``.

    Needs a ``Description`` column; ``load_transactions`` provides one.
    """
    for needed in ("Description", "Category", "Type"):
        if needed not in transactions.columns:
            raise MissingColumnsError(
                f"categorize() needs a '{needed}' column.",
                detected=[str(c) for c in transactions.columns],
            )

    result = transactions.copy()
    text = result["Description"].astype(str).str.lower()
    current = result["Category"].astype(str).str.strip()
    editable = pd.Series(True, index=result.index)
    if not overwrite:
        editable = current.isin(["", UNCATEGORISED, default])

    assigned = pd.Series(False, index=result.index)
    new_category = current.copy()

    user_rules = _compile(rules or {})
    income_rules = _compile(DEFAULT_INCOME_RULES) if use_defaults else []
    expense_rules = _compile(DEFAULT_EXPENSE_RULES) if use_defaults else []

    is_income = result["Type"] == INCOME
    is_expense = result["Type"] == EXPENSE
    passes = [
        (user_rules, pd.Series(True, index=result.index)),
        (income_rules, is_income),
        (expense_rules, is_expense),
    ]
    for compiled, applies_to in passes:
        for category, pattern in compiled:
            hit = editable & ~assigned & applies_to & text.str.contains(pattern)
            new_category = new_category.where(~hit, category)
            assigned = assigned | hit

    blank = editable & ~assigned
    new_category = new_category.where(~blank, default)
    result["Category"] = new_category
    return result


def _compile(rules: Rules) -> List[Tuple[str, "re.Pattern[str]"]]:
    compiled = []
    for category, keywords in rules.items():
        words: Sequence[str] = [keywords] if isinstance(keywords, str) else list(keywords)
        words = [w.strip().lower() for w in words if w and w.strip()]
        if not words:
            continue
        alternatives = "|".join(re.escape(w) for w in words)
        compiled.append((category, re.compile(rf"(?<![a-z0-9])(?:{alternatives})")))
    return compiled
