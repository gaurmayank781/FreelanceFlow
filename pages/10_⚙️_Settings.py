"""Settings — appearance, processing, files, and security info."""
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import store  # noqa: E402
from webapp_utils import apply_branding, page_header  # noqa: E402

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
apply_branding()
page_header("⚙️", "Settings", "Preferences for how FreelanceFlow behaves.")

st.subheader("Appearance")
st.selectbox(
    "Theme", ["System", "Light", "Dark"],
    help="FreelanceFlow follows your browser/OS theme by default. "
         "Use Streamlit's own Settings menu (top-right ⋮) to override it.",
)

st.subheader("Processing")
st.info("All processing runs locally in this app. Nothing you upload is sent to an external server.")

st.subheader("Files")
st.caption(f"Job history and favorites are stored locally at `{store.DATA_DIR}`.")
if st.button("Clear job history"):
    store.save("history", [])
    st.success("Job history cleared.")
if st.button("Clear favorites"):
    store.save("favorites", [])
    st.success("Favorites cleared.")

st.subheader("Security")
st.markdown(
    "- Uploaded files are processed in a temporary folder that's deleted as soon as your "
    "result is ready — nothing is kept on disk after your session.\n"
    "- No credentials are hardcoded anywhere in this app.\n"
    "- Email Automation (SMTP) reads credentials only from environment variables at runtime "
    "and never writes them to disk — see `.env.example` for the variable names."
)
