from utils import content
from utils.courses import category_for_course


def search_lessons(query: str, limit: int = 8) -> tuple[list[tuple[str, dict]], int]:
    """Finds lessons in any course. Every word typed must match the title, course,
    category, type, or source. Returns (top results, total matches)."""
    words = [w for w in query.lower().split() if w]
    if not words:
        return [], 0

    scored = []
    for cid, item in content._load().items():
        title = item["title"].lower()
        course = item["course"].lower()
        category = (category_for_course(item["course"]) or "").lower()
        kind = item["content_type"].lower()
        source = (item.get("citation") or "").lower()
        score = 0
        for w in words:
            if w in title:
                score += 3
            elif w in course:
                score += 2
            elif w in category or w in kind or w in source:
                score += 1
            else:
                score = -1
                break
        if score > 0:
            scored.append((score, item["date_created"], cid, item))

    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [(cid, item) for _, _, cid, item in scored[:limit]], len(scored)
