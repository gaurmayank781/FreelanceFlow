"""Bulk Renamer — rename a batch of uploaded files with a numbered pattern."""
import sys
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bulk_renamer.rename_files import rename_files  # noqa: E402
from core import history  # noqa: E402
from core.errors import show_friendly_error  # noqa: E402
from webapp_utils import (  # noqa: E402
    apply_branding, capture_log, page_header, save_uploads, temp_workspace, zip_folder_bytes,
)

st.set_page_config(page_title="Bulk Renamer", page_icon="📁", layout="wide")
apply_branding()
page_header(
    "📁", "Bulk Renamer",
    "Rename a batch of files with a numbered pattern, keeping each file's original extension.",
)

with st.form("bulk_renamer_form"):
    uploads = st.file_uploader("Files to rename", accept_multiple_files=True)
    col1, col2 = st.columns(2)
    with col1:
        pattern = st.text_input(
            "Naming pattern", value="file_{n}",
            help="Use {n} for the number, e.g. 'vacation_{n}'",
        )
    with col2:
        start = st.number_input("Start number", min_value=0, value=1, step=1)
    dry_run = st.checkbox("Dry run (preview only, don't actually rename)", value=True)
    submitted = st.form_submit_button("Rename Files", type="primary")

if submitted:
    if not uploads:
        st.warning("Upload at least one file first.")
    elif "{n}" not in pattern:
        st.error("Pattern must include {n}, e.g. 'photo_{n}'.")
    else:
        with temp_workspace() as workspace:
            save_uploads(uploads, workspace)
            started = time.time()
            try:
                with capture_log("rename_files") as lines:
                    count = rename_files(workspace, pattern, start=int(start), dry_run=dry_run)
            except Exception as exc:
                history.log_job("Bulk Renamer", f"{len(uploads)} files", status="error", error=str(exc))
                show_friendly_error(exc)
            else:
                st.success(f"{count} file(s) {'would be renamed' if dry_run else 'renamed'}.")
                st.code("\n".join(lines) or "Nothing to show.", language=None)

                if not dry_run and count:
                    history.log_job(
                        "Bulk Renamer", f"{len(uploads)} files", "renamed_files.zip",
                        duration_seconds=round(time.time() - started, 2),
                    )
                    zip_bytes = zip_folder_bytes(workspace)
                    st.download_button(
                        "⬇️ Download renamed files (.zip)",
                        data=zip_bytes,
                        file_name="renamed_files.zip",
                        mime="application/zip",
                    )
                elif dry_run and count:
                    st.info("This was a preview — uncheck 'Dry run' and submit again to actually rename and download.")
