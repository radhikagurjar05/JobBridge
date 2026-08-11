"""
app/main/routes.py — Main Blueprint.

Routes:
    GET  /            — Landing page (home)
    GET  /dashboard   — User dashboard (login required)
    GET  /contact     — Contact / about page
"""

from flask import Blueprint, render_template, redirect, url_for, session
from app.models import get_user_by_id, get_upload_stats, get_user_uploads

main_bp = Blueprint('main', __name__)


def login_required(f):
    """
    Simple decorator to protect routes that need a logged-in user.
    If the user is not in the session, redirect them to the login page.
    """
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@main_bp.route('/')
def home():
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    user    = get_user_by_id(user_id)
    stats   = get_upload_stats(user_id)
    # Last 5 uploads to show in the dashboard preview
    recent_uploads = get_user_uploads(user_id)[:5]

    return render_template(
        'dashboard.html',
        user=user,
        stats=stats,
        recent_uploads=recent_uploads
    )


@main_bp.route('/contact')
def contact():
    return render_template('index.html', scroll_to='contact')
