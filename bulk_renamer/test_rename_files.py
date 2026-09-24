import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bulk_renamer.rename_files import rename_files


def test_renames_files_with_pattern(tmp_path):
    (tmp_path / "a.jpg").touch()
    (tmp_path / "b.png").touch()

    count = rename_files(tmp_path, "photo_{n}")

    assert count == 2
    assert (tmp_path / "photo_1.jpg").exists()
    assert (tmp_path / "photo_2.png").exists()


def test_dry_run_does_not_rename(tmp_path):
    (tmp_path / "a.jpg").touch()

    rename_files(tmp_path, "photo_{n}", dry_run=True)

    assert (tmp_path / "a.jpg").exists()


def test_empty_folder_returns_zero(tmp_path):
    assert rename_files(tmp_path, "photo_{n}") == 0


def test_missing_folder_raises_error(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        rename_files(tmp_path / "does_not_exist", "photo_{n}")
