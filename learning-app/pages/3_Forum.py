import streamlit as st

from utils.styling import inject_base_css, card
from utils.guard import require_login
from utils.auth import get_user
from utils.friends import send_request, accept_request, decline_request, get_status, are_friends, request_pending
from utils.forum import (
    create_chat,
    list_chats_for_course,
    list_chats_by_author_or_replier,
    get_chat,
    mark_read,
    toggle_thumbs_up,
    add_reply,
    vote_poll,
    save_draft,
    list_drafts,
    delete_draft,
)

inject_base_css()
require_login()

user = get_user(st.session_state.username)
me = st.session_state.username
current_course = user.get("current_course")

if not current_course:
    st.warning("You haven't selected a course yet.")
    st.page_link("pages/1_Select_Course.py", label="Go select a course", icon="📚")
    st.stop()

st.title(f"💬 Forum — {current_course}")
st.caption("This forum is shared by everyone taking this course.")

QUICK_EMOJIS = ["😀", "😂", "🎉", "❤️", "👍", "🤔", "😢", "🔥"]


def friend_button(other_user: str, key_suffix: str):
    if other_user == me:
        return
    if are_friends(me, other_user):
        st.caption("✅ Friends")
    elif request_pending(me, other_user):
        st.caption("⏳ Request sent")
    else:
        if st.button("🙂 Friend", key=f"friend_{other_user}_{key_suffix}"):
            ok, msg = send_request(me, other_user)
            if ok:
                st.success(msg)
            else:
                st.info(msg)
            st.rerun()


def preview_text(text: str, n: int = 10) -> str:
    words = text.split()
    if len(words) <= n:
        return text
    return " ".join(words[:n]) + "…"


def emoji_row(state_key: str):
    cols = st.columns(len(QUICK_EMOJIS))
    for i, emoji in enumerate(QUICK_EMOJIS):
        with cols[i]:
            if st.button(emoji, key=f"{state_key}_emoji_{i}"):
                st.session_state[state_key] = st.session_state.get(state_key, "") + emoji
                st.rerun()


# ---------- Sidebar navigation ----------
with st.sidebar:
    st.subheader("Forum")
    view = st.radio("Go to", ["Chats", "Drafts", "Friends", "Sent Messages"])

# ================= DRAFTS =================
if view == "Drafts":
    st.header("📝 Drafts")
    drafts = list_drafts(me, current_course)
    if not drafts:
        st.info("No drafts saved for this course.")
    for did, d in drafts:
        with st.expander(d["title"] or "(untitled draft)"):
            st.write(d["body"])
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Send Now", key=f"send_draft_{did}"):
                    create_chat(current_course, me, d["title"], d["body"], d.get("poll"))
                    delete_draft(me, did)
                    st.success("Sent!")
                    st.rerun()
            with c2:
                if st.button("Delete Draft", key=f"del_draft_{did}"):
                    delete_draft(me, did)
                    st.rerun()

# ================= FRIENDS =================
elif view == "Friends":
    st.header("👥 Friends")
    status = get_status(me)

    st.subheader("Pending Requests")
    if not status["pending_incoming"]:
        st.caption("No pending friend requests.")
    for requester in status["pending_incoming"]:
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(requester)
        if c2.button("Accept", key=f"accept_{requester}"):
            accept_request(me, requester)
            st.rerun()
        if c3.button("Decline", key=f"decline_{requester}"):
            decline_request(me, requester)
            st.rerun()

    st.subheader("Your Friends")
    if not status["friends"]:
        st.caption("No friends yet. Friend people from the forum!")
    for friend in status["friends"]:
        card(friend, "Friend", tone="aqua")

# ================= SENT MESSAGES =================
elif view == "Sent Messages":
    st.header("📤 Sent Messages")
    sent = list_chats_by_author_or_replier(me)
    if not sent:
        st.info("You haven't sent any messages yet.")
    for cid, chat in sent:
        with st.expander(f"{chat['title']} ({chat['course']})"):
            if chat["author"] == me:
                st.write(chat["body"])
            for r in chat["replies"]:
                if r["author"] == me:
                    card("Your reply", r["text"], tone="lavender")

