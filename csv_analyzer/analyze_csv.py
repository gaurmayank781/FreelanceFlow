"""
CSV Analyzer
------------
Helps a freelancer understand a dataset before working on it: row/column
counts, per-column type + missing/unique stats, numeric summary stats,
and a list of plain-language data-quality warnings.

Usage:
    python analyze_csv.py --input data.csv
"""
import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.io_utils import read_table_safe  # noqa: E402
from core.quality import invalid_email_count, looks_like_email_column  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def analyze_csv(input_path: Path) -> dict:
    """
    Analyze a CSV/Excel file and return overview, per-column analysis,
    numeric stats, and data-quality warnings. Never mutates the file.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    df = read_table_safe(input_path)
    if df.empty:
        raise ValueError(f"No data found in {input_path}")

    overview = {
        "rows": len(df),
        "columns": len(df.columns),
        "file_size_bytes": input_path.stat().st_size,
        "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
    }

    column_analysis = []
    for col in df.columns:
        series = df[col]
        column_analysis.append({
            "name": str(col),
            "dtype": str(series.dtype),
            "missing_pct": round(100 * series.isna().mean(), 1),
            "unique_count": int(series.nunique(dropna=True)),
        })

    numeric_stats = {}
    for col in df.select_dtypes(include="number").columns:
        series = df[col].dropna()
        if series.empty:
            continue
        numeric_stats[str(col)] = {
            "min": float(series.min()),
            "max": float(series.max()),
            "mean": round(float(series.mean()), 2),
            "median": float(series.median()),
            "std": round(float(series.std()), 2) if len(series) > 1 else 0.0,
        }

    warnings = []
    dup_count = int(df.duplicated().sum())
    if dup_count:
        warnings.append(f"{dup_count} duplicate row(s)")

    for col in df.columns:
        missing = df[col].isna().sum()
        if missing:
            warnings.append(f"'{col}': {missing} missing value(s)")

    for col in df.select_dtypes(include="number").columns:
        negative = int((df[col] < 0).sum())
        if negative:
            warnings.append(f"'{col}': {negative} negative value(s)")

    for col in df.columns:
        if looks_like_email_column(df[col]):
            invalid = invalid_email_count(df[col])
            if invalid:
                warnings.append(f"'{col}': {invalid} invalid-looking email(s)")

    id_like_cols = [c for c in df.columns if str(c).lower() in ("id", "customer_id", "order_id")]
    for col in id_like_cols:
        dup_ids = int(df[col].duplicated().sum())
        if dup_ids:
            warnings.append(f"'{col}': {dup_ids} duplicate ID(s)")

    return {
        "overview": overview,
        "column_analysis": column_analysis,
        "numeric_stats": numeric_stats,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze a CSV/Excel dataset.")
    parser.add_argument("--input", required=True, help="Path to the CSV/Excel file")
    args = parser.parse_args()

    try:
        result = analyze_csv(Path(args.input))
        ov = result["overview"]
        log.info("Rows: %d | Columns: %d | Size: %d bytes", ov["rows"], ov["columns"], ov["file_size_bytes"])
        for warning in result["warnings"]:
            log.info("⚠ %s", warning)
    except (FileNotFoundError, ValueError) as e:
        log.error("Error: %s", e)
    except Exception as e:
        log.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
