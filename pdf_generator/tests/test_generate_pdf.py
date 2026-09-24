import sys
from pathlib import Path

import pytest
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generate_pdf import generate_pdf


def _write_csv(path: Path, content: str):
    path.write_text(content)


def test_creates_pdf_file(tmp_path):
    _write_csv(tmp_path / "in.csv", "product,units\nA,10\nB,20\n")
    out = tmp_path / "report.pdf"

    summary = generate_pdf(tmp_path / "in.csv", out)

    assert out.exists()
    assert summary["rows_written"] == 2


def test_title_appears_in_pdf(tmp_path):
    _write_csv(tmp_path / "in.csv", "product,units\nA,10\n")
    out = tmp_path / "report.pdf"

    generate_pdf(tmp_path / "in.csv", out, title="My Custom Title")

    reader = PdfReader(out)
    text = reader.pages[0].extract_text()
    assert "My Custom Title" in text


def test_data_appears_in_pdf(tmp_path):
    _write_csv(tmp_path / "in.csv", "product,units\nWidgetXYZ,42\n")
    out = tmp_path / "report.pdf"

    generate_pdf(tmp_path / "in.csv", out)

    reader = PdfReader(out)
    text = reader.pages[0].extract_text()
    assert "WidgetXYZ" in text
    assert "42" in text


def test_missing_file_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        generate_pdf(tmp_path / "does_not_exist.csv", tmp_path / "out.pdf")


def test_empty_csv_raises_error(tmp_path):
    _write_csv(tmp_path / "in.csv", "product,units\n")
    with pytest.raises(ValueError):
        generate_pdf(tmp_path / "in.csv", tmp_path / "out.pdf")
