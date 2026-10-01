from datetime import date
from pathlib import Path

import streamlit as st

from utils.auth import get_user, update_user
from utils.daily import daily_dialog
from utils.rotation import release_due_links
from utils.search import search_lessons
from utils.streak import touch_streak_info
from utils.styling import inject_base_css

LOGO = Path(__file__).resolve().parent / "assets" / "siq_logo.png"

st.set_page_config(page_title="SophosIQ", page_icon=str(LOGO), layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "stage" not in st.session_state:
    st.session_state.stage = "splash"
if st.session_state.logged_in and "theme" not in st.session_state:
    st.session_state.theme = (get_user(st.session_state.username) or {}).get("theme", "light")

inject_base_css()
release_due_links()


def open_result(content_id: str) -> None:
    st.session_state.viewing_content_id = content_id
    st.session_state.trust_confirmed = False
    st.session_state.show_trust_warning = False
    st.session_state.global_search = ""
    st.session_state.goto_course_page = True


def render_search_bar() -> None:
    st.text_input(
        "Search",
        key="global_search",
        placeholder="🔎  Search any lesson in any course (try: fractions, photosynthesis, SAT, Khan Academy)",
        label_visibility="collapsed",
    )
    query = st.session_state.get("global_search", "").strip()
    if not query:
        return
    results, total = search_lessons(query)
    with st.container(border=True):
        if not results:
            st.caption(f"No lessons found for \"{query}\".")
            return
        st.caption(f"{total} lesson{'s' if total != 1 else ''} found" + (" - showing the top 8" if total > 8 else ""))
        for cid, item in results:
            st.button(
                f"{item['title']}  |  {item['course']}  |  {item['content_type']}",
                key=f"search_{cid}",
                on_click=open_result,
                args=(cid,),
                use_container_width=True,
            )


if st.session_state.logged_in:
    st.logo(str(LOGO), size="large")
    me = st.session_state.username

    if "streak_info" not in st.session_state:
        st.session_state.streak_info = touch_streak_info(me)
    if not st.session_state.get("daily_shown"):
        st.session_state.daily_shown = True
        user = get_user(me) or {}
        today = date.today().isoformat()
        if (
            user.get("notifications_enabled")
            and st.session_state.streak_info["status"] != "same_day"
            and user.get("popup_date") != today
        ):
            update_user(me, popup_date=today)
            daily_dialog(st.session_state.streak_info)

    navigation = st.navigation(
        [
            st.Page("pages/0_Home.py", title="Home", icon="🏠", default=True),
            st.Page("pages/1_Select_Course.py", title="Select Course", icon="📚"),
            st.Page("pages/2_Course_Page.py", title="Course Page", icon="📖"),
            st.Page("pages/10_Quizzes.py", title="Quizzes", icon="📝"),
            st.Page("pages/5_View_Mastery.py", title="View Mastery", icon="📊"),
            st.Page("pages/3_Forum.py", title="Forum", icon="💬"),
            st.Page("pages/4_Add_Content.py", title="Add Content", icon="➕"),
            st.Page("pages/6_Clubs.py", title="Student Clubs", icon="🌟"),
            st.Page("pages/7_Help_and_Info.py", title="Help & Info", icon="❓"),
            st.Page("pages/8_Your_Account.py", title="Your Account", icon="👤"),
            st.Page("pages/11_Settings.py", title="Settings", icon="⚙️"),
            st.Page("pages/9_User_Directory.py", title="User Directory", icon="🗂️"),
        ]
    )
    if st.session_state.pop("goto_course_page", False):
        st.switch_page("pages/2_Course_Page.py")
    render_search_bar()
elif st.session_state.stage == "splash":
    navigation = st.navigation([st.Page("screens/splash.py", title="SophosIQ")], position="hidden")
else:
    navigation = st.navigation([st.Page("screens/login.py", title="Log in")], position="hidden")

navigation.run()
