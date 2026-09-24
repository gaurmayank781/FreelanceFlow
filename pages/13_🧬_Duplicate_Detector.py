"""Duplicate Detector — find duplicate rows within a dataset."""
import sys
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.io_utils import read_csv_safe  # noqa: E402
from duplicate_detector.detect_duplicates import detect_duplicates  # noqa: E402
from core import history  # noqa: E402
from core.errors import show_friendly_error  # noqa: E402
from webapp_utils import apply_branding, page_header, temp_workspace  # noqa: E402

st.set_page_config(page_title="Duplicate Detector", page_icon="🧬", layout="wide")
apply_branding()
page_header(
    "🧬", "Duplicate Detector",
    "Find duplicate rows in your data — different from the file-level Duplicate Finder, "
    "this looks INSIDE one dataset.",
)

upload = st.file_uploader("CSV file", type="csv")

if upload:
    with temp_workspace() as workspace:
        input_path = workspace / upload.name
        input_path.write_bytes(upload.getbuffer())

        try:
            df = read_csv_safe(input_path)
        except Exception as exc:
            history.log_job("Duplicate Detector", upload.name, status="error", error=str(exc))
            show_friendly_error(exc, "Make sure the file is a plain CSV with a header row.")
            st.stop()

        mode_label = st.radio(
            "Match mode", ["Exact (every column)", "Selected columns", "Normalized near-match"], horizontal=True,
        )
        columns = None
        if mode_label != "Exact (every column)":
            columns = st.multiselect("Columns to match on", df.columns.tolist())

        if st.button("Find Duplicates", type="primary"):
            mode = {"Exact (every column)": "exact", "Selected columns": "columns", "Normalized near-match": "fuzzy"}[mode_label]
            if mode != "exact" and not columns:
                st.warning("Pick at least one column.")
            else:
                started = time.time()
                try:
                    result = detect_duplicates(df, mode=mode, columns=columns)
                except Exception as exc:
                    history.log_job("Duplicate Detector", upload.name, status="error", error=str(exc))
                    show_friendly_error(exc)
                else:
                    history.log_job(
                        "Duplicate Detector", upload.name, status="success",
                        duration_seconds=round(time.time() - started, 2),
                    )
                    st.caption(result["label"])
                    if mode == "fuzzy":
                        st.info(
                            "These are **potential** duplicates based on a normalized text match "
                            "(case/whitespace/punctuation ignored) — not a certainty. Review before acting."
                        )
                    c1, c2 = st.columns(2)
                    c1.metric("Duplicate rows", result["duplicate_count"])
                    c2.metric("Duplicate groups", result["group_count"])

                    if result["duplicate_count"]:
                        st.subheader("Affected rows")
                        st.dataframe(result["affected_rows"], use_container_width=True, hide_index=True)
                        st.download_button(
                            "⬇️ Download duplicate rows (.csv)",
                            data=result["affected_rows"].to_csv(index=False).encode("utf-8"),
                            file_name=f"duplicates_{upload.name}",
                            mime="text/csv",
                        )
                    else:
                        st.success("No duplicates found with this match mode.")
