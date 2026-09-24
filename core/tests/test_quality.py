import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from core.quality import compute_quality_report, invalid_email_count


def test_clean_dataset_scores_high():
    df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
    result = compute_quality_report(df)
    assert result["score"] == 100
    assert result["issues"] == []


def test_duplicates_and_missing_lower_score():
    df = pd.DataFrame({"name": ["Alice", "Alice", None], "age": [30, 30, 25]})
    result = compute_quality_report(df)
    assert result["score"] < 100
    assert result["duplicate_rows"] == 1
    assert result["missing_cells"] >= 1


def test_invalid_email_count():
    series = pd.Series(["a@x.com", "not-an-email", None])
    assert invalid_email_count(series) == 1
