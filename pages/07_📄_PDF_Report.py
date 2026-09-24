"""PDF Report — turn a CSV into a formatted PDF table report."""
import base64
import sys
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pdf_generator.generate_pdf import generate_pdf  # noqa: E402
from core import history  # noqa: E402
from core.errors import show_friendly_error  # noqa: E402
from core.io_utils import read_csv_safe  # noqa: E402
from webapp_utils import apply_branding, page_header, temp_workspace  # noqa: E402

st.set_page_config(page_title="PDF Report", page_icon="📄", layout="wide")
apply_branding()
page_header(
    "📄", "PDF Report Generator",
    "Turn a CSV into a formatted, print-ready PDF table with a title, timestamp, "
    "and alternating row colors.",
)

with st.form("pdf_report_form"):
    upload = st.file_uploader("CSV file", type="csv")
    title = st.text_input("Report title", value="Report")
    submitted = st.form_submit_button("Generate PDF Report", type="primary")

if submitted:
    if not upload:
        st.warning("Upload a CSV file first.")
    else:
        with temp_workspace() as workspace:
            input_path = workspace / upload.name
            input_path.write_bytes(upload.getbuffer())
            output_path = workspace / (Path(upload.name).stem + "_report.pdf")

            started = time.time()
            try:
                summary = generate_pdf(input_path, output_path, title=title.strip() or "Report")
            except Exception as exc:
                history.log_job("PDF Report", upload.name, status="error", error=str(exc))
                show_friendly_error(exc, "Make sure the file is a plain CSV with a header row.")
            else:
                history.log_job(
                    "PDF Report", upload.name, output_path.name,
                    duration_seconds=round(time.time() - started, 2),
                )
                st.success(f"PDF generated: {summary['rows_written']} rows, {len(summary['columns'])} columns.")

                st.subheader("Preview")
                st.dataframe(read_csv_safe(input_path).head(50), use_container_width=True)

                pdf_bytes = output_path.read_bytes()
                st.download_button(
                    "⬇️ Download PDF report",
                    data=pdf_bytes,
                    file_name=output_path.name,
                    mime="application/pdf",
                )

                with st.expander("Preview PDF"):
                    b64 = base64.b64encode(pdf_bytes).decode()
                    st.markdown(
                        f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600"></iframe>',
                        unsafe_allow_html=True,
                    )
