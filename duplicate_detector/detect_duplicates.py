"""
Duplicate Detector (data-level)
--------------------------------
Finds duplicate ROWS within a dataset — different from the file-level
Duplicate Finder (which compares whole files by content hash).

Three modes:
    exact    -> rows identical across every column
    columns  -> rows identical across a chosen subset of columns
    fuzzy    -> rows whose chosen columns match after normalizing case/
                whitespace/punctuation. Labeled "potential duplicates" —
                this is a normalized-text match, not true fuzzy/Levenshtein
                matching, so it stays fast and predictable on larger files.

Usage:
    python detect_duplicates.py --input customers.csv --mode exact
    python detect_duplicates.py --input customers.csv --mode columns --columns email,phone
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


def _normalize(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    return re.sub(r"[^\w]", "", text)


def detect_duplicates(df: pd.DataFrame, mode: str = "exact", columns: list[str] | None = None) -> dict:
    """
    Detect duplicate rows in `df`.

    Returns a dict with:
        duplicate_count   -> number of rows flagged as duplicates (excluding the first occurrence)
        affected_rows     -> DataFrame of all rows involved in a duplicate group (first + repeats)
        group_count       -> number of distinct duplicate groups
        label             -> "Exact duplicates" | "Duplicates by <cols>" | "Potential duplicates (normalized match)"
    """
    if mode == "exact":
        subset = None
        label = "Exact duplicates"
    elif mode == "columns":
        if not columns:
            raise ValueError("mode='columns' requires at least one column")
        missing = [c for c in columns if c not in df.columns]
        if missing:
            raise ValueError(f"Column(s) not found: {', '.join(missing)}")
        subset = columns
        label = f"Duplicates by {', '.join(columns)}"
    elif mode == "fuzzy":
        if not columns:
            raise ValueError("mode='fuzzy' requires at least one column")
        missing = [c for c in columns if c not in df.columns]
        if missing:
            raise ValueError(f"Column(s) not found: {', '.join(missing)}")
        working = df.copy()
        key_col = "__fuzzy_key__"
        working[key_col] = working[columns].apply(
            lambda row: "|".join(_normalize(v) for v in row), axis=1
        )
        is_dup = working.duplicated(subset=key_col, keep=False) & (working[key_col] != "")
        affected = df[is_dup.values]
        group_count = working.loc[is_dup.values, key_col].nunique()
        duplicate_count = int(is_dup.sum()) - group_count
        return {
            "duplicate_count": max(duplicate_count, 0),
            "affected_rows": affected,
            "group_count": int(group_count),
            "label": "Potential duplicates (normalized match)",
        }
    else:
        raise ValueError(f"Unknown mode: {mode}")

    is_dup_any = df.duplicated(subset=subset, keep=False)
    affected = df[is_dup_any]
    group_count = df[is_dup_any].drop_duplicates(subset=subset).shape[0] if subset else df[is_dup_any].drop_duplicates().shape[0]
    duplicate_count = int(df.duplicated(subset=subset, keep="first").sum())

    return {
        "duplicate_count": duplicate_count,
        "affected_rows": affected,
        "group_count": int(group_count),
        "label": label,
    }


def main():
    parser = argparse.ArgumentParser(description="Detect duplicate rows in a CSV.")
    parser.add_argument("--input", required=True, help="Path to the CSV file")
    parser.add_argument("--mode", choices=["exact", "columns", "fuzzy"], default="exact")
    parser.add_argument("--columns", help="Comma-separated column names (for columns/fuzzy modes)")
    args = parser.parse_args()

    try:
        df = read_csv_safe(Path(args.input))
        columns = [c.strip() for c in args.columns.split(",")] if args.columns else None
        result = detect_duplicates(df, mode=args.mode, columns=columns)
        log.info("%s: %d duplicate row(s) in %d group(s)", result["label"], result["duplicate_count"], result["group_count"])
    except (FileNotFoundError, ValueError) as e:
        log.error("Error: %s", e)
    except Exception as e:
        log.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
