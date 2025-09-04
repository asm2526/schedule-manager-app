import sqlite3
import hashlib
import os

# ---- DB location -----------------------------------------------------------
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schedule_manager.db")


def _get_conn() -> sqlite3.Connection:
    """Open a connection to the single, known DB file."""
    return sqlite3.connect(DB_FILE)


# ---- Password hashing ------------------------------------------------------
def hash_password(password: str) -> str:
    """Hash the password using SHA-256 (simple demo, not production)."""
    return hashlib.sha256(password.encode()).hexdigest()


# ---- Schema init / seeding -------------------------------------------------
def init_db() -> None:
    """Ensure the database and required tables exist."""
    with _get_conn() as conn:
        cur = conn.cursor()

        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)

        # Events table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                title TEXT NOT NULL,
                date TEXT NOT NULL,   -- YYYY-MM-DD
                start TEXT NOT NULL,  -- HH:MM AM/PM
                end   TEXT NOT NULL,  -- HH:MM AM/PM
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)

        conn.commit()


# ---- User functions --------------------------------------------------------
def create_user(username: str, password: str) -> bool:
    """Create a new user. Return True on success, False if username exists."""
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
        return False


def verify_user(username: str, password: str) -> bool:
    """Check if username/password matches DB."""
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        ).fetchone()
    if not row:
        return False
    return row[0] == hash_password(password)


# ---- Event functions -------------------------------------------------------
def add_event(username: str, title: str, date: str, start: str, end: str) -> int:
    """Insert a new event and return its ID."""
    with _get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO events (username, title, date, start, end) VALUES (?, ?, ?, ?, ?)",
            (username, title, date, start, end)
        )
        conn.commit()
        return cur.lastrowid


def get_events_for_day(username: str, date: str) -> list[tuple]:
    """Return [(id, title, start, end)] for a given user and date."""
    with _get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, start, end FROM events WHERE username = ? AND date = ? ORDER BY start",
            (username, date)
        )
        return cur.fetchall()


def get_event(event_id: int):
    """Return (id, username, title, date, start, end) or None."""
    with _get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, title, date, start, end FROM events WHERE id = ?",
            (event_id,)
        )
        return cur.fetchone()


def update_event(event_id: int, title: str, date: str, start: str, end: str) -> None:
    """Update an existing event."""
    with _get_conn() as conn:
        conn.execute(
            "UPDATE events SET title = ?, date = ?, start = ?, end = ? WHERE id = ?",
            (title, date, start, end, event_id)
        )
        conn.commit()


def delete_event(event_id: int) -> None:
    """Delete an event by ID."""
    with _get_conn() as conn:
        conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
        conn.commit()


# ---- Dev test --------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    print("DB initialized at:", DB_FILE)
