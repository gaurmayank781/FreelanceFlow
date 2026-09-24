"""
Shared helpers for the Automation Toolkit Streamlit app.

Keeps every page in `pages/` thin: save uploads to a temp folder, capture
the core scripts' existing logging output so it can be shown on screen,
and zip up results for download. None of this touches the original
tool scripts — they're imported and used exactly as they are.
"""
from __future__ import annotations

import io
import logging
import shutil
import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path


class _ListLogHandler(logging.Handler):
    """A logging handler that collects messages into a list instead of printing them."""

    def __init__(self):
        super().__init__()
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.lines.append(self.format(record))


@contextmanager
def capture_log(logger_name: str):
    """
    Capture everything a core script logs while the `with` block runs,
    so it can be displayed in the UI as a console-style output.

    Usage:
        with capture_log("rename_files") as lines:
            rename_files(...)
        st.code("\\n".join(lines))
    """
    logger = logging.getLogger(logger_name)
    handler = _ListLogHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    previous_level = logger.level
    logger.setLevel(logging.INFO)
    try:
        yield handler.lines
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)


def save_uploads(uploaded_files, folder: Path) -> None:
    """Write a list of Streamlit UploadedFile objects into `folder`."""
    folder.mkdir(parents=True, exist_ok=True)
    for uploaded in uploaded_files:
        (folder / uploaded.name).write_bytes(uploaded.getbuffer())


def zip_folder_bytes(folder: Path) -> bytes:
    """Zip every file under `folder` (recursively) and return the zip's bytes."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(folder.rglob("*")):
            if file.is_file():
                zf.write(file, arcname=file.relative_to(folder))
    return buffer.getvalue()


@contextmanager
def temp_workspace():
    """A temp directory scoped to one run, always cleaned up afterwards."""
    path = Path(tempfile.mkdtemp(prefix="automation_toolkit_"))
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


# ---------------------------------------------------------------------------
# Branding / styling
#
# Streamlit's default look (plain white sidebar, unstyled titles, stock
# menu/footer) reads as "someone's dev script" rather than a product. This
# section adds one CSS block plus two small HTML components — a branded
# sidebar header and a consistent icon-badge page header — and every page
# calls `apply_branding()` once near the top to pick them up.
# ---------------------------------------------------------------------------

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

/* Hide Streamlit's own chrome so the app reads as a standalone product */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* --- Sidebar --------------------------------------------------------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1F4E78 0%, #16374F 100%);
}
[data-testid="stSidebar"] * { color: #F2F6FA !important; }

[data-testid="stSidebarNav"] { padding-top: 0; }
[data-testid="stSidebarNav"] ul { padding-top: 0.25rem; }
[data-testid="stSidebarNav"] a {
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
    margin: 0.12rem 0.6rem;
    transition: background 0.15s ease;
}
[data-testid="stSidebarNav"] a:hover { background: rgba(255,255,255,0.12); }
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: rgba(255,255,255,0.18);
    font-weight: 600;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 1rem 1.1rem 0.9rem 1.1rem;
    border-bottom: 1px solid rgba(255,255,255,0.15);
    margin-bottom: 0.4rem;
}
.sidebar-brand .badge {
    width: 36px; height: 36px;
    border-radius: 10px;
    background: rgba(255,255,255,0.15);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.15rem;
    flex-shrink: 0;
}
.sidebar-brand .name { font-weight: 700; font-size: 0.95rem; line-height: 1.15; }
.sidebar-brand .sub  { font-size: 0.72rem; opacity: 0.75; }

/* --- Home page hero ---------------------------------------------------- */
.hero {
    background: linear-gradient(120deg, #1F4E78 0%, #2E6DA4 100%);
    border-radius: 18px;
    padding: 2.4rem 2.6rem;
    color: white;
    margin-bottom: 1.8rem;
    box-shadow: 0 10px 28px rgba(31,78,120,0.22);
}
.hero h1 { color: white !important; font-size: 2.3rem; margin: 0 0 0.5rem 0; }
.hero p  { color: rgba(255,255,255,0.9); font-size: 1.05rem; max-width: 640px; margin: 0; }

/* --- Tool cards on the home page --------------------------------------- */
div[class*="st-key-card_"] {
    background: #FFFFFF;
    border: 1px solid #E7ECF1;
    border-radius: 14px;
    padding: 1.35rem 1.4rem 1.05rem 1.4rem;
    box-shadow: 0 2px 10px rgba(16,24,40,0.045);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    height: 100%;
}
div[class*="st-key-card_"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 26px rgba(16,24,40,0.1);
}
.tool-icon {
    width: 42px; height: 42px;
    border-radius: 11px;
    background: #EAF1F8;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.35rem;
    margin-bottom: 0.65rem;
}
.tool-title { font-size: 1.1rem; font-weight: 700; color: #16374F; margin-bottom: 0.3rem; }
.tool-desc  { font-size: 0.88rem; color: #5B6B79; line-height: 1.45; min-height: 3.2em; }

[data-testid="stPageLink"] a { font-weight: 600; }

/* --- Tool page header ---------------------------------------------------- */
.page-header {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
    border-bottom: 2px solid #EAF1F8;
}
.page-header .badge {
    width: 46px; height: 46px;
    border-radius: 12px;
    background: linear-gradient(135deg, #1F4E78, #2E6DA4);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.45rem;
    flex-shrink: 0;
}
.page-header .titles h1 { font-size: 1.6rem; margin: 0; color: #16374F; }
.page-header .titles p  { margin: 0.15rem 0 0 0; color: #6B7A87; font-size: 0.92rem; }

/* --- Inputs & buttons ---------------------------------------------------- */
.stButton>button, .stDownloadButton>button, [data-testid="stFormSubmitButton"] button {
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1.25rem;
}
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    border-radius: 8px;
}
[data-testid="stFileUploaderDropzone"] { border-radius: 10px; }
</style>
"""

_SIDEBAR_BRAND = """
<div class="sidebar-brand">
  <div class="badge">🛠️</div>
  <div>
    <div class="name">Automation Toolkit</div>
    <div class="sub">by Mayu</div>
  </div>
</div>
"""


def inject_style() -> None:
    """Inject the shared CSS. Call once near the top of every page."""
    import streamlit as st
    st.markdown(_CSS, unsafe_allow_html=True)


def apply_branding() -> None:
    """Inject CSS and the sidebar brand header. Call once per page, right
    after st.set_page_config()."""
    import streamlit as st
    inject_style()
    st.sidebar.markdown(_SIDEBAR_BRAND, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str) -> None:
    """Render the consistent icon-badge header used on every tool page."""
    import streamlit as st
    st.markdown(
        f"""
        <div class="page-header">
            <div class="badge">{icon}</div>
            <div class="titles">
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
