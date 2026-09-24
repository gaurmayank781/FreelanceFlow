import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from analyze_csv import analyze_csv


def _write_csv(path: Path, content: str):
    path.write_text(content)


def test_overview_counts(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,age\nAlice,30\nBob,25\n")
    result = analyze_csv(tmp_path / "in.csv")
    assert result["overview"]["rows"] == 2
    assert result["overview"]["columns"] == 2


def test_numeric_stats(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,age\nAlice,30\nBob,20\n")
    result = analyze_csv(tmp_path / "in.csv")
    assert result["numeric_stats"]["age"]["min"] == 20
    assert result["numeric_stats"]["age"]["max"] == 30


def test_warns_on_duplicates_and_missing(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,age\nAlice,30\nAlice,30\nBob,\n")
    result = analyze_csv(tmp_path / "in.csv")
    joined = " ".join(result["warnings"])
    assert "duplicate row" in joined
    assert "missing value" in joined


def test_warns_on_invalid_email(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,email\nAlice,alice@example.com\nBob,not-an-email\n")
    result = analyze_csv(tmp_path / "in.csv")
    assert any("invalid-looking email" in w for w in result["warnings"])


def test_empty_file_raises(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,age\n")
    with pytest.raises(ValueError):
        analyze_csv(tmp_path / "in.csv")


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        analyze_csv(tmp_path / "nope.csv")
