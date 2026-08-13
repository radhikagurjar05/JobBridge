"""
app/auth/routes.py — Authentication Blueprint.

Routes:
    GET/POST  /register       — Create a new account
    GET/POST  /login          — Log in with email + password
    GET       /logout         — Clear session and log out

Security:
    - Passwords hashed with werkzeug (scrypt) — never stored in plain text.
    - Duplicate-email protection at app layer AND DB UNIQUE constraint.
    - Brute-force protection: max 10 wrong attempts per email.
      After 10 failures the account is locked for 15 minutes.
      Remaining attempts are shown as a warning after attempt 5.
      Counter resets to 0 on a successful login.
"""

import re
from datetime import datetime, timedelta

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, current_app
)
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import get_user_by_email, create_user

# A Blueprint groups related routes.
auth_bp = Blueprint('auth', __name__)

# Simple email format regex
_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

# ----------------------------------------------------------------
# Brute-force / login-attempt tracking
#
# Structure:
#   _login_attempts = {
#       "user@example.com": {
#           "count":      <int>,          # number of consecutive failures
#           "locked_at":  <datetime|None> # when the lockout started
#       }
#   }
#
# This lives in server memory — it resets when the server restarts,
# which is acceptable for a dev/single-process deployment.
# For production with multiple workers, move this to Redis or a DB table.
# ----------------------------------------------------------------
_login_attempts: dict = {}

MAX_ATTEMPTS   = 10                      # wrong tries before lockout
LOCKOUT_MINUTES = 15                     # how long the lockout lasts
WARN_AFTER     = 5                       # show remaining-attempts warning after this many failures


def _get_attempt_info(email: str) -> dict:
    """Return the attempt record for an email, creating it if absent."""
    if email not in _login_attempts:
        _login_attempts[email] = {"count": 0, "locked_at": None}
    return _login_attempts[email]


def _is_locked(info: dict) -> tuple[bool, int]:
    """
    Check whether an email is currently locked out.

    Returns:
        (locked: bool, minutes_left: int)
    """
    if info["locked_at"] is None:
        return False, 0
    elapsed = datetime.utcnow() - info["locked_at"]
    lockout_duration = timedelta(minutes=LOCKOUT_MINUTES)
    if elapsed < lockout_duration:
        minutes_left = int((lockout_duration - elapsed).total_seconds() // 60) + 1
        return True, minutes_left
    # Lockout has expired — reset automatically
    info["count"]     = 0
    info["locked_at"] = None
    return False, 0


def _record_failure(email: str) -> int:
    """
    Increment the failure counter for an email.
    Triggers a lockout if MAX_ATTEMPTS is reached.

    Returns:
        remaining attempts before lockout (0 means just got locked)
    """
    info = _get_attempt_info(email)
    info["count"] += 1
    if info["count"] >= MAX_ATTEMPTS:
        info["locked_at"] = datetime.utcnow()
        return 0
    return MAX_ATTEMPTS - info["count"]


def _reset_attempts(email: str) -> None:
    """Clear the failure counter after a successful login."""
    if email in _login_attempts:
        _login_attempts[email] = {"count": 0, "locked_at": None}


# ----------------------------------------------------------------
# Register
# ----------------------------------------------------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Create a new user account."""
    # If already logged in, go to dashboard
    if session.get('user_id'):
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # --- Validation: required fields ---
        if not name or not email or not password or not confirm:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        # --- Validation: email format ---
        if not _EMAIL_RE.match(email):
            flash('Please enter a valid email address.', 'error')
            return render_template('register.html')

        # --- Validation: name length ---
        if len(name) < 2:
            flash('Name must be at least 2 characters.', 'error')
            return render_template('register.html')

        # --- Validation: password match ---
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        # --- Validation: password length ---
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        # --- Check: email already registered (app-level guard) ---
        if get_user_by_email(email):
            flash('An account with this email already exists. Please log in instead.', 'error')
            return render_template('register.html')

        # --- Hash the password before saving ---
        hashed = generate_password_hash(password)

        # --- Insert into DB (DB-level UNIQUE constraint is a second safety net) ---
        try:
            user_id = create_user(name=name, email=email, password_hash=hashed)
        except Exception:
            # IntegrityError (MySQL) / OperationalError (SQLite) — race-condition duplicate
            flash('An account with this email already exists. Please log in instead.', 'error')
            return render_template('register.html')

        # --- Start a fresh session ---
        session.clear()
        session['user_id']    = user_id
        session['user_name']  = name
        session['user_email'] = email
        session.modified = True

        flash(f'Welcome to JobBridge, {name}! 🎉', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('register.html')


# ----------------------------------------------------------------
# Login   (with brute-force / attempt-limit protection)
# ----------------------------------------------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log in with email + password.

    Brute-force protection:
    - Each email gets a maximum of MAX_ATTEMPTS (10) wrong attempts.
    - After MAX_ATTEMPTS failures the email is locked for LOCKOUT_MINUTES (15 min).
    - A warning showing remaining attempts is shown after WARN_AFTER (5) failures.
    - The counter resets to 0 on any successful login.
    """
    if session.get('user_id'):
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # --- Basic presence check ---
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')

        # --- Check if this email is currently locked out ---
        info = _get_attempt_info(email)
        locked, minutes_left = _is_locked(info)
        if locked:
            flash(
                f'⛔ Too many failed attempts. Your account is locked. '
                f'Please try again in {minutes_left} minute(s).',
                'error'
            )
            return render_template('login.html')

        # --- Attempt authentication ---
        user = get_user_by_email(email)

        if user and user.get('password_hash') and check_password_hash(user['password_hash'], password):
            # ✅ SUCCESS — reset attempt counter and start session
            _reset_attempts(email)
            session.clear()
            session['user_id']    = user['id']
            session['user_name']  = user['name']
            session['user_email'] = user['email']
            session.modified = True
            flash(f'Welcome back, {user["name"]}! 👋', 'success')
            return redirect(url_for('main.dashboard'))

        else:
            # ❌ FAILURE — record and show appropriate message
            remaining = _record_failure(email)

            if remaining == 0:
                # Just hit the limit — now locked
                flash(
                    f'⛔ Too many failed attempts ({MAX_ATTEMPTS}/{MAX_ATTEMPTS}). '
                    f'Your account is locked for {LOCKOUT_MINUTES} minutes.',
                    'error'
                )
            elif info["count"] > WARN_AFTER:
                # Warn: show how many chances left
                flash(
                    f'❌ Incorrect email or password. '
                    f'⚠️ Warning: {remaining} attempt(s) remaining before lockout.',
                    'error'
                )
            else:
                # First few attempts — just show generic message
                flash('Incorrect email or password. Please try again.', 'error')

    return render_template('login.html')


# ----------------------------------------------------------------
# Logout
# ----------------------------------------------------------------
@auth_bp.route('/logout')
def logout():
    """
    Log the current user out.
    session.clear() + session.modified=True forces Flask to immediately
    write the empty session back to the cookie on this very response.
    """
    session.clear()
    session.modified = True
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
