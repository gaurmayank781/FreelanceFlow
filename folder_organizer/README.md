# Folder Organizer

Sorts every file in a folder into type-based subfolders (Images, Documents, PDFs, Videos, Audio, Archives, Code, Other).

![demo](../assets/demos/folder_organizer.gif)

## Why
Downloads and Desktop folders pile up with mixed file types over time. This
sorts them into clean, browsable categories in one command — no more digging
through 200 files to find one PDF.

## Usage

```bash
# Preview changes first (recommended)
python organize_folder.py --folder ./Downloads --dry-run

# Then actually organize
python organize_folder.py --folder ./Downloads
```

Files with unrecognized extensions go into an `Other/` folder. Add more
extensions to the `CATEGORY_MAP` in `organize_folder.py` if needed.

## Run tests

```bash
python -m pytest tests/
```
