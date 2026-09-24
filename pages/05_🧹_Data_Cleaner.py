"""Data Cleaner — flagship tool: analyze, configure, preview, then clean."""
import sys
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data_cleaner.clean_data import clean_dataframe  # noqa: E402
from core import history  # noqa: E402
from core.errors import show_friendly_error  # noqa: E402
from core.io_utils import read_csv_safe  # noqa: E402
from core.quality import compute_quality_report  # noqa: E402
from webapp_utils import apply_branding, page_header, temp_workspace  # noqa: E402

st.set_page_config(page_title="Data Cleaner", page_icon="🧹", layout="wide")
apply_branding()
page_header(
    "🧹", "Data Cleaner",
    "Clean up a messy CSV: duplicates, missing data, text formatting, dates, columns — "
    "preview before you download, nothing is changed until you confirm.",
)

upload = st.file_uploader("CSV file to clean", type="csv")

if upload:
    with temp_workspace() as workspace:
        input_path = workspace / upload.name
        input_path.write_bytes(upload.getbuffer())

        try:
            df = read_csv_safe(input_path)
        except Exception as exc:
            history.log_job("Data Cleaner", upload.name, status="error", error=str(exc))
            show_friendly_error(exc, "Make sure the file is a plain CSV with a header row.")
            st.stop()

        before_quality = compute_quality_report(df)
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", before_quality["rows"])
        c2.metric("Columns", before_quality["columns"])
        c3.metric("Quality Score (before)", f"{before_quality['score']}/100")

        st.subheader("Cleaning options")
        col1, col2 = st.columns(2)
        with col1:
            remove_duplicates = st.checkbox("Remove duplicate rows", value=True)
            drop_empty_rows = st.checkbox("Remove fully-empty rows", value=True)
            trim_whitespace = st.checkbox("Trim whitespace from text", value=True)
            text_case = st.selectbox("Text case", ["none", "lower", "upper", "title"])
            remove_special_chars = st.checkbox("Remove special characters from text", value=False)
        with col2:
            missing_strategy = st.selectbox(
                "Missing data", ["none", "remove", "fill_value", "fill_mean_median"],
                format_func=lambda v: {
                    "none": "Leave as-is", "remove": "Remove rows with missing values",
                    "fill_value": "Fill with a value", "fill_mean_median": "Fill numeric columns with median",
                }[v],
            )
            fill_value = st.text_input("Fill value", value="", disabled=missing_strategy != "fill_value")
            date_columns = st.multiselect("Standardize date columns", df.columns.tolist())
            drop_columns = st.multiselect("Remove columns", df.columns.tolist())

        options = {
            "remove_duplicates": remove_duplicates,
            "drop_empty_rows": drop_empty_rows,
            "trim_whitespace": trim_whitespace,
            "text_case": text_case,
            "remove_special_chars": remove_special_chars,
            "missing_strategy": missing_strategy,
            "fill_value": fill_value,
            "standardize_dates": date_columns,
            "drop_columns": drop_columns,
        }

        if st.button("Preview Changes", type="primary"):
            try:
                cleaned_df, summary = clean_dataframe(df, options)
            except Exception as exc:
                show_friendly_error(exc)
            else:
                st.session_state["_cleaner_result"] = (cleaned_df, summary)

        result = st.session_state.get("_cleaner_result")
        if result:
            cleaned_df, summary = result
            after_quality = compute_quality_report(cleaned_df)

            st.subheader("Before vs After")
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Rows", summary["original_rows"], delta=summary["final_rows"] - summary["original_rows"])
            b2.metric("Duplicates removed", summary["duplicate_rows_removed"])
            b3.metric("Missing values handled", summary["missing_values_handled"])
            b4.metric("Quality Score", f"{after_quality['score']}/100", delta=after_quality["score"] - before_quality["score"])

            st.subheader("Preview (cleaned)")
            st.dataframe(cleaned_df.head(50), use_container_width=True)

            if st.button("✅ Apply & Download"):
                started = time.time()
                output_path = workspace / f"clean_{upload.name}"
                cleaned_df.to_csv(output_path, index=False)
                history.log_job(
                    "Data Cleaner", upload.name, output_path.name,
                    duration_seconds=round(time.time() - started, 2),
                )
                st.download_button(
                    "⬇️ Download cleaned CSV",
                    data=output_path.read_bytes(),
                    file_name=output_path.name,
                    mime="text/csv",
                )
        else:
            st.info("Choose your options above, then click **Preview Changes** to see the result before downloading.")
