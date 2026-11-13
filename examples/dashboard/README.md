# Streamlit dashboard (demo)

This is the original Personal Finance Analytics dashboard, kept as a working
demo of what you can build on top of the library.

Run it from the project root:

```bash
pip install -r examples/dashboard/requirements.txt
streamlit run examples/dashboard/app.py
```

CSV files are still read by the dashboard's own code. HDFC statement **PDFs**
are read with the library (`load_pdf_transactions`), so `requirements.txt`
includes `open-finance-toolkit[pdf]`. If the PDF is password protected, a
password box appears after you upload it.

Moving CSV reading to the library too is planned for a later release (see
`docs/roadmap.md`). Until then CSV reading has one known quirk: it reads dates
such as `2026-11-01` day-first, so they appear as 11 January. The library fixes
this.
