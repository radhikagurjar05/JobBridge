"""
app/models.py — Database connection and table setup for JobBridge.

We use mysql-connector-python (the official MySQL driver for Python).
There is NO ORM here — just plain SQL, so it's easy to read and explain.

Tables:
    users           — stores registered user accounts
    resume_uploads  — every resume file a user has uploaded
    predictions     — every ML prediction made for a user

How connection works:
    We use Flask's `g` object (request-scoped global storage).
    A new DB connection is opened at the start of each request,
    and closed automatically at the end. This is the recommended Flask pattern.
"""

import os
import sqlite3
try:
    import mysql.connector
    HAS_MYSQL = True
except ImportError:
    mysql = None
    HAS_MYSQL = False
from flask import g, current_app

_use_sqlite = False


class SQLiteCursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor
        self.lastrowid = None

    def execute(self, sql, params=()):
        sql_sqlite = sql.replace('%s', '?')
        self._cursor.execute(sql_sqlite, params)
        self.lastrowid = self._cursor.lastrowid

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [dict(row) for row in rows]

    def close(self):
        self._cursor.close()


class SQLiteConnWrapper:
    def __init__(self, conn):
        self.conn = conn

    def cursor(self, dictionary=False):
        return SQLiteCursorWrapper(self.conn.cursor())

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def is_connected(self):
        return True


def _connect_db(cfg):
    global _use_sqlite
    engine = cfg.get('DB_ENGINE', 'auto').lower()

    if engine == 'sqlite':
        _use_sqlite = True
        conn = sqlite3.connect(cfg['SQLITE_PATH'])
        conn.row_factory = sqlite3.Row
        return SQLiteConnWrapper(conn)

    if engine != 'sqlite' and not _use_sqlite:
        if not HAS_MYSQL:
            if engine == 'mysql':
                raise ImportError("mysql-connector-python package is required when DB_ENGINE='mysql'.")
            print("[JobBridge] mysql-connector module not found. Falling back to SQLite database.")
            _use_sqlite = True
        else:
            try:
                return mysql.connector.connect(
                    host=cfg['MYSQL_HOST'],
                    port=cfg['MYSQL_PORT'],
                    user=cfg['MYSQL_USER'],
                    password=cfg['MYSQL_PASSWORD'],
                    database=cfg['MYSQL_DATABASE'],
                    autocommit=False
                )
            except Exception as err:
                if engine == 'mysql':
                    raise err
                print(f"[JobBridge] MySQL connection failed ({err}). Falling back to SQLite database.")
                _use_sqlite = True

    if _use_sqlite:
        conn = sqlite3.connect(cfg['SQLITE_PATH'])
        conn.row_factory = sqlite3.Row
        return SQLiteConnWrapper(conn)


# ----------------------------------------------------------------
# 1. Get a database connection for the current request
# ----------------------------------------------------------------
def get_db():
    """
    Opens a DB connection and stores it in Flask's `g` object.
    If a connection already exists for this request, it reuses it.
    """
    if 'db' not in g:
        g.db = _connect_db(current_app.config)
    return g.db


def close_db(e=None):
    """
    Closes the DB connection at the end of each request.
    Registered in create_app() via app.teardown_appcontext.
    """
    db = g.pop('db', None)
    if db is not None:
        if hasattr(db, 'is_connected'):
            if db.is_connected():
                db.close()
        else:
            db.close()


# ----------------------------------------------------------------
# 2. Create all tables if they don't exist yet
# ----------------------------------------------------------------
def init_db(app):
    """
    Called once when the app starts.
    Creates all required tables if they do not already exist.
    Safe to call multiple times — uses IF NOT EXISTS.
    """
    with app.app_context():
        conn = _connect_db(app.config)
        cursor = conn.cursor()

        if _use_sqlite:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    name          TEXT NOT NULL,
                    email         TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resume_uploads (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id         INTEGER NOT NULL,
                    filename        TEXT NOT NULL,
                    upload_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    predicted_role  TEXT,
                    resume_score    INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        else:
            # --- users table ---
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            INT AUTO_INCREMENT PRIMARY KEY,
                    name          VARCHAR(150)        NOT NULL,
                    email         VARCHAR(150) UNIQUE NOT NULL,
                    password_hash VARCHAR(256),
                    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # --- resume_uploads table ---
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resume_uploads (
                    id              INT AUTO_INCREMENT PRIMARY KEY,
                    user_id         INT          NOT NULL,
                    filename        VARCHAR(255) NOT NULL,
                    upload_time     DATETIME     DEFAULT CURRENT_TIMESTAMP,
                    predicted_role  VARCHAR(100),
                    resume_score    INT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

        conn.commit()
        cursor.close()
        conn.close()
        db_name = "SQLite (jobbridge.db)" if _use_sqlite else "MySQL"
        print(f"[JobBridge] Database tables are ready using {db_name}.")


# ----------------------------------------------------------------
# 3. Simple query helper functions
# ----------------------------------------------------------------

def get_user_by_email(email):
    """Returns the user row (as a dict) matching the given email, or None."""
    db = get_db()
    cursor = db.cursor(dictionary=True)   # dictionary=True gives us column names as keys
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    return user


def get_user_by_id(user_id):
    """Returns the user row (as a dict) matching the given id, or None."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return user


def create_user(name, email, password_hash=None):
    """
    Inserts a new user into the database.
    Returns the newly created user's ID.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
        (name, email, password_hash)
    )
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    return new_id


def save_upload(user_id, filename, predicted_role, resume_score):
    """
    Logs a resume upload event to the database.
    Returns the new upload record's ID.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO resume_uploads
           (user_id, filename, predicted_role, resume_score)
           VALUES (%s, %s, %s, %s)""",
        (user_id, filename, predicted_role, resume_score)
    )
    db.commit()
    upload_id = cursor.lastrowid
    cursor.close()
    return upload_id


from datetime import datetime


def _ensure_datetime(val):
    """Converts string timestamps (e.g. from SQLite) to Python datetime objects."""
    if val is None or isinstance(val, datetime):
        return val
    if isinstance(val, str):
        s = val.replace('T', ' ').split('.')[0].strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                pass
    return val


def get_user_uploads(user_id):
    """
    Returns all resume uploads for a given user, newest first.
    Each row is a dict with keys: id, filename, upload_time, predicted_role, resume_score.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT id, filename, upload_time, predicted_role, resume_score
           FROM resume_uploads
           WHERE user_id = %s
           ORDER BY upload_time DESC""",
        (user_id,)
    )
    uploads = cursor.fetchall()
    cursor.close()
    for row in uploads:
        if 'upload_time' in row and row['upload_time']:
            row['upload_time'] = _ensure_datetime(row['upload_time'])
    return uploads


def get_upload_stats(user_id):
    """
    Returns a summary dict for the dashboard:
    total_uploads, last_predicted_role, average_score
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT
               COUNT(*)                   AS total_uploads,
               MAX(upload_time)           AS last_upload,
               MAX(predicted_role)        AS last_role,
               ROUND(AVG(resume_score))   AS avg_score
           FROM resume_uploads
           WHERE user_id = %s""",
        (user_id,)
    )
    stats = cursor.fetchone()
    cursor.close()
    if stats and 'last_upload' in stats and stats['last_upload']:
        stats['last_upload'] = _ensure_datetime(stats['last_upload'])
    return stats
