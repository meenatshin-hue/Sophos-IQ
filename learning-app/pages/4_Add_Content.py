import streamlit as st

from utils.styling import inject_base_css, card
from utils.guard import require_login
from utils.auth import get_user
from utils.courses import all_course_keys
from utils.content import (
    CONTENT_TYPES,
    ADD_METHODS,
    create_content,
    list_content_by_creator,
    update_content,
    delete_content,
)

inject_base_css()
require_login()

user = get_user(st.session_state.username)

st.title("➕ Add Content")

if user.get("account_type") != "Administrator":
    st.warning("Only administrator accounts can add content. Content you add will appear on the matching course page.")
    st.stop()

if "add_content_step" not in st.session_state:
    st.session_state.add_content_step = 1
if "add_content_data" not in st.session_state:
    st.session_state.add_content_data = {}


def reset_wizard():
    st.session_state.add_content_step = 1
    st.session_state.add_content_data = {}


st.write("")
col_center = st.columns([1, 2, 1])[1]
with col_center:
    if st.session_state.add_content_step == 1 and st.button(
        "🆕 Create Content", use_container_width=True
    ):
        reset_wizard()
        st.session_state.add_content_step = "form1"
        st.rerun()

st.divider()

# ---------- Step 1: course, title, type ----------
if st.session_state.add_content_step == "form1":
    st.subheader("Step 1: Basics")
    course = st.selectbox("Course Name", all_course_keys())
    title = st.text_input("Title of Content")
    content_type = st.selectbox("Type of Content", CONTENT_TYPES)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancel"):
            reset_wizard()
            st.rerun()
    with c2:
        if st.button("Next ➡️"):
            if not title.strip():
                st.error("Please enter a title.")
            else:
                st.session_state.add_content_data.update(
                    course=course, title=title.strip(), content_type=content_type
                )
                st.session_state.add_content_step = "form2"
                st.rerun()

# ---------- Step 2: how to add content ----------
elif st.session_state.add_content_step == "form2":
    st.subheader("Step 2: Add the Content")
    add_method = st.selectbox("How do you want to add the content?", ADD_METHODS)
    url = st.text_input(
        "Paste the link" if add_method != "Other Link" else "Paste your link",
        help="Paste a Google Slides / Docs / Drawings / Forms, Canva, Kami, or other link.",
    )
    picture = st.file_uploader("Upload a picture for this content", type=["png", "jpg", "jpeg"])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ Back"):
            st.session_state.add_content_step = "form1"
            st.rerun()
    with c2:
        if st.button("Create Content ✅"):
            if not url.strip():
                st.error("Please add a link for the content.")
            else:
                data = st.session_state.add_content_data
                pic_bytes = picture.read() if picture else None
                pic_name = picture.name if picture else None
                create_content(
                    course=data["course"],
                    title=data["title"],
                    content_type=data["content_type"],
                    add_method=add_method,
                    url=url.strip(),
                    creator=st.session_state.username,
                    picture_bytes=pic_bytes,
                    picture_name=pic_name,
                )
                st.success(f"'{data['title']}' was added to {data['course']}.")
                reset_wizard()
                st.rerun()

st.divider()
st.subheader("Content You've Created")

my_content = list_content_by_creator(st.session_state.username)
if not my_content:
    st.info("You haven't created any content yet.")
else:
    for cid, item in my_content:
        with st.expander(f"{item['title']} — {item['course']}"):
            card(
                item["content_type"],
                f"Added via {item['add_method']} on {item['date_created'][:10]}<br>"
                f"<a href='{item['url']}' target='_blank'>{item['url']}</a>",
                tone="green",
            )
            edit_title = st.text_input("Title", value=item["title"], key=f"title_{cid}")
            edit_url = st.text_input("Link", value=item["url"], key=f"url_{cid}")

            e1, e2 = st.columns(2)
            with e1:
                if st.button("Save Changes", key=f"save_{cid}"):
                    update_content(
                        cid, st.session_state.username, title=edit_title, url=edit_url
                    )
                    st.success("Content updated.")
                    st.rerun()
            with e2:
                if st.button("Delete", key=f"delete_{cid}"):
                    delete_content(cid, st.session_state.username)
                    st.warning("Content deleted.")
                    st.rerun()
