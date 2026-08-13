# 03 — Architecture

## Overall Architecture

JobBridge is a **monolithic, server-rendered web application**. There is no separate frontend SPA, no microservices, and no external API layer beyond the app itself. Everything runs inside one Flask process.

```
┌─────────────────────────────────────────────────────────────────┐
│                            USER                                  │
│                     (Browser: Chrome/Firefox)                    │
└───────────────────────────────┬───────────────────────────────────┘
                                  │  HTTPS/HTTP requests
                                  │  (form POST, GET, fetch() for JSON)
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FLASK APPLICATION (WSGI)                     │
│  Entry point: run.py → create_app() in app/__init__.py           │
│                                                                    │
│   ┌───────────────┐   ┌───────────────┐   ┌───────────────────┐  │
│   │  auth_bp       │   │  main_bp       │   │  resume_bp         │  │
│   │ /login         │   │ /              │   │ /upload            │  │
│   │ /register      │   │ /dashboard     │   │ /history           │  │
│   │ /logout        │   │ /contact       │   │ /interview-prep    │  │
│   │                │   │                │   │ /api/questions     │  │
│   └───────┬───────┘   └───────┬───────┘   └─────────┬─────────┘  │
│           │                    │                       │            │
│           └────────────┬───────┴───────────┬──────────┘            │
│                         ▼                   ▼                       │
│               ┌──────────────────┐  ┌───────────────────────┐      │
│               │  app/models.py    │  │  app/ml/predict.py     │      │
│               │  (raw SQL layer)  │  │  app/ml/data.py         │      │
│               └─────────┬────────┘  │  (keyword engine)       │      │
│                          │            └───────────────────────┘      │
└──────────────────────────┼───────────────────────────────────────────┘
                            ▼
                  ┌───────────────────┐
                  │   MySQL Database    │
                  │   jobbridge_db       │
                  │   • users            │
                  │   • resume_uploads   │
                  └───────────────────┘
```

The templates (Jinja2) and static assets (CSS/JS/images) are served directly by Flask's built-in static file handling — there is no separate CDN or static file server in this codebase (see [13_Scalability.md](13_Scalability.md) for what would change at scale).

## Layers, One at a Time

### 1. Frontend (Presentation Layer)
- **Templates**: `templates/*.html`, using Jinja2 template inheritance. Every page `{% extends "base.html" %}` and fills in `{% block content %}` / `{% block extra_scripts %}`. `base.html` owns the `<head>`, navbar, flash-message rendering, and footer, so every page automatically gets consistent chrome.
- **Styling**: One file, [static/css/style.css](../static/css/style.css) (1078 lines), using CSS custom properties (`--primary`, `--bg-color`, etc.) defined in `:root` and overridden under `[data-theme="dark"]` for dark mode. No CSS framework/Sass/build step — plain hand-written CSS.
- **JavaScript**: One shared file, [static/js/main.js](../static/js/main.js), handling the mobile hamburger menu and the dark-mode toggle (persisted to `localStorage`). Page-specific behaviour (drag-and-drop upload, interview question fetching) lives inline in `{% block extra_scripts %}` in [upload.html](../templates/upload.html) and [interview_prep.html](../templates/interview_prep.html) respectively.
- **Icons/Fonts**: Font Awesome and Google Fonts ("Inter") are pulled from public CDNs directly in `base.html` — the only external network dependency in the whole app.

There is **no client-side framework** (no React/Vue/Angular). All dynamic data (dashboard stats, upload history rows, resume-analysis results) is rendered server-side by Jinja2 using data the Flask route already fetched from MySQL. The only place JavaScript talks to the backend asynchronously is the interview-prep page, which calls `GET /api/questions?role=...` and injects the JSON response into the DOM.

### 2. Backend (Application Layer)
- **Framework**: Flask 3.0.2, using the **Application Factory** pattern (`create_app()`), which is the recommended structure for anything beyond a toy script because it makes the app configurable and (in principle) testable without import-time side effects.
- **Blueprints**: Flask Blueprints group related routes. JobBridge has exactly three:
  - `auth_bp` (`app/auth/routes.py`) — registration, login, logout.
  - `main_bp` (`app/main/routes.py`) — home page, dashboard, contact, and the shared `login_required` decorator.
  - `resume_bp` (`app/resume/routes.py`) — upload, history, interview prep, and the questions JSON API.
- **Business logic**: lives in `app/ml/predict.py` (pure functions, no Flask imports — this is intentional so the analysis logic is framework-agnostic and unit-testable in isolation, even though no tests exist yet).
- **Configuration**: `app/config.py`'s `Config` class reads everything from environment variables (loaded via `python-dotenv`'s `load_dotenv()`), with safe fallback defaults for local development only.

### 3. Database Layer
- **MySQL**, accessed with the official `mysql-connector-python` driver — **no ORM** (no SQLAlchemy, no Peewee). Every query in `app/models.py` is raw, parameterized SQL.
- Connections are **request-scoped**: `get_db()` lazily opens a connection and stores it on Flask's `g` object; `close_db()` is registered via `app.teardown_appcontext()` so the connection is closed after every request, success or failure.
- `init_db(app)` runs once at startup (inside `create_app()`) and issues `CREATE TABLE IF NOT EXISTS` for both tables, so a fresh MySQL database self-provisions its schema with no separate migration tool (Alembic, Flyway, etc.) — fine for a small student project, a real gap at scale (see [07_Database.md](07_Database.md) and [13_Scalability.md](13_Scalability.md)).