# ================= CHATS (main forum) =================
else:
    if "composing" not in st.session_state:
        st.session_state.composing = False

    top_l, top_r = st.columns([4, 1])
    with top_r:
        if st.button("💬 New Chat", use_container_width=True):
            st.session_state.composing = not st.session_state.composing

    if st.session_state.composing:
        st.subheader("Start a New Chat")
        title = st.text_input("Title", key="compose_title")
        emoji_row("compose_body")
        body = st.text_area("What's on your mind?", key="compose_body")
        add_poll = st.checkbox("Add a poll")
        poll = None
        if add_poll:
            poll_q = st.text_input("Poll question", key="compose_poll_q")
            poll_opts = []
            for i in range(4):
                opt = st.text_input(f"Option {i + 1}", key=f"compose_poll_opt_{i}")
                if opt.strip():
                    poll_opts.append(opt.strip())
            if poll_q.strip() and len(poll_opts) >= 2:
                poll = {"question": poll_q.strip(), "options": poll_opts, "votes": {}}

        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Send to Everyone"):
                if title.strip() and body.strip():
                    create_chat(current_course, me, title.strip(), body, poll)
                    st.session_state.composing = False
                    st.success("Sent to the course forum!")
                    st.rerun()
                else:
                    st.error("Please add a title and message.")
        with b2:
            if st.button("Save as Draft"):
                save_draft(me, current_course, title.strip(), body, poll)
                st.session_state.composing = False
                st.success("Saved to drafts.")
                st.rerun()
        with b3:
            if st.button("Cancel"):
                st.session_state.composing = False
                st.rerun()

        st.divider()

    chats = list_chats_for_course(current_course)
    if not chats:
        st.info("No chats yet — be the first to start one!")

    for cid, chat in chats:
        is_unread = me not in chat["read_by"]
        label = f"{'🔵 ' if is_unread else ''}{chat['title']} — {chat['author']}, {chat['date'][:10]}"
        with st.expander(label):
            mark_read(cid, me)

            h1, h2 = st.columns([3, 1])
            with h1:
                st.caption(f"From **{chat['author']}** · {chat['date'][:16].replace('T', ' ')}")
            with h2:
                friend_button(chat["author"], key_suffix=f"chat_{cid}")

            st.write(chat["body"])
            st.caption(f"Preview: {preview_text(chat['body'])}")

            if chat.get("poll"):
                poll = chat["poll"]
                st.subheader(f"📊 {poll['question']}")
                tally = {opt: 0 for opt in poll["options"]}
                for v in poll["votes"].values():
                    if 0 <= v < len(poll["options"]):
                        tally[poll["options"][v]] += 1
                choice = st.radio(
                    "Vote",
                    range(len(poll["options"])),
                    format_func=lambda i: f"{poll['options'][i]} ({tally[poll['options'][i]]} votes)",
                    key=f"poll_{cid}",
                    index=poll["votes"].get(me, 0),
                )
                if st.button("Submit Vote", key=f"poll_submit_{cid}"):
                    vote_poll(cid, me, choice)
                    st.rerun()

            th_col, _ = st.columns([1, 4])
            with th_col:
                liked = me in chat["thumbs_up"]
                if st.button(f"{'💙' if liked else '🤍'} {len(chat['thumbs_up'])}", key=f"thumb_{cid}"):
                    toggle_thumbs_up(cid, me)
                    st.rerun()

            st.divider()
            st.markdown("**Replies**")
            for r in chat["replies"]:
                rc1, rc2 = st.columns([3, 1])
                with rc1:
                    card(f"{r['author']} · {r['date'][:16].replace('T', ' ')}", r["text"], tone="green")
                with rc2:
                    friend_button(r["author"], key_suffix=f"reply_{cid}_{r['date']}")

            emoji_row(f"reply_body_{cid}")
            reply_text = st.text_area("Write a reply", key=f"reply_body_{cid}")
            if st.button("Reply", key=f"reply_btn_{cid}"):
                if reply_text.strip():
                    add_reply(cid, me, reply_text.strip())
                    st.rerun()
