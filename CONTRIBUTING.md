# Contributing to Open Finance Toolkit

Thank you for helping. You do not need to be an expert. Fixing a typo, improving the docs, or telling us a bank's column names are all real contributions.

By taking part you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## The most useful thing you can do

Bank formats are the heart of this project, and most of ours are unverified. If you have a statement from any Indian or international bank:

1. Open a [bank format request](https://github.com/Itz-https/open-finance-toolkit/issues/new?template=bank_format_request.yml).
2. Paste **only the column header row**, plus the few lines above it if there are any. Replace names, account numbers and every real amount with fake ones.
3. Tell us which of our layouts loads it correctly or incorrectly.

## Never share real financial data

Do not put real statements, account numbers, names, phone numbers or balances in issues, pull requests or tests. All test data must be invented. If you accidentally post something real, edit or delete it straight away and tell a maintainer.

## Ways to contribute

- Report a bug or ask for a feature using the issue templates.
- Improve the documentation.
- Add or verify a bank layout. See [docs/adding-a-bank-format.md](docs/adding-a-bank-format.md).
- Add merchant keywords to the categoriser (`src/open_finance_toolkit/categorize.py`).
- Pick an issue labelled `good first issue`.

## Setting up on your computer

You need Python 3.9 or newer and Git.

```bash
# 1. Copy the project to your computer (use your own fork's address)
git clone https://github.com/<your-username>/open-finance-toolkit.git
cd open-finance-toolkit

# 2. Make a private Python space so nothing else on your computer is affected
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate

# 3. Install the project and the developer tools
pip install -e ".[dev]"

# 4. Check everything works
pytest
```

If `pytest` ends with green "passed" messages, you are ready.

## Making a change

1. **Fork** the repository using the Fork button on GitHub.
2. Create a branch with a short descriptive name: `git checkout -b add-kotak-layout`.
3. Make your change. Add or update tests for it.
4. Run the checks:
   ```bash
   pytest              # all tests pass
   ruff check .        # code style
   ruff format .       # tidy formatting
   ```
5. Commit with a clear message, for example `Add Kotak layout`.
6. Push your branch and open a **pull request**. Fill in the template.

A maintainer will review it. Reviews are about making the change better, not about judging you. Small pull requests that do one thing are the easiest to review.

## Code guidelines

- Keep it simple and readable. A beginner should be able to follow the code.
- Public functions need a docstring that explains what they do, with an example where it helps.
- New behaviour needs a test. Bug fixes need a test that fails without the fix.
- Raise the library's own errors (see `exceptions.py`) with a message a user can act on.
- Do not add dependencies without opening an issue to discuss it first. Keeping the core to `pandas` alone is a goal.
- The library must never make network calls or send data anywhere.

## Reporting security problems

Please do not open a public issue. See [SECURITY.md](SECURITY.md).

## Releases

Maintainers publish releases. The process is in [docs/publishing-to-pypi.md](docs/publishing-to-pypi.md).
