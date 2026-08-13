"""
app/config.py — All configuration variables in one place.

We read sensitive values (DB password, secret key) from environment variables
so they are never hardcoded in the source code.

How to use:
    Create a .env file in the project root (see .env.example).
    The app will automatically read it via python-dotenv.
"""

import os
from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()


class Config:
    # -------------------------------------------------------
    # Flask secret key — used to sign session cookies.
    # Change this to a long random string in production.
    # -------------------------------------------------------
    SECRET_KEY = os.environ.get('SECRET_KEY', 'jobbridge-dev-secret-key-change-in-production')

    # -------------------------------------------------------
    # Database settings (MySQL with automatic SQLite fallback)
    # -------------------------------------------------------
    DB_ENGINE      = os.environ.get('DB_ENGINE', 'auto')
    MYSQL_HOST     = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT     = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER     = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'jobbridge_db')
    SQLITE_PATH    = os.environ.get('SQLITE_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'jobbridge.db'))



    # -------------------------------------------------------
    # File upload settings
    # -------------------------------------------------------
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024   # 5 MB max upload size
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}

    # -------------------------------------------------------
    # Session cookie security
    # These settings ensure logout truly clears the session:
    #   HTTPONLY  — JS cannot read the session cookie (XSS protection)
    #   SAMESITE  — prevents CSRF attacks
    #   PERMANENT — sessions expire when browser closes (not permanent)
    # -------------------------------------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_PERMANENT       = False   # session dies when browser closes

