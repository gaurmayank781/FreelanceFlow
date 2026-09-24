import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from clean_data import clean_data, _to_snake_case


def test_to_snake_case():
    assert _to_snake_case("Customer Name ") == "customer_name"
    assert _to_snake_case(" Email-Address") == "email_address"


def _write_csv(path: Path, content: str):
    path.write_text(content)


def test_strips_whitespace_from_cells(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,city\n Rahul , Delhi \n")
    out = tmp_path / "out.csv"

    clean_data(tmp_path / "in.csv", out)

    result = out.read_text()
    assert "Rahul,Delhi" in result


def test_removes_duplicate_rows(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,city\nRahul,Delhi\nRahul,Delhi\n")
    out = tmp_path / "out.csv"

    summary = clean_data(tmp_path / "in.csv", out)

    assert summary["duplicate_rows_removed"] == 1
    assert summary["final_rows"] == 1


def test_keep_duplicates_flag(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,city\nRahul,Delhi\nRahul,Delhi\n")
    out = tmp_path / "out.csv"

    summary = clean_data(tmp_path / "in.csv", out, drop_duplicates=False)

    assert summary["duplicate_rows_removed"] == 0
    assert summary["final_rows"] == 2


def test_removes_fully_empty_rows(tmp_path):
    _write_csv(tmp_path / "in.csv", "name,city\nRahul,Delhi\n,\n")
    out = tmp_path / "out.csv"

    summary = clean_data(tmp_path / "in.csv", out)

    assert summary["empty_rows_removed"] == 1
    assert summary["final_rows"] == 1


def test_missing_file_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        clean_data(tmp_path / "does_not_exist.csv", tmp_path / "out.csv")


def test_clean_dataframe_fill_missing_with_value():
    from clean_data import clean_dataframe
    import pandas as pd

    df = pd.DataFrame({"name": ["Rahul", None], "city": ["Delhi", "Mumbai"]})
    cleaned, summary = clean_dataframe(df, {"missing_strategy": "fill_value", "fill_value": "Unknown"})

    assert cleaned["name"].tolist() == ["Rahul", "Unknown"]
    assert summary["missing_values_handled"] == 1


def test_clean_dataframe_text_case_and_special_chars():
    from clean_data import clean_dataframe
    import pandas as pd

    df = pd.DataFrame({"name": ["  Rahul!! ", "shyam@@"]})
    cleaned, _ = clean_dataframe(df, {"text_case": "upper", "remove_special_chars": True})

    assert cleaned["name"].tolist() == ["RAHUL", "SHYAM"]


def test_clean_dataframe_drop_columns():
    from clean_data import clean_dataframe
    import pandas as pd

    df = pd.DataFrame({"Name": ["Rahul"], "Junk Col": [1]})
    cleaned, _ = clean_dataframe(df, {"drop_columns": ["Junk Col"]})

    assert list(cleaned.columns) == ["name"]
