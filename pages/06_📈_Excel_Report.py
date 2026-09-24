"""Excel Report — auto-generated dashboard: KPI cards + charts, no config needed."""
import sys
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from excel_automation.generate_report import generate_dashboard_report  # noqa: E402
from core import history  # noqa: E402
from core.errors import show_friendly_error  # noqa: E402
from core.io_utils import read_csv_safe  # noqa: E402
from webapp_utils import apply_branding, page_header, temp_workspace  # noqa: E402

st.set_page_config(page_title="Excel Report", page_icon="📈", layout="wide")
apply_branding()
page_header(
    "📈", "Excel Dashboard Generator",
    "Turn a CSV into an auto-generated Excel dashboard — KPI cards, a trend chart, a top-items "
    "chart, and a category/regional breakdown. Column roles are detected automatically, "
    "no setup needed.",
)

with st.form("excel_report_form"):
    upload = st.file_uploader("CSV file", type="csv")
    title = st.text_input("Dashboard title (optional)", value="")
    submitted = st.form_submit_button("Generate Dashboard", type="primary")

if submitted:
    if not upload:
        st.warning("Upload a CSV file first.")
    else:
        with temp_workspace() as workspace:
            input_path = workspace / upload.name
            input_path.write_bytes(upload.getbuffer())
            output_path = workspace / (Path(upload.name).stem + "_dashboard.xlsx")

            started = time.time()
            try:
                summary = generate_dashboard_report(input_path, output_path, title=title.strip() or None)
            except Exception as exc:
                history.log_job("Excel Report", upload.name, status="error", error=str(exc))
                show_friendly_error(
                    exc, "Make sure the file is a plain CSV with a header row. "
                    "Files exported from Excel with unusual characters are now handled automatically."
                )
            else:
                history.log_job(
                    "Excel Report", upload.name, output_path.name,
                    duration_seconds=round(time.time() - started, 2),
                )
                st.success(f"Dashboard generated: {summary['rows_written']} rows, {summary['charts_placed']} chart(s).")

                st.subheader("KPI Cards")
                kpi_cols = st.columns(len(summary["kpis"]) or 1)
                for col, (label, value) in zip(kpi_cols, summary["kpis"]):
                    col.metric(label, value)

                if summary["notes"]:
                    for note in summary["notes"]:
                        st.caption(f"ℹ️ {note}")

                with st.expander("How were the columns detected?"):
                    roles = summary["detected_roles"]
                    st.write(f"- **Date column:** {roles['date_col'] or 'not detected'}")
                    st.write(f"- **Main value column:** {roles['primary_numeric_col'] or 'not detected'}")
                    st.write(f"- **Top-items column:** {roles['top_items_col'] or 'not detected'}")
                    st.write(f"- **Breakdown column:** {roles['breakdown_col'] or 'not detected'}")

                st.subheader("Preview (raw data)")
                st.dataframe(read_csv_safe(input_path).head(50), use_container_width=True)

                st.download_button(
                    "⬇️ Download Excel dashboard",
                    data=output_path.read_bytes(),
                    file_name=output_path.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
