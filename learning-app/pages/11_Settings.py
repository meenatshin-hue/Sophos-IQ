import streamlit as st

from utils.auth import get_user, update_user
from utils.guard import require_login
from utils.styling import inject_base_css

inject_base_css()
require_login()

me = st.session_state.username
user = get_user(me)

st.title("⚙️ Settings")

with st.container(border=True):
    st.subheader("Appearance")
    st.caption("Switch the whole app between a bright and a dark look.")
    theme_label = st.radio(
        "Theme",
        ["Light mode", "Dark mode"],
        index=1 if st.session_state.get("theme", "light") == "dark" else 0,
        horizontal=True,
        label_visibility="collapsed",
    )

with st.container(border=True):
    st.subheader("Notifications")
    st.caption(
        "When this is on, you get one daily check-in pop-up the first time you open the app each day. "
        "It has your streak news, a milestone badge if you earned one, and a joke of the day."
    )
    notifications = st.toggle(
        "Enable daily notifications",
        value=bool(user.get("notifications_enabled", False)),
    )

if st.button("Save settings"):
    new_theme = "dark" if theme_label == "Dark mode" else "light"
    update_user(me, theme=new_theme, notifications_enabled=notifications)
    st.session_state.theme = new_theme
    st.toast("Settings saved", icon="✅")
    st.rerun()
