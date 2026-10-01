from utils.content import list_content_for_course

REVIEW_TYPES = {"Practice Sheet", "Reading/Article", "Quiz", "Assignment"}


def _suggested_resources(course: str, topic: str) -> list[str]:
    items = list_content_for_course(course)
    matches = [
        item["title"] for _, item in items
        if item["content_type"] in REVIEW_TYPES
        and (topic.lower() in item["title"].lower() or True)
    ]
    return matches[:2]


def generate_walkthrough(course: str, quiz_entry: dict) -> str:
    missed = [q for q in quiz_entry["questions"] if not q["was_correct"]]
    total = quiz_entry["total"]
    correct = quiz_entry["correct"]

    if not missed:
        return f"🎉 Great work! You got {correct}/{total} correct — that's full marks. Keep it up!"

    lines = [f"You got {correct}/{total} correct ({quiz_entry['score_pct']}%). Let's walk through what to focus on next."]

    topics: dict[str, list[dict]] = {}
    for q in missed:
        topics.setdefault(q["topic"], []).append(q)

    for topic, qs in topics.items():
        lines.append(f"**{topic}** — missed {len(qs)} question(s):")
        for q in qs:
            lines.append(
                f"- You answered *\"{q['chosen_answer']}\"*, but the correct answer was *\"{q['correct_answer']}\"*."
            )
        resources = _suggested_resources(course, topic)
        if resources:
            lines.append(f"  Try reviewing: {', '.join(resources)} on this course's page.")

    lines.append(
        "Keep practicing these topics — your next check-in quiz will cover them again "
        "so you can show what you've improved on."
    )
    return "\n\n".join(lines)
