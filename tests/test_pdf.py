import subprocess
import sys
from pathlib import Path

import pytest

from open_finance_toolkit import (
    FileReadError,
    MissingColumnsError,
    MissingDependencyError,
    categorize,
    load_pdf_transactions,
    summarize,
    totals,
)
from open_finance_toolkit.cli import main
from open_finance_toolkit.pdf import _open_error_message

pytest.importorskip("pdfplumber")

FAKE_PDF = Path(__file__).parent / "data" / "fake_hdfc_statement.pdf"

# These come from tests/data/make_fake_hdfc_pdf.py. Opening balance is 20,000.00.
OPENING_BALANCE = 20000.00
CLOSING_BALANCE = 35781.50


@pytest.fixture(scope="module")
def transactions():
    return load_pdf_transactions(FAKE_PDF)


def make_plain_pdf(lines):
    """Build a tiny valid PDF by hand, so the tests do not need a PDF-writing package."""
    shown = " ".join(f"({line}) Tj T*" for line in lines)
    content = f"BT /F1 10 Tf 40 780 Td 12 TL {shown} ET"
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Contents 4 0 R "
        "/Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(content)} >>\nstream\n{content}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    body = "%PDF-1.4\n"
    offsets = []
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body += f"{number} 0 obj\n{obj}\nendobj\n"
    xref = len(body)
    body += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    body += "".join(f"{offset:010d} 00000 n \n" for offset in offsets)
    body += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return body.encode("latin-1")


class TestReadingTheFakeStatement:
    def test_reads_every_transaction(self, transactions):
        assert len(transactions) == 8
        assert list(transactions.columns) == ["Date", "Type", "Category", "Amount", "Description"]
        assert transactions.attrs["layout"] == "hdfc"
        assert transactions.attrs["source"] == "pdf"
        assert transactions.attrs["dropped_rows"] == 0

    def test_totals_match_the_statement(self, transactions):
        result = totals(transactions)
        assert result.income == pytest.approx(34500.00)
        assert result.expenses == pytest.approx(18718.50)
        # Opening balance + income - expenses must equal the printed closing balance.
        assert OPENING_BALANCE + result.savings == pytest.approx(CLOSING_BALANCE)

    def test_deposits_are_income_and_withdrawals_are_expenses(self, transactions):
        first = transactions.iloc[0]
        assert (first["Type"], first["Amount"]) == ("Income", 30000.00)
        assert transactions.iloc[1]["Type"] == "Expense"

    def test_short_narrations_are_not_mistaken_for_the_date_column(self, transactions):
        # Regression: on a real statement, narrations that end left of the
        # "Narration" header were read as part of the date, dropping the row.
        assert transactions.iloc[0]["Description"] == "FAKE/CR/001"

    def test_wrapped_narration_is_joined(self, transactions):
        assert transactions.iloc[2]["Description"] == (
            "NEFT DR-TEST000-FAKE PERSON- NETBANK, MUM-PERSONAL"
        )

    def test_value_date_is_not_used_as_the_date(self, transactions):
        # The bill payment is dated 27/06/18 but has value date 28/06/18.
        row = transactions[transactions["Description"].str.contains("FAKEBILL")].iloc[0]
        assert row["Date"].strftime("%Y-%m-%d") == "2018-06-27"

    def test_dates_use_day_first_and_two_digit_years(self, transactions):
        assert transactions["Date"].min().strftime("%Y-%m-%d") == "2018-06-02"
        assert transactions["Date"].max().strftime("%Y-%m-%d") == "2018-07-03"

    def test_page_two_branch_details_and_summary_are_ignored(self, transactions):
        text = " ".join(transactions["Description"])
        assert "EXAMPLE ROAD" not in text
        assert "TEST BRANCH" not in text
        assert "SUMMARY" not in text
        assert "computer generated" not in text

    def test_works_with_the_rest_of_the_library(self, transactions):
        categorised = categorize(transactions)
        monthly = summarize(categorised, by="month")
        assert monthly["Period"].tolist() == ["2018-06", "2018-07"]
        assert categorised["Category"].eq("Food").any()  # the Swiggy row


class TestSources:
    def test_accepts_bytes(self):
        assert len(load_pdf_transactions(FAKE_PDF.read_bytes())) == 8

    def test_accepts_an_open_file(self):
        with open(FAKE_PDF, "rb") as handle:
            assert len(load_pdf_transactions(handle)) == 8

    def test_accepts_a_string_path(self):
        assert len(load_pdf_transactions(str(FAKE_PDF))) == 8


class TestErrors:
    def test_missing_file(self):
        with pytest.raises(FileReadError, match="not found"):
            load_pdf_transactions("does-not-exist.pdf")

    def test_not_a_pdf(self):
        with pytest.raises(FileReadError, match="Unable to read this PDF"):
            load_pdf_transactions(b"this is not a pdf")

    def test_pdf_without_a_statement_table(self):
        with pytest.raises(MissingColumnsError, match="HDFC statement table"):
            load_pdf_transactions(make_plain_pdf(["Hello world", "No table here"]))

    def test_password_error_message_is_helpful(self):
        class PDFPasswordIncorrect(Exception):
            pass

        assert "password" in _open_error_message(PDFPasswordIncorrect()).lower()

    def test_wrong_type_is_rejected(self):
        with pytest.raises(TypeError):
            load_pdf_transactions(12345)


class TestOptionalDependency:
    def test_clear_error_when_pdfplumber_is_missing(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "pdfplumber", None)
        with pytest.raises(MissingDependencyError, match=r"open-finance-toolkit\[pdf\]"):
            load_pdf_transactions(FAKE_PDF)

    def test_base_package_imports_without_pdfplumber(self):
        code = "import sys; sys.modules['pdfplumber'] = None; import open_finance_toolkit"
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr


def test_command_line_accepts_a_pdf(capsys):
    code = main(["summary", str(FAKE_PDF)])
    out = capsys.readouterr().out
    assert code == 0
    assert "Income:       34,500.00" in out
    assert "2018-06" in out
