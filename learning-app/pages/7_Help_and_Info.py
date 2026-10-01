import streamlit as st

from utils.styling import inject_base_css, card
from utils.guard import require_login
from utils.help_assistant import answer

inject_base_css()
require_login()

st.title("❓ Help & Info")

card(
    "Getting Started",
    "Select your course from the <b>Select Course</b> page to begin learning.",
    tone="green",
)
card(
    "Account Rules",
    "Only one account is allowed per Gmail address. Your progress is saved automatically.",
    tone="aqua",
)

st.divider()
st.subheader("🤖 Ask the Help Assistant")
st.caption("A quick, rule-based helper for common questions about using the site.")

if "help_chat" not in st.session_state:
    st.session_state.help_chat = []

for q, a in st.session_state.help_chat:
    card("You asked", q, tone="lavender")
    card("Assistant", a, tone="aqua")

question = st.text_input("What do you need help with?")
if st.button("Ask"):
    if question.strip():
        response = answer(question.strip())
        st.session_state.help_chat.append((question.strip(), response))
        st.rerun()
