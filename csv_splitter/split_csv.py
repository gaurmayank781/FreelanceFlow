"""
CSV Splitter
------------
Splits one CSV into multiple files, either by a fixed number of rows
per file or by grouping rows on a column's value.

Usage:
    python split_csv.py --input customers.csv --by-rows 50000
    python split_csv.py --input customers.csv --by-column Country
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


def _safe_filename_part(value: str) -> str:
    value = str(value).strip() or "unknown"
    return re.sub(r"[^\w\-. ]", "_", value)


def plan_split_by_rows(
    df: pd.DataFrame, rows_per_file: int, start_number: int = 1, filename_pattern: str = "part_{n}",
) -> list[tuple[str, pd.DataFrame]]:
    """Return [(filename, chunk_df), ...] without writing anything to disk."""
    if rows_per_file <= 0:
        raise ValueError("rows_per_file must be greater than 0")

    chunks = []
    for i, start in enumerate(range(0, len(df), rows_per_file), start=start_number):
        chunk = df.iloc[start:start + rows_per_file]
        name = f"{filename_pattern.format(n=i)}.csv"
        chunks.append((name, chunk))
    return chunks


def plan_split_by_column(df: pd.DataFrame, column: str) -> list[tuple[str, pd.DataFrame]]:
    """Return [(filename, group_df), ...], one file per unique value in `column`."""
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in file")

    groups = []
    for value, group in df.groupby(column, dropna=False):
        name = f"{_safe_filename_part(value)}.csv"
        groups.append((name, group))
    return groups


def split_csv(
    input_path: Path,
    output_dir: Path,
    by_rows: int | None = None,
    by_column: str | None = None,
    filename_pattern: str = "part_{n}",
    start_number: int = 1,
) -> dict:
    """
    Split a CSV file into multiple files under `output_dir`. Exactly one
    of `by_rows` / `by_column` should be given. Returns a summary dict.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")
    if not by_rows and not by_column:
        raise ValueError("Provide either by_rows or by_column")

    df = read_csv_safe(input_path)

    if by_rows:
        plan = plan_split_by_rows(df, by_rows, start_number, filename_pattern)
    else:
        plan = plan_split_by_column(df, by_column)

    output_dir.mkdir(parents=True, exist_ok=True)
    for name, chunk in plan:
        chunk.to_csv(output_dir / name, index=False)
        log.info("Wrote %s (%d rows)", name, len(chunk))

    return {
        "total_rows": len(df),
        "files_created": len(plan),
        "filenames": [name for name, _ in plan],
    }


def main():
    parser = argparse.ArgumentParser(description="Split a CSV file into multiple files.")
    parser.add_argument("--input", required=True, help="Path to the CSV file")
    parser.add_argument("--output-dir", default="split_output", help="Folder to write split files into")
    parser.add_argument("--by-rows", type=int, help="Rows per output file")
    parser.add_argument("--by-column", help="Column name to split by")
    args = parser.parse_args()

    try:
        summary = split_csv(
            Path(args.input), Path(args.output_dir),
            by_rows=args.by_rows, by_column=args.by_column,
        )
        log.info("\nCreated %d file(s) from %d rows.", summary["files_created"], summary["total_rows"])
    except (FileNotFoundError, ValueError) as e:
        log.error("Error: %s", e)
    except Exception as e:
        log.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
