"""
app/auth/routes.py — Authentication Blueprint.

Routes:
    GET/POST  /register       — Create a new account
    GET/POST  /login          — Log in with email + password
    GET       /logout         — Clear session and log out
    GET       /login/google   — Redirect to Google OAuth (optional)
    GET       /login/google/callback — Handle Google OAuth callback (optional)

Security:
    Passwords are NEVER stored in plain text.
    We use werkzeug.security to hash them before saving.
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, current_app
)
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import get_user_by_email, create_user

# A Blueprint groups related routes. The first argument is its name.
auth_bp = Blueprint('auth', __name__)


# ----------------------------------------------------------------
# Register
# ----------------------------------------------------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # If already logged in, go to dashboard
    if session.get('user_id'):
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # --- Validation ---
        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        if get_user_by_email(email):
            flash('An account with this email already exists.', 'error')
            return render_template('register.html')

        # --- Hash the password before saving ---
        # generate_password_hash creates a one-way hash like:
        # "scrypt:32768:8:1$abc123$..." — never reversible.
        hashed = generate_password_hash(password)

        user_id = create_user(name=name, email=email, password_hash=hashed)

        # Log the user in immediately after registering
        session['user_id']   = user_id
        session['user_name'] = name
        session['user_email'] = email

        flash(f'Welcome to JobCatch, {name}! 🎉', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('register.html')


# ----------------------------------------------------------------
# Login
# ----------------------------------------------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = get_user_by_email(email)

        # check_password_hash compares the plain password against the stored hash
        if user and user['password_hash'] and check_password_hash(user['password_hash'], password):
            session['user_id']    = user['id']
            session['user_name']  = user['name']
            session['user_email'] = user['email']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Incorrect email or password. Please try again.', 'error')

    return render_template('login.html')


# ----------------------------------------------------------------
# Logout
# ----------------------------------------------------------------
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))



