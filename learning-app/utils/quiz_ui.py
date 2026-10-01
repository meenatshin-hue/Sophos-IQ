import time

import streamlit as st

from utils.content import list_content_for_course
from utils.quiz import record_quiz_result

_REVIEW_TYPES = {"Reading/Article", "Interactive Simulation", "Practice Sheet", "Listening/Audio File", "External Link"}


def _key(key: str) -> str:
    return f"qz_{key}"


def start(key: str, questions: list[dict]) -> None:
    st.session_state[_key(key)] = {
        "questions": questions,
        "i": 0,
        "phase": "ask",
        "attempts": 0,
        "first": [None] * len(questions),
        "chosen": None,
        "entry": None,
    }


def reset(key: str) -> None:
    st.session_state.pop(_key(key), None)


def is_active(key: str) -> bool:
    return _key(key) in st.session_state


def _related_titles(course: str, limit: int = 3) -> list[str]:
    titles = [item["title"] for _, item in list_content_for_course(course) if item["content_type"] in _REVIEW_TYPES]
    return titles[:limit]


def _review_panel(course: str, q: dict, chosen_idx: int) -> None:
    correct = q["options"][q["correct"]]
    picked = q["options"][chosen_idx]
    st.markdown(
        "<div style='background:#F6EEFF;border:1.5px solid #B7A6E8;border-radius:12px;padding:1em 1.2em;'>"
        "<div style='font-size:1.15rem;font-weight:700;margin-bottom:.4em;'>Not quite, let's look at what happened</div>"
        f"<div><b>Question:</b> {q['q']}</div>"
        f"<div style='margin-top:.5em;'><b>You chose:</b> {picked}</div>"
        f"<div><b>Correct answer:</b> {correct}</div>"
        f"<div><b>Topic:</b> {q['topic']}</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    explanation = q.get("explanation")
    st.markdown("**How to fix it**")
    if explanation:
        st.write(explanation)
    st.write(
        f"- Re-read the question and underline the key words.\n"
        f"- Say out loud why **{correct}** fits the question, and why **{picked}** does not.\n"
        f"- This one is about **{q['topic']}**, so review that idea before you retry."
    )
    related = _related_titles(course)
    if related:
        st.markdown("**Good places to review on this course's page:** " + "; ".join(related))


def run_quiz(key: str, course: str, quiz_type: str, heading: str, username: str) -> dict | None:
    """Shows the quiz one question at a time. Returns the saved result once finished."""
    s = st.session_state.get(_key(key))
    if s is None:
        return None
    if s["entry"] is not None:
        return s["entry"]

    questions = s["questions"]
    n = len(questions)
    i = s["i"]
    q = questions[i]

    st.subheader(heading)
    st.progress(i / n, text=f"Question {i + 1} of {n}")

    if s["phase"] == "ask":
        st.markdown(f"### {q['q']}")
        choice = st.radio(
            "Choose one",
            q["options"],
            index=None,
            key=f"{_key(key)}_r_{i}_{s['attempts']}",
            label_visibility="collapsed",
        )
        if s["attempts"] > 0:
            st.caption("Try again, you can do it.")
        if st.button("Check answer", key=f"{_key(key)}_check_{i}_{s['attempts']}", disabled=choice is None):
            idx = q["options"].index(choice)
            if s["first"][i] is None:
                s["first"][i] = idx
            s["chosen"] = idx
            s["phase"] = "correct" if idx == q["correct"] else "wrong"
            st.rerun()
        return None

    if s["phase"] == "correct":
        st.markdown(
            "<div style='text-align:center;padding:1.2em;background:#E6F8EE;border-radius:14px;'>"
            "<div style='font-size:4rem;line-height:1.1;'>😊</div>"
            "<div style='font-size:1.3rem;font-weight:700;'>Correct!</div></div>",
            unsafe_allow_html=True,
        )
        time.sleep(1.3)
        s["i"] += 1
        s["attempts"] = 0
        s["phase"] = "ask"
        s["chosen"] = None
        if s["i"] >= n:
            answers = [a if a is not None else -1 for a in s["first"]]
            s["entry"] = record_quiz_result(username, course, quiz_type, questions, answers)
        st.rerun()
        return None

    _review_panel(course, q, s["chosen"])
    if st.button("Try again", key=f"{_key(key)}_retry_{i}_{s['attempts']}"):
        s["phase"] = "ask"
        s["attempts"] += 1
        s["chosen"] = None
        st.rerun()
    return None
