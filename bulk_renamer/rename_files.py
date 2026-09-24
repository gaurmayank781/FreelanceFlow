"""
Bulk File Renamer
------------------
Renames all files in a folder using a numbered pattern (e.g. img_1.jpg, img_2.jpg).

Usage:
    python rename_files.py --folder ./photos --pattern "vacation_{n}"
    python rename_files.py --folder ./photos --pattern "vacation_{n}" --start 1 --dry-run
"""

import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def rename_files(folder: Path, pattern: str, start: int = 1, dry_run: bool = False) -> int:
    """
    Rename every file in `folder` to `pattern` with an incrementing number,
    keeping each file's original extension.

    Returns the number of files renamed.
    """
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")

    files = sorted(p for p in folder.iterdir() if p.is_file())
    if not files:
        log.info("No files found in %s", folder)
        return 0

    count = 0
    for i, file in enumerate(files, start=start):
        new_name = f"{pattern.format(n=i)}{file.suffix}"
        new_path = file.parent / new_name

        if dry_run:
            log.info("[DRY RUN] %s -> %s", file.name, new_name)
        else:
            file.rename(new_path)
            log.info("%s -> %s", file.name, new_name)
        count += 1

    return count


def main():
    parser = argparse.ArgumentParser(description="Bulk rename files in a folder.")
    parser.add_argument("--folder", required=True, help="Folder containing files to rename")
    parser.add_argument("--pattern", required=True, help="Naming pattern, use {n} for the number, e.g. 'photo_{n}'")
    parser.add_argument("--start", type=int, default=1, help="Starting number (default: 1)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without renaming")
    args = parser.parse_args()

    try:
        count = rename_files(Path(args.folder), args.pattern, args.start, args.dry_run)
        log.info("\nDone. %d file(s) %s.", count, "would be renamed" if args.dry_run else "renamed")
    except FileNotFoundError as e:
        log.error("Error: %s", e)
    except Exception as e:
        log.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