### 4. Authentication
- **Session-based**, using Flask's built-in signed cookie session (`SECRET_KEY` signs it — the browser stores `user_id`, `user_name`, `user_email` in a tamper-evident but *not encrypted* cookie).
- **Password storage**: `werkzeug.security.generate_password_hash()` (scrypt-based) at registration; `check_password_hash()` at login. Plaintext passwords are never persisted.
- **Route protection**: a hand-written `login_required` decorator (in `app/main/routes.py`, imported into `app/resume/routes.py`) checks `session.get('user_id')` and redirects to `/login` if absent.
- There is **no** JWT, **no** OAuth (despite the `.env.example` placeholders and a docstring mentioning Google login — not implemented), and **no** CSRF token on forms. See [12_Security.md](12_Security.md) for the full breakdown of what is and isn't covered.

### 5. External APIs
JobBridge does **not** call any third-party AI/ML API (no OpenAI, no HuggingFace inference endpoint, nothing). The only outbound network calls the *browser* makes are to Google Fonts and the Font Awesome CDN for styling assets — purely cosmetic, not part of the application's logic. The `requests` library is listed in `requirements.txt` but is not actually imported or used anywhere in `app/` — it is an unused dependency.

### 6. Storage
- **Resume files are never written to disk or to a blob store.** `extract_text()` reads the uploaded file straight from the in-memory `FileStorage` object into `io.BytesIO`, extracts text, and discards the binary content once the request ends. Only the **filename string** (sanitized via `secure_filename()`) and the **extracted analysis results** are persisted, inside MySQL — not the original file bytes.
- **Static assets** (CSS/JS/team images in `static/images/`) are stored as plain files in the repository and served by Flask's default static route.

### 7. Deployment
There is **no deployment configuration in this repository** — no Dockerfile, no `Procfile`, no gunicorn/uWSGI config, no CI/CD pipeline, no cloud IaC. The only way to run the app today is:
```bash
python run.py
```
which starts Flask's built-in development server with `debug=True` — explicitly documented in `run.py`'s own comment as unsafe for production ("NEVER set debug=True in production"). See [13_Scalability.md](13_Scalability.md) for what a real deployment would need (gunicorn/uWSGI behind Nginx, environment-based secrets, a managed MySQL instance, etc.).

## Request Lifecycle Diagram (Generic)
```
User
  │
  ▼
Browser sends HTTP request (GET or POST)
  │
  ▼
Flask WSGI app receives request
  │
  ▼
URL routing → matches a Blueprint route (auth / main / resume)
  │
  ▼
Route function runs:
   - Reads session / request.form / request.files
   - Calls app/models.py for DB reads/writes (get_db() opens a
     per-request MySQL connection lazily)
   - Calls app/ml/predict.py for resume analysis (upload route only)
  │
  ▼
Route renders a Jinja2 template with the computed data
  │
  ▼
teardown_appcontext fires → close_db() closes the MySQL connection
  │
  ▼
HTML response sent back to the browser
```

## Component Diagram (Package-Level)
```
run.py
  └── app/__init__.py :: create_app()
        ├── app/config.py :: Config
        ├── app/models.py :: init_db, close_db, get_db, ...
        ├── app/auth/routes.py :: auth_bp
        │       └── app/models.py :: get_user_by_email, create_user
        ├── app/main/routes.py :: main_bp, login_required
        │       └── app/models.py :: get_user_by_id, get_upload_stats,
        │                             get_user_uploads
        └── app/resume/routes.py :: resume_bp
                ├── app/ml/predict.py :: analyze_resume
                │       └── app/ml/data.py :: ROLE_KEYWORDS, SUGGESTED_SKILLS
                ├── app/ml/data.py :: INTERVIEW_QUESTIONS
                ├── app/models.py :: save_upload, get_user_uploads
                └── app/main/routes.py :: login_required (reused)
```

## Why This Architecture Was Chosen (and what it trades off)
- **App factory + blueprints** instead of one flat `app.py`: keeps auth/main/resume concerns separated even though the app is small, and makes the code easy to navigate feature-by-feature — a good default even for small projects, since it costs almost nothing and pays off the moment the app grows.
- **No ORM**: raw SQL keeps every query visible and easy to explain in an interview, at the cost of losing automatic protection against typos, migrations, and cross-database portability that an ORM like SQLAlchemy would give you.
- **No background job queue / async processing**: resume analysis is fast (pure string/keyword operations, no network calls), so it runs synchronously inside the request — appropriate for the current scale, but would need to move to a task queue (Celery/RQ) if resumes were ever processed by something slower (e.g. a real ML model or an external OCR service for scanned PDFs).
- **Server-rendered templates instead of a JS framework + REST API**: matches the scope of the project (mostly server-driven CRUD pages) and avoids the complexity of a separate frontend build pipeline, at the cost of a less "modern SPA" feel and no client-side routing.
