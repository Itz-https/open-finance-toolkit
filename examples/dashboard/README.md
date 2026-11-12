# Streamlit dashboard (demo)

This is the original Personal Finance Analytics dashboard, kept as a working
demo of what you can build on top of the library.

Run it from the project root:

```bash
pip install -r examples/dashboard/requirements.txt
streamlit run examples/dashboard/app.py
```

It does not use the library yet. That is planned for a later release (see
`docs/roadmap.md`). Until then it has one known quirk: it reads dates such as
`2026-11-01` day-first, so they appear as 11 January. The library fixes this.
