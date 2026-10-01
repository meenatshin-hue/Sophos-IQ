import json
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "learnhub.db"

# table name -> legacy JSON file it is imported from the first time
TABLES = {
    "users": "users.json",
    "content": "content.json",
    "forum_chats": "forum_chats.json",
    "forum_drafts": "forum_drafts.json",
    "friends": "friends.json",
    "clubs": "clubs.json",
    "quiz_results": "quiz_results.json",
    "link_pool": "link_pool.json",
    "rotation_state": "rotation_state.json",
}

_ready = False


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _init() -> None:
    global _ready
    if _ready:
        return
    conn = _connect()
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS meta (name TEXT PRIMARY KEY, value TEXT)")
        for table in TABLES:
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table} (id TEXT PRIMARY KEY, data TEXT NOT NULL)")
        # Real, queryable columns for the user directory
        conn.execute(
            "CREATE TABLE IF NOT EXISTS user_directory ("
            "username TEXT PRIMARY KEY, display_name TEXT, account_type TEXT, "
            "date_joined TEXT, courses_taken TEXT, current_course TEXT, streak INTEGER)"
        )
        conn.commit()
        for table, filename in TABLES.items():
            done = conn.execute("SELECT 1 FROM meta WHERE name=?", (f"imported_{table}",)).fetchone()
            if done:
                continue
            legacy = DATA_DIR / filename
            if legacy.exists():
                try:
                    with open(legacy, "r", encoding="utf-8-sig") as f:
                        _write_rows(conn, table, json.load(f))
                except (ValueError, OSError):
                    pass
            conn.execute("INSERT OR REPLACE INTO meta (name, value) VALUES (?, '1')", (f"imported_{table}",))
        conn.commit()
    finally:
        conn.close()
    _ready = True


def _to_rows(obj) -> dict[str, str]:
    if isinstance(obj, list):
        return {str(i): json.dumps(v) for i, v in enumerate(obj)}
    return {str(k): json.dumps(v) for k, v in obj.items()}


def _write_rows(conn: sqlite3.Connection, table: str, obj) -> None:
    rows = _to_rows(obj)
    existing = dict(conn.execute(f"SELECT id, data FROM {table}").fetchall())
    for gone in set(existing) - set(rows):
        conn.execute(f"DELETE FROM {table} WHERE id=?", (gone,))
    for key, text in rows.items():
        if existing.get(key) != text:
            conn.execute(f"INSERT OR REPLACE INTO {table} (id, data) VALUES (?, ?)", (key, text))
    if table == "users":
        conn.execute("DELETE FROM user_directory")
        for name, u in (obj or {}).items():
            conn.execute(
                "INSERT OR REPLACE INTO user_directory VALUES (?,?,?,?,?,?,?)",
                (
                    name,
                    u.get("display_name", name),
                    u.get("account_type", "Student"),
                    u.get("date_joined", ""),
                    ", ".join(u.get("courses_taken", [])),
                    u.get("current_course") or "",
                    int(u.get("streak", 0)),
                ),
            )


def load(table: str, as_list: bool = False):
    _init()
    conn = _connect()
    try:
        rows = conn.execute(f"SELECT id, data FROM {table}").fetchall()
    finally:
        conn.close()
    if as_list:
        return [json.loads(d) for _, d in sorted(rows, key=lambda r: int(r[0]))]
    return {k: json.loads(d) for k, d in rows}


def save(table: str, obj) -> None:
    _init()
    conn = _connect()
    try:
        with conn:
            _write_rows(conn, table, obj)
    finally:
        conn.close()
