"""
Lab 7 — Code Security and More
================================
A user authentication and file upload service with intentional
security vulnerabilities (OWASP Top 10). Participants use Copilot
to find and fix them.
"""

import hashlib
import os
import sqlite3
import subprocess
from pathlib import Path
from typing import Optional


DB_PATH = "users.db"
UPLOAD_DIR = "uploads"


# ── Database setup ───────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()


# ── VULN 1: SQL Injection ───────────────────────────────────────────

def login(username: str, password: str) -> Optional[dict]:
    """Authenticate user. Returns user dict or None."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # VULNERABLE: string formatting in SQL query
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "email": row[3], "role": row[4]}
    return None


def search_users(search_term: str) -> list[dict]:
    """Search users by username."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # VULNERABLE: SQL injection via string concatenation
    cursor.execute("SELECT id, username, email FROM users WHERE username LIKE '%" + search_term + "%'")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "username": r[1], "email": r[2]} for r in rows]


# ── VULN 2: Insecure Password Storage ───────────────────────────────

def register_user(username: str, password: str, email: str) -> dict:
    """Register a new user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # VULNERABLE: MD5 hash with no salt
    hashed = hashlib.md5(password.encode()).hexdigest()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, hashed, email),
        )
        conn.commit()
        return {"status": "ok", "user_id": cursor.lastrowid}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "Username already exists"}
    finally:
        conn.close()


# ── VULN 3: Path Traversal ──────────────────────────────────────────

def upload_file(filename: str, content: bytes) -> str:
    """Save uploaded file. Returns the file path."""
    # VULNERABLE: no sanitization of filename — allows ../../../etc/passwd
    filepath = os.path.join(UPLOAD_DIR, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(content)
    return filepath


def read_file(filename: str) -> Optional[bytes]:
    """Read an uploaded file."""
    # VULNERABLE: path traversal
    filepath = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return f.read()
    return None


# ── VULN 4: Command Injection ───────────────────────────────────────

def get_file_info(filename: str) -> str:
    """Get file metadata using system command."""
    # VULNERABLE: shell=True with user input
    result = subprocess.run(
        f"file {UPLOAD_DIR}/{filename}",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def compress_file(filename: str) -> str:
    """Compress a file using gzip."""
    # VULNERABLE: command injection
    filepath = f"{UPLOAD_DIR}/{filename}"
    os.system(f"gzip {filepath}")
    return f"{filepath}.gz"


# ── VULN 5: Hardcoded Secrets ────────────────────────────────────────

API_KEY = "sk-1234567890abcdef1234567890abcdef"
DB_PASSWORD = "admin123"
JWT_SECRET = "super-secret-jwt-key-do-not-share"


def get_api_headers() -> dict:
    return {
        "Authorization": f"Bearer {API_KEY}",
        "X-Api-Key": API_KEY,
    }


# ── VULN 6: Insecure Deserialization ────────────────────────────────

import pickle


def save_session(session_data: dict, filepath: str) -> None:
    """Save session data to file."""
    with open(filepath, "wb") as f:
        pickle.dump(session_data, f)


def load_session(filepath: str) -> dict:
    """Load session data from file."""
    # VULNERABLE: pickle.load with untrusted data
    with open(filepath, "rb") as f:
        return pickle.load(f)


# ── VULN 7: Missing Access Control ──────────────────────────────────

def get_user_profile(requesting_user_id: int, target_user_id: int) -> Optional[dict]:
    """Get any user's profile — no authorization check."""
    # VULNERABLE: no check that requesting_user has permission to view target_user
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, role FROM users WHERE id = ?", (target_user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "email": row[2], "role": row[3]}
    return None


def delete_user(requesting_user_id: int, target_user_id: int) -> bool:
    """Delete a user — no role check."""
    # VULNERABLE: any user can delete any other user
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (target_user_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


# ── VULN 8: Information Exposure ─────────────────────────────────────

def handle_error(error: Exception) -> dict:
    """Handle errors — exposes too much information."""
    # VULNERABLE: leaks stack trace, internal paths, and DB details
    import traceback
    return {
        "error": str(error),
        "type": type(error).__name__,
        "traceback": traceback.format_exc(),
        "db_path": DB_PATH,
        "server_os": os.name,
        "python_path": os.sys.executable,
    }
