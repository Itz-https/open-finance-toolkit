import io
from pathlib import Path

import pandas as pd
import pytest

from open_finance_toolkit import (
    EmptyFileError,
    FileReadError,
    MissingColumnsError,
    NoValidTransactionsError,
    OpenFinanceError,
    clean_transactions,
    load_transactions,
)
from open_finance_toolkit.parsing import parse_amount, parse_dates

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

STANDARD = (
    "Date,Type,Category,Amount\n2026-11-01,Income,Salary,25000\n2026-11-02,Expense,Food,3500\n"
)


def load(text, **kwargs):
    return load_transactions(text.encode("utf-8"), **kwargs)


class TestStandardLayout:
    def test_reads_standard_csv(self):
        df = load(STANDARD)
        assert list(df.columns) == ["Date", "Type", "Category", "Amount", "Description"]
        assert df["Type"].tolist() == ["Income", "Expense"]
        assert df["Amount"].tolist() == [25000.0, 3500.0]
        assert df.attrs["layout"] == "standard"

    def test_iso_dates_are_year_month_day(self):
        # Regression: dayfirst=True used to turn 2026-11-01 into 11 January.
        df = load(STANDARD)
        assert df["Date"].dt.strftime("%Y-%m-%d").tolist() == ["2026-11-01", "2026-11-02"]

    def test_headers_are_case_and_space_insensitive(self):
        df = load(" date ,TYPE,category,AMOUNT\n2026-11-01,income,Salary,100\n")
        assert df.loc[0, "Type"] == "Income"

    def test_bom_and_commas_in_amounts(self):
        text = '﻿Date,Type,Category,Amount\n2026-11-01,Income,Salary,"1,25,000.50"\n'
        assert load(text).loc[0, "Amount"] == 125000.50

    def test_blank_category_becomes_uncategorised(self):
        df = load("Date,Type,Category,Amount\n2026-11-01,Expense,,100\n")
        assert df.loc[0, "Category"] == "Uncategorised"

    def test_invalid_rows_are_dropped_and_counted(self):
        text = (
            "Date,Type,Category,Amount\n"
            "2026-11-01,Income,Salary,100\n"
            "not a date,Expense,Food,50\n"
            "2026-11-02,Transfer,Other,50\n"
            "2026-11-03,Expense,Food,-5\n"
            "2026-11-04,Expense,Food,abc\n"
        )
        df = load(text)
        assert len(df) == 1
        assert df.attrs["dropped_rows"] == 4

    def test_description_column_is_kept(self):
        df = load("Date,Type,Category,Amount,Description\n2026-11-01,Expense,Food,10, Lunch \n")
        assert df.loc[0, "Description"] == "Lunch"


class TestDebitCreditLayout:
    HDFC_LIKE = (
        "Date,Narration,Chq./Ref.No.,Value Dt,Withdrawal Amt.,Deposit Amt.,Closing Balance\n"
        '01/10/26,NEFT SALARY,1,01/10/26,,"85,000.00","85,000.00"\n'
        '02/10/26,UPI SWIGGY,2,02/10/26,450.00,,"84,550.00"\n'
    )

    def test_detects_hdfc_like_headers(self):
        df = load(self.HDFC_LIKE)
        assert df.attrs["layout"] == "hdfc"
        assert df["Type"].tolist() == ["Income", "Expense"]
        assert df["Amount"].tolist() == [85000.0, 450.0]
        assert df["Date"].dt.strftime("%Y-%m-%d").tolist() == ["2026-10-01", "2026-10-02"]

    def test_day_first_is_the_default_for_slashed_dates(self):
        df = load("Date,Debit,Credit\n03/04/2026,100,\n")
        assert df.loc[0, "Date"].month == 4

    def test_dayfirst_can_be_turned_off(self):
        df = load("Date,Debit,Credit\n03/04/2026,100,\n", dayfirst=False)
        assert df.loc[0, "Date"].month == 3

    @pytest.mark.parametrize(
        "header,name",
        [
            ("Txn Date,Description,Debit,Credit", "sbi"),
            (
                "Transaction Date,Transaction Remarks,"
                "Withdrawal Amount (INR ),Deposit Amount (INR )",
                "icici",
            ),
            ("Tran Date,PARTICULARS,DR,CR", "axis"),
            ("Posting Date,Details,Paid Out,Paid In", "generic-debit-credit"),
        ],
    )
    def test_other_bank_style_headers(self, header, name):
        df = load(f"{header}\n05/11/2026,Coffee,120.00,\n06/11/2026,Refund,,20.00\n")
        assert df.attrs["layout"] == name
        assert df["Type"].tolist() == ["Expense", "Income"]
        assert df["Amount"].tolist() == [120.0, 20.0]
        assert df["Category"].tolist() == ["Uncategorised", "Uncategorised"]

    def test_zero_rows_are_dropped(self):
        df = load("Date,Debit,Credit\n01/11/2026,0,\n02/11/2026,10,\n")
        assert len(df) == 1

    def test_preamble_and_footer_are_skipped(self):
        text = (
            "Bank Name - Statement\n"
            "Customer: Someone\n"
            "\n"
            "Date,Narration,Withdrawal Amt.,Deposit Amt.\n"
            "01/10/26,Tea,20.00,\n"
            "TOTAL,,,\n"
        )
        df = load(text)
        assert len(df) == 1
        assert df.loc[0, "Description"] == "Tea"

    def test_sample_file_in_examples(self):
        df = load_transactions(EXAMPLES / "sample_debit_credit.csv")
        assert len(df) == 10
        assert df["Type"].eq("Income").sum() == 2


