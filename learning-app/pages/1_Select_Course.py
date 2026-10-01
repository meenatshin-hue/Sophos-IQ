import streamlit as st

from utils.styling import inject_base_css, card
from utils.guard import require_login
from utils.auth import get_user, update_user
from utils.courses import COURSE_CATALOG, category_for_course

inject_base_css()
require_login()

user = get_user(st.session_state.username)

st.title("📚 Select a Course")
st.write("Browse by category, then pick a course. Your progress is saved automatically to your account.")

current_course = user.get("current_course")
default_category = category_for_course(current_course) if current_course else None
categories = list(COURSE_CATALOG.keys())

category = st.selectbox(
    "Category",
    categories,
    index=categories.index(default_category) if default_category in categories else 0,
)

courses_in_category = COURSE_CATALOG[category]
default_index = (
    courses_in_category.index(current_course) if current_course in courses_in_category else 0
)
course = st.selectbox("Course", courses_in_category, index=default_index)

if st.button("Go to Course"):
    update_user(st.session_state.username, current_course=course)
    courses_taken = set(user.get("courses_taken", []))
    courses_taken.add(course)
    update_user(st.session_state.username, courses_taken=list(courses_taken))
    st.success(f"Selected: {course}. Open the Course Page from the sidebar to continue.")
    st.rerun()

st.divider()
card("Currently Continuing", current_course or "No course selected yet.", tone="lavender")

if user.get("courses_taken"):
    st.subheader("Courses You've Taken")
    st.write(", ".join(user["courses_taken"]))
