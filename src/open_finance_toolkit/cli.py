"""Command-line interface: ``open-finance-toolkit summary statement.csv``."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__
from .categorize import categorize
from .duplicates import remove_duplicates
from .exceptions import OpenFinanceError
from .importer import load_transactions
from .summary import spending_by_category, summarize, totals


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="open-finance-toolkit",
        description="Summarise a bank statement or transactions CSV.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (
        ("summary", "Show totals and a monthly or yearly summary"),
        ("categories", "Show spending per category"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("file", help="Path to the CSV file")
        command.add_argument(
            "--layout", default="auto", help="Statement layout (default: auto-detect)"
        )
        command.add_argument(
            "--no-dayfirst",
            action="store_true",
            help="Read ambiguous dates like 03/04/2026 as month first",
        )
        command.add_argument(
            "--remove-duplicates",
            action="store_true",
            help="Drop rows that look like duplicates before calculating",
        )
        if name == "summary":
            command.add_argument(
                "--by", choices=("month", "year"), default="month", help="Group by"
            )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = load_transactions(args.file, layout=args.layout, dayfirst=not args.no_dayfirst)
        if args.remove_duplicates:
            data = remove_duplicates(data)
        data = categorize(data)
    except OpenFinanceError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    if args.command == "summary":
        overall = totals(data)
        print(f"Income:       {overall.income:,.2f}")
        print(f"Expenses:     {overall.expenses:,.2f}")
        print(f"Savings:      {overall.savings:,.2f}")
        print(f"Savings rate: {overall.savings_rate:.1f}%")
        print()
        print(summarize(data, by=args.by).to_string(index=False, float_format="{:,.2f}".format))
    else:
        print(spending_by_category(data).to_string(index=False, float_format="{:,.2f}".format))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
