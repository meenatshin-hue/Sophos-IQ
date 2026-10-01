import json
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

from utils import content

from utils import db

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
POOL_FILE = DATA_DIR / "link_pool.json"
STATE_FILE = DATA_DIR / "rotation_state.json"

LINKS_PER_COURSE = 2
DAYS_PER_ROTATION = 3
MAX_CATCHUP_ROTATIONS = 10

_METHOD_BY_HOST = [
    ("docs.google.com/presentation", "Google Slides"),
    ("docs.google.com/drawings", "Google Drawings"),
    ("docs.google.com/forms", "Google Forms"),
    ("docs.google.com", "Google Docs"),
    ("gimkit.com", "Gimkit"),
    ("blooket.com", "Blooket"),
    ("canva.com", "Canva"),
    ("kamiapp.com", "Kami"),
]


def _table(path: Path) -> str:
    return "link_pool" if path == POOL_FILE else "rotation_state"


def _read(path: Path, default):
    data = db.load(_table(path), as_list=(path == POOL_FILE))
    return data if data else default


def _write(path: Path, data) -> None:
    db.save(_table(path), data)


def _method_for(url: str) -> str:
    u = url.lower()
    for needle, method in _METHOD_BY_HOST:
        if needle in u:
            return method
    return "Other Link"


def pool_size() -> int:
    return len(_read(POOL_FILE, []))


def release_due_links(today: date | None = None) -> int:
    """Adds LINKS_PER_COURSE queued links to every course for each full
    DAYS_PER_ROTATION-day period that has passed since the last release.
    Safe to call on every page load; returns how many links were added."""
    today = today or date.today()
    state = _read(STATE_FILE, {})
    if "last_release" not in state:
        state["last_release"] = today.isoformat()
        _write(STATE_FILE, state)
        return 0

    last = date.fromisoformat(state["last_release"])
    periods = (today - last).days // DAYS_PER_ROTATION
    if periods <= 0:
        return 0
    periods = min(periods, MAX_CATCHUP_ROTATIONS)

    pool = _read(POOL_FILE, [])
    if not pool:
        state["last_release"] = (last + timedelta(days=DAYS_PER_ROTATION * periods)).isoformat()
        _write(STATE_FILE, state)
        return 0

    items = content._load()
    have = {(v["course"], v["url"]) for v in items.values()}
    added = 0
    for _ in range(periods):
        released_per_course: dict[str, int] = {}
        remaining = []
        for entry in pool:
            course = entry["course"]
            if (course, entry["url"]) in have:
                continue
            if released_per_course.get(course, 0) >= LINKS_PER_COURSE:
                remaining.append(entry)
                continue
            released_per_course[course] = released_per_course.get(course, 0) + 1
            have.add((course, entry["url"]))
            items[str(uuid.uuid4())] = {
                "course": course,
                "title": entry["title"],
                "content_type": entry["content_type"],
                "add_method": _method_for(entry["url"]),
                "url": entry["url"],
                "creator": content.AI_CREATOR,
                "date_created": datetime.now().isoformat(),
                "picture": None,
                "votes": {},
                "comments": [],
                "is_ai_seeded": True,
                "citation": entry.get("source", "") + " (real resource found via web search)",
            }
            added += 1
        pool = remaining

    content._save(items)
    _write(POOL_FILE, pool)
    state["last_release"] = (last + timedelta(days=DAYS_PER_ROTATION * periods)).isoformat()
    _write(STATE_FILE, state)
    return added
