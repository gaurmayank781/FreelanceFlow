"""CSV Splitter — split one CSV into multiple files."""
import sys
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.io_utils import read_csv_safe  # noqa: E402
from csv_splitter.split_csv import plan_split_by_column, plan_split_by_rows  # noqa: E402
from core import history  # noqa: E402
from core.errors import show_friendly_error  # noqa: E402
from webapp_utils import apply_branding, page_header, temp_workspace, zip_folder_bytes  # noqa: E402

st.set_page_config(page_title="CSV Splitter", page_icon="✂️", layout="wide")
apply_branding()
page_header("✂️", "CSV Splitter", "Split one CSV into multiple files — by row count or by a column's value.")

upload = st.file_uploader("CSV file", type="csv")

if upload:
    with temp_workspace() as workspace:
        input_path = workspace / upload.name
        input_path.write_bytes(upload.getbuffer())

        try:
            df = read_csv_safe(input_path)
        except Exception as exc:
            history.log_job("CSV Splitter", upload.name, status="error", error=str(exc))
            show_friendly_error(exc, "Make sure the file is a plain CSV with a header row.")
            st.stop()

        st.caption(f"{len(df)} rows, {len(df.columns)} columns loaded.")
        mode = st.radio("Split by", ["Row count", "Column value"], horizontal=True)

        plan = None
        if mode == "Row count":
            col1, col2, col3 = st.columns(3)
            with col1:
                rows_per_file = st.number_input("Rows per file", min_value=1, value=max(1, len(df) // 2 or 1))
            with col2:
                start_number = st.number_input("Starting number", min_value=1, value=1)
            with col3:
                pattern = st.text_input("Filename pattern", value="part_{n}", help="{n} is replaced with the file number")
            if st.button("Preview split", type="primary"):
                try:
                    st.session_state["_split_plan"] = plan_split_by_rows(df, int(rows_per_file), int(start_number), pattern)
                except Exception as exc:
                    show_friendly_error(exc)
        else:
            column = st.selectbox("Column to split by", df.columns)
            if st.button("Preview split", type="primary"):
                try:
                    st.session_state["_split_plan"] = plan_split_by_column(df, column)
                except Exception as exc:
                    show_friendly_error(exc)

        plan = st.session_state.get("_split_plan")

        if plan:
            st.subheader(f"Preview — {len(plan)} file(s) will be created")
            for name, chunk in plan[:10]:
                st.write(f"**{name}** — {len(chunk)} rows")
                st.dataframe(chunk.head(3), use_container_width=True, hide_index=True)
            if len(plan) > 10:
                st.caption(f"...and {len(plan) - 10} more file(s).")

            if st.button("Create Split Files"):
                started = time.time()
                out_dir = workspace / "split_output"
                out_dir.mkdir(exist_ok=True)
                for name, chunk in plan:
                    chunk.to_csv(out_dir / name, index=False)
                history.log_job(
                    "CSV Splitter", upload.name, f"{len(plan)} files (zip)",
                    duration_seconds=round(time.time() - started, 2),
                )
                st.success(f"Created {len(plan)} file(s).")
                st.download_button(
                    "⬇️ Download all as .zip",
                    data=zip_folder_bytes(out_dir),
                    file_name="split_output.zip",
                    mime="application/zip",
                )
