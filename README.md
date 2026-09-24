# 🛠️ Python Automation Toolkit

A Streamlit web app that puts a clean UI in front of 7 everyday automation
tasks — no command line required. Upload files, click a button, download
the result.

| Tool | What it does |
|---|---|
| 📁 Bulk Renamer | Rename a batch of files with a numbered pattern |
| 🗂️ Folder Organizer | Sort files into type-based folders (Images, PDFs, Docs, ...) |
| 📊 CSV Merger | Combine several CSVs into one, even with mismatched columns |
| 🧹 Data Cleaner | Standardize column names, strip whitespace, drop blanks/duplicates |
| 📈 Excel Report | Turn a CSV into a styled, multi-sheet Excel report |
| 📄 PDF Report | Turn a CSV into a formatted PDF table report |
| ✉️ Email Automation | Send personalized bulk emails from a CSV + template |

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`. Pick a tool from
the home page or the sidebar.

Every upload is processed in a temporary folder that's deleted as soon as
your result is ready — nothing is stored on disk or sent anywhere else.

## Project structure

```
PythonAutomationToolkit/
├── app.py                  # Streamlit home page
├── pages/                  # One page per tool (auto-detected by Streamlit)
├── webapp_utils.py         # Shared helpers (temp workspace, zipping, log capture)
├── requirements.txt
├── bulk_renamer/           # Original CLI tool + tests (used as-is by the app)
├── folder_organizer/
├── csv_merger/
├── data_cleaner/
├── excel_automation/
├── pdf_generator/
└── email_automation/
```

Each tool's core logic still lives in its own folder exactly as before —
the app imports and reuses those functions directly. The original
command-line scripts still work too (see each folder's `README.md`), and
each has its own test suite (`pytest <folder>`).

## Notes on the Email Automation tool

- Defaults to a **dry run** (preview only) — you have to explicitly check a
  box to actually send.
- SMTP credentials are entered in the form and used only in memory for that
  run; they're never written to disk or logged.
- For Gmail, use an **App Password** rather than your normal account
  password.

## Deploying

This app has no external dependencies beyond the packages in
`requirements.txt`, so it deploys as-is to
[Streamlit Community Cloud](https://streamlit.io/cloud) (free) — handy for
linking a live demo from your portfolio, GitHub, or Upwork profile.
