"""
Safe file-reading helpers shared by every automation.

Why this exists: pandas' `pd.read_csv` defaults to strict UTF-8. Files
exported from Excel on Windows (or edited on macOS) are very often
cp1252/latin-1 instead, and contain bytes like 0xA0 (a non-breaking
space) that aren't valid UTF-8 — that's exactly what throws
`UnicodeDecodeError: 'utf-8' codec can't decode byte 0xa0`.
`read_csv_safe` tries a short list of common encodings in order instead
of failing on the first one.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

# Ordered by how common each is for CSVs freelancers actually receive.
ENCODINGS_TO_TRY = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]


def read_csv_safe(path: Path, **kwargs) -> pd.DataFrame:
    """
    Read a CSV file, falling back through common encodings if the file
    isn't plain UTF-8. Raises the original UnicodeDecodeError only if
    every encoding in ENCODINGS_TO_TRY fails.
    """
    last_error: UnicodeDecodeError | None = None
    for encoding in ENCODINGS_TO_TRY:
        try:
            return pd.read_csv(path, encoding=encoding, **kwargs)
        except UnicodeDecodeError as exc:
            last_error = exc
            continue
    # Every encoding failed — re-raise the last error so callers can
    # still pattern-match on UnicodeDecodeError.
    raise last_error


def read_table_safe(path: Path, **kwargs) -> pd.DataFrame:
    """Read a CSV or Excel file (by extension), using read_csv_safe for CSVs."""
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(path, **kwargs)
    return read_csv_safe(path, **kwargs)
