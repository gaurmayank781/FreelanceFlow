import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from merge_csvs import merge_csvs


def _write_csv(path: Path, content: str):
    path.write_text(content)


def test_merges_files_with_same_columns(tmp_path):
    _write_csv(tmp_path / "a.csv", "name,age\nAlice,30\n")
    _write_csv(tmp_path / "b.csv", "name,age\nBob,25\n")

    merged = merge_csvs(tmp_path, tmp_path / "out.csv")

    assert len(merged) == 2
    assert set(merged["name"]) == {"Alice", "Bob"}


def test_handles_mismatched_columns(tmp_path):
    _write_csv(tmp_path / "a.csv", "name,age\nAlice,30\n")
    _write_csv(tmp_path / "b.csv", "name,age,city\nBob,25,Delhi\n")

    merged = merge_csvs(tmp_path, tmp_path / "out.csv")

    assert "city" in merged.columns
    assert pd.isna(merged.loc[merged["name"] == "Alice", "city"]).all()


def test_adds_source_file_column_by_default(tmp_path):
    _write_csv(tmp_path / "a.csv", "name,age\nAlice,30\n")

    merged = merge_csvs(tmp_path, tmp_path / "out.csv")

    assert "source_file" in merged.columns
    assert merged["source_file"].iloc[0] == "a.csv"


def test_no_source_column_when_disabled(tmp_path):
    _write_csv(tmp_path / "a.csv", "name,age\nAlice,30\n")

    merged = merge_csvs(tmp_path, tmp_path / "out.csv", add_source_column=False)

    assert "source_file" not in merged.columns


def test_no_csv_files_raises_error(tmp_path):
    (tmp_path / "notes.txt").touch()

    with pytest.raises(ValueError):
        merge_csvs(tmp_path, tmp_path / "out.csv")


def test_missing_folder_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        merge_csvs(tmp_path / "does_not_exist", tmp_path / "out.csv")


def test_ignore_unmatched_keeps_only_common_columns(tmp_path):
    _write_csv(tmp_path / "a.csv", "name,age\nAlice,30\n")
    _write_csv(tmp_path / "b.csv", "name,age,city\nBob,25,Delhi\n")

    merged = merge_csvs(tmp_path, tmp_path / "out.csv", column_mode="ignore_unmatched")

    assert "city" not in merged.columns
    assert set(merged["name"]) == {"Alice", "Bob"}


def test_fill_missing_fills_blank_cells(tmp_path):
    _write_csv(tmp_path / "a.csv", "name,age\nAlice,30\n")
    _write_csv(tmp_path / "b.csv", "name,age,city\nBob,25,Delhi\n")

    merged = merge_csvs(tmp_path, tmp_path / "out.csv", column_mode="fill_missing", fill_value="N/A")

    assert merged.loc[merged["name"] == "Alice", "city"].iloc[0] == "N/A"
