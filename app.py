"""
FreelanceFlow — Dashboard
==========================
Product home screen: greeting, quick actions, job stats, recent jobs,
and popular automations. The actual tool pages live under pages/.

Run with:
    streamlit run app.py
"""
from datetime import datetime

import streamlit as st

from core import favorites, history
from core.registry import TOOLS, get_tool
from webapp_utils import apply_branding

st.set_page_config(page_title="FreelanceFlow", page_icon="🛠️", layout="wide")
apply_branding()

hour = datetime.now().hour
greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"

st.markdown(
    f"""
    <div class="hero">
        <h1>{greeting} 👋</h1>
        <p>Automate your repetitive work in a few clicks — upload a file, configure it,
        preview the result, and download.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

query = st.text_input("What do you want to automate?", placeholder="Search automations…", key="dashboard_search")
if query.strip():
    q = query.strip().lower()
    matches = [t for t in TOOLS if q in t["name"].lower() or q in t["description"].lower()]
    if matches:
        st.write("**Matching automations:**")
        for t in matches:
            st.page_link(t["page"], label=f"{t['icon']} {t['name']} — {t['description']}")
    else:
        st.caption("No matches — try the Automation Center to browse everything.")
    st.divider()

st.subheader("Quick Actions")
qa_cols = st.columns(4)
quick_actions = [
    ("🧹", "Clean Data", "data_cleaner"),
    ("📊", "Merge CSVs", "csv_merger"),
    ("📈", "Create Report", "excel_report"),
    ("📁", "Organize Files", "folder_organizer"),
]
for col, (icon, label, slug) in zip(qa_cols, quick_actions):
    tool = get_tool(slug)
    with col:
        if tool:
            st.page_link(tool["page"], label=f"{icon} {label}")

st.divider()

stats = history.get_stats()
s1, s2, s3 = st.columns(3)
s1.metric("Jobs Completed", stats["jobs_completed"])
s2.metric("Files Processed", stats["files_processed"])
s3.metric("Estimated Time Saved", f"{stats['estimated_minutes_saved']} min")
st.caption(
    "Time saved is an estimate (a fixed few minutes per completed job vs. doing it by hand), "
    "not a measured figure."
)

st.divider()

col_recent, col_popular = st.columns([2, 1])
with col_recent:
    st.subheader("Recent Jobs")
    recent = history.get_recent(6)
    if not recent:
        st.caption("No jobs run yet — try an automation from the Automation Center.")
    else:
        for job in recent:
            status_icon = "✅" if job["status"] == "success" else "⚠️"
            when = job["timestamp"].replace("T", " ")
            out = job.get("output") or "—"
            st.markdown(f"{status_icon} **{job['tool']}** · `{job['input']}` → `{out}` · {when}")

with col_popular:
    st.subheader("Popular Automations")
    popular_slugs = history.get_popular_tools(4)
    show_slugs = popular_slugs if popular_slugs else [t["slug"] for t in TOOLS[:4]]
    favorited = set(favorites.get_all())
    for slug in show_slugs:
        tool = get_tool(slug)
        if tool:
            star = "★" if slug in favorited else ""
            st.page_link(tool["page"], label=f"{tool['icon']} {tool['name']} {star}")

st.markdown(
    """
    <p style="margin-top:1.8rem; color:#6B7A87; font-size:0.88rem;">
    <strong>How it works:</strong> every tool runs locally in this app. Files you upload are
    processed in a temporary folder that's deleted as soon as your result is ready to
    download — nothing is uploaded anywhere else or kept on disk.
    </p>
    """,
    unsafe_allow_html=True,
)
