# CSV Merger

Combines all CSV files in a folder into one — handles files with different or
partially overlapping columns without breaking.

![demo](../assets/demos/csv_merger.gif)

## Why
Monthly reports, exported data dumps, or multi-source datasets often need to
be combined for analysis. Columns don't always match exactly across files —
this merges them anyway, filling missing values instead of crashing.

## Usage

```bash
# Merge all CSVs in a folder into one file
python merge_csvs.py --folder ./monthly_reports --output combined.csv

# Skip the source_file tracking column
python merge_csvs.py --folder ./monthly_reports --output combined.csv --no-source-column
```

Each output row gets a `source_file` column by default, so you can trace
which original file it came from — useful for debugging merged data.

## Run tests

```bash
python -m pytest tests/
```
'''cd csv_merger
pip3 install -r requirements.txt
python3 merge_csvs.py --folder sample_data --output merged_sales.csv --dry-run   # nahi, is tool mein dry-run nahi hai, seedha:
python3 merge_csvs.py --folder sample_data --output merged_sales.csv'''