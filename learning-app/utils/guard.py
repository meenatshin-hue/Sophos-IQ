import streamlit as st

from utils.rotation import release_due_links
from utils.streak import show_streak


def logout() -> None:
    st.session_state.logged_in = False
    st.session_state.username = None
    for key in ("streak_info", "daily_shown", "global_search", "theme"):
        st.session_state.pop(key, None)


def require_login():
    release_due_links()
    if not st.session_state.get("logged_in"):
        st.warning("Please log in from the Home page first.")
        st.page_link("app.py", label="Go to Home", icon="🏠")
        st.stop()
    show_streak(st.session_state.username)
