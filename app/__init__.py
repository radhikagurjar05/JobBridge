"""
app/__init__.py — The App Factory for JobCatch.

What is an App Factory?
    Instead of creating a global `app = Flask(__name__)` object at the module level
    (which makes testing and configuration hard), we put the creation inside a function
    called create_app(). This is the standard Flask pattern for medium-to-large projects.

Steps inside create_app():
    1. Create the Flask app object
    2. Load configuration from Config class
    3. Register blueprints (auth, main, resume)
    4. Set up database connection teardown
    5. Create DB tables on first run
"""

from flask import Flask
from app.config import Config
from app.models import close_db, init_db


def create_app():
    """Creates and configures the Flask application."""

    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # ---- Load all config from our Config class ----
    app.config.from_object(Config)

    # ---- Tell Flask to close the DB connection after every request ----
    app.teardown_appcontext(close_db)

    # ---- Register Blueprints ----
    # A Blueprint is just a group of related routes.
    # We have three groups: auth, main, and resume.

    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)          # /login, /register, /logout

    from app.main.routes import main_bp
    app.register_blueprint(main_bp)          # /, /dashboard, /contact

    from app.resume.routes import resume_bp
    app.register_blueprint(resume_bp)        # /upload, /history, /interview-prep

    # ---- Initialize the database (create tables if they don't exist) ----
    init_db(app)

    return app
