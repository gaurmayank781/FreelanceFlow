# Bulk File Renamer

Renames every file in a folder to a clean, numbered pattern — keeps original extensions.

![demo](../assets/demos/bulk_renamer.gif)

## Why
Downloaded photos, screenshots, and exports often have messy inconsistent names
(`IMG_2034.jpg`, `WhatsApp Image 2024.jpg`, `Screenshot 001.png`). This turns
them into a clean, ordered sequence in one command.

## Usage

```bash
# Preview changes first (recommended)
python rename_files.py --folder ./photos --pattern "vacation_{n}" --dry-run

# Then actually rename
python rename_files.py --folder ./photos --pattern "vacation_{n}"

# Start numbering from a specific number
python rename_files.py --folder ./photos --pattern "vacation_{n}" --start 10
```

## Run tests

```bash
python -m pytest tests/
```
