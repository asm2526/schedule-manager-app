# database.py
# Centralizes all SQLite access so every part of the app hits the SAME DB file.

import sqlite3
import hashlib
import os

# ---- DB location -----------------------------------------------------------
# Use an ABSOLUTE path anchored to THIS file's folder, so it doesn't depend on
# where you launched Python from (cwd). This is the core fix for "registered
# but can't login" when modules live in subfolders.
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "schedule_manager.db")

def _get_conn() -> sqlite3.Connection:
    """Open a connection to the single, known DB file."""
    return sqlite3.connect(DB_FILE)

# ---- Password hashing ------------------------------------------------------
def hash_password(password: str) -> str:
    """
    Hash the password using SHA-256. (Still sqlite3—this is just the hashing step.)
    NOTE: For production you’d use bcrypt/argon2, but SHA-256 is fine for this demo.
    """
    return hashlib.sha256(password.encode()).hexdigest()

# ---- Schema init / sample seeding -----------------------------------------
def init_db() -> None:
    """
    Ensure the database and 'users' table exist.
    Also (optionally) seed the 'tester' user for quick dev testing.
    """
    with _get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)

        # Optional: clear and re-seed the sample 'tester' account for dev
        cur.execute("DELETE FROM users WHERE username = ?", ("tester",))
        try:
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ("tester", hash_password("Testing123456!"))
            )
            print("Sample user added: tester")
        except sqlite3.IntegrityError:
            # Already exists, ignore
            pass
        conn.commit()

        cur.execute("""
            Create TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    title TEXT NOT NULL,
                    start_iso TEXT NOT NULL, -- ISO 8601 datetime string
                    duration_minutes INTEGER NOT NULL DEFAULT 60,
                    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                    FOREIGN KEY (username) REFERENCES users(username)
                    )
                """)

# ---- Public helpers used by your pages ------------------------------------
def create_user(username: str, password: str) -> bool:
    """
    Create a new user in SQLite (using sqlite3). Returns True on success.
    Returns False if the username already exists or bad input.
    """
    if not username or not password:
        return False
    try:
        with _get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hash_password(password))
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        # UNIQUE constraint failed: users.username
        return False

def verify_user(username: str, password: str) -> bool:
    """
    Validate a username/password against the DB (still sqlite3 under the hood).
    """
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        ).fetchone()
    if not row:
        return False
    return row[0] == hash_password(password)

def add_event(username: str, title: str, start_iso: str, duration_minutes: int = 60) -> bool:
    """ Add a single event for a given user
    - start_iso 'YYY-MM-DD HH:MM' (local time)
    REturns the new event ID on success"""
    if not username or not title or not start_iso:
        raise ValueError("Missing required fields")
    with _get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            " INSERT INTO events (username, title, start_iso, duration_minutes) VALUES (?, ?, ?, ?)",
            (username, title, start_iso, duration_minutes)
        )
        conn.commit()
        return cur.lastrowid
    
def get_event_by_id(event_id: int):
    with _get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SElECT id, username, title, start_iso, duration_minutes, created_at "
            "FROM events WHERE id = ?",
            (event_id,)
        )
        return cur.fetchone()

def get_events_for_day(username: str, date_iso: str) -> list[tuple]:
    """
    Fetch events for a user on a specific day (date_iso: 'YYYY-MM-DD'), ordered by start time.
    Returns a list of rows: (id, title, start_iso, duration_minutes)
    """
    with _get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, title, start_iso, duration_minutes
            FROM events
            WHERE username = ?
              AND substr(start_iso, 1, 10) = ?
            ORDER BY start_iso ASC
            """,
            (username, date_iso),
        )
        return cur.fetchall()

def update_event(event_id: int, title: str, start_iso: str, duration_minutes: int) -> None:
    with _get_conn() as conn:
        conn.execute(
            "UPDATE events SET title = ?, start_iso = ?, duration_minutes = ? WHERE id = ?",
            (title.strip(), start_iso, int(duration_minutes), event_id)
        )
        conn.commit()

def delete_event(event_id: int) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
        conn.commit()

# ---- Dev smoke test --------------------------------------------------------
if __name__ == "__main__":
    init_db()
    ok = verify_user("tester", "Testing123456!")
    print("verification test:", "Success" if ok else "Failed")
    print("DB file:", DB_FILE)
