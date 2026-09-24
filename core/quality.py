"""
Shared data-quality scoring.

One function, used everywhere a "how healthy is this dataset" number is
needed: Data Cleaner (before/after), CSV Analyzer, and the Data Quality
Report. Keeping the scoring logic in one place means all three always
agree on what a given dataset's score is.
"""
from __future__ import annotations

import re

import pandas as pd

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def looks_like_email_column(series: pd.Series) -> bool:
    name = str(series.name).lower()
    return "email" in name or "e-mail" in name


def invalid_email_count(series: pd.Series) -> int:
    values = series.dropna().astype(str)
    if values.empty:
        return 0
    return int((~values.apply(lambda v: bool(_EMAIL_RE.match(v.strip())))).sum())


def compute_quality_report(df: pd.DataFrame) -> dict:
    """
    Compute a 0-100 data quality score plus the underlying issue counts.

    The score starts at 100 and loses points for: duplicate rows,
    missing values, and invalid-looking emails (in columns that look
    like an email column). This is a heuristic, not a certified metric —
    it's meant to give a freelancer a quick directional read on a
    dataset, which is exactly what it's used for everywhere it appears.
    """
    rows = len(df)
    columns = len(df.columns)

    duplicate_rows = int(df.duplicated().sum())
    missing_cells = int(df.isna().sum().sum())
    total_cells = max(rows * columns, 1)
    missing_pct = round(100 * missing_cells / total_cells, 1)

    email_columns = [c for c in df.columns if looks_like_email_column(df[c])]
    invalid_emails = sum(invalid_email_count(df[c]) for c in email_columns)

    score = 100.0
    if rows:
        score -= min(40, (duplicate_rows / rows) * 100 * 0.5)
        score -= min(40, missing_pct * 0.5)
        if email_columns:
            email_cells = sum(df[c].notna().sum() for c in email_columns) or 1
            score -= min(20, (invalid_emails / email_cells) * 100 * 0.4)
    score = max(0, round(score))

    issues = []
    if duplicate_rows:
        issues.append(f"{duplicate_rows} duplicate row(s)")
    if missing_cells:
        issues.append(f"{missing_cells} missing value(s) ({missing_pct}% of cells)")
    if invalid_emails:
        issues.append(f"{invalid_emails} invalid email(s) in {', '.join(email_columns)}")

    recommendations = []
    if duplicate_rows:
        recommendations.append("Remove duplicate rows")
    if missing_cells:
        recommendations.append("Handle missing values (remove or fill)")
    if invalid_emails:
        recommendations.append("Review/validate email addresses")
    if not recommendations:
        recommendations.append("No major issues found — dataset looks clean")

    return {
        "rows": rows,
        "columns": columns,
        "score": score,
        "duplicate_rows": duplicate_rows,
        "missing_cells": missing_cells,
        "missing_pct": missing_pct,
        "invalid_emails": invalid_emails,
        "email_columns": email_columns,
        "issues": issues,
        "recommendations": recommendations,
    }
