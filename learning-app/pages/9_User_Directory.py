import streamlit as st

from utils.styling import inject_base_css
from utils.guard import require_login
from utils.auth import list_all_users

inject_base_css()
require_login()

st.title("🗂️ User Directory")
st.caption("All students and administrators on SophosIQ.")

users = list_all_users()
search = st.text_input("🔍 Search by username")

rows = []
for username, u in users.items():
    if search and search.lower() not in username.lower():
        continue
    rows.append({
        "Username": username,
        "Display Name": u.get("display_name", username),
        "Status": u.get("account_type", "Student"),
        "Date Joined": u.get("date_joined", "Unknown"),
        "Courses Taken": ", ".join(u.get("courses_taken", [])) or "—",
        "Streak": u.get("streak", 0),
    })

rows.sort(key=lambda r: r["Username"].lower())
st.dataframe(rows, use_container_width=True, hide_index=True)
