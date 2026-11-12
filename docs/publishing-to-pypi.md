# Publishing to PyPI (maintainers)

PyPI is where `pip install open-finance-toolkit` downloads packages from. This project publishes **automatically from GitHub** using *trusted publishing*, so there are no passwords or tokens to store, and you can do the whole thing from a web browser.

> **Important:** a version number on PyPI can never be reused or replaced, even if you delete the release. Always test before releasing.

## One-time setup

### 1. Create a PyPI account
1. Register at <https://pypi.org/account/register/> with an email address you control.
2. Turn on **two-factor authentication** in your account settings. PyPI requires it to publish.

### 2. Tell PyPI to trust this repository
Because the project does not exist on PyPI yet, you register a *pending publisher*:

1. On PyPI, open your account menu, then **Your projects**, then **Publishing**.
2. Under **Add a new pending publisher**, choose **GitHub** and fill in:
   - PyPI project name: `open-finance-toolkit`
   - Owner: `Itz-https`
   - Repository name: `open-finance-toolkit`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
3. Save.

### 3. Create the matching environment on GitHub
1. In the repository, open **Settings**, then **Environments**, then **New environment**.
2. Name it exactly `pypi`.
3. Optional but recommended: tick **Required reviewers** and add yourself, so a release waits for your approval.

## Releasing a version

### 1. Prepare
1. Make sure the **CI** badge on the README is green on `main`.
2. Edit `src/open_finance_toolkit/__init__.py` and set `__version__` (for example `"0.1.0"`).
3. In `CHANGELOG.md`, move the items from **Unreleased** into a new version heading with today's date.
4. Commit these changes to `main` (through a pull request if you prefer).

### 2. Publish a GitHub release
1. Go to **Releases**, then **Draft a new release**.
2. Click **Choose a tag** and type `v0.1.0` (the version with a `v` in front). Choose **Create new tag**.
3. Set the title to `v0.1.0` and paste the changelog notes.
4. Click **Publish release**.

### 3. Watch it
Open the **Actions** tab. The *Publish to PyPI* workflow builds the package and uploads it. It stops with an error if the tag and `__version__` do not match, which protects you from mistakes.

### 4. Check
1. Open <https://pypi.org/project/open-finance-toolkit/>.
2. In a clean Python environment, run `pip install open-finance-toolkit` and then `open-finance-toolkit --version`.
3. Add a PyPI badge to the README:
   ```markdown
   [![PyPI](https://img.shields.io/pypi/v/open-finance-toolkit.svg)](https://pypi.org/project/open-finance-toolkit/)
   ```
4. Update the README install note, since it will no longer need the "not on PyPI yet" warning.

## If something goes wrong

- **The workflow fails before uploading.** Nothing was published. Fix the problem, delete the release and tag, and publish again.
- **The name is taken or the publisher is rejected.** Re-check the five values in step 2 of one-time setup. They must match exactly, including the workflow file name.
- **A bad version went out.** On PyPI, open the release and use **Yank**. Users will stop getting it by default. Then publish a new version with a higher number, such as `0.1.1`.

## Version numbers

We use [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`. While the project is at `0.x`, minor versions may change behaviour. Bug fixes increase the last number.
