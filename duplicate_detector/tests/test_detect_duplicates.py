import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from detect_duplicates import detect_duplicates


def test_exact_duplicates():
    df = pd.DataFrame({"name": ["Alice", "Alice", "Bob"], "age": [30, 30, 25]})
    result = detect_duplicates(df, mode="exact")
    assert result["duplicate_count"] == 1
    assert len(result["affected_rows"]) == 2


def test_columns_mode():
    df = pd.DataFrame({
        "email": ["a@x.com", "a@x.com", "b@x.com"],
        "name": ["Alice", "Alice B.", "Bob"],
    })
    result = detect_duplicates(df, mode="columns", columns=["email"])
    assert result["duplicate_count"] == 1


def test_fuzzy_normalized_match():
    df = pd.DataFrame({"name": ["Rahul Sharma", " rahul sharma ", "Priya"]})
    result = detect_duplicates(df, mode="fuzzy", columns=["name"])
    assert result["duplicate_count"] == 1
    assert "Potential" in result["label"]


def test_unknown_column_raises():
    df = pd.DataFrame({"name": ["Alice"]})
    with pytest.raises(ValueError):
        detect_duplicates(df, mode="columns", columns=["nope"])


def test_no_duplicates():
    df = pd.DataFrame({"name": ["Alice", "Bob"]})
    result = detect_duplicates(df, mode="exact")
    assert result["duplicate_count"] == 0
