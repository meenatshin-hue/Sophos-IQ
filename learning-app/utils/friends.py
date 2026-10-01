import json
from pathlib import Path

from utils import db

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FRIENDS_FILE = DATA_DIR / "friends.json"


def _load() -> dict:
    return db.load("friends")


def _save(data: dict) -> None:
    db.save("friends", data)


def _ensure(data: dict, username: str) -> None:
    if username not in data:
        data[username] = {"friends": [], "pending_incoming": [], "pending_outgoing": []}


def send_request(from_user: str, to_user: str) -> tuple[bool, str]:
    if from_user == to_user:
        return False, "You can't friend yourself."

    data = _load()
    _ensure(data, from_user)
    _ensure(data, to_user)

    if to_user in data[from_user]["friends"]:
        return False, "You're already friends."
    if to_user in data[from_user]["pending_outgoing"]:
        return False, "Friend request already sent."

    data[from_user]["pending_outgoing"].append(to_user)
    data[to_user]["pending_incoming"].append(from_user)
    _save(data)
    return True, "Friend request sent."


def accept_request(username: str, from_user: str) -> tuple[bool, str]:
    data = _load()
    _ensure(data, username)
    _ensure(data, from_user)

    if from_user not in data[username]["pending_incoming"]:
        return False, "No pending request from that user."

    data[username]["pending_incoming"].remove(from_user)
    if from_user in data[username].get("pending_outgoing", []):
        data[username]["pending_outgoing"].remove(from_user)
    if username in data[from_user].get("pending_outgoing", []):
        data[from_user]["pending_outgoing"].remove(username)

    if from_user not in data[username]["friends"]:
        data[username]["friends"].append(from_user)
    if username not in data[from_user]["friends"]:
        data[from_user]["friends"].append(username)

    _save(data)
    return True, "You are now friends."


def decline_request(username: str, from_user: str) -> tuple[bool, str]:
    data = _load()
    _ensure(data, username)
    _ensure(data, from_user)

    if from_user in data[username]["pending_incoming"]:
        data[username]["pending_incoming"].remove(from_user)
    if username in data[from_user]["pending_outgoing"]:
        data[from_user]["pending_outgoing"].remove(username)

    _save(data)
    return True, "Request declined."


def get_status(username: str) -> dict:
    data = _load()
    _ensure(data, username)
    return data[username]


def are_friends(user_a: str, user_b: str) -> bool:
    data = _load()
    return user_b in data.get(user_a, {}).get("friends", [])


def request_pending(from_user: str, to_user: str) -> bool:
    data = _load()
    return to_user in data.get(from_user, {}).get("pending_outgoing", [])
