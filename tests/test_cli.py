from pathlib import Path

from open_finance_toolkit.cli import main

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_summary_command(capsys):
    code = main(["summary", str(EXAMPLES / "sample_transactions.csv")])
    out = capsys.readouterr().out
    assert code == 0
    assert "Savings rate:" in out
    assert "2026-11" in out


def test_summary_by_year_with_bank_style_file(capsys):
    path = str(EXAMPLES / "sample_debit_credit.csv")
    code = main(["summary", path, "--by", "year", "--remove-duplicates"])
    out = capsys.readouterr().out
    assert code == 0
    assert "2026" in out
    # The duplicate Amazon row (1,299.00) is removed: 1299 appears only once in totals.
    assert "Expenses:     " in out


def test_categories_command(capsys):
    code = main(["categories", str(EXAMPLES / "sample_debit_credit.csv")])
    out = capsys.readouterr().out
    assert code == 0
    assert "Rent" in out


def test_missing_file_gives_friendly_error(capsys):
    code = main(["summary", "does-not-exist.csv"])
    assert code == 1
    assert "Error:" in capsys.readouterr().err


def test_unknown_layout_gives_friendly_error(capsys):
    code = main(["summary", str(EXAMPLES / "sample_transactions.csv"), "--layout", "nope"])
    assert code == 2
    assert "Unknown layout" in capsys.readouterr().err


def test_version_flag(capsys):
    try:
        main(["--version"])
    except SystemExit as exit_info:
        assert exit_info.code == 0
    assert "0.1.0" in capsys.readouterr().out
