import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from utils import db

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONTENT_FILE = DATA_DIR / "content.json"
CONTENT_PICS_DIR = DATA_DIR / "content_pics"

CONTENT_TYPES = [
    "Slides", "Reading/Article", "Interactive Simulation", "External Link",
    "Listening/Audio File", "Writing Prompt", "Print Out", "Quiz",
    "Practice Sheet", "Assignment",
]

ADD_METHODS = [
    "Google Slides", "Google Docs", "Google Drawings", "Google Forms",
    "Canva", "Kami", "Gimkit", "Blooket", "Other Link",
]

AI_CREATOR = "LearnHub AI Curator"


def _load() -> dict:
    return db.load("content")


def _save(content: dict) -> None:
    db.save("content", content)


def create_content(
    course: str,
    title: str,
    content_type: str,
    add_method: str,
    url: str,
    creator: str,
    picture_bytes: bytes | None,
    picture_name: str | None,
    citation: str | None = None,
) -> str:
    content_id = str(uuid.uuid4())

    picture_path = None
    if picture_bytes and picture_name:
        CONTENT_PICS_DIR.mkdir(parents=True, exist_ok=True)
        ext = os.path.splitext(picture_name)[1] or ".png"
        picture_path = str(CONTENT_PICS_DIR / f"{content_id}{ext}")
        with open(picture_path, "wb") as f:
            f.write(picture_bytes)

    items = _load()
    items[content_id] = {
        "course": course,
        "title": title,
        "content_type": content_type,
        "add_method": add_method,
        "url": url,
        "creator": creator,
        "date_created": datetime.now().isoformat(),
        "picture": picture_path,
        "votes": {},
        "comments": [],
        "is_ai_seeded": creator == AI_CREATOR,
        "citation": citation,
    }
    _save(items)
    return content_id


def delete_content_admin(content_id: str) -> tuple[bool, str]:
    """Deletes any content regardless of creator. Caller must have already verified
    the requester is an Administrator account."""
    items = _load()
    if content_id not in items:
        return False, "Content not found."
    del items[content_id]
    _save(items)
    return True, "Content deleted."


def list_content_for_course(course: str) -> list[tuple[str, dict]]:
    items = _load()
    matches = [(cid, c) for cid, c in items.items() if c["course"] == course]
    matches.sort(key=lambda pair: pair[1]["date_created"], reverse=True)
    return matches


def list_content_by_creator(creator: str) -> list[tuple[str, dict]]:
    items = _load()
    matches = [(cid, c) for cid, c in items.items() if c["creator"] == creator]
    matches.sort(key=lambda pair: pair[1]["date_created"], reverse=True)
    return matches


def get_content(content_id: str) -> dict | None:
    items = _load()
    return items.get(content_id)


def update_content(content_id: str, requester: str, **fields) -> tuple[bool, str]:
    items = _load()
    item = items.get(content_id)
    if not item:
        return False, "Content not found."
    if item["creator"] != requester:
        return False, "Only the creator can edit this content."
    item.update(fields)
    _save(items)
    return True, "Content updated."


def delete_content(content_id: str, requester: str) -> tuple[bool, str]:
    items = _load()
    item = items.get(content_id)
    if not item:
        return False, "Content not found."
    if item["creator"] != requester:
        return False, "Only the creator can delete this content."
    del items[content_id]
    _save(items)
    return True, "Content deleted."


def vote_difficulty(content_id: str, username: str, score: int) -> tuple[bool, str]:
    items = _load()
    item = items.get(content_id)
    if not item:
        return False, "Content not found."
    item["votes"][username] = score
    _save(items)
    return True, "Vote recorded."


def average_difficulty(item: dict) -> float | None:
    votes = item.get("votes", {})
    if not votes:
        return None
    return sum(votes.values()) / len(votes)


def add_comment(content_id: str, username: str, text: str) -> tuple[bool, str]:
    items = _load()
    item = items.get(content_id)
    if not item:
        return False, "Content not found."
    item["comments"].append(
        {"user": username, "text": text, "date": datetime.now().isoformat()}
    )
    _save(items)
    return True, "Comment added."