class TestSignedLayout:
    def test_negative_means_expense(self):
        df = load("Date,Description,Amount\n2026-11-01,Salary,1000\n2026-11-02,Rent,-400\n")
        assert df.attrs["layout"] == "generic-signed"
        assert df["Type"].tolist() == ["Income", "Expense"]
        assert df["Amount"].tolist() == [1000.0, 400.0]

    def test_accounting_negative_in_brackets(self):
        df = load('Date,Amount\n2026-11-01,"(1,500.00)"\n')
        assert df.loc[0, "Type"] == "Expense"
        assert df.loc[0, "Amount"] == 1500.0


class TestErrors:
    def test_empty_file(self):
        with pytest.raises(EmptyFileError, match="empty"):
            load("")
        with pytest.raises(EmptyFileError):
            load("   \n\n")

    def test_missing_columns_lists_what_was_found(self):
        with pytest.raises(MissingColumnsError) as info:
            load("Foo,Bar\n1,2\n")
        assert info.value.detected == ["Foo", "Bar"]
        assert "Date, Type, Category and Amount" in str(info.value)

    def test_no_valid_transactions(self):
        with pytest.raises(NoValidTransactionsError):
            load("Date,Type,Category,Amount\nnope,Income,Salary,abc\n")

    def test_header_only_file(self):
        with pytest.raises(NoValidTransactionsError):
            load("Date,Type,Category,Amount\n")

    def test_missing_file_path(self, tmp_path):
        with pytest.raises(FileReadError, match="Could not open"):
            load_transactions(tmp_path / "nope.csv")

    def test_all_errors_share_a_base_class(self):
        for error in (EmptyFileError, FileReadError, MissingColumnsError, NoValidTransactionsError):
            assert issubclass(error, OpenFinanceError)

    def test_unknown_layout_name(self):
        with pytest.raises(ValueError, match="Unknown layout"):
            load(STANDARD, layout="made-up")

    def test_forcing_a_layout_that_does_not_fit(self):
        with pytest.raises(MissingColumnsError):
            load(STANDARD, layout="hdfc")

    def test_wrong_source_type(self):
        with pytest.raises(TypeError):
            load_transactions(123)


class TestSources:
    def test_path_string_and_pathlib(self, tmp_path):
        path = tmp_path / "t.csv"
        path.write_text(STANDARD, encoding="utf-8")
        assert len(load_transactions(str(path))) == 2
        assert len(load_transactions(path)) == 2

    def test_binary_and_text_file_objects(self):
        assert len(load_transactions(io.BytesIO(STANDARD.encode()))) == 2
        assert len(load_transactions(io.StringIO(STANDARD))) == 2

    def test_file_object_can_be_read_again(self):
        handle = io.BytesIO(STANDARD.encode())
        load_transactions(handle)
        assert len(load_transactions(handle)) == 2

    def test_non_utf8_file_still_reads(self):
        data = "Date,Description,Amount\n2026-11-01,Caf\xe9,-5\n".encode("cp1252")
        assert load_transactions(data).loc[0, "Description"] == "Café"

    def test_clean_transactions_accepts_a_dataframe(self):
        raw = pd.DataFrame(
            {"date": ["2026-11-01"], "type": ["income"], "category": ["Salary"], "amount": ["10"]}
        )
        assert clean_transactions(raw).loc[0, "Amount"] == 10.0


class TestParsing:
    def test_parse_amount_variants(self):
        values = pd.Series(["1,234.50", "₹ 99", "Rs. 10", "INR 5", "(20)", "", "abc"])
        result = parse_amount(values)
        assert result.tolist()[:5] == [1234.5, 99.0, 10.0, 5.0, -20.0]
        assert result.iloc[5:].isna().all()

    def test_parse_dates_mixed_formats(self):
        result = parse_dates(pd.Series(["2026-11-01", "01/11/2026", "1 Nov 2026", "junk"]))
        assert result.iloc[:3].dt.strftime("%Y-%m-%d").tolist() == ["2026-11-01"] * 3
        assert pd.isna(result.iloc[3])
