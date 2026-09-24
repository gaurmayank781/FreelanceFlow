"""Data Quality Report — quality score, issues, recommendations. Export to Excel/PDF."""
import sys
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data_quality.generate_quality_report import (  # noqa: E402
    build_quality_summary, export_quality_report_excel, export_quality_report_pdf,
)
from core import history  # noqa: E402
from core.errors import show_friendly_error  # noqa: E402
from webapp_utils import apply_branding, page_header, temp_workspace  # noqa: E402

st.set_page_config(page_title="Data Quality Report", page_icon="🏅", layout="wide")
apply_branding()
page_header(
    "🏅", "Data Quality Report",
    "A professional summary connecting the CSV Analyzer and Data Cleaner — score, issues, "
    "and recommendations, exportable to Excel or PDF.",
)

upload = st.file_uploader("CSV or Excel file", type=["csv", "xlsx", "xls"])

if upload:
    with temp_workspace() as workspace:
        input_path = workspace / upload.name
        input_path.write_bytes(upload.getbuffer())

        started = time.time()
        try:
            summary = build_quality_summary(input_path)
        except Exception as exc:
            history.log_job("Data Quality Report", upload.name, status="error", error=str(exc))
            show_friendly_error(exc, "Make sure the file has a header row and at least one row of data.")
        else:
            history.log_job(
                "Data Quality Report", upload.name, status="success",
                duration_seconds=round(time.time() - started, 2),
            )
            c1, c2, c3 = st.columns(3)
            c1.metric("Rows", summary["rows"])
            c2.metric("Columns", summary["columns"])
            c3.metric("Quality Score", f"{summary['score']}/100")

            st.subheader("Issues")
            if summary["issues"]:
                for issue in summary["issues"]:
                    st.warning(issue)
            else:
                st.success("No issues found — dataset looks clean.")

            st.subheader("Recommendations")
            for rec in summary["recommendations"]:
                st.markdown(f"- {rec}")

            st.divider()
            st.subheader("Export")
            col1, col2 = st.columns(2)
            with col1:
                excel_path = workspace / (input_path.stem + "_quality_report.xlsx")
                export_quality_report_excel(summary, excel_path)
                st.download_button(
                    "⬇️ Download Excel report", data=excel_path.read_bytes(),
                    file_name=excel_path.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            with col2:
                pdf_path = workspace / (input_path.stem + "_quality_report.pdf")
                export_quality_report_pdf(summary, pdf_path)
                st.download_button(
                    "⬇️ Download PDF report", data=pdf_path.read_bytes(),
                    file_name=pdf_path.name, mime="application/pdf",
                )
