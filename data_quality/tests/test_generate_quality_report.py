import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generate_quality_report import (
    build_quality_summary, export_quality_report_excel, export_quality_report_pdf,
)


def _write_csv(path: Path, content: str):
    path.write_text(content)


def test_build_quality_summary(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,email\nAlice,alice@example.com\nAlice,alice@example.com\n")
    summary = build_quality_summary(tmp_path / "in.csv")
    assert summary["dataset_name"] == "in.csv"
    assert summary["duplicate_rows"] == 1
    assert 0 <= summary["score"] <= 100


def test_export_excel(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,age\nAlice,30\nBob,25\n")
    summary = build_quality_summary(tmp_path / "in.csv")
    out = tmp_path / "report.xlsx"
    export_quality_report_excel(summary, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_export_pdf(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,age\nAlice,30\nBob,25\n")
    summary = build_quality_summary(tmp_path / "in.csv")
    out = tmp_path / "report.pdf"
    export_quality_report_pdf(summary, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        build_quality_summary(tmp_path / "nope.csv")
