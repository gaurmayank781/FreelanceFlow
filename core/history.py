"""
Local job history — every automation run gets logged here so the
Dashboard and History page can show "what did I run, and when".

Nothing sensitive is stored: just tool name, filenames, status and
timing. No file contents are kept.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from core import store

_KEY = "history"
MAX_ENTRIES = 200

# Rough, clearly-labeled estimate of manual minutes a completed job
# replaces. This is NOT measured — it's a fixed per-job estimate used
# only to give a directional "time saved" number on the dashboard.
_ESTIMATED_MINUTES_PER_JOB = 5


def log_job(
    tool: str,
    input_name: str,
    output_name: str | None = None,
    status: str = "success",
    duration_seconds: float | None = None,
    error: str | None = None,
) -> None:
    """Record one automation run (call this right after a tool finishes)."""
    jobs = store.load(_KEY, [])
    jobs.insert(0, {
        "tool": tool,
        "input": input_name,
        "output": output_name,
        "status": status,
        "duration_seconds": duration_seconds,
        "error": error,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })
    store.save(_KEY, jobs[:MAX_ENTRIES])


def get_recent(limit: int = 10) -> list[dict[str, Any]]:
    return store.load(_KEY, [])[:limit]


def get_all() -> list[dict[str, Any]]:
    return store.load(_KEY, [])


def get_stats() -> dict[str, Any]:
    """Dashboard summary numbers. `estimated_minutes_saved` is explicitly
    an estimate (see _ESTIMATED_MINUTES_PER_JOB) — never present it as measured."""
    jobs = store.load(_KEY, [])
    completed = [j for j in jobs if j.get("status") == "success"]
    return {
        "jobs_completed": len(completed),
        "files_processed": len(completed),
        "estimated_minutes_saved": len(completed) * _ESTIMATED_MINUTES_PER_JOB,
    }


def get_popular_tools(limit: int = 3) -> list[str]:
    """Tool slugs ordered by how often they've been run successfully."""
    jobs = [j for j in store.load(_KEY, []) if j.get("status") == "success"]
    counts: dict[str, int] = {}
    for j in jobs:
        counts[j["tool"]] = counts.get(j["tool"], 0) + 1
    return [tool for tool, _ in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)][:limit]
