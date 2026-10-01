import streamlit as st

from utils.styling import inject_base_css, card
from utils.guard import require_login
from utils.auth import get_user
from utils.content import (
    get_content,
    list_content_for_course,
    vote_difficulty,
    average_difficulty,
    add_comment,
    update_content,
    delete_content,
    delete_content_admin,
)
from utils.quiz import generate_quiz, has_taken_today, record_quiz_result, mastery_band, get_citation
from utils.coach import generate_walkthrough
from utils import quiz_ui

inject_base_css()
require_login()

user = get_user(st.session_state.username)
current_course = user.get("current_course")

if not current_course:
    st.warning("You haven't selected a course yet.")
    st.page_link("pages/1_Select_Course.py", label="Go select a course", icon="📚")
    st.stop()

st.title(f"**{current_course}**")


def open_quiz(quiz_type: str) -> None:
    st.session_state["auto_start_quiz"] = quiz_type
    st.switch_page("pages/10_Quizzes.py")


if not has_taken_today(st.session_state.username, current_course, "check-in"):
    with st.container(border=True):
        q1, q2 = st.columns([4, 1.4])
        q1.markdown("**Time for your check-in quiz!** It opens in the Quizzes tab and takes a few minutes.")
        if q2.button("Start check-in", key="cp_checkin", use_container_width=True):
            open_quiz("check-in")

if "viewing_content_id" not in st.session_state:
    st.session_state.viewing_content_id = None
if "trust_confirmed" not in st.session_state:
    st.session_state.trust_confirmed = False


def difficulty_label(score: float | None) -> str:
    if score is None:
        return "Not yet rated"
    return f"{'👍' * round(score)} ({score:.1f}/10)"


# ---------- Detail view ----------
if st.session_state.viewing_content_id:
    item = get_content(st.session_state.viewing_content_id)
    if not item:
        st.error("This content no longer exists.")
        st.session_state.viewing_content_id = None
        st.stop()

    if st.button("⬅️ Back to course"):
        st.session_state.viewing_content_id = None
        st.session_state.trust_confirmed = False
        st.rerun()

    if item.get("picture"):
        st.image(item["picture"], width=300)

    st.header(item["title"])
    st.caption(
        f"{item['course']} · {item['content_type']} · Created by {item['creator']} on {item['date_created'][:10]}"
    )
    st.write(f"**Difficulty:** {difficulty_label(average_difficulty(item))}")
    if item.get("citation"):
        st.caption(f"Source: {item['citation']}")

    st.divider()
    st.subheader("Open This Content")

    if not st.session_state.trust_confirmed:
        if st.button("Open Content"):
            st.session_state.show_trust_warning = True
            st.rerun()

        if st.session_state.get("show_trust_warning"):
            st.warning(
                "⚠️ This is taking you to an external link. "
                "Make sure you trust the creator before proceeding."
            )
            w1, w2 = st.columns(2)
            with w1:
                if st.button("✅ Yes, I trust them"):
                    st.session_state.trust_confirmed = True
                    st.session_state.show_trust_warning = False
                    st.rerun()
            with w2:
                if st.button("⬅️ No, go back"):
                    st.session_state.show_trust_warning = False
                    st.rerun()
    else:
        st.link_button(f"Open on {item['add_method']} (new tab)", item["url"])
        st.caption("If the site asks you to make a copy, you can do that once it opens.")

    st.divider()

    if user.get("account_type") == "Student":
        st.subheader("Rate the Difficulty")
        score = st.select_slider(
            "How hard was this activity?",
            options=list(range(1, 11)),
            format_func=lambda n: "👍" * n,
            value=item.get("votes", {}).get(st.session_state.username, 5),
        )
        if st.button("Submit Rating"):
            vote_difficulty(st.session_state.viewing_content_id, st.session_state.username, score)
            st.success("Thanks for rating!")
            st.rerun()

    st.subheader("Comments")
    for c in item.get("comments", []):
        card(c["user"], c["text"], tone="lavender")

    new_comment = st.text_area("Leave feedback for future students")
    if st.button("Post Comment"):
        if new_comment.strip():
            add_comment(st.session_state.viewing_content_id, st.session_state.username, new_comment.strip())
            st.rerun()

    is_creator = item["creator"] == st.session_state.username
    is_admin_override = user.get("account_type") == "Administrator" and item.get("is_ai_seeded")
    if is_creator or is_admin_override:
        st.divider()
        with st.expander("Manage this content"):
            new_title = st.text_input("Title", value=item["title"], key="edit_title_detail")
            new_url = st.text_input("Link", value=item["url"], key="edit_url_detail")
            m1, m2 = st.columns(2)
            with m1:
                if st.button("Save Changes", key="save_detail"):
                    if is_creator:
                        update_content(
                            st.session_state.viewing_content_id,
                            st.session_state.username,
                            title=new_title,
                            url=new_url,
                        )
                    else:
                        update_content(
                            st.session_state.viewing_content_id,
                            item["creator"],
                            title=new_title,
                            url=new_url,
                        )
                    st.success("Updated.")
                    st.rerun()
            with m2:
                if st.button("Delete Content", key="delete_detail"):
                    if is_creator:
                        delete_content(st.session_state.viewing_content_id, st.session_state.username)
                    else:
                        delete_content_admin(st.session_state.viewing_content_id)
                    st.session_state.viewing_content_id = None
                    st.rerun()

    st.stop()

# ---------- Content feed ----------
content_items = list_content_for_course(current_course)

if not content_items:
    st.info("No content has been added for this course yet.")
    if user.get("account_type") == "Administrator":
        st.page_link("pages/4_Add_Content.py", label="Add content for this course", icon="➕")
else:
    cols = st.columns(3)
    for i, (cid, item) in enumerate(content_items):
        with cols[i % 3]:
            if item.get("picture"):
                st.image(item["picture"], use_container_width=True)
            st.markdown(f"**{item['title']}**")
            st.caption(
                f"{item['content_type']} · by {item['creator']}<br>"
                f"{item['date_created'][:10]} · {difficulty_label(average_difficulty(item))}",
                unsafe_allow_html=True,
            )
            if st.button("View", key=f"view_{cid}"):
                st.session_state.viewing_content_id = cid
                st.session_state.trust_confirmed = False
                st.rerun()

st.divider()
st.subheader("Wrapping up for today?")
st.caption("Take a quick check-out quiz before you go. It opens in the Quizzes tab and helps track your mastery over time.")
if has_taken_today(st.session_state.username, current_course, "check-out"):
    st.caption("You've already completed today's check-out quiz for this course.")
elif st.button("Finish for Today (check-out quiz)"):
    open_quiz("check-out")
