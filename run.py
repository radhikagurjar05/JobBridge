"""
run.py — Entry point for the JobCatch Flask application.

Usage:
    python run.py

This file simply creates the app using our app factory (app/__init__.py)
and starts the development server.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True gives us auto-reload and detailed error pages during development.
    # NEVER set debug=True in production.
    app.run(debug=True)
