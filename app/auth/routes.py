"""
app/auth/routes.py — Authentication Blueprint.

Routes:
    GET/POST  /register       — Create a new account
    GET/POST  /login          — Log in with email + password
    GET       /logout         — Clear session and log out

Security:
    Passwords are NEVER stored in plain text.
    We use werkzeug.security to hash them before saving.
    Duplicate-email protection is enforced both at the app layer
    (get_user_by_email check) AND at the DB layer (UNIQUE constraint
    caught via IntegrityError) so re-registration is impossible.
"""

import re

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, current_app
)
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import get_user_by_email, create_user

# A Blueprint groups related routes. The first argument is its name.
auth_bp = Blueprint('auth', __name__)

# Simple email format regex
_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


# ----------------------------------------------------------------
# Register
# ----------------------------------------------------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Create a new user account.

    BUG FIXES applied here:
    1. Email format validated with regex before any DB call.
    2. Duplicate-email check done BEFORE hashing (fast path).
    3. create_user() wrapped in try/except to catch DB-level
       UNIQUE constraint errors (IntegrityError / OperationalError)
       so even a race-condition duplicate is rejected cleanly.
    4. confirm_password is always validated — even when field is blank.
    5. session is fully cleared before writing new session data
       so stale session values can never bleed through.
    """
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
        # generate_password_hash creates a one-way hash — never reversible.
        hashed = generate_password_hash(password)

        # --- Insert into DB (DB-level UNIQUE constraint is a second safety net) ---
        try:
            user_id = create_user(name=name, email=email, password_hash=hashed)
        except Exception:
            # Catches IntegrityError (MySQL) / OperationalError (SQLite) from
            # the UNIQUE constraint on users.email — e.g. a race-condition duplicate.
            flash('An account with this email already exists. Please log in instead.', 'error')
            return render_template('register.html')

        # --- Start a fresh session (clear first to prevent session fixation) ---
        session.clear()
        session['user_id']    = user_id
        session['user_name']  = name
        session['user_email'] = email
        session.modified = True

        flash(f'Welcome to JobBridge, {name}! 🎉', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('register.html')


# ----------------------------------------------------------------
# Login
# ----------------------------------------------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Log in with email + password.

    BUG FIXES applied here:
    1. session.clear() before writing new session data prevents any
       stale values from a previous user from leaking into the new session.
    2. Email is normalised (strip + lowercase) before DB lookup so
       'User@Example.COM' matches 'user@example.com' stored at register.
    3. Generic error message prevents email enumeration.
    """
    if session.get('user_id'):
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')

        user = get_user_by_email(email)

        # check_password_hash compares the plain password against the stored hash
        if user and user.get('password_hash') and check_password_hash(user['password_hash'], password):
            # Clear any stale session data before writing new session
            session.clear()
            session['user_id']    = user['id']
            session['user_name']  = user['name']
            session['user_email'] = user['email']
            session.modified = True
            flash(f'Welcome back, {user["name"]}! 👋', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            # Generic message — don't reveal whether email exists
            flash('Incorrect email or password. Please try again.', 'error')

    return render_template('login.html')


# ----------------------------------------------------------------
# Logout
# ----------------------------------------------------------------
@auth_bp.route('/logout')
def logout():
    """Log the current user out.

    BUG FIX: session.clear() removes ALL session keys including user_id,
    user_name, user_email. Setting session.modified = True forces Flask
    to immediately write the empty session back to the cookie, ensuring
    the browser receives a cleared cookie on this very response.
    """
    session.clear()
    session.modified = True
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))



