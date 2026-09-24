"""
Turns raw exceptions into a friendly on-screen message + reason,
while still logging the full traceback for debugging. No automation
page should ever show a raw Python traceback to the user.
"""
from __future__ import annotations

import logging

import streamlit as st

log = logging.getLogger("freelanceflow")

_FRIENDLY_REASONS = {
    "FileNotFoundError": "That file couldn't be found.",
    "ValueError": "The file's contents don't look right for this tool.",
    "UnicodeDecodeError": (
        "This file's text encoding couldn't be read. It may not be a plain "
        "CSV, or it was saved with an unusual encoding."
    ),
    "KeyError": "A column this tool expects wasn't found in your file.",
    "EmptyDataError": "The file appears to be empty.",
    "PermissionError": "The app doesn't have permission to read/write that location.",
}


def show_friendly_error(exc: Exception, suggestion: str | None = None) -> None:
    """
    Show a clean error + reason to the user (no traceback), log the
    real exception, and optionally suggest what to do next.
    """
    log.exception("Automation failed: %s", exc)

    reason = _FRIENDLY_REASONS.get(type(exc).__name__, "Something went wrong while processing this file.")
    st.error(f"**Unable to process this file.**\n\nReason: {reason}")

    if suggestion:
        st.info(suggestion)

    with st.expander("Technical details (for debugging)"):
        st.code(f"{type(exc).__name__}: {exc}")
