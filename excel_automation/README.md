# Excel Report Generator

Turns a plain CSV into a formatted Excel report — styled header, auto-sized
columns, frozen header row, and an automatic Summary sheet with stats
(count, sum, average, min, max) for every numeric column.

![demo](../assets/demos/excel_automation.gif)

## Why
Manually formatting Excel reports (bold headers, column widths, computing
totals/averages) is repetitive busywork. This turns raw CSV data into a
client-ready report in one command.

## Usage

```bash
# Basic report
python generate_report.py --input sales.csv --output report.xlsx

# With a title and custom sheet name
python generate_report.py --input sales.csv --output report.xlsx --title "Q1 Sales Report" --sheet-name "Sales"
```

The Summary sheet is added automatically whenever the data has at least one
numeric column — no flag needed.

## Run tests

```bash
python -m pytest tests/
```
cd excel_automation
pip3 install -r requirements.txt
python3 generate_report.py --input sample_data/sales_data.csv --output sample_data/sales_report.xlsx --title "Q1 Sales Report"