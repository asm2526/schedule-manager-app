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

# ---- Public helpers used by your pages ------------------------------------
def create_user(username: str, password: str) -> bool:
    """
    Create a new user in SQLite (using 