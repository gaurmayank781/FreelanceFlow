"""CSV Analyzer — understand a dataset before working on it."""
import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from csv_analyzer.analyze_csv import analyze_csv  # noqa: E402
from core import history  # noqa: E402
from core.errors import show_friendly_error  # noqa: E402
from webapp_utils import apply_branding, page_header, temp_workspace  # noqa: E402

st.set_page_config(page_title="CSV Analyzer", page_icon="🔎", layout="wide")
apply_branding()
page_header(
    "🔎", "CSV Analyzer",
    "Understand a dataset before you work on it — overview, per-column stats, "
    "numeric summaries, and data-quality warnings. Read-only, nothing is changed.",
)

upload = st.file_uploader("CSV or Excel file", type=["csv", "xlsx", "xls"])

if upload:
    with temp_workspace() as workspace:
        input_path = workspace / upload.name
        input_path.write_bytes(upload.getbuffer())

        started = time.time()
        try:
            result = analyze_csv(input_path)
        except Exception as exc:
            history.log_job("CSV Analyzer", upload.name, status="error", error=str(exc))
            show_friendly_error(exc, "Make sure the file has a header row and at least one row of data.")
        else:
            history.log_job(
                "CSV Analyzer", upload.name, status="success",
                duration_seconds=round(time.time() - started, 2),
            )
            ov = result["overview"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Rows", ov["rows"])
            c2.metric("Columns", ov["columns"])
            c3.metric("File size", f"{ov['file_size_bytes'] / 1024:.1f} KB")
            c4.metric("In-memory size", f"{ov['memory_usage_bytes'] / 1024:.1f} KB")

            st.subheader("Column Analysis")
            st.dataframe(pd.DataFrame(result["column_analysis"]), use_container_width=True, hide_index=True)

            if result["numeric_stats"]:
                st.subheader("Numeric Statistics")
                stats_df = pd.DataFrame(result["numeric_stats"]).T
                st.dataframe(stats_df, use_container_width=True)

            st.subheader("Data Quality Warnings")
            if result["warnings"]:
                for w in result["warnings"]:
                    st.warning(w)
            else:
                st.success("No warnings — this dataset looks clean.")
