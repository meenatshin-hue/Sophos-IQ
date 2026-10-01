import streamlit as st

from utils.styling import inject_base_css, card
from utils.guard import require_login
from utils.auth import get_user
from utils.courses import all_course_keys
from utils.clubs import (
    create_club, list_clubs, get_club, join_club, leave_club, is_member, club_forum_key,
)
from utils.content import CONTENT_TYPES, ADD_METHODS, create_content, list_content_for_course
from utils.forum import (
    create_chat, list_chats_for_course, add_reply, toggle_thumbs_up, mark_read,
)

inject_base_css()
require_login()

me = st.session_state.username
st.title("🌟 Student Owned Clubs")
st.caption("Create or join educational clubs — each has its own forum and member-added lessons.")

if "selected_club_id" not in st.session_state:
    st.session_state.selected_club_id = None


# ================= Club Detail View =================
if st.session_state.selected_club_id:
    club_id = st.session_state.selected_club_id
    club = get_club(club_id)

    if not club:
        st.error("This club no longer exists.")
        st.session_state.selected_club_id = None
        st.stop()

    if st.button("⬅️ Back to all clubs"):
        st.session_state.selected_club_id = None
        st.rerun()

    if club.get("picture"):
        st.image(club["picture"], width=200)
    st.header(club["name"])
    st.caption(f"Related course: {club['course']} · Founded by {club['founder']}")
    st.write(club["description"])
    st.write(f"**Members ({len(club['members'])}):** {', '.join(club['members'])}")

    member = is_member(club_id, me)
    if not member:
        if st.button("➕ Join Club"):
            join_club(club_id, me)
            st.rerun()
    elif me != club["founder"]:
        if st.button("🚪 Leave Club"):
            leave_club(club_id, me)
            st.rerun()

    if not member:
        st.info("Join this club to access its forum and lessons.")
        st.stop()

    forum_key = club_forum_key(club_id)
    tab_lessons, tab_forum = st.tabs(["📚 Club Lessons", "💬 Club Forum"])

    with tab_lessons:
        st.subheader("Add a Lesson")
        with st.expander("Create new club content"):
            title = st.text_input("Title", key="club_content_title")
            content_type = st.selectbox("Type", CONTENT_TYPES, key="club_content_type")
            add_method = st.selectbox("How are you adding it?", ADD_METHODS, key="club_content_method")
            url = st.text_input("Link", key="club_content_url")
            picture = st.file_uploader("Picture (optional)", type=["png", "jpg", "jpeg"], key="club_content_pic")
            if st.button("Add to Club", key="club_content_submit"):
                if title.strip() and url.strip():
                    pic_bytes = picture.read() if picture else None
                    pic_name = picture.name if picture else None
                    create_content(
                        course=forum_key, title=title.strip(), content_type=content_type,
                        add_method=add_method, url=url.strip(), creator=me,
                        picture_bytes=pic_bytes, picture_name=pic_name,
                    )
                    st.success("Added!")
                    st.rerun()
                else:
                    st.error("Please add a title and a link.")

        st.divider()
        lessons = list_content_for_course(forum_key)
        if not lessons:
            st.info("No lessons added yet — be the first!")
        for cid, item in lessons:
            with st.expander(f"{item['title']} ({item['content_type']}) — by {item['creator']}"):
                if item.get("picture"):
                    st.image(item["picture"], width=200)
                st.write(f"Added via {item['add_method']} on {item['date_created'][:10]}")
                st.link_button("Open Lesson", item["url"])

    with tab_forum:
        if "club_composing" not in st.session_state:
            st.session_state.club_composing = False

        if st.button("💬 New Chat", key="club_new_chat_btn"):
            st.session_state.club_composing = not st.session_state.club_composing

        if st.session_state.club_composing:
            ctitle = st.text_input("Title", key="club_chat_title")
            cbody = st.text_area("Message", key="club_chat_body")
            if st.button("Send", key="club_chat_send"):
                if ctitle.strip() and cbody.strip():
                    create_chat(forum_key, me, ctitle.strip(), cbody, None)
                    st.session_state.club_composing = False
                    st.rerun()
                else:
                    st.error("Add a title and message.")

        st.divider()
        chats = list_chats_for_course(forum_key)
        if not chats:
            st.info("No chats yet in this club's forum.")
        for cid, chat in chats:
            with st.expander(f"{chat['title']} — {chat['author']}, {chat['date'][:10]}"):
                mark_read(cid, me)
                st.write(chat["body"])
                liked = me in chat["thumbs_up"]
                if st.button(f"{'💙' if liked else '🤍'} {len(chat['thumbs_up'])}", key=f"club_thumb_{cid}"):
                    toggle_thumbs_up(cid, me)
                    st.rerun()
                for r in chat["replies"]:
                    card(r["author"], r["text"], tone="green")
                reply_text = st.text_area("Reply", key=f"club_reply_{cid}")
                if st.button("Reply", key=f"club_reply_btn_{cid}"):
                    if reply_text.strip():
                        add_reply(cid, me, reply_text.strip())
                        st.rerun()

    st.stop()


# ================= Club Directory =================
with st.expander("➕ Start a New Club"):
    name = st.text_input("Club Name")
    course = st.selectbox("Related Course", all_course_keys())
    description = st.text_area("Description")
    picture = st.file_uploader("Club Picture (optional)", type=["png", "jpg", "jpeg"])
    if st.button("Create Club"):
        if name.strip() and description.strip():
            pic_bytes = picture.read() if picture else None
            pic_name = picture.name if picture else None
            create_club(name.strip(), course, description.strip(), me, pic_bytes, pic_name)
            st.success(f"Club '{name}' created!")
            st.rerun()
        else:
            st.error("Please add a club name and description.")

st.divider()
search = st.text_input("🔍 Search clubs")

for club_id, club in list_clubs():
    if search and search.lower() not in club["name"].lower() and search.lower() not in club["course"].lower():
        continue
    c1, c2 = st.columns([4, 1])
    with c1:
        card(
            club["name"],
            f"{club['course']} · {len(club['members'])} members<br>{club['description']}",
            tone="lavender",
        )
    with c2:
        if st.button("Open", key=f"open_{club_id}"):
            st.session_state.selected_club_id = club_id
            st.rerun()
