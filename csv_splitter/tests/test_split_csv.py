import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from split_csv import split_csv


def _write_csv(path: Path, content: str):
    path.write_text(content)


def test_split_by_rows(tmp_path):
    rows = "\n".join(f"row{i},{i}" for i in range(5))
    _write_csv(tmp_path / "in.csv", f"name,n\n{rows}\n")

    summary = split_csv(tmp_path / "in.csv", tmp_path / "out", by_rows=2)

    assert summary["files_created"] == 3
    assert summary["total_rows"] == 5
    assert (tmp_path / "out" / "part_1.csv").exists()
    assert (tmp_path / "out" / "part_3.csv").exists()


def test_split_by_column(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,country\nAlice,India\nBob,USA\nCarol,India\n")

    summary = split_csv(tmp_path / "in.csv", tmp_path / "out", by_column="country")

    assert summary["files_created"] == 2
    assert "India.csv" in summary["filenames"]
    assert "USA.csv" in summary["filenames"]


def test_split_by_column_missing_column_raises(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,country\nAlice,India\n")
    with pytest.raises(ValueError):
        split_csv(tmp_path / "in.csv", tmp_path / "out", by_column="nope")


def test_requires_one_mode(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,country\nAlice,India\n")
    with pytest.raises(ValueError):
        split_csv(tmp_path / "in.csv", tmp_path / "out")


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        split_csv(tmp_path / "nope.csv", tmp_path / "out", by_rows=10)
