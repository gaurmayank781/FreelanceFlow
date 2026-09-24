"""
CSV Merger
----------
Merges all CSV files in a folder into a single CSV. Handles files with
different (or partially overlapping) columns gracefully.

Usage:
    python merge_csvs.py --folder ./monthly_reports --output combined.csv
    python merge_csvs.py --folder ./monthly_reports --output combined.csv --no-source-column
"""

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.io_utils import read_csv_safe  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def merge_csvs(
    folder: Path,
    output: Path,
    add_source_column: bool = True,
    column_mode: str = "keep_all",
    fill_value: str = "",
) -> pd.DataFrame:
    """
    Merge every .csv file in `folder` into a single DataFrame and write it to `output`.

    column_mode controls how mismatched columns are handled:
        "keep_all"          -> union of all columns, missing cells become NaN (default)
        "fill_missing"      -> union of all columns, missing cells filled with `fill_value`
        "ignore_unmatched"  -> intersection only — columns not present in every file are dropped

    Returns the merged DataFrame.
    """
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")

    csv_files = sorted(folder.glob("*.csv"))
    if not csv_files:
        raise ValueError(f"No CSV files found in {folder}")

    frames = []
    for file in csv_files:
        df = read_csv_safe(file)
        if add_source_column:
            df["source_file"] = file.name
        frames.append(df)
        log.info("Read %s (%d rows)", file.name, len(df))

    if column_mode == "ignore_unmatched" and len(frames) > 1:
        common_cols = set(frames[0].columns)
        for f in frames[1:]:
            common_cols &= set(f.columns)
        # keep original column order from the first file
        ordered_common = [c for c in frames[0].columns if c in common_cols]
        frames = [f[ordered_common] for f in frames]

    merged = pd.concat(frames, ignore_index=True, sort=False)

    if column_mode == "fill_missing":
        merged = merged.fillna(fill_value)

    merged.to_csv(output, index=False)
    log.info("\nMerged %d files -> %s (%d total rows)", len(csv_files), output, len(merged))

    return merged


def main():
    parser = argparse.ArgumentParser(description="Merge all CSVs in a folder into one file.")
    parser.add_argument("--folder", required=True, help="Folder containing CSV files")
    parser.add_argument("--output", required=True, help="Path for the merged output CSV")
    parser.add_argument("--no-source-column", action="store_true", help="Don't add a source_file column")
    args = parser.parse_args()

    try:
        merge_csvs(Path(args.folder), Path(args.output), add_source_column=not args.no_source_column)
    except (FileNotFoundError, ValueError) as e:
        log.error("Error: %s", e)
    except Exception as e:
        log.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
