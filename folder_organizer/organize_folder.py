"""
Folder Organizer
-----------------
Sorts files in a folder into type-based subfolders (Images, Documents, PDFs, etc.)

Usage:
    python organize_folder.py --folder ./Downloads
    python organize_folder.py --folder ./Downloads --dry-run
"""

import argparse
import logging
import shutil
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# Extension -> destination folder mapping. Add more as needed.
CATEGORY_MAP = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".heic"},
    "Documents": {".doc", ".docx", ".txt", ".md", ".rtf", ".odt"},
    "PDFs": {".pdf"},
    "Spreadsheets": {".xlsx", ".xls", ".csv"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv"},
    "Audio": {".mp3", ".wav", ".m4a"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".html", ".css", ".json", ".ipynb"},
}


def _category_for(extension: str) -> str:
    for category, extensions in CATEGORY_MAP.items():
        if extension.lower() in extensions:
            return category
    return "Other"


def organize_folder(folder: Path, dry_run: bool = False) -> dict:
    """
    Move every file in `folder` (non-recursive) into a type-based subfolder.

    Returns a dict of {category: file_count} summarizing what was moved.
    """
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")

    files = [p for p in folder.iterdir() if p.is_file()]
    if not files:
        log.info("No files found in %s", folder)
        return {}

    summary = {}
    for file in files:
        category = _category_for(file.suffix)
        dest_folder = folder / category
        dest_path = dest_folder / file.name

        if dry_run:
            log.info("[DRY RUN] %s -> %s/", file.name, category)
        else:
            dest_folder.mkdir(exist_ok=True)
            # Avoid overwriting an existing file with the same name
            if dest_path.exists():
                dest_path = dest_folder / f"{file.stem}_1{file.suffix}"
            shutil.move(str(file), str(dest_path))
            log.info("%s -> %s/", file.name, category)

        summary[category] = summary.get(category, 0) + 1

    return summary


def main():
    parser = argparse.ArgumentParser(description="Organize files in a folder by type.")
    parser.add_argument("--folder", required=True, help="Folder to organize")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")
    args = parser.parse_args()

    try:
        summary = organize_folder(Path(args.folder), args.dry_run)
        log.info("\nSummary:")
        for category, count in summary.items():
            log.info("  %s: %d file(s)", category, count)
    except FileNotFoundError as e:
        log.error("Error: %s", e)
    except Exception as e:
        log.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
