"""Favorites — quick access to the automations you've starred."""
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import favorites  # noqa: E402
from core.registry import get_tool  # noqa: E402
from webapp_utils import apply_branding, page_header  # noqa: E402

st.set_page_config(page_title="Favorites", page_icon="⭐", layout="wide")
apply_branding()
page_header("⭐", "Favorites", "The automations you've starred for quick access.")

favorited_slugs = favorites.get_all()
tools = [get_tool(slug) for slug in favorited_slugs]
tools = [t for t in tools if t]  # drop any stale slugs

if not tools:
    st.info("No favorites yet. Star a tool from the Automation Center to see it here.")
    st.page_link("pages/01_🧰_Automation_Center.py", label="Go to Automation Center →")
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
                    if st.button("Remove", key=f"unfav_{tool['slug']}"):
                        favorites.toggle(tool["slug"])
                        st.rerun()
