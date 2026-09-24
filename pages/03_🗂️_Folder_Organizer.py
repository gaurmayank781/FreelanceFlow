"""Folder Organizer — sort uploaded files into type-based folders."""
import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from folder_organizer.organize_folder import organize_folder  # noqa: E402
from core import history  # noqa: E402
from core.errors import show_friendly_error  # noqa: E402
from webapp_utils import (  # noqa: E402
    apply_branding, capture_log, page_header, save_uploads, temp_workspace, zip_folder_bytes,
)

st.set_page_config(page_title="Folder Organizer", page_icon="🗂️", layout="wide")
apply_branding()
page_header(
    "🗂️", "Folder Organizer",
    "Sort a messy batch of files into type-based folders — Images, Documents, PDFs, "
    "Spreadsheets, Videos, Audio, Archives, Code, and Other.",
)

with st.form("folder_organizer_form"):
    uploads = st.file_uploader("Files to organize", accept_multiple_files=True)
    dry_run = st.checkbox("Dry run (preview only, don't actually move files)", value=True)
    submitted = st.form_submit_button("Organize Files", type="primary")

if submitted:
    if not uploads:
        st.warning("Upload at least one file first.")
    else:
        with temp_workspace() as workspace:
            save_uploads(uploads, workspace)
            started = time.time()
            try:
                with capture_log("organize_folder") as lines:
                    summary = organize_folder(workspace, dry_run=dry_run)
            except Exception as exc:
                history.log_job("Folder Organizer", f"{len(uploads)} files", status="error", error=str(exc))
                show_friendly_error(exc)
            else:
                st.code("\n".join(lines) or "Nothing to show.", language=None)

                if summary:
                    st.subheader("Summary")
                    st.bar_chart(pd.Series(summary, name="files"))

                if not dry_run and summary:
                    history.log_job(
                        "Folder Organizer", f"{len(uploads)} files", "organized_files.zip",
                        duration_seconds=round(time.time() - started, 2),
                    )
                    zip_bytes = zip_folder_bytes(workspace)
                    st.download_button(
                        "⬇️ Download organized folder (.zip)",
                        data=zip_bytes,
                        file_name="organized_files.zip",
                        mime="application/zip",
                    )
                elif dry_run and summary:
                    st.info("This was a preview — uncheck 'Dry run' and submit again to actually organize and download.")
