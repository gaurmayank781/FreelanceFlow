import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from organize_folder import organize_folder, _category_for


def test_categorizes_known_extensions():
    assert _category_for(".jpg") == "Images"
    assert _category_for(".pdf") == "PDFs"
    assert _category_for(".py") == "Code"


def test_unknown_extension_goes_to_other():
    assert _category_for(".xyz") == "Other"


def test_moves_files_into_category_folders(tmp_path):
    (tmp_path / "photo.jpg").touch()
    (tmp_path / "notes.txt").touch()

    summary = organize_folder(tmp_path)

    assert summary == {"Images": 1, "Documents": 1}
    assert (tmp_path / "Images" / "photo.jpg").exists()
    assert (tmp_path / "Documents" / "notes.txt").exists()


def test_dry_run_does_not_move_files(tmp_path):
    (tmp_path / "photo.jpg").touch()

    organize_folder(tmp_path, dry_run=True)

    assert (tmp_path / "photo.jpg").exists()
    assert not (tmp_path / "Images").exists()


def test_name_collision_does_not_overwrite(tmp_path):
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "photo.jpg").write_text("existing")
    (tmp_path / "photo.jpg").write_text("new")

    organize_folder(tmp_path)

    assert (tmp_path / "Images" / "photo.jpg").read_text() == "existing"
    assert (tmp_path / "Images" / "photo_1.jpg").read_text() == "new"


def test_missing_folder_raises_error(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        organize_folder(tmp_path / "does_not_exist")
