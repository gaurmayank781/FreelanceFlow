# Data Cleaner

Cleans a messy CSV: standardizes column names to snake_case, strips
whitespace, removes fully-empty rows, and drops duplicate rows.

![demo](../assets/demos/data_cleaner.gif)

## Why
Raw exports (from forms, scraped data, or manual entry) are rarely clean —
inconsistent spacing, messy headers like `"Customer Name "`, duplicate
entries, and blank rows. This gets a CSV analysis-ready in one command.

## Usage

```bash
# Clean a CSV (removes duplicates by default)
python clean_data.py --input messy.csv --output clean.csv

# Keep duplicate rows
python clean_data.py --input messy.csv --output clean.csv --keep-duplicates
```

Prints a summary: rows removed (empty/duplicate), final row count, and any
column names that were standardized.

## Run tests

```bash
python -m pytest tests/
```
cd data_cleaner
pip3 install -r requirements.txt
python3 clean_data.py --input sample_data/messy_customers.csv --output sample_data/clean_customers.csv
