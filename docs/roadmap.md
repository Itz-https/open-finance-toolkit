# Roadmap

This is a direction, not a promise. Priorities change as real users tell us what they need.

## Now (0.1)
- Core import, categorise, duplicates, summaries
- Layouts for generic debit/credit and signed statements
- Unverified HDFC, SBI, ICICI and Axis layouts

## Next
- **Verify bank layouts against real statements.** This is the biggest need.
- Handle a single amount column with `Dr`/`Cr` markers
- More categorisation keywords from real-world merchants
- Make the demo dashboard use the library, which also fixes its date reading
- Export helpers (clean CSV, Excel)

## Later
- More banks (Kotak, Yes Bank, IDFC First, Bank of Baroda, PNB, and others)
- Credit card statement support
- Recurring-payment detection (subscriptions, EMIs)
- Fuzzy duplicate detection (dates a day apart, slightly different text)
- Documentation site

## Good first issues

Beginner-friendly starting points:

- Add keywords for a merchant you use to `categorize.py`, with a test
- Test an existing layout with a fake file and report the result
- Improve a docstring or a docs page
- Add another example script to `examples/`

## Ideas we are not planning

- Anything that sends financial data over the network
- Reading PDF statements in the core package (it could become an optional add-on)
