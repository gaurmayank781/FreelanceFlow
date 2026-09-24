# PDF Report Generator

Turns a CSV file into a formatted PDF report — title, generated timestamp,
and a styled table with a colored header and alternating row shading.

![demo](../assets/demos/pdf_generator.gif)

## Why
Sharing raw CSVs with clients looks unpolished, and manually formatting a
PDF report in another tool is slow. This generates a clean, print-ready PDF
in one command — useful for invoices, sales summaries, or any tabular report.

## Usage

```bash
# Basic report
python generate_pdf.py --input sales.csv --output report.pdf

# With a custom title
python generate_pdf.py --input sales.csv --output report.pdf --title "Q1 Sales Report"
```

The table header row repeats automatically if the data spans multiple pages.

## Run tests

```bash
python -m pytest tests/
```
cd pdf_generator
pip3 install -r requirements.txt
python3 generate_pdf.py --input sample_data/sales_data.csv --output sample_data/sales_report.pdf --title "Q1 Sales Report"

