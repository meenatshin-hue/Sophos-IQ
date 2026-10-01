import streamlit as st

from utils.auth import get_user
from utils.daily import joke_html, milestone_html
from utils.guard import logout, require_login
from utils.styling import card, inject_base_css

inject_base_css()
require_login()

user = get_user(st.session_state.username)
name = user.get("display_name") or st.session_state.username

st.title(f"Welcome back, {name}! 🎓")
st.write("Use the sidebar to open your courses, quizzes, forum, clubs, and more.")

streak = int(user.get("streak", 0))
banner = milestone_html(streak)
if banner:
    st.markdown(banner, unsafe_allow_html=True)
st.markdown(joke_html(), unsafe_allow_html=True)
st.write("")

col1, col2, col3 = st.columns(3)
with col1:
    card("Grade Level", user.get("grade_level", "Not set"), tone="green")
with col2:
    card("Current Course", user.get("current_course") or "None selected yet", tone="aqua")
with col3:
    card("School District", user.get("school_district", "Not set"), tone="lavender")

st.divider()
st.subheader("Where to go next")
card(
    "Select a Course",
    "Head to <b>Select Course</b> in the sidebar to pick up where you left off or choose a new subject.",
    tone="green",
)
card(
    "Quizzes",
    "Take today's practice quiz or your unit test on the <b>Quizzes</b> page.",
    tone="aqua",
)
card(
    "View Mastery",
    "Check <b>View Mastery</b> to see how you're progressing in each course.",
    tone="lavender",
)

st.divider()
if st.button("Log out"):
    logout()
    st.rerun()
