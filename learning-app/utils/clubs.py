import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from utils import db

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CLUBS_FILE = DATA_DIR / "clubs.json"
CLUB_PICS_DIR = DATA_DIR / "club_pics"


def _load() -> dict:
    return db.load("clubs")


def _save(data: dict) -> None:
    db.save("clubs", data)


def club_forum_key(club_id: str) -> str:
    return f"club:{club_id}"


def create_club(
    name: str,
    course: str,
    description: str,
    founder: str,
    picture_bytes: bytes | None,
    picture_name: str | None,
) -> str:
    club_id = str(uuid.uuid4())

    picture_path = None
    if picture_bytes and picture_name:
        CLUB_PICS_DIR.mkdir(parents=True, exist_ok=True)
        ext = os.path.splitext(picture_name)[1] or ".png"
        picture_path = str(CLUB_PICS_DIR / f"{club_id}{ext}")
        with open(picture_path, "wb") as f:
            f.write(picture_bytes)

    clubs = _load()
    clubs[club_id] = {
        "name": name,
        "course": course,
        "description": description,
        "founder": founder,
        "members": [founder],
        "picture": picture_path,
        "date_created": datetime.now().isoformat(),
    }
    _save(clubs)
    return club_id


def list_clubs() -> list[tuple[str, dict]]:
    clubs = _load()
    return sorted(clubs.items(), key=lambda pair: pair[1]["name"].lower())


def get_club(club_id: str) -> dict | None:
    clubs = _load()
    return clubs.get(club_id)


def join_club(club_id: str, username: str) -> None:
    clubs = _load()
    club = clubs.get(club_id)
    if club and username not in club["members"]:
        club["members"].append(username)
        _save(clubs)


def leave_club(club_id: str, username: str) -> None:
    clubs = _load()
    club = clubs.get(club_id)
    if club and username in club["members"] and username != club["founder"]:
        club["members"].remove(username)
        _save(clubs)


def is_member(club_id: str, username: str) -> bool:
    clubs = _load()
    club = clubs.get(club_id)
    return bool(club and username in club["members"])
