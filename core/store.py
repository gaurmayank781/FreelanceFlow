"""
Tiny local JSON key-value store.

FreelanceFlow keeps everything local — no database, no external service.
Each "table" (history, favorites, presets) is just a JSON file under
data/. Reads/writes are whole-file (fine at this scale); if a file is
missing or corrupted we fall back to the caller's default rather than
crashing the app.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load(name: str, default: Any) -> Any:
    """Load data/<name>.json, or return `default` if it doesn't exist / is corrupt."""
    path = DATA_DIR / f"{name}.json"
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def save(name: str, data: Any) -> None:
    """Write data/<name>.json, creating the data/ folder if needed."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
