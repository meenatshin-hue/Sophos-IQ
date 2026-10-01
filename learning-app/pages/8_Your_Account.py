import os

import streamlit as st

from utils.styling import inject_base_css
from utils.guard import logout, require_login
from utils.auth import get_user, update_user, GRADE_LEVELS, PROFILE_PICS_DIR
from utils.friends import get_status

inject_base_css()
require_login()

user = get_user(st.session_state.username)

st.title("👤 Your Account")

col1, col2 = st.columns([1, 2])
with col1:
    if user.get("profile_picture"):
        st.image(user["profile_picture"], width=150)
    else:
        st.write("No profile picture set.")
    new_pic = st.file_uploader("Update Profile Picture (optional)", type=["png", "jpg", "jpeg"])
    if new_pic and st.button("Upload Picture"):
        PROFILE_PICS_DIR.mkdir(parents=True, exist_ok=True)
        ext = os.path.splitext(new_pic.name)[1] or ".png"
        pic_path = str(PROFILE_PICS_DIR / f"{st.session_state.username}{ext}")
        with open(pic_path, "wb") as f:
            f.write(new_pic.read())
        update_user(st.session_state.username, profile_picture=pic_path)
        st.success("Profile picture updated.")
        st.rerun()

with col2:
    st.write(f"**Username:** {st.session_state.username}")
    st.write(f"**Account Type:** {user.get('account_type', '')} (cannot be changed)")
    st.write(f"**Email:** {user.get('email', '')}")
    st.write(f"**Member Since:** {user.get('date_joined', 'Unknown')}")

st.divider()
st.subheader("Edit Details")

display_name = st.text_input("Display Name", value=user.get("display_name", st.session_state.username))
bio = st.text_area("About Me (optional)", value=user.get("bio", ""))
hobbies = st.text_input("Hobbies (optional)", value=user.get("hobbies", ""))
school_district = st.text_input("School District", value=user.get("school_district", ""))
grade_level = st.selectbox(
    "Grade Level",
    GRADE_LEVELS,
    index=GRADE_LEVELS.index(user.get("grade_level")) if user.get("grade_level") in GRADE_LEVELS else 0,
)
location = st.text_input("Location", value=user.get("location", ""))

if st.button("Save Changes"):
    update_user(
        st.session_state.username,
        display_name=display_name.strip() or st.session_state.username,
        bio=bio.strip(),
        hobbies=hobbies.strip(),
        school_district=school_district,
        grade_level=grade_level,
        location=location,
    )
    st.success("Account updated.")
    st.rerun()

st.divider()
st.subheader("👥 Your Friends")
status = get_status(st.session_state.username)
if not status["friends"]:
    st.caption("No friends yet — make some in the Forum!")
else:
    cols = st.columns(4)
    for i, friend in enumerate(status["friends"]):
        friend_user = get_user(friend)
        with cols[i % 4]:
            if friend_user and friend_user.get("profile_picture"):
                st.image(friend_user["profile_picture"], width=80)
            st.write(f"**{friend_user.get('display_name', friend) if friend_user else friend}**")

st.divider()
if st.button("Log out"):
    logout()
    st.rerun()
