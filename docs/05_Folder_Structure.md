# 05 — Folder Structure

```
JobBridge/
├── app/                          # All Python application code
│   ├── __init__.py                # App Factory: create_app()
│   ├── config.py                  # Config class (env vars → settings)
│   ├── models.py                  # Raw-SQL database layer (no ORM)
│   │
│   ├── auth/                      # Blueprint: authentication
│   │   ├── __init__.py            # empty — marks this as a package
│   │   └── routes.py              # auth_bp: /register /login /logout
│   │
│   ├── main/                      # Blueprint: core site pages
│   │   ├── __init__.py            # empty — marks this as a package
│   │   └── routes.py              # main_bp: / /dashboard /contact
│   │                               #   + login_required decorator (shared)
│   │
│   ├── resume/                    # Blueprint: resume features
│   │   ├── __init__.py            # empty — marks this as a package
│   │   └── routes.py              # resume_bp: /upload /history
│   │                               #   /interview-prep /api/questions
│   │
│   └── ml/                        # "ML" / analysis engine (pure Python)
│       ├── __init__.py            # empty — marks this as a package
│       ├── data.py                # ROLE_KEYWORDS, INTERVIEW_QUESTIONS,
│       │                           #   SUGGESTED_SKILLS (all static data)
│       └── predict.py             # predict_role, compute_score,
│                                   #   extract_skills, analyze_resume
│
├── templates/                     # Jinja2 HTML templates
│   ├── base.html                  # Shared layout: navbar, flash msgs, footer
│   ├── index.html                 # Landing page (hero, features, testimonials)
│   ├── login.html                 # Login form
│   ├── register.html              # Registration form
│   ├── dashboard.html             # Logged-in user's summary/stats page
│   ├── upload.html                # Resume upload form + analysis results
│   ├── history.html               # Full upload history table
│   └── interview_prep.html        # Role picker + dynamic Q&A list
│
├── static/                        # Assets served as-is by Flask
│   ├── css/
│   │   └── style.css              # Single unified stylesheet (~1078 lines)
│   ├── js/
│   │   └── main.js                # Shared JS: hamburger menu, dark mode
│   └── images/                    # Team/testimonial photos (jpg)
│
├── venv/                          # Local Python virtual environment
│                                   #   (NOT part of the source project —
│                                   #    should be .gitignore'd, and is)
│
├── run.py                         # Entry point: `python run.py`
├── requirements.txt               # Pinned Python dependencies
├── .env                           # Actual local secrets (gitignored)
├── .env.example                   # Template showing required env vars
├── .gitignore                     # Excludes venv/, __pycache__/, .env, etc.
└── README.md                      # Setup instructions + feature summary
```

## Why Each Major Piece Exists

