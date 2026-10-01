import json
import hashlib
import os
from datetime import date
from pathlib import Path

from utils import db

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"
PROFILE_PICS_DIR = DATA_DIR / "profile_pics"

GRADE_LEVELS = [
    "Pre-K", "Kindergarten",
    "1st Grade", "2nd Grade", "3rd Grade", "4th Grade", "5th Grade",
    "6th Grade", "7th Grade", "8th Grade",
    "9th Grade", "10th Grade", "11th Grade", "12th Grade",
    "College and above", "SAT Prep",
]

ACCOUNT_TYPES = ["Student", "Administrator"]


def _load_users() -> dict:
    return db.load("users")


def _save_users(users: dict) -> None:
    db.save("users", users)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def email_already_registered(email: str) -> bool:
    email = email.strip().lower()
    users = _load_users()
    return any(u["email"].strip().lower() == email for u in users.values())


def username_taken(username: str) -> bool:
    users = _load_users()
    return username in users


def create_account(
    account_type: str,
    username: str,
    password: str,
    school_district: str,
    grade_level: str,
    location: str,
    email: str,
    profile_picture_bytes: bytes | None,
    profile_picture_name: str | None,
) -> tuple[bool, str]:
    email = email.strip().lower()

    if not email.endswith("@gmail.com"):
        return False, "Please sign up with a Gmail address (must end in @gmail.com)."

    if not username or not password:
        return False, "Username and password are required."

    if username_taken(username):
        return False, "That username is already taken."

    if email_already_registered(email):
        return False, "An account already exists for this Gmail address. Only one account is allowed per Gmail address."

    pic_path = None
    if profile_picture_bytes and profile_picture_name:
        PROFILE_PICS_DIR.mkdir(parents=True, exist_ok=True)
        ext = os.path.splitext(profile_picture_name)[1] or ".png"
        pic_path = str(PROFILE_PICS_DIR / f"{username}{ext}")
        with open(pic_path, "wb") as f:
            f.write(profile_picture_bytes)

    users = _load_users()
    users[username] = {
        "account_type": account_type,
        "password_hash": _hash_password(password),
        "school_district": school_district,
        "grade_level": grade_level,
        "location": location,
        "email": email,
        "profile_picture": pic_path,
        "current_course": None,
        "courses_taken": [],
        "progress": {},
        "date_joined": date.today().isoformat(),
        "display_name": username,
        "bio": "",
        "hobbies": "",
    }
    _save_users(users)
    return True, "Account created successfully."


def verify_login(username: str, password: str) -> tuple[bool, str]:
    users = _load_users()
    if username not in users:
        return False, "No account found with that username."
    if users[username]["password_hash"] != _hash_password(password):
        return False, "Incorrect password."
    return True, "Login successful."


def get_user(username: str) -> dict | None:
    users = _load_users()
    return users.get(username)


def list_all_users() -> dict:
    return _load_users()


def update_user(username: str, **fields) -> None:
    users = _load_users()
    if username in users:
        users[username].update(fields)
        _save_users(users)
