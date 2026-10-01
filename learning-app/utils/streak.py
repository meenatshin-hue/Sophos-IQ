from datetime import date, timedelta

import streamlit as st

from utils.auth import get_user, update_user

MAX_STREAK = 200

# (minimum streak, tier name, CSS filter applied to the fire emoji)
TIERS = [
    (200, "Legendary", "hue-rotate(35deg) saturate(2) brightness(1.15) drop-shadow(0 0 5px #F5C518)"),
    (100, "Purple flame", "hue-rotate(255deg) saturate(1.6)"),
    (30, "Blue flame", "hue-rotate(185deg) saturate(1.8)"),
    (7, "Red flame", "hue-rotate(-14deg) saturate(2)"),
    (2, "Orange flame", "none"),
    (0, "No streak yet", "grayscale(1) opacity(0.55)"),
]


def _tier(count: int) -> tuple[str, str]:
    for minimum, name, css in TIERS:
        if count >= minimum:
            return name, css
    return TIERS[-1][1], TIERS[-1][2]


def touch_streak_info(username: str, today: date | None = None) -> dict:
    """Counts today's visit and says what happened.
    status: 'new_user' | 'same_day' | 'continued' | 'broken'"""
    today = today or date.today()
    user = get_user(username) or {}
    last = user.get("streak_last")
    count = int(user.get("streak", 0))
    previous = count

    if last == today.isoformat():
        return {"count": count, "status": "same_day", "previous": previous}

    if last is None:
        status, count = "new_user", 1
    elif last == (today - timedelta(days=1)).isoformat():
        status, count = "continued", min(MAX_STREAK, count + 1)
    else:
        status, count = "broken", 1

    best = max(int(user.get("best_streak", 0)), count)
    update_user(username, streak=count, streak_last=today.isoformat(), best_streak=best)
    return {"count": count, "status": status, "previous": previous}


def touch_streak(username: str, today: date | None = None) -> int:
    return touch_streak_info(username, today)["count"]


def render_streak_badge(count: int) -> None:
    name, css = _tier(count)
    label = "MAX" if count >= MAX_STREAK else str(count)
    st.markdown(
        f"""
        <div title="{count} day streak · {name}" style="position:fixed; top:66px; right:18px;
             z-index:999; background:#FFFFFF; border:1.5px solid #B7A6E8; border-radius:999px;
             padding:3px 12px 3px 8px; display:flex; align-items:center; gap:5px;
             box-shadow:0 1px 4px rgba(0,0,0,0.12);">
            <span style="font-size:1.25rem; line-height:1; filter:{css};">🔥</span>
            <span style="color:#000000; font-weight:700; font-size:0.95rem;">{label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_streak(username: str) -> int:
    count = touch_streak(username)
    render_streak_badge(count)
    return count
