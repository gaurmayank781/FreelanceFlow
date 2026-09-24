"""Automation Center — search, filter, and favorite every automation tool."""
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import favorites  # noqa: E402
from core.registry import CATEGORIES, TOOLS  # noqa: E402
from webapp_utils import apply_branding, page_header  # noqa: E402

st.set_page_config(page_title="Automation Center", page_icon="🧰", layout="wide")
apply_branding()
page_header("🧰", "Automation Center", "Search, filter, and favorite the automations you use most.")

col_search, col_filter = st.columns([3, 1])
with col_search:
    query = st.text_input("What do you want to automate?", placeholder="e.g. clean, merge, rename…")
with col_filter:
    category = st.selectbox("Category", ["All"] + CATEGORIES)

favorited = set(favorites.get_all())

tools = TOOLS
if category != "All":
    tools = [t for t in tools if t["category"] == category]
if query.strip():
    q = query.strip().lower()
    tools = [t for t in tools if q in t["name"].lower() or q in t["description"].lower()]

if not tools:
    st.info("No automations match that search.")
else:
    cols = st.columns(3, gap="medium")
    for i, tool in enumerate(tools):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {tool['icon']} {tool['name']}")
                st.caption(tool["category"])
                st.write(tool["description"])
                b1, b2 = st.columns([1, 1])
                with b1:
                    st.page_link(tool["page"], label="Open →")
                with b2:
                    is_fav = tool["slug"] in favorited
                    if st.button("★ Favorited" if is_fav else "☆ Favorite", key=f"fav_{tool['slug']}"):
                        favorites.toggle(tool["slug"])
                        st.rerun()
