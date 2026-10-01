import streamlit as st

from utils.styling import inject_base_css
from utils.guard import require_login
from utils.quiz import get_all_courses_with_results, get_results_for_course, mastery_band, label_for, MASTERY_BANDS
from utils.coach import generate_walkthrough

inject_base_css()
require_login()

MAX_BARS = 12
PLOT_HEIGHT = 200
BAR_WIDTH = 64

st.title("📊 View Mastery")
st.write("Every quiz you take shows up here as a colored bar for its course.")

legend = "".join(
    f"<span style='display:inline-flex;align-items:center;gap:6px;margin-right:18px;'>"
    f"<span style='width:14px;height:14px;border-radius:3px;background:{color};display:inline-block;'></span>"
    f"<span style='font-size:.9rem;'>{label} ({low}-{high}%)</span></span>"
    for low, high, label, color in MASTERY_BANDS
)
st.markdown(f"<div style='margin:.2rem 0 1rem 0;'>{legend}</div>", unsafe_allow_html=True)

courses = get_all_courses_with_results(st.session_state.username)
if not courses:
    st.info("No quizzes taken yet. Visit a course page to take your first check-in quiz!")
    st.stop()


def build_chart(results: list[dict]) -> str:
    shown = results[-MAX_BARS:]
    line50 = PLOT_HEIGHT * 0.5
    line85 = PLOT_HEIGHT * 0.85
    bars = ""
    for r in shown:
        band, color = mastery_band(r["score_pct"])
        h = max(6, round(PLOT_HEIGHT * r["score_pct"] / 100))
        bars += (
            f"<div style='position:relative;width:{BAR_WIDTH}px;height:100%;display:flex;"
            f"flex-direction:column;justify-content:flex-end;align-items:center;'>"
            f"<div style='font-size:.8rem;font-weight:700;margin-bottom:3px;'>{r['score_pct']:g}%</div>"
            f"<div title='{band}' style='width:100%;height:{h}px;background:{color};"
            f"border:1px solid rgba(0,0,0,.25);border-radius:6px 6px 0 0;'></div>"
            f"<div style='position:absolute;top:calc(100% + 8px);width:{BAR_WIDTH + 12}px;text-align:center;"
            f"font-size:.72rem;line-height:1.15;'>{label_for(r['quiz_type'])}<br>{r['date'][5:10]}</div>"
            f"</div>"
        )
    return (
        f"<div style='padding:34px 8px 64px 8px;'>"
        f"<div style='position:relative;height:{PLOT_HEIGHT}px;display:flex;align-items:flex-end;gap:16px;"
        f"padding:0 40px 0 6px;border-bottom:2px solid currentColor;border-left:2px solid currentColor;overflow:visible;'>"
        f"<div style='position:absolute;left:0;right:0;bottom:{line85}px;border-top:1px dashed #999;'>"
        f"<span style='position:absolute;right:0;top:-16px;font-size:.7rem;'>86%</span></div>"
        f"<div style='position:absolute;left:0;right:0;bottom:{line50}px;border-top:1px dashed #999;'>"
        f"<span style='position:absolute;right:0;top:-16px;font-size:.7rem;'>51%</span></div>"
        f"{bars}</div></div>"
    )


for course in courses:
    results = get_results_for_course(st.session_state.username, course)
    if not results:
        continue
    avg = sum(r["score_pct"] for r in results) / len(results)
    latest = results[-1]
    band, color = mastery_band(latest["score_pct"])

    with st.container(border=True):
        head_l, head_r = st.columns([3, 2])
        with head_l:
            st.markdown(f"### {course}")
            st.caption(f"{len(results)} quiz{'zes' if len(results) != 1 else ''} taken")
        with head_r:
            st.markdown(
                f"<div style='text-align:right;padding-top:.4rem;'>"
                f"<div style='font-size:.85rem;'>Average <b>{avg:.0f}%</b> &nbsp;|&nbsp; Latest <b>{latest['score_pct']:g}%</b></div>"
                f"<span style='display:inline-block;margin-top:4px;padding:2px 12px;border-radius:999px;"
                f"background:{color};font-weight:700;font-size:.85rem;'>{band}</span></div>",
                unsafe_allow_html=True,
            )

        st.markdown(build_chart(results), unsafe_allow_html=True)
        if len(results) > MAX_BARS:
            st.caption(f"Showing your {MAX_BARS} most recent quizzes.")

        c1, c2 = st.columns(2)
        with c1:
            with st.expander("Topics covered"):
                topics = sorted({q["topic"] for r in results for q in r["questions"]})
                st.write(", ".join(topics) if topics else "No topics recorded yet.")
        with c2:
            with st.expander("Walkthrough of your latest quiz"):
                st.caption(f"{label_for(latest['quiz_type'])} on {latest['date'][:10]}")
                st.markdown(generate_walkthrough(course, latest))