### `app/__init__.py` — The App Factory
Flask apps can be built two ways: a single global `app = Flask(__name__)` at module scope, or a **factory function** `create_app()` that builds and returns the app when called. JobBridge uses the factory pattern. Why this matters: it avoids import-time side effects (the app object doesn't exist until something explicitly calls `create_app()`), which makes it possible to create multiple app instances with different configs (e.g., one for tests, one for production) without one polluting the other. `run.py` is the only place that actually calls it.

### `app/config.py` — Centralized Configuration
All environment-dependent values (`SECRET_KEY`, MySQL host/port/user/password/database, upload size limit, allowed file extensions) live in one `Config` class. This exists so that **no secret or environment-specific value is hardcoded anywhere else in the codebase** — every other file reads from `current_app.config[...]`. `python-dotenv`'s `load_dotenv()` is called at import time in this file, which is what makes a local `.env` file "just work" without extra setup in `run.py`.

### `app/models.py` — The Only File That Talks SQL
This is the single point of contact with MySQL. Every other file that needs data (routes in `auth/`, `main/`, `resume/`) imports specific functions from here (`get_user_by_email`, `create_user`, `save_upload`, etc.) rather than writing SQL themselves. This exists so that if the database engine or schema ever changed, only this one file would need to change — the blueprint route files wouldn't need to know SQL at all.

### `app/auth/`, `app/main/`, `app/resume/` — Blueprints as Feature Folders
Each folder is a Flask **Blueprint** — a self-contained group of related routes with its own `__init__.py` (which is empty, just marking the folder as an importable Python package) and a `routes.py`. This exists to keep the codebase navigable by feature: if you're debugging a login problem, you only need to open `app/auth/routes.py`, not scroll through one giant `app.py` with fifteen mixed routes.

### `app/ml/` — Deliberately Isolated "Brain"
`data.py` holds all static knowledge (which keywords belong to which role, what interview questions exist, what skills to suggest) completely separated from `predict.py`, which holds the *logic* that operates on that data. This separation exists so that:
- Non-programmers (or anyone) could extend the app's knowledge (add a 26th role, add more interview questions) by editing only `data.py`, without touching any logic.
- `predict.py` has **zero Flask imports** — it's pure Python functions that take a string in and return a dict out. This makes it trivially unit-testable in isolation (even though, as noted elsewhere, no tests currently exist) and reusable outside a web context (e.g., a CLI script or a batch job could call `analyze_resume()` directly).

### `templates/` — One Shared Layout, Many Pages
`base.html` is the only file that defines `<html>`, `<head>`, the navbar, flash message rendering, and the footer. Every other template extends it and only supplies its unique `content` block. This exists so a navbar change (say, adding a new nav link) happens in exactly one file instead of eight.

### `static/` — Assets Flask Serves Directly
Flask's app factory call (`Flask(__name__, template_folder='../templates', static_folder='../static')`) explicitly points at these two folders (note they're one level up from `app/`, since the Flask *package* lives inside `app/` but the templates/static folders are at the project root — a slightly unusual but valid layout choice). CSS, JS, and images are not compiled/bundled (no Webpack/Vite) — they're just static files referenced with Jinja2's `url_for('static', filename=...)` helper, which also handles cache-busting-friendly URL generation.

### `run.py` — The Only Entry Point
This is the file you actually execute (`python run.py`). It does exactly two things: call `create_app()` and, if run directly (`__name__ == '__main__'`), start Flask's development server. Nothing else in the codebase starts the app — this single entry point keeps "how do I run this" unambiguous.

### `requirements.txt` — Pinned Dependencies
Every dependency has an exact pinned version (e.g. `Flask==3.0.2`), which exists so the project behaves identically on any machine it's installed on — no "works on my machine" surprises from an untested newer library version.

### `.env` / `.env.example` — Secrets Kept Out of Source Control
`.env` (gitignored) holds the actual local secrets; `.env.example` is committed and shows *which* variables are needed without exposing real values. This exists purely for security hygiene — so a `SECRET_KEY` or DB password is never accidentally pushed to GitHub.

## How Files Communicate (Dependency Flow)

```
run.py
  ↓ imports
app/__init__.py (create_app)
  ↓ imports
app/config.py (Config)          app/models.py (init_db, close_db)
  ↓                                ↓
app/auth/routes.py ──────────► app/models.py
app/main/routes.py ──────────► app/models.py
app/resume/routes.py ─────────► app/models.py
       │                         ▲
       │                         │ (uses login_required from)
       └────────────────────► app/main/routes.py
       │
       └────────────────────► app/ml/predict.py
                                    ↓ imports
                               app/ml/data.py

app/*/routes.py ──renders──► templates/*.html
                                    ↓ extends
                               templates/base.html
                                    ↓ links to
                               static/css/style.css, static/js/main.js
```

**Key dependency rule visible in the code**: dependencies only flow "inward and downward" — `app/ml/` never imports from `app/auth/`, `app/main/`, or `app/resume/` (no circular imports), and `app/models.py` never imports from any blueprint. The one cross-blueprint import (`resume/routes.py` importing `login_required` from `main/routes.py`) is the only place two feature folders talk directly to each other, and it's a one-way, one-function dependency.

## Project Organization Philosophy
This is a **feature-folder-per-blueprint** layout, not a **layer-per-folder** layout (i.e., it's not organized as `controllers/`, `services/`, `models/` at the top level — except `app/models.py` and `app/ml/` which behave like shared layers). For a project this size, this hybrid works well: small enough that a single `models.py` doesn't get unwieldy, but organized enough that each feature area (auth, main, resume) is self-contained and easy to reason about independently.
