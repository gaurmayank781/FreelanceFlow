"""Job History — every automation run, most recent first."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import history  # noqa: E402
from webapp_utils import apply_branding, page_header  # noqa: E402

st.set_page_config(page_title="History", page_icon="🕘", layout="wide")
apply_branding()
page_header("🕘", "Job History", "Every automation run in this app, most recent first.")

jobs = history.get_all()

if not jobs:
    st.info("No jobs yet — run an automation and it'll show up here.")
else:
    df = pd.DataFrame(jobs)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.rename(columns={
        "tool": "Tool", "input": "Input", "output": "Output",
        "status": "Status", "duration_seconds": "Duration (s)", "timestamp": "When",
    })
    display_cols = [c for c in ["When", "Tool", "Input", "Output", "Status", "Duration (s)"] if c in df.columns]

    status_filter = st.selectbox("Filter by status", ["All", "success", "error"])
    view = df if status_filter == "All" else df[df["Status"] == status_filter]

    st.dataframe(
        view[display_cols].sort_values("When", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    errors = df[df["Status"] == "error"]
    if not errors.empty:
        with st.expander(f"⚠️ {len(errors)} failed job(s) — error details"):
            for _, row in errors.iterrows():
                st.write(f"**{row['Tool']}** — {row['Input']}")
                st.code(row.get("error") or "No details recorded.", language=None)
