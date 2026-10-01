import json
import uuid
from datetime import datetime
from pathlib import Path

from utils import db

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHATS_FILE = DATA_DIR / "forum_chats.json"
DRAFTS_FILE = DATA_DIR / "forum_drafts.json"


def _table(path) -> str:
    return "forum_chats" if path == CHATS_FILE else "forum_drafts"


def _load(path: Path) -> dict:
    return db.load(_table(path))


def _save(path: Path, data: dict) -> None:
    db.save(_table(path), data)


# ---------- Chats ----------

def create_chat(course: str, author: str, title: str, body: str, poll: dict | None) -> str:
    chats = _load(CHATS_FILE)
    chat_id = str(uuid.uuid4())
    chats[chat_id] = {
        "course": course,
        "author": author,
        "title": title,
        "body": body,
        "date": datetime.now().isoformat(),
        "read_by": [author],
        "thumbs_up": [],
        "replies": [],
        "poll": poll,
    }
    _save(CHATS_FILE, chats)
    return chat_id


def list_chats_for_course(course: str) -> list[tuple[str, dict]]:
    chats = _load(CHATS_FILE)
    matches = [(cid, c) for cid, c in chats.items() if c["course"] == course]
    matches.sort(key=lambda pair: pair[1]["date"], reverse=True)
    return matches


def list_chats_by_author_or_replier(username: str) -> list[tuple[str, dict]]:
    chats = _load(CHATS_FILE)
    matches = []
    for cid, c in chats.items():
        replied = any(r["author"] == username for r in c["replies"])
        if c["author"] == username or replied:
            matches.append((cid, c))
    matches.sort(key=lambda pair: pair[1]["date"], reverse=True)
    return matches


def get_chat(chat_id: str) -> dict | None:
    chats = _load(CHATS_FILE)
    return chats.get(chat_id)


def mark_read(chat_id: str, username: str) -> None:
    chats = _load(CHATS_FILE)
    chat = chats.get(chat_id)
    if chat and username not in chat["read_by"]:
        chat["read_by"].append(username)
        _save(CHATS_FILE, chats)


def toggle_thumbs_up(chat_id: str, username: str) -> None:
    chats = _load(CHATS_FILE)
    chat = chats.get(chat_id)
    if not chat:
        return
    if username in chat["thumbs_up"]:
        chat["thumbs_up"].remove(username)
    else:
        chat["thumbs_up"].append(username)
    _save(CHATS_FILE, chats)


def add_reply(chat_id: str, author: str, text: str) -> None:
    chats = _load(CHATS_FILE)
    chat = chats.get(chat_id)
    if not chat:
        return
    chat["replies"].append(
        {"author": author, "text": text, "date": datetime.now().isoformat()}
    )
    _save(CHATS_FILE, chats)


def vote_poll(chat_id: str, username: str, option_index: int) -> None:
    chats = _load(CHATS_FILE)
    chat = chats.get(chat_id)
    if not chat or not chat.get("poll"):
        return
    chat["poll"]["votes"][username] = option_index
    _save(CHATS_FILE, chats)


# ---------- Drafts ----------

def save_draft(username: str, course: str, title: str, body: str, poll: dict | None, draft_id: str | None = None) -> str:
    drafts = _load(DRAFTS_FILE)
    user_drafts = drafts.setdefault(username, {})
    draft_id = draft_id or str(uuid.uuid4())
    user_drafts[draft_id] = {
        "course": course,
        "title": title,
        "body": body,
        "poll": poll,
        "date_saved": datetime.now().isoformat(),
    }
    _save(DRAFTS_FILE, drafts)
    return draft_id


def list_drafts(username: str, course: str) -> list[tuple[str, dict]]:
    drafts = _load(DRAFTS_FILE)
    user_drafts = drafts.get(username, {})
    matches = [(did, d) for did, d in user_drafts.items() if d["course"] == course]
    matches.sort(key=lambda pair: pair[1]["date_saved"], reverse=True)
    return matches


def delete_draft(username: str, draft_id: str) -> None:
    drafts = _load(DRAFTS_FILE)
    user_drafts = drafts.get(username, {})
    if draft_id in user_drafts:
        del user_drafts[draft_id]
        _save(DRAFTS_FILE, drafts)
