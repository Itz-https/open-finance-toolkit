"""Generate tests/data/fake_hdfc_statement.pdf.

Everything in the PDF is invented: the names, addresses, account number and
transactions are fake. The layout copies the quirks of a real HDFC statement
so the PDF reader is tested on them:

* a header row on page 1 only
* short narrations that end well left of the Narration header
* narrations that wrap onto a second line
* a value date that differs from the transaction date
* a block of branch details at the top of page 2 that is not part of the table
* a "STATEMENT SUMMARY" block after the last transaction

Run it from the project root if you ever need to regenerate the file::

    pip install reportlab
    python tests/data/make_fake_hdfc_pdf.py

The reportlab package is only needed for this script, not for the tests.
"""

from pathlib import Path

from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = 638, 842
OUT = Path(__file__).with_name("fake_hdfc_statement.pdf")

# (date, narration lines, ref, value date, withdrawal, deposit)
ROWS = [
    ("02/06/18", ["FAKE/CR/001"], "REF0001", "02/06/18", None, 30000.00),
    ("03/06/18", ["UPI-SWIGGY-FAKE@UPI-0001"], "REF0002", "03/06/18", 450.50, None),
    ("04/06/18", ["NEFT DR-TEST000-FAKE PERSON-", "NETBANK, MUM-PERSONAL"], "REF0003",
     "04/06/18", 5000.00, None),
    ("05/06/18", ["EMI 0000001 CHQ S00000010001"], "REF0004", "05/06/18", 2268.00, None),
    ("05/06/18", ["UPI-FAKE@UPI-FREELANCE-OK"], "REF0005", "05/06/18", None, 1500.00),
    ("27/06/18", ["IB BILLPAY DR-FAKEBILL"], "REF0006", "28/06/18", 1000.00, None),
    ("02/07/18", ["ATM WDL FAKE ROAD MUMBAI"], "REF0007", "02/07/18", 10000.00, None),
    ("03/07/18", ["UPI-FAKE@UPI-REFUND-OK"], "REF0008", "03/07/18", None, 3000.00),
]
OPENING_BALANCE = 20000.00
FIRST_PAGE_ROWS = 4

# x positions copied from a real statement: left edge for text, right edge for numbers.
# The text under Narration starts far to the left of its header, as in the real thing.
X_DATE, X_NARR, X_REF, X_VALUE = 34, 72, 289, 362
# The header words sit at different positions from the text under them.
HEADER_NARR, HEADER_REF = 153, 292
X_WITHDRAWAL_RIGHT, X_DEPOSIT_RIGHT, X_BALANCE_RIGHT = 470, 548, 627


def money(value):
    return f"{value:,.2f}"


def text(c, x, top, value, size=8, right=False):
    y = PAGE_H - top
    if right:
        c.drawRightString(x, y, value)
    else:
        c.drawString(x, y, value)


def branch_block(c, top):
    for index, (label, value) in enumerate(
        [
            ("Account Branch", "TEST BRANCH - FAKE ROAD"),
            ("Address", "1 EXAMPLE ROAD"),
            ("City", "EXAMPLEPUR 000000"),
            ("Account No", "00000000000000"),
        ]
    ):
        text(c, 340, top + index * 9, label)
        text(c, 397, top + index * 9, ":")
        text(c, 403, top + index * 9, value)


def main():
    c = canvas.Canvas(str(OUT), pagesize=(PAGE_W, PAGE_H))
    c.setFont("Helvetica", 8)

    # ---- page 1
    text(c, 500, 20, "Page No .: 1")
    branch_block(c, 53)
    text(c, 34, 80, "MR. TEST USER")
    text(c, 34, 100, "1 EXAMPLE ROAD")
    text(c, 34, 120, "EXAMPLEPUR 000000")
    text(c, 34, 200, "From : 01/06/2018")
    text(c, 250, 200, "To : 10/10/2018")
    text(c, 400, 200, "Statement of account")

    text(c, X_DATE, 234, "Date")
    text(c, HEADER_NARR, 234, "Narration")
    text(c, HEADER_REF, 234, "Chq./Ref.No.")
    text(c, X_VALUE, 234, "Value Dt")
    text(c, 405, 234, "Withdrawal Amt.")
    text(c, 491, 234, "Deposit Amt.")
    text(c, 564, 234, "Closing Balance")

    balance = OPENING_BALANCE
    top = 251
    debit_total = credit_total = 0.0
    for number, (date, narration, ref, value_date, withdrawal, deposit) in enumerate(ROWS):
        if number == FIRST_PAGE_ROWS:
            c.showPage()
            c.setFont("Helvetica", 8)
            text(c, 292, 19, "Page No .: 2")
            branch_block(c, 53)  # branch details repeat at the top of later pages
            top = 140
        balance += (deposit or 0) - (withdrawal or 0)
        debit_total += withdrawal or 0
        credit_total += deposit or 0
        text(c, X_DATE, top, date)
        text(c, X_NARR, top, narration[0])
        text(c, X_REF, top, ref)
        text(c, X_VALUE, top, value_date)
        if withdrawal:
            text(c, X_WITHDRAWAL_RIGHT, top, money(withdrawal), right=True)
        if deposit:
            text(c, X_DEPOSIT_RIGHT, top, money(deposit), right=True)
        text(c, X_BALANCE_RIGHT, top, money(balance), right=True)
        for extra in narration[1:]:
            top += 9
            text(c, X_NARR, top, extra)
        top += 26

    top += 20
    text(c, 34, top, "STATEMENT SUMMARY :-")
    text(c, 34, top + 12, "Opening Balance")
    text(c, 150, top + 12, "Debits")
    text(c, 250, top + 12, "Credits")
    text(c, 350, top + 12, "Closing Bal")
    text(c, 34, top + 24, money(OPENING_BALANCE))
    text(c, 150, top + 24, money(debit_total))
    text(c, 250, top + 24, money(credit_total))
    text(c, 350, top + 24, money(balance))
    text(c, 34, top + 60, "This is a computer generated statement with fake data.")
    c.save()
    print(f"wrote {OUT} (closing balance {money(balance)})")


if __name__ == "__main__":
    main()
