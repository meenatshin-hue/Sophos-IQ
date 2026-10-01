from datetime import date, datetime, timedelta

import streamlit as st

from utils import quiz_ui
from utils.auth import get_user, update_user
from utils.coach import generate_walkthrough
from utils.courses import all_course_keys
from utils.guard import require_login
from utils.quiz import (
    PRACTICE_DAYS_SHOWN,
    UNIT_TEST_EVERY_DAYS,
    generate_practice_quiz,
    generate_quiz,
    has_taken_today,
    generate_unit_test,
    get_all_courses_with_results,
    get_results_for_course,
    has_taken_type,
    mastery_band,
    practice_quiz_type,
    unit_test_periods_due,
    unit_test_type,
)
from utils.styling import inject_base_css

inject_base_css()
require_login()

me = st.session_state.username
user = get_user(me)
today = date.today()

if not user.get("date_joined"):
    earliest = [
        r["date"][:10]
        for c in get_all_courses_with_results(me)
        for r in get_results_for_course(me, c)
    ]
    joined = min(earliest) if earliest else today.isoformat()
    update_user(me, date_joined=joined)
    user = get_user(me)
join_date = date.fromisoformat(user["date_joined"])

st.title("📝 Quizzes")
st.write("Take extra quizzes any time. A new practice quiz appears for every course every day, and a longer unit test unlocks every 7 days.")

active = st.session_state.get("active_quiz_page")


def finish_view(course: str, entry: dict, title: str) -> None:
    band, color = mastery_band(entry["score_pct"])
    if entry["score_pct"] >= 86 and st.session_state.get("_celebrated") != entry["date"]:
        st.session_state["_celebrated"] = entry["date"]
        st.balloons()
    st.markdown(
        f"<div style='background:{color};padding:1em;border-radius:10px;'>"
        f"<b>{title} complete!</b> Score: {entry['score_pct']:g}% - {band} "
        f"({entry['correct']}/{entry['total']} right on the first try)</div>",
        unsafe_allow_html=True,
    )
    st.markdown(generate_walkthrough(course, entry))
    if st.button("Back to quizzes"):
        st.session_state.pop("active_quiz_page", None)
        st.session_state.pop("quiz_page_result", None)
        st.rerun()


if active:
    course, quiz_type, title = active["course"], active["quiz_type"], active["title"]
    result = st.session_state.get("quiz_page_result")
    if result:
        finish_view(course, result, title)
        st.stop()
    st.caption(course)
    entry = quiz_ui.run_quiz("page_quiz", course, quiz_type, title, me)
    if entry:
        st.session_state["quiz_page_result"] = entry
        quiz_ui.reset("page_quiz")
        st.rerun()
    if st.button("Leave this quiz"):
        quiz_ui.reset("page_quiz")
        st.session_state.pop("active_quiz_page", None)
        st.rerun()
    st.stop()


def start(course: str, quiz_type: str, title: str, questions: list[dict]) -> None:
    quiz_ui.start("page_quiz", questions)
    st.session_state["active_quiz_page"] = {"course": course, "quiz_type": quiz_type, "title": title}
    st.session_state.pop("quiz_page_result", None)
    st.rerun()


auto = st.session_state.pop("auto_start_quiz", None)
if auto in ("check-in", "check-out") and user.get("current_course"):
    nice = "Check-in Quiz" if auto == "check-in" else "Check-out Quiz"
    if not has_taken_today(me, user["current_course"], auto):
        start(user["current_course"], auto, nice, generate_quiz(user["current_course"], me))


def best_line(course: str, quiz_type: str) -> str:
    scores = [r["score_pct"] for r in get_results_for_course(me, course) if r["quiz_type"] == quiz_type]
    if not scores:
        return "Not taken yet"
    return f"Best score {max(scores):g}% ({len(scores)} attempt{'s' if len(scores) != 1 else ''})"


tab_daily, tab_practice, tab_unit = st.tabs(["Check-in & check-out", "Practice quizzes", "Unit tests"])

with tab_daily:
    current = user.get("current_course")
    if not current:
        st.info("Pick a course on the Select Course page first. Your check-in and check-out quizzes are for your current course.")
    else:
        st.markdown(f"#### {current}")
        st.caption("Take one at the start of your study time and one when you finish. Each can be taken once a day.")
        for qtype, title, blurb in [
            ("check-in", "Check-in Quiz", "A quick warm-up on what you've learned so far."),
            ("check-out", "Check-out Quiz", "A wrap-up quiz before you go."),
        ]:
            done = has_taken_today(me, current, qtype)
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 3, 1.4])
                c1.markdown(f"**{title}**  \n{blurb}")
                if done:
                    todays = [r for r in get_results_for_course(me, current)
                              if r["quiz_type"] == qtype and r["date"][:10] == today.isoformat()]
                    c2.caption(f"Done today: {todays[-1]['score_pct']:g}%")
                    c3.button("Done", key=f"daily_{qtype}", disabled=True)
                else:
                    c2.caption("Ready when you are")
                    if c3.button("Start", key=f"daily_{qtype}"):
                        start(current, qtype, title, generate_quiz(current, me))

with tab_practice:
    all_courses = all_course_keys()
    default = user.get("current_course")
    course = st.selectbox(
        "Course",
        all_courses,
        index=all_courses.index(default) if default in all_courses else 0,
        key="practice_course",
    )
    st.caption("Same format as your check-in quizzes: one question at a time, with a review if you miss one.")
    for offset in range(PRACTICE_DAYS_SHOWN):
        day = today - timedelta(days=offset)
        qtype = practice_quiz_type(day)
        label = "Today's quiz" if offset == 0 else day.strftime("Quiz of %b %d").replace(" 0", " ")
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 3, 1.4])
            c1.markdown(f"**{label}**" + (" &nbsp;🆕" if offset == 0 else ""))
            c2.caption(best_line(course, qtype))
            if c3.button("Start" if not has_taken_type(me, course, qtype) else "Retake", key=f"pq_{course}_{day}"):
                start(course, qtype, label, generate_practice_quiz(course, day))

with tab_unit:
    st.caption(
        f"A unit test unlocks every {UNIT_TEST_EVERY_DAYS} days from the day you joined "
        f"({join_date.strftime('%b %d, %Y')}), even if you don't log in. Each has 10-20 questions."
    )
    my_courses = set(user.get("courses_taken", [])) | set(get_all_courses_with_results(me))
    if user.get("current_course"):
        my_courses.add(user["current_course"])
    ks = unit_test_periods_due(join_date, today)
    if not my_courses:
        st.info("Pick a course on the Select Course page and its unit tests will show up here.")
    elif not ks:
        next_day = join_date + timedelta(days=UNIT_TEST_EVERY_DAYS)
        st.info(f"Your first unit test unlocks on {next_day.strftime('%b %d, %Y')}.")
    else:
        for course in sorted(my_courses):
            st.markdown(f"#### {course}")
            for k in reversed(ks[-4:]):
                qtype = unit_test_type(k)
                due_date = join_date + timedelta(days=UNIT_TEST_EVERY_DAYS * k)
                taken = has_taken_type(me, course, qtype)
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 3, 1.4])
                    c1.markdown(f"**Unit Test {k}**  \nUnlocked {due_date.strftime('%b %d')}")
                    c2.caption(best_line(course, qtype) if taken else "Due now")
                    if c3.button("Retake" if taken else "Start", key=f"ut_{course}_{k}"):
                        start(course, qtype, f"Unit Test {k}", generate_unit_test(course, k))
