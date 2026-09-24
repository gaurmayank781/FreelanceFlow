"""CSV Merger — combine several CSV files into one."""
import sys
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from csv_merger.merge_csvs import merge_csvs  # noqa: E402
from core import history  # noqa: E402
from core.errors import show_friendly_error  # noqa: E402
from core.io_utils import read_csv_safe  # noqa: E402
from webapp_utils import apply_branding, page_header, save_uploads, temp_workspace  # noqa: E402

st.set_page_config(page_title="CSV Merger", page_icon="📊", layout="wide")
apply_branding()
page_header(
    "📊", "CSV Merger",
    "Combine several CSV files into one. Columns don't need to match exactly.",
)

with st.form("csv_merger_form"):
    uploads = st.file_uploader("CSV files to merge", type="csv", accept_multiple_files=True)

    mode_label = st.radio(
        "Mismatched columns",
        ["Keep all columns", "Fill missing values", "Ignore unmatched columns"],
        horizontal=True,
        help="Keep all: union of columns, blanks stay empty. Fill missing: union, blanks get a fill value. "
             "Ignore unmatched: only columns present in every file are kept.",
    )
    fill_value = ""
    if mode_label == "Fill missing values":
        fill_value = st.text_input("Fill value", value="N/A")

    add_source = st.checkbox("Add a 'source_file' column so you know where each row came from", value=True)
    output_name = st.text_input("Output file name", value="merged.csv")
    submitted = st.form_submit_button("Merge CSVs", type="primary")

if submitted:
    if not uploads or len(uploads) < 2:
        st.warning("Upload at least two CSV files to merge.")
    else:
        column_mode = {
            "Keep all columns": "keep_all",
            "Fill missing values": "fill_missing",
            "Ignore unmatched columns": "ignore_unmatched",
        }[mode_label]

        with temp_workspace() as workspace:
            save_uploads(uploads, workspace)

            before_files = list(workspace.glob("*.csv"))
            before_rows = 0
            before_columns = set()
            for f in before_files:
                d = read_csv_safe(f)
                before_rows += len(d)
                before_columns |= set(d.columns)

            output_path = workspace / (output_name.strip() or "merged.csv")
            input_label = f"{len(uploads)} CSV files"
            started = time.time()
            try:
                merged = merge_csvs(
                    workspace, output_path, add_source_column=add_source,
                    column_mode=column_mode, fill_value=fill_value,
                )
            except Exception as exc:
                history.log_job("CSV Merger", input_label, status="error", error=str(exc))
                show_friendly_error(exc, "Make sure every uploaded file is a plain CSV with a header row.")
            else:
                history.log_job(
                    "CSV Merger", input_label, output_path.name,
                    duration_seconds=round(time.time() - started, 2),
                )
                st.success(f"Merged {len(uploads)} files into {len(merged)} total rows.")

                b1, b2 = st.columns(2)
                with b1:
                    st.markdown("**Before**")
                    st.write(f"Files: {len(before_files)}")
                    st.write(f"Total rows: {before_rows}")
                    st.write(f"Total distinct columns: {len(before_columns)}")
                with b2:
                    st.markdown("**After**")
                    st.write(f"Merged rows: {len(merged)}")
                    st.write(f"Merged columns: {len(merged.columns)}")

                st.subheader("Preview")
                st.dataframe(merged.head(50), use_container_width=True)

                st.download_button(
                    "⬇️ Download merged CSV",
                    data=output_path.read_bytes(),
                    file_name=output_path.name,
                    mime="text/csv",
                )
