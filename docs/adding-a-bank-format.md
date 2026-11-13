# Adding or verifying a bank format

A *layout* tells the library which column headers mean what. Adding a bank is usually one small entry in `src/open_finance_toolkit/formats.py`.

## Step 1: collect only what is safe to share

From your statement you need:

1. The **header row** (the line with column names).
2. Any lines **above** the header (bank name, account details). Replace personal details with fake ones.
3. How **dates** look, with a made-up example such as `05/11/26`.
4. How **amounts** are shown: separate Debit and Credit columns, one signed column, or an extra Dr/Cr column.

Never share real transactions, names, account numbers or balances.

## Step 2: see what already happens

Create a tiny fake file with your header row and two invented rows, then run:

```python
from open_finance_toolkit import load_transactions
df = load_transactions("fake.csv")
print(df.attrs["layout"])
print(df)
```

If the dates, types and amounts look right, the existing generic layout already works. Tell us in an issue. That is a valuable contribution because it lets us mark the layout verified.

## Step 3: add a layout

Open `formats.py` and add an entry to `LAYOUTS`, **above** the two `generic-` entries:

```python
Layout(
    name="kotak",
    label="Kotak Mahindra Bank (unverified)",
    kind="debit_credit",
    date=("transactiondate",),
    description=("narration",),
    debit=("debitamount",),
    credit=("creditamount",),
),
```

Header names are written **normalised**: lower-case, with everything except letters and digits removed. `Withdrawal Amount (INR )` becomes `withdrawalamountinr`.

`kind` is one of:

| kind | Amounts look like |
|---|---|
| `debit_credit` | Separate Debit and Credit columns |
| `signed` | One Amount column, negative means money out |
| `typed` | A Type column says Income or Expense |

Leave `verified` off until someone has checked the layout against a real statement. Set `verified=True` only in a pull request that says who checked it, and with what kind of statement (savings, credit card, and so on).

## Step 4: add a test

In `tests/test_importer.py`, add your header to the `test_other_bank_style_headers` parameter list:

```python
("Transaction Date,Narration,Debit Amount,Credit Amount", "kotak"),
```

Run `pytest`.

## Step 5: open a pull request

Mention the bank, the type of statement, and whether you tested a real file. Do not attach the file.

## Things we cannot handle yet

Help is welcome with these:

- Statements where one column holds both the amount and `Dr`/`Cr` (for example `1,250.00 Dr`)
- Credit card statements that use a different sign convention
- PDF statements from banks other than HDFC (see `src/open_finance_toolkit/pdf.py` and `tests/data/make_fake_hdfc_pdf.py` to see how the HDFC one works)
- Statements with several account sections in one file
