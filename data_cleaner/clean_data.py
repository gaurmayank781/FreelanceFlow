"""
Data Cleaner
------------
Cleans a messy CSV: strips whitespace, standardizes column names to
snake_case, drops fully-empty rows, and removes duplicate rows.

Usage:
    python clean_data.py --input messy.csv --output clean.csv
    python clean_data.py --input messy.csv --output clean.csv --keep-duplicates
"""

import argparse
import logging
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.io_utils import read_csv_safe  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def _to_snake_case(column: str) -> str:
    column = column.strip()
    column = re.sub(r"[\s\-]+", "_", column)
    column = re.sub(r"[^\w_]", "", column)
    return column.lower()


def clean_data(input_path: Path, output_path: Path, drop_duplicates: bool = True) -> dict:
    """
    Clean a CSV file and write the result to `output_path`.

    Steps: standardize column names -> strip whitespace from text cells ->
    drop fully-empty rows -> drop duplicate rows (optional).

    Returns a summary dict of what changed.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    df = read_csv_safe(input_path)
    original_rows = len(df)
    original_columns = list(df.columns)

    # 1. Standardize column names
    df.columns = [_to_snake_case(c) for c in df.columns]

    # 2. Strip whitespace from string/object columns
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)

    # 3. Drop fully-empty rows
    df = df.dropna(how="all")
    rows_after_empty_drop = len(df)

    # 4. Drop duplicate rows
    duplicates_removed = 0
    if drop_duplicates:
        before = len(df)
        df = df.drop_duplicates()
        duplicates_removed = before - len(df)

    df.to_csv(output_path, index=False)

    summary = {
        "original_rows": original_rows,
        "empty_rows_removed": original_rows - rows_after_empty_drop,
        "duplicate_rows_removed": duplicates_removed,
        "final_rows": len(df),
        "columns_renamed": {
            old: new for old, new in zip(original_columns, df.columns) if old != new
        },
    }
    return summary


def clean_dataframe(df: pd.DataFrame, options: dict) -> tuple[pd.DataFrame, dict]:
    """
    Clean an in-memory DataFrame according to `options`, without touching
    disk. Used by the Data Cleaner page so it can show a live preview
    before the user confirms and downloads.

    Recognized options (all optional, defaults shown):
        standardize_columns: bool = True      -> snake_case column names
        trim_whitespace: bool = True           -> strip text cells
        text_case: "none"|"lower"|"upper"|"title" = "none"
        remove_special_chars: bool = False     -> strip non-alphanumeric from text cells
        drop_empty_rows: bool = True
        remove_duplicates: bool = True
        missing_strategy: "none"|"remove"|"fill_value"|"fill_mean_median" = "none"
        fill_value: str = ""
        standardize_dates: list[str] = []      -> columns to coerce to YYYY-MM-DD
        drop_columns: list[str] = []
        rename_columns: dict[str, str] = {}

    Returns (cleaned_df, summary_dict).
    """
    df = df.copy()
    original_rows = len(df)
    original_columns = list(df.columns)

    if options.get("standardize_columns", True):
        df.columns = [_to_snake_case(c) for c in df.columns]

    if options.get("drop_columns"):
        # translate requested names through the same snake_case rule so
        # the option works whether the user typed the original or new name
        drop_set = {_to_snake_case(c) if options.get("standardize_columns", True) else c
                    for c in options["drop_columns"]}
        df = df.drop(columns=[c for c in df.columns if c in drop_set], errors="ignore")

    if options.get("rename_columns"):
        df = df.rename(columns=options["rename_columns"])

    text_cols = df.select_dtypes(include=["object", "string"]).columns

    if options.get("trim_whitespace", True):
        for col in text_cols:
            df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)

    text_case = options.get("text_case", "none")
    if text_case != "none":
        caser = {"lower": str.lower, "upper": str.upper, "title": str.title}[text_case]
        for col in text_cols:
            df[col] = df[col].apply(lambda v: caser(v) if isinstance(v, str) else v)

    if options.get("remove_special_chars"):
        for col in text_cols:
            df[col] = df[col].apply(
                lambda v: re.sub(r"[^\w\s]", "", v) if isinstance(v, str) else v
            )

    for col in options.get("standardize_dates", []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

    empty_rows_removed = 0
    if options.get("drop_empty_rows", True):
        before = len(df)
        df = df.dropna(how="all")
        empty_rows_removed = before - len(df)

    missing_strategy = options.get("missing_strategy", "none")
    missing_handled = 0
    if missing_strategy == "remove":
        before = len(df)
        df = df.dropna()
        missing_handled = before - len(df)
    elif missing_strategy == "fill_value":
        missing_handled = int(df.isna().sum().sum())
        df = df.fillna(options.get("fill_value", ""))
    elif missing_strategy == "fill_mean_median":
        missing_handled = int(df.isna().sum().sum())
        for col in df.select_dtypes(include="number").columns:
            df[col] = df[col].fillna(df[col].median())

    duplicates_removed = 0
    if options.get("remove_duplicates", True):
        before = len(df)
        df = df.drop_duplicates()
        duplicates_removed = before - len(df)

    summary = {
        "original_rows": original_rows,
        "empty_rows_removed": empty_rows_removed,
        "duplicate_rows_removed": duplicates_removed,
        "missing_values_handled": missing_handled,
        "final_rows": len(df),
        "columns_renamed": {
            old: new for old, new in zip(original_columns, df.columns) if old != new
        } if len(original_columns) == len(df.columns) else {},
    }
    return df, summary


def main():
    parser = argparse.ArgumentParser(description="Clean a messy CSV file.")
    parser.add_argument("--input", required=True, help="Path to the messy input CSV")
    parser.add_argument("--output", required=True, help="Path for the cleaned output CSV")
    parser.add_argument("--keep-duplicates", action="store_true", help="Don't remove duplicate rows")
    args = parser.parse_args()

    try:
        summary = clean_data(Path(args.input), Path(args.output), drop_duplicates=not args.keep_duplicates)
        log.info("Original rows: %d", summary["original_rows"])
        log.info("Empty rows removed: %d", summary["empty_rows_removed"])
        log.info("Duplicate rows removed: %d", summary["duplicate_rows_removed"])
        log.info("Final rows: %d", summary["final_rows"])
        if summary["columns_renamed"]:
            log.info("Columns renamed: %s", summary["columns_renamed"])
        log.info("\nSaved to %s", args.output)
    except FileNotFoundError as e:
        log.error("Error: %s", e)
    except Exception as e:
        log.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
