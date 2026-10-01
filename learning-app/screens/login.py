import base64
from pathlib import Path

import streamlit as st

from utils.auth import ACCOUNT_TYPES, GRADE_LEVELS, create_account, verify_login

LOGO = Path(__file__).resolve().parent.parent / "assets" / "siq_logo.png"

st.markdown(
    """
    <style>
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

encoded = base64.b64encode(LOGO.read_bytes()).decode()
st.markdown(
    f"""
    <div style="display:flex;flex-direction:column;align-items:center;margin:1rem 0 1.5rem 0;">
        <img src="data:image/png;base64,{encoded}" style="width:110px;border-radius:18px;" />
        <div style="margin-top:10px;font-size:1.8rem;font-weight:800;letter-spacing:.04em;">SophosIQ</div>
        <div style="font-size:.95rem;">A learning app for ages 3-18: math, science, reading, and more.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

_, middle, _ = st.columns([1, 2, 1])
with middle:
    tab_login, tab_signup = st.tabs(["Log In", "Create Account"])

    with tab_login:
        st.subheader("Log In")
        st.caption("You must create an account before logging in.")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log In", key="login_btn"):
            ok, msg = verify_login(login_username, login_password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.rerun()
            else:
                st.error(msg)

    with tab_signup:
        st.subheader("Create Account")
        st.caption("Only one account is allowed per Gmail address.")

        account_type = st.selectbox("Account Type", ACCOUNT_TYPES)
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type="password", key="signup_password")
        school_district = st.text_input("School District")
        grade_level = st.selectbox("Grade Level", GRADE_LEVELS)
        location = st.text_input("Location (City, State)")
        email = st.text_input("Email (must be a Gmail address)")
        profile_picture = st.file_uploader("Profile Picture", type=["png", "jpg", "jpeg"])

        if st.button("Create Account", key="signup_btn"):
            ok, msg = create_account(
                account_type=account_type,
                username=new_username,
                password=new_password,
                school_district=school_district,
                grade_level=grade_level,
                location=location,
                email=email,
                profile_picture_bytes=profile_picture.read() if profile_picture else None,
                profile_picture_name=profile_picture.name if profile_picture else None,
            )
            if ok:
                st.success(msg + " You can now log in from the Log In tab.")
            else:
                st.error(msg)
