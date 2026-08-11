# JobCatch — Complete Project Interview Guide

> Everything in this document is verified directly against the actual source code in this repository (`app/`, `templates/`, `static/`, `run.py`, `requirements.txt`). Nothing here is guessed or invented. Wherever something described in a comment, README, or `.env.example` is **not actually implemented**, this guide says so explicitly — that honesty is itself one of your strongest interview talking points.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Elevator Pitch](#2-elevator-pitch)
3. [Complete Application Flow](#3-complete-application-flow)
4. [System Architecture](#4-system-architecture)
5. [Folder Structure](#5-folder-structure)
6. [Technology Stack](#6-technology-stack)
7. [Database Design](#7-database-design)
8. [API Documentation](#8-api-documentation)
9. [Authentication & Authorization](#9-authentication--authorization)
10. [Feature Breakdown](#10-feature-breakdown)
11. [Code Walkthrough](#11-code-walkthrough)
12. [Important Functions](#12-important-functions)
13. [Interview Questions](#13-interview-questions)
14. [Cross Questions](#14-cross-questions)
15. [Challenges Faced](#15-challenges-faced)
16. [Improvements](#16-improvements)
17. [Scalability](#17-scalability)
18. [Security Analysis](#18-security-analysis)
19. [Resume Questions](#19-resume-questions)
20. [Weak Areas](#20-weak-areas)
21. [One-Day Revision Notes](#21-one-day-revision-notes)
22. [Cheat Sheet](#22-cheat-sheet)

---

## 1. Project Overview

### Project Name
**JobCatch** — tagline used in the app itself: *"Your AI-Powered Career Companion"* (see [README.md](README.md) and the hero section of [templates/index.html](templates/index.html)).

### Purpose
JobCatch is a Flask web application that:
- Accepts a resume file (PDF or DOCX).
- Extracts the raw text from it.
- Runs the text through a **rule-based keyword-matching engine** (not a trained ML model) to guess the most likely job role out of **25 predefined categories**.
- Scores the resume out of 100 based on structural checks.
- Shows which of that role's key skills are present in the resume and which are missing.
- Suggests additional trending skills for that role.
- Stores every result in a MySQL database against the logged-in user, so a dashboard and history page can show progress over time.
- Offers a separate "Interview Prep" page with curated question-and-answer pairs — but only for **10 of the 25** roles (this gap is explained in detail later in this guide).

### Problem Statement
Most freshers and job seekers do not know:
1. Which job role their resume is actually best suited for.
2. Whether their resume is structurally "good enough" (contact info, sections, length, etc.).
3. Which specific technical skills they are missing for the role they want.
4. What kind of questions they will actually be asked in an interview for that role.

Normally this feedback only comes from a mentor, a senior, or a paid resume-review service. JobCatch gives an **instant, free, first-pass answer** to all four questions the moment a user uploads their resume.

### Target Users
- **Final-year students / freshers** applying for their first job.
- **Job seekers** who want a quick, free sanity check on their resume before applying.
- **Anyone preparing for interviews** who wants role-specific practice questions.

### Main Features
Every item below is backed by real, working code — nothing is a wishlist.

| Feature | Where it lives |
|---|---|
| Register / Login / Logout (session-based auth) | [app/auth/routes.py](app/auth/routes.py) |
| Resume upload (PDF/DOCX) + text extraction | [app/resume/routes.py](app/resume/routes.py) |
| Role prediction (25 categories, keyword counting) | [app/ml/predict.py](app/ml/predict.py), [app/ml/data.py](app/ml/data.py) |
| Resume score (0–100, 7 rule-based checks) | `compute_score()` in `app/ml/predict.py` |
| Found vs. missing skill extraction | `extract_skills()` in `app/ml/predict.py` |
| Suggested "next skills to learn" | `SUGGESTED_SKILLS` in `app/ml/data.py` |
| Upload history table | `history()` in `app/resume/routes.py` |
| Dashboard (totals, average score, last role) | `dashboard()` in `app/main/routes.py` |
| Interview Prep page + JSON API | `interview_prep()`, `get_questions()` in `app/resume/routes.py` |
| Dark mode toggle (frontend only, `localStorage`) | [static/js/main.js](static/js/main.js) |

### Real-World Use Case
- A student about to apply to a company uploads their resume, sees they are missing "REST API" and "JUnit" for a Java Developer role, adds those skills, and re-uploads to confirm the change.
- A bootcamp graduate is unsure whether their resume "counts" as a Data Science resume or a Python Developer resume — JobCatch answers objectively based on keyword density.
- Someone practices the curated Q&A for "Python Developer" the night before an interview.

### Why This Project Is a Strong Interview Vehicle
- It is a **complete, working, full-stack CRUD + auth + file-processing application** — good for demonstrating backend fundamentals (Flask, blueprints, MySQL, sessions, password hashing, file parsing).
- It deliberately avoids "black box" AI: the matching logic is transparent keyword counting — every prediction can be justified by listing which keywords matched.
- It touches many topics interviewers probe: authentication security, file upload handling, database design, request lifecycle, session management, template rendering, and an honestly-labelled rule-based "AI" feature.

### High-Level Overview Diagram
```
                     ┌───────────────────────────────┐
                     │        Browser (Client)        │
                     │  HTML + CSS + Vanilla JS        │
                     └───────────────┬────────────────┘
                                      │  HTTP (forms / fetch)
                                      ▼
                     ┌───────────────────────────────┐
                     │   Flask Application (run.py)    │
                     │   App Factory: app/__init__.py │
                     │                                 │
                     │   Blueprints:                   │
                     │     auth_bp    → /login /register│
                     │     main_bp    → / /dashboard    │
                     │     resume_bp  → /upload /history│
                     └───────────────┬────────────────┘
                                      │
                        ┌─────────────┼─────────────────┐
                        ▼             ▼                 ▼
                 ┌─────────────┐ ┌───────────┐   ┌────────────────┐
                 │ app/models.py│ │ app/ml/    │   │ PyPDF2 /       │
                 │ (raw SQL)    │ │ predict.py │   │ python-docx     │
                 │              │ │ + data.py  │   │ (text extraction)│
                 └──────┬──────┘ └───────────┘   └────────────────┘
                        │
                        ▼
                 ┌─────────────┐
                 │   MySQL DB   │
                 │ jobcatch_db  │
                 │ users,       │
                 │ resume_uploads│
                 └─────────────┘
```

This project is intentionally **simple and monolithic** — a single Flask app, no microservices, no external AI API, no containerization. You can explain every single line of the request path, which is exactly what an interviewer wants to verify.

> **Honesty note — things mentioned but NOT actually implemented:**
> - Google OAuth login (`GOOGLE_OAUTH_CLIENT_ID`/`SECRET` exist in `.env.example`, and the docstring in `app/auth/routes.py` mentions `/login/google` routes) — **no such route exists** in the code.
> - The docstring in `app/models.py` mentions a `predictions` table — `init_db()` only actually creates `users` and `resume_uploads`. There is **no third table**.
> - There are **no automated tests, no Docker setup, and no deployment/CI configuration** anywhere in the repository.

---

## 2. Elevator Pitch

Practice these out loud — don't memorize word-for-word, internalize the structure.

### 30-Second Explanation
> "JobCatch is a Flask web app I built where you upload your resume — PDF or Word — and it instantly tells you which of 25 job roles fits you best, gives your resume a score out of 100, and shows you exactly which skills you have and which ones you're missing for that role. It also has a login system and an interview-prep section with practice questions. The matching engine isn't a black-box AI model — it's a transparent keyword-counting algorithm, so I can explain exactly why it made every single prediction."

### 2-Minute Explanation
> "JobCatch solves a problem a lot of students have: you don't really know if your resume is good, or which role it's actually aimed at, until a recruiter tells you — usually after you've already been rejected. So I built a tool that gives that feedback instantly.
>
> Architecturally it's a classic Flask app using the **application factory pattern** — `create_app()` in `app/__init__.py` builds the Flask app, loads config from environment variables via `python-dotenv`, and registers three blueprints: `auth` for login/register/logout, `main` for the homepage and dashboard, and `resume` for upload, history, and interview prep.
>
> For the database I didn't use an ORM like SQLAlchemy — I used the raw `mysql-connector-python` driver with plain SQL, so every query is visible in `app/models.py`. There are two tables: `users`, which stores name, email, and a hashed password, and `resume_uploads`, which stores every resume a user has uploaded along with its predicted role and score, linked by a foreign key with `ON DELETE CASCADE`.
>
> The 'AI' part is intentionally not a machine learning model. It's a dictionary of 25 job roles, each mapped to about 15 keywords. When you upload a resume, I clean the text, lowercase it, and count how many keywords from each role appear. The role with the highest count wins. If nothing matches, it falls back to 'General / Other'. I chose this over a trained model because it's 100% explainable.
>
> On top of that, resume scoring checks seven things — email present, phone present, skills section, education section, experience section, length over 250 words, and projects/achievements — each worth different points, totaling 100.
>
> Security-wise, passwords are hashed with Werkzeug's `generate_password_hash` (scrypt-based), never stored in plain text, and authentication state is kept in Flask's signed session cookie. Login is protected with a custom `login_required` decorator.
>
> The frontend is plain HTML/CSS/JavaScript with Jinja2 templates — no React or Vue — with a dark mode toggle stored in `localStorage` and a drag-and-drop upload zone."

### 5-Minute Detailed Explanation
> "JobCatch is a resume-analysis and career-guidance web application I built with Flask. Let me walk through the problem, the architecture, the core algorithm, the data model, and the security decisions.
>
> **The problem**: job seekers often don't know which role their resume actually targets, whether it's structurally complete, or which specific skills they're missing — and getting that feedback from a person is slow and often costs money. JobCatch automates the first pass of that feedback.
>
> **The architecture** follows the Flask 'application factory' pattern instead of a single global `app = Flask(__name__)`. `create_app()` in `app/__init__.py` creates the app, loads `Config` (which pulls `SECRET_KEY` and MySQL credentials from environment variables via `python-dotenv`, so nothing sensitive is hardcoded), registers `app.teardown_appcontext(close_db)` so the database connection always closes at the end of a request, registers three blueprints (`auth_bp`, `main_bp`, `resume_bp`), and finally calls `init_db(app)`, which connects to MySQL and runs `CREATE TABLE IF NOT EXISTS` for `users` and `resume_uploads` — so the schema self-heals on first run without a separate migration step.
>
> **The request flow for the core feature (resume upload)** starts at `GET /upload`, which shows the drag-and-drop form. On `POST /upload`, the route in `app/resume/routes.py` validates that a file was attached and that its extension is `.pdf` or `.docx`, then calls `extract_text()`, which uses `PyPDF2.PdfReader` for PDFs or `python-docx`'s `Document` for Word files. If extraction returns nothing — which happens with scanned/image-only PDFs — the user gets a friendly flash message instead of a crash. The extracted text then goes into `analyze_resume()` in `app/ml/predict.py`, which composes three functions: `predict_role()` counts keyword hits per role and returns whichever role has the most hits (or 'General / Other' if none match); `compute_score()` runs seven independent regex/substring checks summing to a maximum of 100; and `extract_skills()` re-uses the predicted role's keyword list to split it into 'found' vs. 'missing' skills. The final result dictionary is both rendered back to the user immediately and persisted via `save_upload()` into the `resume_uploads` table.
>
> **Data model**: two tables only. `users(id, name, email UNIQUE, password_hash, created_at)` and `resume_uploads(id, user_id FK→users.id ON DELETE CASCADE, filename, upload_time, predicted_role, resume_score)`. No ORM — I use `mysql-connector-python` directly with parameterized queries (`%s` placeholders), which is also how I avoid SQL injection.
>
> **Security decisions**: passwords are hashed with Werkzeug's `generate_password_hash`/`check_password_hash` (scrypt), never compared or stored in plain text. Login state lives in Flask's signed session cookie, and a `login_required` decorator guards `/dashboard`, `/upload`, and `/history`. File uploads never touch disk — the file is read into memory (`io.BytesIO`) and only the extracted text and the `secure_filename()`-sanitized name are kept. I'm upfront that this project does **not** implement CSRF tokens, rate limiting, email verification, or the Google OAuth flow referenced in comments and `.env.example` — those are known gaps, not secrets.
>
> **Frontend**: server-rendered Jinja2 templates extending one `base.html`, vanilla CSS with light/dark theme CSS variables toggled via a `data-theme` attribute and persisted in `localStorage`, and a small amount of vanilla JS for drag-and-drop upload UX and for fetching interview questions from a JSON endpoint without a page reload.
>
> If I were scaling this or hardening it for production, the first things I'd add are: CSRF protection, connection pooling instead of one connection per request, pagination on the history table, and turning the keyword engine into a pluggable interface so a real ML model could be swapped in later without changing the routes."

---

## 3. Complete Application Flow

Every flow below is traced directly from the code — file and function names are exact.

### Generic Request Lifecycle
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

### Feature 1: User Registration
```
User visits /register (GET)
   ↓
templates/register.html rendered (empty form)
   ↓
User fills Name, Email, Password, Confirm Password → submits (POST /register)
   ↓
app/auth/routes.py :: register()
   ↓
Validation (in order):
   - name/email/password not empty?
   - password == confirm_password?
   - len(password) >= 6?
   - get_user_by_email(email) already exists?
   ↓ (any failure → flash error, re-render register.html)
Passed all checks
   ↓
generate_password_hash(password)  [werkzeug, scrypt]
   ↓
create_user(name, email, password_hash) → app/models.py
   ↓ INSERT INTO users (...) VALUES (...)
   ↓
session['user_id'], session['user_name'], session['user_email'] set
   ↓
flash("Welcome to JobCatch, {name}!")
   ↓
redirect → /dashboard
```
**Database interaction**: one `SELECT` (duplicate-email check) + one `INSERT INTO users`. Registration auto-logs the user in — there is no separate email-verification step.

### Feature 2: User Login
```
GET /login → templates/login.html
   ↓
User submits email + password (POST /login)
   ↓
app/auth/routes.py :: login()
   ↓
get_user_by_email(email) → SELECT * FROM users WHERE email = %s
   ↓
user found? → check_password_hash(user['password_hash'], password)
   ↓ (fail → flash "Incorrect email or password", re-render login.html)
Success
   ↓
session['user_id'] = user['id']; session['user_name'] = user['name']; session['user_email'] = user['email']
   ↓
flash("Welcome back, {name}!")
   ↓
redirect → /dashboard
```
**Note**: the same generic error is shown whether the email doesn't exist or the password is wrong — this deliberately avoids "user enumeration."

### Feature 3: Logout
```
User clicks Logout (GET /logout)
   ↓
app/auth/routes.py :: logout()
   ↓
session.clear()
   ↓
flash("You have been logged out.")
   ↓
redirect → / (home)
```
**Note**: this is a `GET` request that changes state, which is a minor CSRF-style smell — low impact since it only logs the user out.

### Feature 4: Resume Upload & Analysis (the core feature)
```
GET /upload (must be logged in — login_required)
   ↓
templates/upload.html (empty dropzone form)
   ↓
User drags/selects a .pdf or .docx file → POST /upload (multipart/form-data)
   ↓
app/resume/routes.py :: upload()
   ↓
Validation:
   - 'resume' in request.files?
   - file.filename != ''?
   - allowed_file(filename) → extension in {pdf, docx}?
   ↓ (fail → flash error, re-render upload.html with no results)
extract_text(file)
   ├── .pdf  → PyPDF2.PdfReader(io.BytesIO(file.read())) → loop pages → extract_text()
   └── .docx → docx.Document(io.BytesIO(file.read())) → join paragraph texts
   ↓
resume_text.strip() empty? → flash "Could not extract text..." (e.g. scanned image PDF)
   ↓ (else continue)
analyze_resume(resume_text)  → app/ml/predict.py
   ├── predict_role(resume_text)     → clean_text() → count keyword hits per role → argmax
   ├── compute_score(resume_text)    → 7 rule-based checks → sum points (max 100)
   ├── extract_skills(text, role)    → found vs missing keywords for the predicted role
   └── get_suggested_skills(role)    → SUGGESTED_SKILLS[role]
   ↓
results = { predicted_role, score, score_details, found_skills, missing_skills, suggested_skills }
   ↓
secure_filename(file.filename) → filename
   ↓
save_upload(user_id, filename, predicted_role, score) → INSERT INTO resume_uploads
   ↓
render_template('upload.html', results=results, filename=filename)
   ↓
Response: same upload page, now showing predicted role + score ring, score breakdown,
          found/missing skills, suggested skills, and CTA buttons.
```
**Note**: this is a **POST-then-render**, not **POST-Redirect-GET** — refreshing the results page may prompt a form resubmission in some browsers. A known, minor UX gap.

### Feature 5: Dashboard
```
GET /dashboard (login_required)
   ↓
app/main/routes.py :: dashboard()
   ↓
user_id = session['user_id']
   ↓
get_user_by_id(user_id)         → SELECT * FROM users WHERE id = %s
get_upload_stats(user_id)       → SELECT COUNT(*), MAX(upload_time),
                                     MAX(predicted_role), ROUND(AVG(resume_score))
                                     FROM resume_uploads WHERE user_id = %s
get_user_uploads(user_id)[:5]   → SELECT ... ORDER BY upload_time DESC
                                     (then sliced in Python to first 5)
   ↓
render_template('dashboard.html', user=user, stats=stats, recent_uploads=recent_uploads)
```
**Efficiency note**: `get_user_uploads()` fetches **all** uploads and only *then* slices `[:5]` in Python — a `LIMIT 5` in SQL would be the correct fix at scale.

### Feature 6: Upload History
```
GET /history (login_required)
   ↓
app/resume/routes.py :: history()
   ↓
get_user_uploads(session['user_id'])
   ↓ SELECT id, filename, upload_time, predicted_role, resume_score
     FROM resume_uploads WHERE user_id = %s ORDER BY upload_time DESC
   ↓
render_template('history.html', uploads=uploads)
```
No pagination — every row for the user is returned unbounded.

### Feature 7: Interview Prep
```
GET /interview-prep
   ↓
roles = list(INTERVIEW_QUESTIONS.keys())   [from app/ml/data.py — only 10 of 25 roles]
   ↓
render_template('interview_prep.html', roles=roles)
   ↓
User picks a role → JS 'change' event fires
   ↓
fetch('/api/questions?role=<role>')
   ↓
app/resume/routes.py :: get_questions()
   ↓
questions = INTERVIEW_QUESTIONS.get(role, [])
   ↓
return jsonify(questions)
   ↓
JS builds question-card DOM elements (click to expand/collapse the answer)
```
**Gap**: `INTERVIEW_QUESTIONS` only has entries for **10 of the 25** roles (Python Developer, Data Science, Web Designing, Java Developer, DevOps Engineer, Testing, HR, Business Analyst, Sales, Network Security Engineer). For the other 15 roles, the API returns `[]` and the UI shows "No questions available for this role yet." — handled gracefully, not a crash.

### Cross-Cutting Flow: Route Protection (`login_required`)
```
Any protected route (/dashboard, /upload, /history)
   ↓
@login_required decorator (app/main/routes.py) runs BEFORE the view function
   ↓
session.get('user_id') present?
   ├── No  → redirect(url_for('auth.login'))
   └── Yes → call the actual view function
```
Defined once in `app/main/routes.py`, imported into `app/resume/routes.py` — the one cross-blueprint coupling in the whole codebase.

### Cross-Cutting Flow: Database Connection Per Request
```
Any request that touches the DB
   ↓
get_db() called (from any models.py function)
   ↓
'db' not in flask.g?  → open new mysql.connector.connect(...) → store in g.db
   ↓
... query runs using g.db ...
   ↓
Request finishes (success OR exception)
   ↓
app.teardown_appcontext(close_db) fires automatically
   ↓
close_db(): g.pop('db', None) → if connected, db.close()
```
A MySQL connection never leaks past a single request.

---

## 4. System Architecture

JobCatch is a **monolithic, server-rendered web application**. There is no separate frontend SPA, no microservices, and no external API layer beyond the app itself.

### ASCII Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                            USER                                  │
│                     (Browser: Chrome/Firefox)                    │
└───────────────────────────────┬───────────────────────────────────┘
                                  │  HTTP requests
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
                  │   jobcatch_db       │
                  │   • users            │
                  │   • resume_uploads   │
                  └───────────────────┘
```

Templates (Jinja2) and static assets (CSS/JS/images) are served directly by Flask's built-in static file handling — there is no CDN or separate static file server.

### 1. Frontend
- **Templates**: `templates/*.html`, using Jinja2 inheritance — every page `{% extends "base.html" %}`.
- **Styling**: one file, `static/css/style.css` (~1078 lines), CSS custom properties for theming.
- **JavaScript**: one shared file, `static/js/main.js` (hamburger menu, dark mode), plus page-specific inline scripts in `upload.html` and `interview_prep.html`.
- **No client-side framework** — no React/Vue/Angular. The only place JS talks to the backend asynchronously is `/api/questions`.

### 2. Backend
- **Flask 3.0.2**, Application Factory pattern (`create_app()`).
- **Blueprints**: `auth_bp`, `main_bp`, `resume_bp`.
- **Business logic**: `app/ml/predict.py` — pure functions, zero Flask imports (framework-agnostic, in principle unit-testable, though no tests exist yet).
- **Configuration**: `app/config.py`'s `Config` class, reading environment variables via `python-dotenv`.

### 3. Database
- **MySQL** via `mysql-connector-python` — **no ORM**.
- Connections are **request-scoped** via Flask's `g` object; closed via `teardown_appcontext`.
- `init_db(app)` runs `CREATE TABLE IF NOT EXISTS` for both tables at startup — schema self-provisions, no migration tool.

### 4. Authentication
- **Session-based**, Flask's signed cookie session (`SECRET_KEY` signs it).
- **Password storage**: Werkzeug's `generate_password_hash`/`check_password_hash` (scrypt).
- **Route protection**: hand-written `login_required` decorator.
- **No JWT, no OAuth (despite placeholders), no CSRF token.**

### 5. External APIs
JobCatch does **not** call any third-party AI/ML API. The only outbound browser calls are to Google Fonts and Font Awesome CDNs for styling — purely cosmetic. `requests` is listed in `requirements.txt` but is **never actually imported anywhere in `app/`** — an unused dependency, likely left over from planning the never-built OAuth flow.

### 6. Storage
- **Resume files are never written to disk or a blob store.** `extract_text()` reads the uploaded file straight into `io.BytesIO`, extracts text, and discards the binary content. Only the filename string and extracted analysis results are persisted — never the original file bytes.
- Static assets (CSS/JS/team images) are plain files served by Flask's default static route.

### 7. Deployment
**There is no deployment configuration in this repository** — no Dockerfile, no Procfile, no gunicorn/uWSGI config, no CI/CD, no cloud IaC. The only way to run the app is:
```bash
python run.py
```
which starts Flask's development server with `debug=True` — explicitly documented in `run.py`'s own comment as unsafe for production.

### Why This Architecture Was Chosen
- **App factory + blueprints** instead of one flat `app.py`: keeps auth/main/resume concerns separated, easy to navigate feature-by-feature.
- **No ORM**: raw SQL keeps every query visible and easy to explain, at the cost of losing automatic migration/typo protection an ORM would give.
- **No background job queue**: resume analysis is fast pure-Python string work, so it runs synchronously — appropriate for the current scale.
- **Server-rendered templates instead of a JS framework + REST API**: matches the scope of a mostly server-driven CRUD app.

---

## 5. Folder Structure

```
JobCatch/
├── app/                          # All Python application code
│   ├── __init__.py                # App Factory: create_app()
│   ├── config.py                  # Config class (env vars → settings)
│   ├── models.py                  # Raw-SQL database layer (no ORM)
│   │
│   ├── auth/                      # Blueprint: authentication
│   │   └── routes.py              # auth_bp: /register /login /logout
│   │
│   ├── main/                      # Blueprint: core site pages
│   │   └── routes.py              # main_bp: / /dashboard /contact + login_required
│   │
│   ├── resume/                    # Blueprint: resume features
│   │   └── routes.py              # resume_bp: /upload /history /interview-prep /api/questions
│   │
│   └── ml/                        # "ML" / analysis engine (pure Python)
│       ├── data.py                # ROLE_KEYWORDS, INTERVIEW_QUESTIONS, SUGGESTED_SKILLS
│       └── predict.py             # predict_role, compute_score, extract_skills, analyze_resume
│
├── templates/                     # Jinja2 HTML templates
│   ├── base.html                  # Shared layout: navbar, flash msgs, footer
│   ├── index.html                 # Landing page
│   ├── login.html / register.html # Auth forms
│   ├── dashboard.html             # Logged-in user's summary/stats page
│   ├── upload.html                # Resume upload form + analysis results
│   ├── history.html               # Full upload history table
│   └── interview_prep.html        # Role picker + dynamic Q&A list
│
├── static/
│   ├── css/style.css              # Single unified stylesheet
│   ├── js/main.js                 # Shared JS: hamburger menu, dark mode
│   └── images/                    # Team/testimonial photos
│
├── run.py                         # Entry point: `python run.py`
├── requirements.txt               # Pinned Python dependencies
├── .env / .env.example            # Secrets (gitignored) / template
└── README.md
```

### Why Each Major Piece Exists

**`app/__init__.py` — The App Factory.** Instead of a global `app = Flask(__name__)`, `create_app()` builds the app when called. This avoids import-time side effects, allowing multiple configured instances (e.g., different configs for dev/test) without conflict.

**`app/config.py` — Centralized Configuration.** All environment-dependent values live in one `Config` class, so no secret or environment-specific value is hardcoded anywhere else.

**`app/models.py` — The Only File That Talks SQL.** Every route file imports specific functions from here instead of writing SQL themselves — if the DB engine ever changed, only this file needs to change.

**`app/auth/`, `app/main/`, `app/resume/` — Blueprints as Feature Folders.** Each is a self-contained group of routes, keeping the codebase navigable by feature.

**`app/ml/` — Deliberately Isolated "Brain".** `data.py` holds static knowledge; `predict.py` holds pure logic with zero Flask imports, so it's reusable and unit-testable in isolation (even though no tests exist yet).

**`templates/` — One Shared Layout, Many Pages.** `base.html` is the only file defining `<html>`, `<head>`, navbar, and footer — a navbar change happens in exactly one file.

**`static/` — Assets Flask Serves Directly.** No build step (no Webpack/Vite) — plain files referenced via `url_for('static', ...)`.

**`run.py` — The Only Entry Point.** Calls `create_app()` and starts the dev server if run directly.

### Dependency Flow Diagram
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
```

**Key rule**: dependencies flow "inward and downward" — `app/ml/` never imports from any blueprint, and `app/models.py` never imports from any blueprint. The one cross-blueprint import (`resume/routes.py` importing `login_required` from `main/routes.py`) is the only place two feature folders talk directly to each other.

This is a **feature-folder-per-blueprint** layout, not a **layer-per-folder** (MVC-style) layout — a good hybrid for a project this size.

---

## 6. Technology Stack

Every technology listed is actually present in `requirements.txt` or the codebase — nothing speculative.

### Python 3
- **What it is**: general-purpose, interpreted, dynamically-typed language.
- **Why used**: Flask is a Python framework; huge ecosystem for file parsing (`PyPDF2`, `python-docx`).
- **Advantages**: readable syntax, fast to prototype, great for string/text processing.
- **Disadvantages**: slower than compiled languages; GIL limits multi-core parallelism (not a real concern here — the workload is I/O/string-bound).
- **Alternatives**: Node.js, Java, Go, Ruby.
- **Why chosen**: richest resume-parsing library ecosystem, and the language most commonly taught first.

### Flask 3.0.2
- **What it is**: a lightweight, unopinionated ("micro") web framework.
- **Why used**: the entire app — routing, blueprints, templating, sessions.
- **Advantages**: minimal boilerplate, easy to read end-to-end, flexible.
- **Disadvantages**: you must make your own decisions about structure/ORM/auth/forms — easy to skip something important (true here: no CSRF, no ORM).
- **Alternatives**: Django, FastAPI.
- **Why not Django**: Django is batteries-included (ORM, admin panel, built-in CSRF) — heavier/more opinionated than this project's scope needed.
- **Why not FastAPI**: FastAPI is async-first, built around JSON APIs (Pydantic) — this app is primarily server-rendered HTML, Flask's sweet spot.

### Werkzeug 3.0.1
- **What it is**: the WSGI utility library Flask is built on.
- **Why used**: `generate_password_hash()`/`check_password_hash()` for password security, `secure_filename()` for filename sanitization.
- **Advantages**: bundled with Flask, scrypt hashing by default (memory-hard, brute-force-resistant).
- **Disadvantages**: not a full auth system — no session-lifetime management, no password-reset flow built in.
- **Alternatives**: `bcrypt`, `argon2-cffi`.

### mysql-connector-python 8.3.0
- **What it is**: MySQL's official pure-Python driver.
- **Why used**: `mysql.connector.connect()` + parameterized `cursor.execute()` calls throughout `app/models.py`.
- **Advantages**: officially maintained, no C library needed, parameterized queries prevent SQL injection.
- **Disadvantages**: no ORM convenience, no connection pooling used here.
- **Alternatives**: `PyMySQL`, `SQLAlchemy` (ORM).
- **Why not SQLAlchemy**: for two tables and simple queries, raw SQL is easier to read and explain than ORM query-building.

### MySQL (Database Engine)
- **What it is**: a relational (SQL) DBMS.
- **Why used**: a clear one-to-many relationship + simple aggregates (`COUNT`, `AVG`, `MAX`) — a textbook relational use case.
- **Advantages**: ACID transactions, FK constraints with `ON DELETE CASCADE`, mature tooling.
- **Disadvantages**: requires a running server (not embedded); schema changes need explicit migrations at scale (none exist here).
- **Alternatives**: PostgreSQL, SQLite, MongoDB.
- **Why not MongoDB**: the data is inherently relational — a document store offers no advantage here and would lose the enforced FK cascade.

### PyPDF2 3.0.1
- **What it is**: a pure-Python PDF reading library.
- **Why used**: `extract_text()` uses `PdfReader` to loop pages and extract text.
- **Disadvantages**: **cannot read scanned/image-only PDFs** (no OCR) — handled gracefully with a flash message.
- **Alternatives**: `pdfplumber`, `pymupdf`, `pytesseract` (OCR).

### python-docx 1.1.0
- **What it is**: a library for reading/writing `.docx` files.
- **Why used**: joins the text of every paragraph via `doc.paragraphs`.
- **Disadvantages**: only supports modern `.docx` (not legacy `.doc`); **does not read table content** — only `doc.paragraphs`, not `doc.tables`.

### python-dotenv 1.0.1
- **What it is**: loads `.env` key=value pairs into `os.environ`.
- **Why used**: `app/config.py` calls `load_dotenv()` so secrets stay out of source code.
- **Disadvantages**: not a production secrets manager.

### requests 2.31.0 — *listed but unused*
- Present in `requirements.txt`, likely added for the never-implemented Google OAuth flow. **No `import requests` exists anywhere in `app/`** — confirmed by inspection.

### Jinja2 (via Flask)
- **What it is**: Python's default templating engine.
- **Why used**: every template uses `{% extends %}`, `{% block %}`, `{{ variable }}`.
- **Advantages**: auto-escapes variables by default (real XSS defense), template inheritance keeps navbar/footer DRY.

### HTML5, CSS3 (Vanilla), JavaScript (Vanilla)
- **Why used**: interactivity needs are genuinely small — toggle a class, fetch one JSON endpoint.
- **Alternatives**: React, Vue, Alpine.js.
- **Why chosen**: pulling in a full frontend framework would be over-engineering for this scope.

### Explicitly NOT Used

| Technology | Status |
|---|---|
| SQLAlchemy / any ORM | Not used — raw SQL only |
| JWT | Not used — session cookies only |
| Docker | Not used — no `Dockerfile` |
| Any cloud SDK (AWS/Azure/GCP) | Not used |
| Celery / RQ / task queue | Not used — analysis runs synchronously |
| Redis / Memcached | Not used — no caching layer |
| React / Vue / Angular | Not used — server-rendered Jinja2 only |
| pytest / unittest | Not used — no test suite exists |
| Google OAuth libraries | Not used — only placeholder env vars |

---

## 7. Database Design

All schema definitions below are copied directly from `app/models.py`'s `init_db()` — the actual executable source of truth (there is no separate `.sql` file or migration tool).

### ER Diagram (ASCII)
```
┌───────────────────────────────┐
│            users               │
├───────────────────────────────┤
│ PK  id             INT AUTO_INC│
│     name           VARCHAR(150)│
│ UQ  email          VARCHAR(150)│
│     password_hash  VARCHAR(256)│
│     created_at     DATETIME     │
└───────────────┬───────────────┘
                │ 1
                │ has many
                │ N
┌───────────────▼───────────────┐
│        resume_uploads          │
├───────────────────────────────┤
│ PK  id             INT AUTO_INC│
│ FK  user_id  ───────► users.id │
│     filename       VARCHAR(255)│
│     upload_time    DATETIME     │
│     predicted_role VARCHAR(100)│
│     resume_score   INT          │
└───────────────────────────────┘
        ON DELETE CASCADE
```

There are only **two tables** — a simple one-to-many relationship.

> **Discrepancy to flag proactively**: the docstring at the top of `app/models.py` says *"Tables: users, resume_uploads, predictions"* — but `init_db()` only creates `users` and `resume_uploads`. **There is no `predictions` table.** The prediction is instead stored as a column directly on `resume_uploads`.

### `users` Table
| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` | Unique surrogate key |
| `name` | `VARCHAR(150)` | `NOT NULL` | Display name |
| `email` | `VARCHAR(150)` | `UNIQUE NOT NULL` | Login identifier |
| `password_hash` | `VARCHAR(256)` | nullable | scrypt hash string |
| `created_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | Registration timestamp |

**Why nullable `password_hash`**: a hint that the design anticipated a second signup method (e.g., OAuth, where there'd be no local password) — consistent with the unused OAuth env vars, even though not implemented. In practice, every current user always has a hash.

### `resume_uploads` Table
| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` | Unique surrogate key |
| `user_id` | `INT` | `NOT NULL FK → users(id) ON DELETE CASCADE` | Owner of the upload |
| `filename` | `VARCHAR(255)` | `NOT NULL` | Sanitized filename — **not** a path (file is never saved to disk) |
| `upload_time` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | Used for `ORDER BY` |
| `predicted_role` | `VARCHAR(100)` | nullable | Result of `predict_role()` |
| `resume_score` | `INT` | nullable | Result of `compute_score()` |

### Primary Keys
Both tables use a simple auto-incrementing surrogate integer key (`id`) — standard practice, avoids using a mutable natural key (like email) as the primary key.

### Foreign Keys
Exactly one: `resume_uploads.user_id → users.id`, with `ON DELETE CASCADE`. Deleting a user automatically deletes all of their upload records at the database level. (There is currently no "delete account" feature that would trigger this — but the schema is ready for one.)

### Indexes
- Both `id` columns are indexed automatically (`PRIMARY KEY`).
- `users.email` has an implicit unique index from the `UNIQUE` constraint.
- `resume_uploads.user_id`, being a foreign key under InnoDB, automatically gets an index.
- **No explicit index on `upload_time`.** Every history/dashboard query does `ORDER BY upload_time DESC`; at large scale a composite index `(user_id, upload_time DESC)` would help.

### Constraints Summary
| Constraint | Where |
|---|---|
| `NOT NULL` | `users.name`, `users.email`, `resume_uploads.user_id`, `resume_uploads.filename` |
| `UNIQUE` | `users.email` |
| `PRIMARY KEY` | `users.id`, `resume_uploads.id` |
| `FOREIGN KEY ... ON DELETE CASCADE` | `resume_uploads.user_id → users.id` |
| `DEFAULT CURRENT_TIMESTAMP` | `users.created_at`, `resume_uploads.upload_time` |

There are **no `CHECK` constraints** — nothing in the database itself enforces `resume_score BETWEEN 0 AND 100`; that range is only guaranteed by construction in `compute_score()` (the 7 point values sum to exactly 100).

### Normalization
The schema is effectively in **Third Normal Form (3NF)**:
- **1NF**: every column holds a single atomic value.
- **2NF**: no composite primary key, so partial-dependency issues don't apply.
- **3NF**: no column depends on a non-key column — `predicted_role`/`resume_score` depend only on the upload's own `id`.

**Why designed this way**: two tables is the minimum needed to model "a user can have many uploads, and we need history for each" without duplicating user info on every upload row. A flattened single-table design would lose history (only the latest value could be kept).

### What a `predictions` Table Would Have Looked Like
```
predictions
├── PK id
├── FK upload_id  → resume_uploads.id
├── role           VARCHAR(100)
├── keyword_score  INT
├── created_at     DATETIME
```
This would let one upload have multiple prediction attempts recorded over time — a good "how would you refactor this?" answer.

---

## 8. API Documentation

JobCatch is mostly a server-rendered app (HTML responses). Only **one** route (`/api/questions`) returns pure JSON — the rest return rendered HTML pages.

### `GET /`
- **Purpose**: Landing page.
- **Auth**: No.
- **Output**: renders `index.html`.

### `GET /contact`
- **Purpose**: Meant to scroll to a contact section.
- **Output**: `render_template('index.html', scroll_to='contact')`.
- **Real gap**: `scroll_to` is passed to the template but **never referenced anywhere** in `index.html` — a dead/unfinished parameter. `/contact` behaves identically to `/`.
- **Auth**: No.

### `GET, POST /register`
- **Purpose**: Create a new account.
- **Request (POST form)**: `name`, `email`, `password`, `confirm_password`.
- **Response**: `GET` → form. `POST` success → `302` redirect to `/dashboard`. `POST` failure → re-render with flash error, `200`.
- **Validation** (first failure wins): all fields non-empty → `password == confirm_password` → `len(password) >= 6` → email not already registered.
- **Possible errors**: a true race condition (two simultaneous registrations, same email) could raise an unhandled `IntegrityError` since there's no `try/except` around the `INSERT`.
- **Auth**: No (redirects to dashboard if already logged in).

### `GET, POST /login`
- **Purpose**: Authenticate a user.
- **Request (POST form)**: `email`, `password`.
- **Response**: `GET` → form. `POST` success → redirect to `/dashboard`. `POST` failure → generic flash error.
- **Validation**: `get_user_by_email()` returns a row **and** `password_hash` truthy **and** `check_password_hash()` passes.
- **Possible errors**: DB connectivity failure surfaces as an unhandled `mysql.connector.Error` → Flask's default 500 page.
- **Auth**: No.

### `GET /logout`
- **Purpose**: End the session.
- **Response**: `302` redirect to `/` + flash info.
- **Note**: state-changing `GET` — mild CSRF surface.

### `GET /dashboard`
- **Purpose**: Show the logged-in user's stats.
- **Response**: renders `dashboard.html` with `user`, `stats`, `recent_uploads` (first 5).
- **Possible errors**: if `user_id` refers to a deleted user (no such feature exists yet), `get_user_by_id` returns `None` → template `AttributeError`/500.
- **Auth**: **Yes**.

### `GET, POST /upload`
- **Purpose**: Upload a resume, receive full analysis.
- **Request (POST)**: `multipart/form-data`, file field `resume`.
- **Validation**: file present → non-empty filename → extension `pdf`/`docx` → `extract_text()` doesn't raise → extracted text non-blank.
- **`results` payload shape**:
```json
{
  "predicted_role": "Python Developer",
  "score": 82,
  "score_details": [
    {"label": "Has email address", "passed": true, "points": 15}
  ],
  "found_skills": ["python", "flask", "rest api"],
  "missing_skills": ["django", "celery"],
  "suggested_skills": ["FastAPI", "Docker", "PostgreSQL", "Redis", "AWS Lambda"]
}
```
- **Possible errors**: file-read errors are caught and shown via flash, including the raw exception string (`f'Could not read the file. Error: {str(e)}'`) — a minor information-disclosure smell.
- **File size limit**: `MAX_CONTENT_LENGTH = 5MB` — Werkzeug raises `413` automatically before the route runs; no custom `413` handler exists, so the user sees Flask's default error page.
- **Auth**: **Yes**.

### `GET /history`
- **Purpose**: Show every past upload.
- **Response**: `history.html` with all uploads, newest first, **no pagination**.
- **Auth**: **Yes**.

### `GET /interview-prep`
- **Purpose**: Role picker page.
- **Response**: `roles = list(INTERVIEW_QUESTIONS.keys())` — only the **10** roles with curated Q&A.
- **Auth**: No — publicly accessible even when logged out.

### `GET /api/questions?role=<role>` — the one true JSON API
- **Purpose**: Return interview Q&A for a role, consumed by client-side `fetch()`.
- **Input**: query param `role`.
- **Output**: `200 OK`, JSON array of `{q, a}` objects, or `[]` for unknown/missing roles.
- **Validation**: none needed — `.get(role, [])` safely defaults; **impossible to trigger a `400`**.
- **Internal flow**:
```
Browser: fetch('/api/questions?role=Python%20Developer')
   ↓
Flask routes to resume_bp.get_questions
   ↓
request.args.get('role', '') → "Python Developer"
   ↓
INTERVIEW_QUESTIONS.get("Python Developer", [])
   ↓
jsonify(questions) → HTTP 200, JSON body
```
- **Auth**: No.

### Endpoints Summary Table
| Method | Path | Auth? | Returns | Blueprint |
|---|---|---|---|---|
| GET | `/` | No | HTML | main |
| GET | `/contact` | No | HTML (same as `/`) | main |
| GET/POST | `/register` | No | HTML | auth |
| GET/POST | `/login` | No | HTML | auth |
| GET | `/logout` | No | Redirect | auth |
| GET | `/dashboard` | **Yes** | HTML | main |
| GET/POST | `/upload` | **Yes** | HTML | resume |
| GET | `/history` | **Yes** | HTML | resume |
| GET | `/interview-prep` | No | HTML | resume |
| GET | `/api/questions` | No | **JSON** | resume |

**Not implemented despite being referenced elsewhere**: `/login/google`, `/login/google/callback`.

---

## 9. Authentication & Authorization

### Login Flow
Email + password. `login()` in `app/auth/routes.py` looks up the user by email, then calls `check_password_hash()` to compare the submitted password against the stored hash. On success, `session['user_id']`, `session['user_name']`, `session['user_email']` are set.

### Registration Flow
`register()` validates all fields, checks the password confirmation and minimum length (6 chars), checks the email isn't taken, hashes the password with `generate_password_hash()`, inserts the user, and **auto-logs them in immediately** — there is no email verification step.

### Password Storage
- **Algorithm**: `werkzeug.security.generate_password_hash()` — **scrypt** by default in modern Werkzeug.
- Passwords are **hashed, never encrypted** — a one-way transformation. Login re-hashes the submitted password's comparison via `check_password_hash()`; the stored hash is never reversed.
- Stored in `users.password_hash VARCHAR(256)`.
- **Gap**: minimum length is only 6 characters, no complexity requirement, no breached-password check.

### JWT
**Not used at all.** Authentication state lives entirely in Flask's server-signed session cookie. JWT would make more sense if this app exposed its API to a separate mobile app or SPA that couldn't rely on cookies — for a same-origin server-rendered app, session cookies are the simpler, correct choice.

### Sessions
Flask's built-in client-side session, **signed but not encrypted** using `SECRET_KEY` (`itsdangerous` under the hood). It stores `user_id`, `user_name`, `user_email` — these values are readable (base64-decodable) by anyone with the cookie, but cannot be tampered with without knowing `SECRET_KEY`.
- **Gap**: no `PERMANENT_SESSION_LIFETIME` configured — sessions expire when the browser closes by default.

### Cookies
`SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE` are **not explicitly set** — Flask's defaults apply (`HttpOnly=True`, `Secure=False`, `SameSite=Lax`). Because `SESSION_COOKIE_SECURE` isn't forced `True`, the cookie could be sent over plain HTTP if ever deployed without HTTPS enforced elsewhere.

### Roles
There is only **one** user role in this system — no admin/staff distinction. Every registered user has identical permissions. Authorization is purely "is this session logged in" plus "does every query filter by `session['user_id']`."

### Route Protection
A hand-written `login_required` decorator (in `app/main/routes.py`, reused in `app/resume/routes.py`) checks `session.get('user_id')` and redirects to `/login` if absent. Applied to `/dashboard`, `/upload`, `/history`.

```python
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated
```

### Security Summary
| Control | Status |
|---|---|
| Password hashing | ✅ Werkzeug scrypt |
| JWT | ❌ Not used (session cookies instead) |
| CSRF tokens | ❌ Missing on all forms |
| Rate limiting on login | ❌ Missing |
| Email verification | ❌ Missing |
| Google OAuth | ❌ Referenced in `.env.example`/docstrings, never implemented |
| Multi-factor auth | ❌ Not implemented |
| Account lockout | ❌ Not implemented |
| Data scoping (authorization) | ✅ Every query filtered by `session['user_id']` |

If authentication features are asked about and don't exist here, the honest answer is exactly that — say so plainly rather than guessing.

---

## 10. Feature Breakdown

### Feature: Authentication (Register / Login / Logout)
- **Purpose**: Identify users so uploads/stats can be tracked individually.
- **Internal working**: a user = name + unique email + hashed password. Session state is the only signal distinguishing logged-in from logged-out.
- **Files**: `app/auth/routes.py`, `app/models.py`, `templates/login.html`, `templates/register.html`.
- **Execution flow**: see Section 3, Features 1–3.
- **Edge cases**: race condition on duplicate email registration (unhandled `IntegrityError`); no password complexity beyond length 6; no login rate limiting; `/logout` is a state-changing `GET`.

### Feature: Resume Upload & Text Extraction
- **Purpose**: Accept a PDF/DOCX and turn it into plain text for analysis.
- **Internal working**: only two file types accepted; files read entirely in memory, never written to disk; 5MB cap enforced by Flask config; empty extraction is detected and reported to the user.
- **Files**: `app/resume/routes.py` (`allowed_file`, `extract_text`, `upload`), `templates/upload.html`.
- **Edge cases**: corrupted/password-protected PDFs raise exceptions caught by a generic handler; `.docx` table content is silently missed (only `doc.paragraphs` is read); extension spoofing fails safely at parse time (never executed, never saved).

### Feature: Role Prediction Engine
- **Purpose**: Guess which of 25 job roles best matches a resume, transparently.
- **Internal working**: each role has ~15 lowercase keywords (`ROLE_KEYWORDS`). Text is cleaned and lowercased; for each role, count keyword substring matches; highest count wins; all-zero falls back to `"General / Other"`.
- **Files**: `app/ml/predict.py` (`clean_text`, `predict_role`), `app/ml/data.py`.
- **Execution flow**:
```
resume_text
   ↓
clean_text() — strip URLs, keep [a-zA-Z0-9\s/+#.], collapse whitespace, lowercase
   ↓
for each of 25 roles: count = keywords found as substrings in cleaned text
   ↓
predicted_role = role with max(count)
   ↓
if max count == 0 → "General / Other"
```
- **Edge cases**: **substring matching, not word-boundary matching** — `"java"` matches inside `"javascript"`. **Duplicate dictionary key**: `ROLE_KEYWORDS` defines `"Data Science"` twice in `app/ml/data.py`; Python silently keeps only the second definition, making the first block's keywords (including `jupyter`) dead code.

### Feature: Resume Scoring (0–100)
- **Purpose**: Give an objective structural quality score, independent of role.
- **Internal working**: 7 checks, summing to exactly 100:

| Check | Points | How detected |
|---|---|---|
| Has email address | 15 | regex `[\w.-]+@[\w.-]+\.\w+` |
| Has phone number | 15 | regex `(\+?\d[\d\s\-]{8,}\d)` |
| Has Skills section | 20 | substring `'skill'` present |
| Has Education section | 15 | any of `education, degree, university, college, bachelor, master` |
| Has Experience section | 15 | any of `experience, work history, employment, internship` |
| Sufficient length (250+ words) | 10 | `len(resume_text.split()) >= 250` |
| Has Projects/Achievements | 10 | any of `project, achievement, built, developed, designed` |

- **Files**: `app/ml/predict.py::compute_score`.
- **Edge cases**: "no experience yet, fresher" still scores 15 points for "Experience" (word-presence, not semantic understanding); "upskill" would trigger the Skills check.

### Feature: Skill Gap Analysis (Found vs. Missing)
- **Purpose**: Show which of the predicted role's keywords are present/absent in the resume.
- **Internal working**: reuses `ROLE_KEYWORDS[role]` — the same list drives both prediction and gap analysis.
- **Files**: `app/ml/predict.py::extract_skills`.
- **Edge case**: `"General / Other"` isn't a key in `ROLE_KEYWORDS`, so `extract_skills` returns `([], [])`.

### Feature: Suggested Skills
- **Purpose**: Recommend forward-looking "next skills to learn," distinct from current requirements.
- **Internal working**: a static dictionary `SUGGESTED_SKILLS` mapping each role to 4–5 trending skills — shown unconditionally, **not** cross-checked against the resume.
- **Files**: `app/ml/predict.py::get_suggested_skills`, `app/ml/data.py::SUGGESTED_SKILLS`.

### Feature: Dashboard & Upload History
- **Purpose**: Aggregate stats + full upload browsing.
- **Internal working**: no caching or pre-computed aggregates — every load runs fresh `COUNT`/`AVG`/`MAX` SQL.
- **Files**: `app/main/routes.py::dashboard`, `app/resume/routes.py::history`, `app/models.py`.
- **Edge case**: a brand-new user (0 uploads) — `MAX`/`AVG` over zero rows return `NULL`, handled in templates with `{{ stats.avg_score or 0 }}` fallbacks.

### Feature: Interview Prep
- **Purpose**: Study curated Q&A for a specific role, open to all visitors.
- **Internal working**: `INTERVIEW_QUESTIONS` covers only **10 of 25** roles, 5 Q&A pairs each. Questions load asynchronously via `/api/questions` — no full page reload.
- **Files**: `app/resume/routes.py`, `templates/interview_prep.html`.
- **Edge case**: unsupported role → `[]` → "No questions available for this role yet." — gracefully handled, not a bug, just incomplete content.

---

## 11. Code Walkthrough

If you did not write this project, read the files in **this exact order**.

### Step 1 — Entry Point: `run.py`
```python
from app import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True)
```
Two lines that matter — everything else exists to make `create_app()` return a fully configured app.

### Step 2 — The App Factory: `app/__init__.py`
This is the "table of contents" of the whole backend: creates the `Flask` instance, loads `Config`, registers `close_db` teardown, registers the 3 blueprints, calls `init_db(app)`.

### Step 3 — Configuration: `app/config.py`
Shows every environment variable the app depends on and its local-dev fallback.

### Step 4 — The Database Layer: `app/models.py`
Read before any blueprint, since every blueprint calls into it:
1. **Connection management** (`get_db`, `close_db`).
2. **Schema setup** (`init_db`).
3. **Query helpers** (`get_user_by_email`, `get_user_by_id`, `create_user`, `save_upload`, `get_user_uploads`, `get_upload_stats`).

### Step 5 — Routing (Blueprints, in Feature Order)
**5a. `app/auth/routes.py`** — read `register()`, `login()`, `logout()`. Teaches the standard route pattern used everywhere:
```python
@blueprint.route('/path', methods=['GET', 'POST'])
def view():
    if request.method == 'POST':
        # read request.form, validate, call models.py, update session/flash
        # redirect or re-render
    return render_template('template.html')
```
**5b. `app/main/routes.py`** — read `login_required` first (reused by `resume`), then `home()`, `dashboard()`, `contact()`.
**5c. `app/resume/routes.py`** — the most important blueprint: `allowed_file()`/`extract_text()` → `upload()` → `history()` → `interview_prep()`/`get_questions()`.

### Step 6 — The "ML" Engine: `app/ml/data.py` then `app/ml/predict.py`
Read `data.py` first (pure data, no logic). Then `predict.py` top to bottom: `clean_text()` → `predict_role()` → `compute_score()` → `extract_skills()` → `get_suggested_skills()` → `analyze_resume()` (the "public API" — the only function `app/resume/routes.py` imports).

### Step 7 — Templates
Read `base.html` first — it defines the shared shell every other template extends.

### Step 8 — Static Assets (only if debugging visuals)

### "Where Do I Start Reading?" — One-Line Answer
**`run.py` → `app/__init__.py` → `app/models.py` → whichever blueprint matches the feature → `app/ml/predict.py` + `app/ml/data.py` if it's the resume-analysis feature.**

### MVC-Style Mapping
| MVC-style Layer | This Project's Equivalent |
|---|---|
| Entry point | `run.py` |
| App bootstrap | `app/__init__.py :: create_app()` |
| Configuration | `app/config.py :: Config` |
| Routing + Controllers | `app/auth/routes.py`, `app/main/routes.py`, `app/resume/routes.py` |
| Services / Business Logic | `app/ml/predict.py` (pure functions — closest thing to a service layer) |
| Data / Models | `app/models.py` (raw SQL, no `models/` directory with per-table classes) |
| Views | `templates/*.html` |
| Static config data | `app/ml/data.py` |

### Execution Trace (Concrete: Uploading a Resume)
```
1. python run.py                     → Flask dev server starts on :5000
2. Browser: POST /upload (file attached)
3. Router matches resume_bp's /upload rule
4. app/resume/routes.py :: upload() begins
5.   → allowed_file() checks extension
6.   → extract_text() called
7.        → PyPDF2.PdfReader / docx.Document parses the in-memory file
8.   → app/ml/predict.py :: analyze_resume(text) called
9.        → predict_role() reads app/ml/data.py :: ROLE_KEYWORDS
10.       → compute_score() runs its 7 regex/substring checks
11.       → extract_skills() reads ROLE_KEYWORDS again, for the winning role
12.       → get_suggested_skills() reads SUGGESTED_SKILLS
13.  → app/models.py :: save_upload() called
14.       → get_db() opens (or reuses) a MySQL connection stored in flask.g
15.       → INSERT INTO resume_uploads ... ; db.commit()
16.  → render_template('upload.html', results=..., filename=...)
17. Flask finishes the response
18. app.teardown_appcontext fires → close_db() closes the MySQL connection
19. HTML sent back to the browser
```

---

## 12. Important Functions

### `create_app()` — `app/__init__.py`
- **Purpose**: build and return a fully configured Flask app.
- **Input**: none. **Output**: a `Flask` instance.
- **Logic**: create `Flask()` → load `Config` → register `close_db` teardown → register 3 blueprints → call `init_db()`.
- **Why it exists**: avoids a module-level global `app`, supporting different configs without import-time side effects.

### `get_db()` — `app/models.py`
- **Purpose**: return a MySQL connection scoped to the current request.
- **Input**: none (reads `flask.g`, `flask.current_app.config`). **Output**: a connection object.
- **Logic**: `if 'db' not in g: g.db = mysql.connector.connect(...)`.
- **Why it exists**: one connection per request, reused by every query helper within that request.

### `close_db(e=None)` — `app/models.py`
- **Purpose**: close the request-scoped connection at request end.
- **Logic**: `g.pop('db', None)` → if connected, `.close()`.
- **Called by**: Flask via `app.teardown_appcontext(close_db)`.

### `init_db(app)` — `app/models.py`
- **Purpose**: ensure tables exist before serving traffic.
- **Logic**: opens its own connection (outside request context), runs `CREATE TABLE IF NOT EXISTS` for `users` and `resume_uploads`, commits, closes.

### `get_user_by_email(email)` / `get_user_by_id(user_id)` — `app/models.py`
- **Purpose**: single-row user lookups by email or ID.
- **Output**: dict or `None`.
- **Why parameterized queries matter**: prevents SQL injection — user input is never string-concatenated into SQL text.

### `create_user(name, email, password_hash=None)` — `app/models.py`
- **Purpose**: insert a new user row.
- **Output**: `cursor.lastrowid`.

### `save_upload(user_id, filename, predicted_role, resume_score)` — `app/models.py`
- **Purpose**: persist one resume-upload event.
- **Output**: the new row's `id`.

### `get_user_uploads(user_id)` — `app/models.py`
- **Purpose**: fetch every upload for a user, newest first.
- **Called by**: `history()` (full list) and `dashboard()` (only `[:5]` — a real inefficiency, see Section 15/16).

### `get_upload_stats(user_id)` — `app/models.py`
- **Purpose**: compute dashboard aggregates in a single query.
- **Why it matters**: pushes aggregation down to the database instead of pulling all rows into Python — the correct, efficient pattern.

### `register()` / `login()` — `app/auth/routes.py`
- **Purpose**: handle account creation / authentication (GET shows form, POST processes it).
- **Calls**: `get_user_by_email`, `generate_password_hash`/`check_password_hash`, `create_user`.

### `login_required(f)` — `app/main/routes.py`
- **Purpose**: decorator requiring a logged-in session.
- **Why `functools.wraps(f)` matters**: without it, Flask would see every decorated view as having the same name (`decorated`), breaking `url_for`'s function-name-based routing.
- **Reused by**: `resume/routes.py` (the one cross-blueprint import in the codebase).

### `allowed_file(filename)` — `app/resume/routes.py`
- **Purpose**: check the file extension is permitted.
- **Logic**: `'.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS`.
- **Edge case**: a filename with no `.` correctly short-circuits to `False` before `.rsplit()` could raise.

### `extract_text(file)` — `app/resume/routes.py`
- **Purpose**: convert an uploaded PDF/DOCX into plain text.
- **Why `io.BytesIO`**: both `PdfReader` and `Document` accept file-like objects — no filesystem interaction ever needed.

### `clean_text(text)` — `app/ml/predict.py`
- **Purpose**: normalize raw resume text for reliable keyword matching.
- **Logic**: strip URLs → keep only `[a-zA-Z0-9\s/+#.]` → collapse whitespace → lowercase.
- **Why `/+#.` are preserved**: keywords like `"c#"`, `".net"`, `"ci/cd"` in `ROLE_KEYWORDS` need those characters to ever match.

### `predict_role(resume_text)` — `app/ml/predict.py`
- **Purpose**: the core "AI" — pick the best-fit role.
- **Output**: `(predicted_role: str, scores: dict)`.
- **Note**: `_scores` is computed but discarded by the caller (`analyze_resume`) — a missed opportunity to show the user *why* a role was picked.

### `compute_score(resume_text)` — `app/ml/predict.py`
- **Purpose**: produce the 0–100 score and its breakdown.
- **Output**: `{"score": int, "details": [{"label", "passed", "points"}, ...]}`.

### `extract_skills(resume_text, role)` — `app/ml/predict.py`
- **Purpose**: split a role's keyword list into found vs. missing.
- **Output**: `(found: list, missing: list)`.

### `analyze_resume(resume_text)` — `app/ml/predict.py`
- **Purpose**: the single "public API" of the ML module — composes all four analysis functions.
- **Why it exists**: encapsulation — the web layer doesn't need to know how analysis is internally composed.

### `get_questions()` — `app/resume/routes.py`
- **Purpose**: serve interview Q&A as JSON.
- **Logic**: `INTERVIEW_QUESTIONS.get(role, [])` — can never raise from bad input.

---

## 13. Interview Questions

### BASIC

1. **What does JobCatch do, in one sentence?** — A Flask app where you upload a resume (PDF/DOCX) and it instantly predicts your best-fit job role out of 25 categories, scores your resume out of 100, and shows which skills you have vs. are missing.
2. **What tech stack did you use?** — Python + Flask backend, MySQL via `mysql-connector-python` (no ORM), Jinja2 + vanilla HTML/CSS/JS frontend, PyPDF2 and python-docx for parsing.
3. **Why Flask instead of Django?** — Flask is a micro-framework — I only needed routing, templating, and sessions, and wanted to write my own SQL/auth logic rather than adopt Django's full conventions for a project this size.
4. **What is the Application Factory pattern, and where did you use it?** — Instead of a global `app = Flask(__name__)`, `create_app()` in `app/__init__.py` builds and configures the app when called; `run.py` calls it.
5. **What is a Flask Blueprint?** — A way to group related routes: `auth_bp`, `main_bp`, `resume_bp`.
6. **How do you handle passwords securely?** — `generate_password_hash()` (scrypt) at registration, `check_password_hash()` at login — never plaintext.
7. **What database did you use and why?** — MySQL, because the data is relational (a user has many uploads).
8. **Do you use an ORM?** — No — raw parameterized SQL in `app/models.py`, for transparency given the small schema.
9. **How many tables does your database have?** — Two: `users` and `resume_uploads`, linked by a foreign key with `ON DELETE CASCADE`.
10. **What file types can users upload?** — PDF and DOCX only, extension allow-listed, 5MB cap.
11. **How do you extract text from a PDF?** — PyPDF2's `PdfReader`, looping every page and concatenating `.extract_text()`.
12. **How do you extract text from a DOCX?** — `python-docx`'s `Document`, joining every paragraph's `.text`.
13. **How does your app predict a job role?** — Count keyword matches per role (25 roles, ~15 keywords each); highest count wins.
14. **Is this a machine learning model?** — No — a transparent rule-based keyword-counting engine, chosen deliberately for full explainability.
15. **How is the resume score calculated?** — Seven rule-based checks (email, phone, skills, education, experience, length, projects) summing to 100.
16. **What happens if no keywords match any role?** — Falls back to `"General / Other"`.
17. **How do users log in?** — Email + password; `check_password_hash()` verifies against the stored hash, then session keys are set.
18. **How do you protect routes that require login?** — A custom `login_required` decorator checking `session.get('user_id')`.
19. **What is a Python decorator?** — A function wrapping another function to add behavior without modifying it — `login_required` wraps view functions to add an auth check.
20. **What is session management in Flask?** — Session data lives in a cookie signed with `SECRET_KEY` — tamper-evident, not encrypted.
21. **What is the purpose of `SECRET_KEY`?** — Cryptographically signs session cookies and flash messages.
22. **What is `.env` and why use it?** — Holds environment-specific secrets, read via `python-dotenv`, kept out of version control.
23. **What is a foreign key, and where do you use one?** — `resume_uploads.user_id` references `users.id`, with `ON DELETE CASCADE`.
24. **What does `ON DELETE CASCADE` mean?** — Deleting a parent row automatically deletes all referencing child rows.
25. **How do you prevent SQL injection?** — Every query uses `%s` parameterized placeholders, values passed separately — never string-concatenated.
26. **What is Jinja2?** — Flask's default templating engine, auto-escapes variables by default.
27. **What is template inheritance, and how did you use it?** — `base.html` defines the shared layout; every page extends it and fills in its content block.
28. **What does `secure_filename()` do?** — Sanitizes a filename, stripping dangerous characters like path-traversal sequences.
29. **Where are uploaded resume files actually stored?** — Nowhere on disk — parsed entirely in memory (`io.BytesIO`), only the extracted results and sanitized filename are saved to MySQL.
30. **What is the maximum upload file size, and how is it enforced?** — 5MB, via Flask's `MAX_CONTENT_LENGTH` config; Werkzeug rejects larger files before the route even runs.
31. **What is the `/api/questions` endpoint?** — The one true JSON API — returns `{q, a}` pairs for a given role.
32. **How many job roles does your app support?** — 25 for prediction, but only 10 of those have curated interview questions.
33. **What happens when a user picks a role with no interview questions?** — The API returns `[]`, the UI shows "No questions available for this role yet."
34. **What is `flash()` used for?** — Queuing one-time messages that survive a redirect and display once.
35. **What is `render_template()`?** — Renders a Jinja2 template file with optional variables passed in.
36. **What are `redirect()` and `url_for()`?** — `redirect()` sends an HTTP redirect; `url_for()` generates a URL from a view function's name, avoiding hardcoded paths.

### INTERMEDIATE

37. **Walk me through what happens when a user uploads a resume.** — Form POST → validate file → `extract_text()` → `analyze_resume()` (predict role, score, extract skills, suggest skills) → `save_upload()` → re-render with results.
38. **Why did you separate `app/ml/data.py` from `app/ml/predict.py`?** — `data.py` is pure static data; `predict.py` is pure logic with zero Flask dependencies — separation of concerns, independently testable.
39. **Why does `predict.py` have no Flask imports?** — To keep analysis logic framework-agnostic — takes a string in, returns a dict out, reusable/testable outside a request context.
40. **What's a real limitation in your keyword-matching logic?** — Substring matching, not word-boundary matching — `"java"` matches inside `"javascript"`.
41. **Explain the duplicate key bug.** — `ROLE_KEYWORDS` defines `"Data Science"` twice; Python dict literals silently keep only the last occurrence, making the first block's keywords dead code.
42. **How would you fix the substring-matching problem?** — Replace `kw in text` with `re.search(r'\b' + re.escape(kw) + r'\b', text)` for word-boundary matching.
43. **Is `resume_score` capped at 100 by the database?** — No — the 7 point values are hand-designed to sum to 100 by construction in `compute_score()`, not enforced by a `CHECK` constraint.
44. **Explain the request-scoped database connection pattern.** — `get_db()` opens a connection stored on `flask.g` only if one doesn't exist; `close_db()` (via `teardown_appcontext`) closes it after every request, success or failure.
45. **Why didn't you use connection pooling?** — Simple/correct for low concurrent traffic; pooling is the first infrastructure upgrade needed before production load.
46. **How does `get_upload_stats()` compute dashboard numbers efficiently?** — One SQL query with `COUNT`/`MAX`/`AVG`, aggregated inside MySQL, not pulled into Python.
47. **Is there anywhere your code fetches too much data?** — Yes — `get_user_uploads(user_id)[:5]` fetches ALL uploads, then slices in Python; `LIMIT 5` in SQL would be correct.
48. **How do you scope data so users can't see each other's uploads?** — Every query filters `WHERE user_id = %s` using `session['user_id']` — never a client-supplied ID.
49. **What happens with a race condition on duplicate email registration?** — No `try/except` around the `INSERT` — a true race could raise an unhandled `IntegrityError` → 500 error.
50. **Why is the same error shown for wrong email vs. wrong password?** — To avoid "user enumeration" — not revealing which part of the credentials failed.
51. **Why is `/logout` a GET request a concern?** — State-changing actions conventionally use POST; GET-based logout is a mild CSRF surface (low impact here).
52. **Does your app have CSRF protection?** — No — no tokens on any form, no Flask-WTF. Would add `CSRFProtect`.
53. **Is your app vulnerable to XSS?** — Mostly no — Jinja2 auto-escapes. One caveat: `interview_prep.html`'s JS uses `innerHTML` with data from a hardcoded dictionary (low risk today, would matter if user-editable).
54. **How would you add rate limiting to prevent brute-force login?** — Flask-Limiter with a per-IP/per-email decorator on `/login`.
55. **Session-based auth vs. JWT — which did you use and why?** — Session cookies, because this is a same-origin server-rendered app, not a separate API client needing statelessness.
56. **How would you implement "forgot password"?** — A signed, time-limited token (via `itsdangerous`, already a Flask dependency) emailed to the user, verified on a reset page.
57. **How would you add email verification?** — An `is_verified` boolean column, a signed verification link, restrict login until clicked.
58. **Why is `login_required` defined in `main/routes.py` but used in `resume/routes.py` too?** — Cross-blueprint code reuse — the one deliberate coupling point in the codebase.
59. **Why is `analyze_resume()` the only function imported from `predict.py`?** — It's the deliberate public API — encapsulates internal composition so the web layer doesn't need to know how analysis works internally.
60. **Why does `clean_text()` preserve `/+#.`?** — Because keywords like `"c#"`, `".net"`, `"ci/cd"` rely on those characters to ever match.
61. **What's the difference between `compute_score()`'s and `predict_role()`'s text processing?** — `compute_score()` uses raw `.lower()`; `predict_role()`/`extract_skills()` run the fuller `clean_text()` (URL stripping, character filtering) — a minor inconsistency.
62. **How would you add pagination to `/history`?** — Add `limit`/`offset` params to `get_user_uploads()`, `LIMIT %s OFFSET %s` in SQL, read `?page=` in the route.
63. **What does `MAX_CONTENT_LENGTH` do?** — Makes Werkzeug reject any body larger than 5MB with a 413, before the route runs; no custom 413 handler exists.
64. **Why is checking only the file extension a weak validation?** — A renamed file could pass the extension check but fail parsing — low practical risk since files are never saved/executed, just parsed.
65. **What would you change about `upload()`'s success handling?** — Switch to Post/Redirect/Get instead of re-rendering directly, avoiding form-resubmission-on-refresh.
66. **How does your app avoid duplicate DB connections within one request?** — `get_db()` checks `g` before opening a new connection.
67. **Explain dark mode in your frontend.** — CSS custom properties under `[data-theme="dark"]`; JS toggles the attribute and persists to `localStorage`.
68. **How does interview-prep load questions without a full reload?** — `fetch('/api/questions?role=...')` on the dropdown's `change` event, then DOM built from the JSON response.
69. **Difference between `request.form` and `request.args`?** — `request.form` reads POST body fields; `request.args` reads URL query params (used by `get_questions()`).
70. **Where would you start adding unit tests?** — `app/ml/predict.py`'s pure functions — no Flask/DB dependency, trivial to test in isolation.
71. **How would you containerize this app with Docker?** — A `Dockerfile` on `python:3.12-slim`, `pip install -r requirements.txt`, run via gunicorn instead of the dev server.
72. **Why does `run.py` say "NEVER set debug=True in production"?** — Debug mode's interactive debugger can execute arbitrary code if reached by an attacker after an unhandled exception — a real RCE risk; it also leaks stack traces.

### ADVANCED

73. **If this app had to serve 1 million users, what would you change first?** — Connection pooling, add `LIMIT` to unbounded queries, move to gunicorn/uWSGI + load balancer (already stateless via cookie sessions), add composite indexes.
74. **Why is this app's session design "already scale-friendly"?** — All session state lives in the signed client cookie, not server memory — any instance behind a load balancer can serve any request, no sticky sessions needed.
75. **Would you introduce microservices? Why or why not?** — Not yet — the domain is small and the hot path is cheap. Only worth extracting the resume-analysis engine if it later needs dedicated infrastructure (e.g., GPU inference).
76. **How would you migrate this schema safely without a migration tool today?** — Introduce Alembic, write incremental migrations, use expand-contract for breaking changes.
77. **Give a scenario where the keyword algorithm gives a clearly wrong prediction.** — A Business Analyst resume heavy on "sql," "agile," "jira" (shared across multiple role lists) could tie with or beat a better semantic fit, since counting has no context awareness.
78. **How would you evolve this into a real ML classifier?** — Collect labeled resumes, use TF-IDF/embeddings + a classifier, but keep the rule-based system as an explainable fallback.
79. **What happens if MySQL is down when a request comes in?** — `get_db()`'s `connect()` raises, uncaught anywhere → Flask 500. No retry/circuit breaker exists.
80. **How would you rate-limit per-user instead of per-IP?** — Key Flask-Limiter on `session['user_id']` for authenticated routes; fall back to IP for `/login` (no session yet).
81. **If `resume_uploads` grew to 500 million rows, what breaks first?** — Un-indexed `ORDER BY upload_time` sorts become expensive; fix with a composite index `(user_id, upload_time DESC)` plus pagination everywhere.
82. **What's the risk of storing `user_name`/`user_email` in the session cookie?** — Signed but not encrypted — readable (not forgeable) by anyone with the cookie; a mild information-exposure concern.
83. **How would "delete my account" interact with the FK cascade?** — `DELETE FROM users WHERE id = %s` would automatically cascade-delete all of that user's `resume_uploads` rows.
84. **How would you introduce a read replica?** — Route read-only queries to the replica, keep writes on the primary; watch for replication lag on time-sensitive reads (though `upload()` renders from memory, so it's unaffected).
85. **What would a CI/CD pipeline look like, given none exists?** — Lint + test on push, build a Docker image, run integration tests against a test MySQL container, deploy on merge to main.
86. **How would you add structured logging/monitoring?** — Replace the single `print()` in `init_db()` with the `logging` module; prioritize logging failed logins, upload failures, and slow queries.
87. **Prove there's no SQL injection risk, using your actual code.** — Every query uses `%s` placeholders with values passed as a separate tuple — never string-interpolated SQL.
88. **How would you redesign the never-implemented `predictions` table?** — A separate table with `upload_id` FK, `role`, `keyword_score`, `created_at` — decoupling the upload event from a specific prediction run.
89. **What testing strategy for the keyword engine specifically?** — Table-driven tests: (resume_text, expected_role) pairs, boundary cases, a regression test asserting `len(ROLE_KEYWORDS) == 25`.
90. **How would you handle i18n for non-English resumes?** — Technical keywords mostly transfer as-is; structural section-heading checks (education/experience/skill) would need language-specific keyword sets.
91. **When would you switch from inline analysis to a background job?** — Only if analysis became slow/unreliable (OCR, external ML API) — inline is correct today since keyword matching is fast.
92. **What would the full Google OAuth flow look like if implemented?** — Register in Google Cloud Console, add `/login/google` + `/login/google/callback`, exchange the auth code via `requests` (already an unused dependency), add a `google_id` column, leave `password_hash` nullable (already the case).
93. **How would you avoid leaking internal error details in `upload()`'s exception handler?** — Log the full exception server-side; show a generic safe message instead of `str(e)`.
94. **A load test shows `/dashboard` is slowest under load — how do you diagnose it?** — Profile the three DB calls first; likely `get_user_uploads` (no `LIMIT`); fix with a proper `LIMIT 5` query; also check pooling overhead.
95. **Why might `MAX(predicted_role)` in `get_upload_stats()` be semantically wrong?** — It returns the alphabetically largest role string, not necessarily the most recent one — `MAX()` per column is independent, no row-level guarantee.
96. **How would you support a manually-chosen target role instead of only the auto-predicted one?** — Add an optional `target_role` form field; `extract_skills()` already accepts any role generically, so no signature change needed.
97. **What single change most improves trustworthiness without changing the algorithm?** — Surface the already-computed `_scores` dict (currently discarded) to show which keywords drove the prediction.
98. **Top 5 changes for production-grade in one sprint?** — (1) CSRF protection, (2) connection pooling + missing `LIMIT`s, (3) gunicorn + Dockerfile, (4) structured logging + health check, (5) a pytest suite starting with `predict.py`.
99. **Is zero automated tests actually a problem at this scale?** — A reasonable trade-off for a solo student project, but the duplicate-key bug is proof it becomes a real problem the moment complexity or contributors grow.
100. **If an interviewer says "this isn't AI, it's just `if` statements" — how do you respond?** — Agree calmly: it's a keyword-counting rule engine, chosen deliberately for full explainability, not disguised as ML.

---

## 14. Cross Questions

Realistic follow-up chains — practice going down each one out loud.

### Chain 1: Framework Choice
```
Why Flask?
   ↓ "Lightweight — I only needed routing, templating, and sessions."
Why not Django, since it gives you all that for free?
   ↓ "Django's ORM/admin/CSRF come with conventions I'd have to adopt —
      more structure than a 2-table, 10-route app needed."
Why not FastAPI — isn't it faster and more modern?
   ↓ "FastAPI is async-first, built around typed JSON APIs — this app is
      server-rendered HTML, exactly Flask's use case."
So what are the actual trade-offs?
   ↓ "Flask = flexibility, more decisions (and more risk of skipping
      something, like CSRF, which I did). Django = safer defaults, less
      flexible. FastAPI = best for async JSON APIs, not HTML rendering."
Given you skipped CSRF, doesn't that prove Django would've been safer?
   ↓ "Fair — Django's forms include CSRF tokens by default. My choice
      traded default safety for flexibility, and CSRF is exactly what
      that trade-off cost me. I'd add Flask-WTF to close the gap."
```
**Lesson**: don't defend your original choice reflexively — acknowledge a fair critique honestly.

### Chain 2: The "AI" Claim
```
Is this AI?
   ↓ "No — rule-based keyword counting, not a trained model."
Then why call it "AI-Powered" in the README?
   ↓ "That's marketing language on the landing page — in a technical
      discussion I'd always describe it accurately as rule-based. Fair
      critique of the marketing copy, not the engineering."
What would you need to add to honestly call it AI?
   ↓ "A model trained on labeled data — e.g. TF-IDF + logistic regression,
      or embeddings + a classifier."
Would you actually replace the current system with that?
   ↓ "Not replace — augment. Keep the rule-based system as an explainable
      baseline/fallback, since losing explainability is a real cost."
How would you measure whether the learned model outperforms the rule-based one?
   ↓ "Same labeled test set, compare accuracy side by side, inspect
      disagreements specifically."
```
**Lesson**: agree with any fair critique immediately, then pivot to the deliberate reasoning behind the choice.

### Chain 3: Database Choice
```
Why MySQL and not MongoDB?
   ↓ "Data is relational — one-to-many, and I need aggregates like AVG."
Couldn't you embed uploads as an array in the user document?
   ↓ "Yes, technically — but updating/aggregating over a growing embedded
      array is awkward vs. a SQL JOIN/aggregate, and I'd lose the
      DB-enforced FK cascade."
Why not PostgreSQL instead, since it has more advanced SQL features?
   ↓ "Functionally equivalent for this schema — I don't use any
      Postgres-specific feature. MySQL is just more commonly taught in
      the environment I built this in."
If you needed a flexible JSON field later, how would you add that in MySQL?
   ↓ "MySQL has a native JSON column type since 5.7 — no need to switch
      databases at all."
```
**Lesson**: know your stack's escape hatches before assuming you'd need to switch technology entirely.

### Chain 4: No ORM
```
Why no ORM like SQLAlchemy?
   ↓ "Two tables, a handful of queries — raw SQL is easier to read and
      explain end-to-end."
Won't that become unmaintainable as the schema grows?
   ↓ "Yes — explicitly a small-scale trade-off. Past ~5 more tables I'd
      introduce SQLAlchemy, both for Alembic migrations and to avoid
      hand-written JOINs."
How do you currently handle schema changes without a migration tool?
   ↓ "Honestly, I don't — init_db() only does CREATE TABLE IF NOT EXISTS,
      fine for a fresh DB, not for altering a populated one safely."
Walk me through how Alembic would solve that.
   ↓ "Alembic tracks schema versions as incremental scripts with
      upgrade()/downgrade() functions, applied via `alembic upgrade head`,
      tracked in a version table — unlike my current approach which has
      no concept of versions at all."
```
**Lesson**: "I don't have a real answer for X today, here's what I'd add" is often a better answer than pretending a solution exists.

### Chain 5: Passwords & Session Security
```
How are passwords stored?
   ↓ "Hashed with Werkzeug's generate_password_hash(), scrypt-based,
      never plaintext."
Why scrypt over bcrypt?
   ↓ "I didn't choose it explicitly — it's Werkzeug's current default.
      Both are memory-hard, brute-force-resistant; the key property
      either way is slow, salted hashing."
What's stored in the session — safe if the cookie is stolen?
   ↓ "user_id, user_name, user_email — signed (can't be tampered with)
      but not encrypted (readable in plaintext by anyone with the
      cookie)."
What's the actual worst-case impact of a stolen cookie?
   ↓ "The attacker could act as that user for the cookie's lifetime —
      upload resumes, view history. No destructive action is gated only
      by session (no account deletion exists), so impact is bounded to
      impersonating activity, not full account takeover."
How would you reduce that impact further?
   ↓ "Explicit SESSION_COOKIE_SECURE=True once on HTTPS, a session
      expiry, re-authentication before any future sensitive action."
```
**Lesson**: security follow-ups reward reasoning about actual blast radius, not vague alarm.

### Chain 6: Keyword-Matching Weaknesses
```
How does role prediction work?
   ↓ "Count keyword matches per role, highest count wins."
What's a concrete failure case?
   ↓ "'java' matches as a substring inside 'javascript' — a JS resume
      could get a false-positive point toward Java Developer."
How would you actually fix that in code?
   ↓ "Switch from `kw in text` to word-boundary regex:
      re.search(r'\bjava\b', text)."
Would that fix introduce new problems?
   ↓ "Some keywords contain regex special characters — 'c#', '.net',
      'ci/cd' — I'd need re.escape() around each keyword first."
Are there keywords in your actual data that would hit that exact problem?
   ↓ "Yes — 'c#' and '.net' under DotNet Developer, 'ci/cd' under DevOps
      Engineer and Automation Testing — re.escape() would be required,
      not optional, for the fix to work."
```
**Lesson**: naming the *specific* keywords in your *actual* data proves you read the code, not just described the algorithm abstractly.

### Chain 7: "What Would You Improve" (Generic Closer)
```
What would you improve with another week?
   ↓ "Fix the duplicate 'Data Science' key, add CSRF protection, add
      LIMIT to the unbounded history query — highest-impact,
      lowest-effort."
With another month instead?
   ↓ "A real test suite starting with predict.py's pure functions,
      word-boundary matching, interview Q&A for the remaining 15 roles,
      connection pooling."
With another year and a full team?
   ↓ "Evolve toward a hybrid explainable ML model, OCR for scanned PDFs,
      Alembic migrations, containerize + deploy behind a load balancer
      with monitoring, account management features."
```
**Lesson**: the week/month/year structure shows prioritization at every timescale instead of one flat wishlist.

---

## 15. Challenges Faced

All challenges below are grounded in the actual implementation — nothing invented.

### Challenge 1: Substring Keyword Matching Produces False Positives
- **Problem**: `predict_role()` and `extract_skills()` both check `kw in cleaned_text` — plain substring search. `"java"` matches inside `"javascript"`; `"skill"` matches inside `"upskill"`.
- **Root cause**: the simplest possible "does this keyword appear" implementation is substring search, not word-boundary matching.
- **Solution**: use regex with word boundaries, e.g. `re.search(r'\b' + re.escape(kw) + r'\b', text)`.
- **Learning**: "simple" and "correct" aren't the same — naive matching can look fine in demos while silently being wrong in edge cases.

### Challenge 2: Duplicate Dictionary Key Silently Overwrites Data
- **Problem**: `ROLE_KEYWORDS` defines `"Data Science"` twice in `app/ml/data.py` — Python dict literals silently keep only the last assignment.
- **Root cause**: likely a copy-paste/merge mistake while iteratively adding roles; Python doesn't error on duplicate literal keys.
- **Solution**: merge both keyword lists into one canonical entry; add a startup assertion like `len(ROLE_KEYWORDS) == 25`.
- **Learning**: shows the value of static analysis / linting (e.g., pylint's duplicate-key check) or a simple unit test.

### Challenge 3: Scanned/Image-Only PDFs Produce No Extractable Text
- **Problem**: `PyPDF2` can only read actual text objects, not text baked into an image.
- **Root cause**: a fundamental library limitation, not a bug.
- **Solution implemented today**: the app detects empty extraction and flashes a clear message rather than silently returning a wrong analysis. A deeper fix would add OCR (`pytesseract` + `pdf2image`).
- **Learning**: good defensive coding sometimes means "detect the failure clearly and tell the user" as the first step, before deciding whether the deeper fix is worth the added complexity.

### Challenge 4: `.docx` Table Content Is Never Extracted
- **Problem**: `extract_text()`'s DOCX branch only reads `doc.paragraphs` — content inside Word tables (common in two-column resumes) is invisible.
- **Root cause**: `python-docx`'s simplest API doesn't recurse into tables by default.
- **Solution**: extend `extract_text()` to also loop `doc.tables`.
- **Learning**: library "simple/obvious" methods often cover the common case but silently miss valid document structures.

### Challenge 5: No Database Connection Pooling
- **Problem**: `get_db()` opens a brand-new connection per request.
- **Root cause**: the simplest correct pattern for a small app, chosen for clarity over performance.
- **Solution**: `mysql.connector.pooling.MySQLConnectionPool`, or move to SQLAlchemy's pooled engine.
- **Learning**: the right complexity level depends on scale — pooling would be premature for a handful of users, but it's the first infrastructure change needed before production traffic.

### Challenge 6: Comment/Docstring Drift From Actual Implementation
- **Problem**: `app/models.py`'s docstring mentions a `predictions` table that's never created; `app/auth/routes.py`'s docstring mentions `/login/google` routes that don't exist.
- **Root cause**: likely planned features documented while designing, then descoped before shipping.
- **Solution**: either implement the missing pieces or update the docstrings to match reality.
- **Learning**: stale comments actively mislead the next reader — spotting and naming this drift proactively is a strong signal of code-reading discipline.

### Challenge 7: `/upload`'s POST Handler Re-renders Instead of Redirecting
- **Problem**: a successful upload re-renders `upload.html` directly rather than using Post/Redirect/Get, risking form-resubmission warnings on refresh.
- **Root cause**: simplest way to pass the `results` dict to the template without inventing a redirect-then-refetch mechanism.
- **Solution**: redirect to `/upload/results/<upload_id>` after `save_upload()`, re-querying and rendering by ID.
- **Learning**: a good example of a small UX rough edge that doesn't affect correctness but comes up in "how would you improve this."

---

## 16. Improvements

### If Given Another Month

**Optimization**
- Add composite index `(user_id, upload_time DESC)` on `resume_uploads`.
- Push the "recent 5 uploads" `LIMIT` into SQL instead of Python-slicing.
- Add short-TTL caching (Redis) for dashboard aggregate stats.

**Performance**
- Introduce connection pooling.
- Serve static assets via a CDN.
- Self-host Font Awesome/Google Fonts to remove the external CDN round-trip.

**Maintainability**
- Add a test suite — start with `app/ml/predict.py`'s pure functions.
- Fix the duplicate `"Data Science"` key; add a regression assertion guarding against it.
- Reconcile docstrings with actual implemented routes/tables.
- Add type hints across `app/ml/predict.py` and `app/models.py`.
- Introduce Alembic instead of `CREATE TABLE IF NOT EXISTS`.

**Feature-level**
- Fill in `INTERVIEW_QUESTIONS` for the remaining 15 of 25 roles.
- Add word-boundary-aware keyword matching.
- Add "forgot password" and email verification flows.
- Add pagination to `/history`.
- Add CSRF protection (Flask-WTF) and rate limiting (Flask-Limiter).
- Surface the discarded `_scores` dict in `predict_role()` so users can see *why* a role was predicted.

### Why Each Improvement Matters
Each change above directly closes a gap documented elsewhere in this guide (Sections 15, 18, 20) — they are not speculative wishlist items, they are the concrete, named fixes for concrete, named problems found by reading the actual code.

---

## 17. Scalability

This is a forward-looking design discussion, clearly separated from what's actually implemented today (Section 4).

### Current Bottlenecks
1. **One MySQL connection opened per request** (`get_db()`) — no pooling. At high concurrency this would exhaust MySQL's `max_connections`.
2. **`get_user_uploads()` has no `LIMIT`** — both `/history` and the dashboard's "recent 5" fetch the entire upload history every time.
3. **Synchronous, in-request resume analysis** — fine today because keyword matching is fast, but would block requests if analysis ever got heavier (OCR, a real ML model).
4. **No caching layer** — dashboard stats are recomputed from scratch on every request.
5. **Single Flask process, single server** — `app.run(debug=True)` cannot handle concurrent load or multiple workers.
6. **No CDN** — static assets served directly by the app.
7. **No read replicas / no horizontal DB scaling.**

### Improvements, in Priority Order

**1. Caching** — Redis-backed short-TTL cache for dashboard stats. Static role/keyword data (`app/ml/data.py`) is already effectively cached as in-process Python constants — no need to move it to Redis.

**2. Database Scaling**
- Composite index `(user_id, upload_time DESC)`.
- Connection pooling (`mysql.connector.pooling.MySQLConnectionPool`).
- Read replicas for read-heavy dashboard/history queries, writes stay on the primary.
- Pagination (`LIMIT`/`OFFSET` or keyset pagination) on `get_user_uploads()`.
- A real migration tool (Alembic) instead of `CREATE TABLE IF NOT EXISTS`.

**3. Load Balancing** — Multiple stateless Flask instances (gunicorn/uWSGI workers) behind a load balancer. Straightforward because session state lives entirely in the signed client cookie, not server memory — **no sticky sessions needed**. This is a genuine existing architectural strength.

**4. Async Jobs / Queues** — If analysis ever became slow (OCR, external ML API), move to Celery + Redis/RabbitMQ: enqueue on upload, respond immediately, worker processes the job, result written back once ready. Premature today given millisecond-fast keyword matching.

**5. CDN** — Serve `static/css/style.css`, `static/js/main.js`, and images from CloudFront/Cloudflare instead of the app server.

**6. Horizontal Scaling** — Containerize (add a `Dockerfile`, currently missing), put behind a load balancer, point every instance at the same MySQL host.

**7. Microservices** — Not yet, and maybe never fully — the domain is small and the compute-heavy path is cheap. The only plausible future service boundary is the resume-analysis engine itself, if it ever needed dedicated hardware.

**8. Monitoring & Logging** — Currently **zero structured logging** (only one `print()` in `init_db()`). Add Python's `logging` module (JSON output), an APM tool (or Prometheus + Grafana), centralized log aggregation, and alerting.

**9. Cloud Improvements** — Managed MySQL (RDS/Cloud SQL) for backups/failover, managed secrets (AWS Secrets Manager) instead of `.env`, auto-scaling app tier, S3 if resume files were ever persisted.

### What Would NOT Need to Change
- The **relational schema** is already well-normalized and would scale fine with proper indexing.
- The **stateless session design** is already scale-friendly.
- The **keyword-matching engine** is computationally trivial and stays fast at any request volume — the bottleneck at scale is infrastructure, not this logic.

---

## 18. Security Analysis

An honest audit — what is and isn't implemented, based only on the code.

### SQL Injection
**Not vulnerable.** Every SQL statement in `app/models.py` uses `%s` placeholders with values passed as a separate tuple to `cursor.execute()` — the correct parameterized-query defense. No string concatenation or f-string-built SQL exists anywhere.

### XSS (Cross-Site Scripting)
**Mostly protected.** Jinja2 auto-escapes all `{{ }}` output by default. **One caveat**: `templates/interview_prep.html`'s inline JS builds question cards using `innerHTML` from JSON data — bypassing Jinja's escaping. Risk is low today because the data source (`INTERVIEW_QUESTIONS`) is a hardcoded dictionary, not user input — but the *pattern* would become dangerous if that data source ever became user-editable.

### CSRF (Cross-Site Request Forgery)
**Not implemented.** No CSRF token on any form (`login.html`, `register.html`, `upload.html`), no Flask-WTF. Practical impact is low today (no destructive actions exposed), but this is a real, fixable gap — add Flask-WTF's `CSRFProtect`.

### Authentication
**Implemented**: email + password via Flask sessions. **Not implemented**: email verification, "forgot password," MFA, account lockout, Google OAuth (despite `.env.example` placeholders).

### Authorization
**Implemented**: `login_required` decorator on protected routes; every data query is scoped to `session['user_id']`. **Not implemented**: only one user role exists (no admin distinction); no explicit object-ownership check exists, though none is currently needed since no route accepts a client-supplied upload ID.

### Input Validation
**Implemented**: non-empty field checks, password confirmation/length, duplicate-email check, file extension allow-list, file-size cap. **Gaps**: no server-side email format validation beyond HTML5 `type="email"`; no custom 413 error page; `allowed_file()` checks extension only, not actual MIME type.

### Secrets Management
**Implemented correctly for local dev**: `SECRET_KEY` and MySQL credentials read from environment variables via `python-dotenv`; `.env` is gitignored; `.env.example` documents required keys without real values. **Gap for production**: no integration with a real secrets manager.

### HTTPS
**Not configured anywhere** — no Flask-Talisman, no HSTS, no redirect-to-HTTPS. The app runs via `app.run(debug=True)`, which doesn't support TLS termination itself.

### Password Storage
**Correct**: `werkzeug.security.generate_password_hash()` (scrypt), `check_password_hash()` at login. Never stored/logged in plaintext. **Gap**: minimum length is only 6 characters, no complexity requirement.

### Summary Table
| Control | Status | Notes |
|---|---|---|
| Password hashing | ✅ Implemented | Werkzeug scrypt |
| SQL injection defense | ✅ Implemented | Parameterized queries throughout |
| XSS defense (server-rendered) | ✅ Implemented | Jinja2 auto-escaping |
| XSS defense (client-side JS) | ⚠️ Partial | `innerHTML` in interview-prep JS, low risk (static data source) |
| File upload validation | ⚠️ Partial | Extension allow-list + size cap; no MIME sniffing |
| Login rate limiting | ❌ Missing | No brute-force protection |
| CSRF protection | ❌ Missing | No tokens on any form |
| Email verification | ❌ Missing | Registration = instant login |
| HTTPS enforcement | ❌ Missing | No config in this codebase |
| Secure cookie flags | ⚠️ Partial | Flask defaults only, not explicitly hardened |
| Secrets in env vars | ✅ Implemented | `.env` + `python-dotenv` |
| Authorization (data scoping) | ✅ Implemented | All queries scoped to `session['user_id']` |
| Google OAuth | ❌ Not implemented | Env vars exist, no route code |

**How to talk about this in an interview**: don't hide the gaps — naming them accurately and explaining the fix demonstrates more engineering maturity than pretending everything is already secure.

---

## 19. Resume Questions

If your resume has a line like *"Built JobCatch — a Flask-based resume analysis platform with MySQL, achieving resume scoring and 25-role prediction,"* expect questions like these.

### Project Scope & Ownership
1. **Did you build this alone?** — Yes, solo project.
2. **What was the hardest part to build?** — Reliable text extraction across PDF and DOCX, and designing a scoring rubric without a labeled dataset to validate against.
3. **What would you do differently if you started over?** — Add tests from day one — the duplicate `"Data Science"` key would have been caught immediately.
4. **Is this project deployed anywhere live?** — No — no Dockerfile, no cloud config; runs only via `python run.py` locally.

### Architecture & Design Decisions
5. **Why blueprints?** — To separate auth, main pages, and resume features into independently readable modules.
6. **What is the Application Factory pattern and why use it?** — `create_app()` builds the app on demand, supporting different configs without import-time side effects.
7. **Why no ORM?** — Two tables, simple queries — raw SQL kept everything transparent for a project this size.
8. **How is your code organized?** — Feature-folder blueprints (`auth/`, `main/`, `resume/`) plus shared layers `models.py` (data access) and `ml/` (business logic).
9. **What design pattern does `login_required` use?** — The decorator pattern, using `functools.wraps` to preserve the wrapped function's identity for Flask's routing.

### The Core "AI" Feature
10. **Explain your resume-matching algorithm.** — Keyword counting against a 25-role dictionary; highest count wins; `"General / Other"` fallback.
11. **Is this real machine learning?** — No — rule-based and 100% explainable, a deliberate choice.
12. **How accurate is your prediction algorithm?** — Never formally measured against a labeled dataset — no accuracy metric currently exists.
13. **What's a known weakness of your algorithm?** — Substring matching causes false positives (`"java"` inside `"javascript"`).
14. **How many roles do you support, and how were they chosen?** — 25, covering a broad mix of tech and non-tech careers.
15. **Why only 10 of 25 roles have interview questions?** — Time constraints during development — an intentionally incomplete content set, handled gracefully.
16. **How do you score a resume?** — Seven weighted structural checks summing to 100.
17. **Could someone game your scoring system?** — Yes — since checks are substring/regex based, padding a resume with trigger words could inflate the score without real substance.

### Database
18. **What database did you use and why?** — MySQL, for its relational fit.
19. **Describe your schema.** — Two tables, `users` and `resume_uploads`, linked by an FK with `ON DELETE CASCADE`.
20. **How do you prevent SQL injection?** — Parameterized `%s` queries everywhere.
21. **How do you manage the DB connection lifecycle?** — Request-scoped via Flask's `g`, closed via `teardown_appcontext`.
22. **Do you use migrations?** — No — `CREATE TABLE IF NOT EXISTS` only.
23. **What indexes exist?** — Primary keys, a unique index on `email`, an implicit FK index on `user_id`. No explicit index on `upload_time`.

### Authentication & Security
24. **How do you handle authentication?** — Session-based, Werkzeug-hashed passwords, a custom `login_required` decorator.
25. **Do you use JWT?** — No — session cookies, appropriate for a same-origin server-rendered app.
26. **Is there CSRF protection?** — No, a known gap — would add Flask-WTF.
27. **How are passwords stored?** — Hashed (scrypt), never plaintext.
28. **What happens on failed login?** — A generic error, deliberately not revealing which part was wrong.
29. **Is there rate limiting on login?** — No — a real gap, would close with Flask-Limiter.

### File Handling
30. **How do you handle file uploads?** — In-memory only, never saved to disk, parsed via PyPDF2/python-docx and discarded.
31. **What file types and size limits?** — PDF and DOCX, up to 5MB.
32. **What happens with a scanned/image-only PDF?** — No extractable text (no OCR) — a clear flash message, not a broken result.

### Testing & Quality
33. **Do you have automated tests?** — No, honestly — a real gap; would start with `app/ml/predict.py`'s pure functions.
34. **What's a bug you found reviewing your own code?** — The duplicate `"Data Science"` key in `ROLE_KEYWORDS`.
35. **How would you catch that bug automatically going forward?** — A test asserting `len(ROLE_KEYWORDS) == 25`.

### Frontend
36. **What frontend framework did you use?** — None — vanilla HTML/CSS/JS with Jinja2, deliberately, given small interactivity needs.
37. **How does dark mode work?** — CSS custom properties toggled via `data-theme`, persisted in `localStorage`.

### Scalability & Deployment
38. **Is this deployed anywhere?** — No — local development only.
39. **How would you deploy this to production?** — Gunicorn behind Nginx, managed MySQL, environment-based secrets, HTTPS at the proxy layer.
40. **What's the biggest performance bottleneck today?** — No connection pooling, and an unbounded `get_user_uploads()` query.

### Honesty / Self-Awareness Checks
41. **What does your README claim that isn't fully true in the code?** — Google OAuth and a `predictions` table are referenced but not implemented.
42. **What's the single thing you're least confident about?** — The scoring rubric's point values were chosen by intuition, never validated against real recruiter judgments.
43. **If I opened your code right now, what would embarrass you first?** — The lack of tests, and the duplicate dictionary key — both found by re-reading my own code, not by an external reviewer.
44. **Would you put this project on your resume again, knowing its gaps?** — Yes — it demonstrates full-stack fundamentals end-to-end, and discussing its real limitations honestly is itself valuable interview material.
45. **What did you learn building this you'd apply to your next project?** — The value of writing tests alongside features, not after — and how much a small data bug can silently change behavior with no error raised.

---

## 20. Weak Areas

Topics ranked by how likely they are to expose a shallow understanding if you didn't build this project yourself.

### Tier 1 — Non-Negotiable
1. **The keyword-matching algorithm, including its flaws** — the exact flow, the substring false-positive problem, the duplicate `"Data Science"` key. Being able to name a specific, real flaw unprompted is one of the highest-signal things you can do.
2. **"Is this AI?" — the honesty question** — say "no, it's rule-based" plainly and immediately, then pivot to why that was a deliberate, defensible choice. Getting defensive here is the single most damaging response possible.
3. **SQL injection defense** — point at actual code (`%s` placeholders), don't just recite the concept.
4. **Password hashing, not encryption** — confusing these two is an instant red flag.
5. **What is and isn't actually implemented** — the `predictions` table, Google OAuth, CSRF, tests, Docker — all missing. Confidently stating what's missing is more impressive than vaguely implying everything works.

### Tier 2 — Very Likely to Come Up
6. **Session management: signed vs. encrypted** — a subtle distinction, easy to get backwards under pressure.
7. **The request lifecycle and `flask.g`** — `get_db()`/`close_db()` and why teardown functions guarantee cleanup even on exceptions.
8. **CSRF: what it is, and why this app lacks it.**
9. **Why files are never saved to disk** — know it as a deliberate architectural strength, not just a passing fact.
10. **The two-table schema and the FK cascade** — foundational to every data question.

### Tier 3 — Good to Have Ready
11. **Scalability priorities, in order** — connection pooling and missing `LIMIT`s before load balancers/microservices.
12. **Why no tests exist, and what you'd test first.**
13. **The one cross-blueprint coupling (`login_required`).**
14. **The `MAX(predicted_role)` subtlety** in `get_upload_stats()` — a genuinely subtle correctness issue.
15. **Comment/docstring drift as a concept** — you have two concrete examples ready.

### How to Use This
Read Tier 1 the night before, out loud, without notes. Skim Tier 2 the morning of. Keep Tier 3 as a mental reserve — you don't need to lead with it, but never be caught not knowing it if asked directly.

---

## 21. One-Day Revision Notes

*(Read in about 20 minutes.)*

**What Is JobCatch?** A Flask app: upload a resume (PDF/DOCX) → get a predicted job role (out of 25), a resume quality score (0–100), found/missing skills, and suggested skills. Also has login/register, upload history, a dashboard, and an interview-prep Q&A page (10 of 25 roles have questions).

**Tech Stack (one line each)**
- Python 3 + Flask 3.0.2 — app factory pattern (`create_app()`).
- MySQL + `mysql-connector-python` — raw SQL, no ORM, two tables.
- Werkzeug — password hashing (scrypt) and `secure_filename()`.
- PyPDF2 / python-docx — text extraction, entirely in-memory.
- Jinja2 — server-rendered templates, auto-escapes output.
- Vanilla CSS/JS — no framework; dark mode via `data-theme` + `localStorage`.
- `python-dotenv` — loads `.env` for config.
- `requests` — listed but **unused anywhere in the code**.

**Architecture**
```
Browser → Flask (auth_bp, main_bp, resume_bp) → app/models.py (raw SQL) → MySQL
                                                → app/ml/predict.py + data.py (keyword engine)
```
No microservices, no ORM, no queue, no Docker, no deployment config.

**The Three Blueprints**
| Blueprint | Routes |
|---|---|
| `auth_bp` | `/register`, `/login`, `/logout` |
| `main_bp` | `/`, `/dashboard` (protected), `/contact` |
| `resume_bp` | `/upload` (protected), `/history` (protected), `/interview-prep`, `/api/questions` |

**The Two Database Tables**
```
users(id PK, name, email UNIQUE, password_hash, created_at)
resume_uploads(id PK, user_id FK→users.id ON DELETE CASCADE,
                filename, upload_time, predicted_role, resume_score)
```
No `predictions` table despite a stale docstring.

**The Core Algorithm**
```
resume_text → clean_text() [strip URLs, keep a-z0-9/+#., lowercase]
           → predict_role(): count keyword hits per role (25 roles) → argmax
                              → "General / Other" if all zero
           → compute_score(): 7 checks (email 15, phone 15, skills 20,
                              education 15, experience 15, 250+ words 10,
                              projects 10) = 100 max
           → extract_skills(): found vs missing keywords for predicted role
           → get_suggested_skills(): static list per role
           → analyze_resume() composes all of the above into one dict
```

**Known Bugs / Gaps (say these proactively — they build trust)**
1. Duplicate `"Data Science"` key in `ROLE_KEYWORDS` — second silently wins.
2. Substring matching, not word-boundary — "java" matches inside "javascript."
3. No `predictions` table despite a stale docstring.
4. No Google OAuth despite `.env.example` placeholders.
5. No CSRF protection on any form.
6. No rate limiting on login.
7. No connection pooling.
8. No `LIMIT` on `get_user_uploads()`.
9. No tests, no Docker, no CI/CD, no migrations.
10. `MAX(predicted_role)` returns the alphabetically largest role, not necessarily the most recent.
11. Only 10 of 25 roles have interview questions.
12. `.docx` tables aren't read — only paragraphs.
13. Scanned/image PDFs produce no text (handled gracefully, not a crash).
14. `/logout` is a GET request — a minor CSRF surface.
15. `/contact` passes `scroll_to='contact'` but the template never uses it — dead parameter.

**Security Cheat Facts**
- Passwords: hashed (scrypt), never plaintext, never "decrypted."
- SQL: 100% parameterized — no injection risk found.
- XSS: Jinja2 auto-escapes; one `innerHTML` caveat in interview-prep JS (low risk).
- Sessions: signed, not encrypted — readable but not forgeable without `SECRET_KEY`.
- Files: never written to disk.
- Missing: CSRF tokens, rate limiting, HTTPS config, hardened cookie flags, email verification.

**Scalability — Fix in This Order**
1. Connection pooling.
2. `LIMIT` + composite index on upload queries.
3. Gunicorn/uWSGI + load balancer (already stateless).
4. Redis caching for dashboard stats.
5. Read replicas / Alembic migrations / CDN — only once the above is done and still insufficient.

**Your 30-Second Pitch**
"JobCatch is a Flask app where you upload a resume and it instantly predicts your best-fit job role out of 25 categories, scores your resume out of 100, and shows what skills you have versus what's missing. The matching engine isn't a black-box AI model — it's a transparent keyword-counting algorithm, so I can explain exactly why it made every prediction."

**If Asked "Is This AI?"**
Say **no**, immediately and calmly: "It's rule-based keyword counting, not a trained model — a deliberate choice for full explainability." This is a trust test, not a technical test.

**The One Sentence to Start Any Code Walkthrough With**
"Start with `app/__init__.py`'s `create_app()` function — it names every other important file in the project in about 30 lines."

**Last-Minute Confidence Boosters (what you did right)**
- Files are never saved to disk — a real, deliberate security strength.
- Aggregate stats computed in one SQL query, not pulled into Python.
- Every SQL query is parameterized — zero injection risk.
- `predict.py` has zero Flask dependencies — clean separation of business logic from web framework.
- Unmatched resumes fall back to `"General / Other"` instead of forcing a wrong guess.

---

## 22. Cheat Sheet

### Project Summary
Flask app: upload resume (PDF/DOCX) → predicts 1 of 25 job roles via keyword counting → scores resume 0–100 (7 checks) → shows found/missing skills → suggests next skills → saves to MySQL → dashboard/history tracks it over time → separate interview-prep page (10/25 roles have Q&A).

### Architecture
```
Browser → Flask (auth_bp, main_bp, resume_bp) → app/models.py (raw SQL) → MySQL
                                               → app/ml/{data,predict}.py (keyword engine)
```
App Factory pattern. No ORM. No microservices. No Docker. Dev server only (`python run.py`).

### Tech Stack
| Layer | Tech |
|---|---|
| Backend | Python 3, Flask 3.0.2, Werkzeug |
| DB | MySQL, `mysql-connector-python` (raw SQL) |
| File parsing | PyPDF2 (PDF), python-docx (DOCX) |
| Templates | Jinja2 |
| Frontend | Vanilla HTML/CSS/JS, no framework |
| Config | `python-dotenv` + `.env` |
| Auth | Session cookies + Werkzeug password hashing (scrypt) |

### Database
```
users(id PK, name, email UNIQUE, password_hash, created_at)
   │ 1:N (ON DELETE CASCADE)
resume_uploads(id PK, user_id FK, filename, upload_time,
                predicted_role, resume_score)
```
No `predictions` table (stale docstring). No migrations. No explicit index on `upload_time`.

### APIs
| Method | Path | Auth | Returns |
|---|---|---|---|
| GET/POST | `/register`, `/login` | No | HTML |
| GET | `/logout` | No | Redirect |
| GET | `/dashboard` | Yes | HTML |
| GET/POST | `/upload` | Yes | HTML |
| GET | `/history` | Yes | HTML |
| GET | `/interview-prep` | No | HTML |
| GET | `/api/questions?role=` | No | **JSON** (only real API) |

### Authentication
- Register/Login → `werkzeug.security` scrypt hash → Flask session (`user_id`, `user_name`, `user_email`), signed not encrypted.
- `login_required` decorator (in `main/routes.py`, reused in `resume/routes.py`) guards `/dashboard`, `/upload`, `/history`.
- No JWT, no OAuth (despite env var placeholders), no CSRF, no rate limiting.

### Major Features & Core Functions
| Feature | Function | File |
|---|---|---|
| Role prediction | `predict_role()` | `app/ml/predict.py` |
| Resume scoring | `compute_score()` | `app/ml/predict.py` |
| Skill gap | `extract_skills()` | `app/ml/predict.py` |
| Suggested skills | `get_suggested_skills()` | `app/ml/predict.py` |
| Orchestrator | `analyze_resume()` | `app/ml/predict.py` |
| Text extraction | `extract_text()` | `app/resume/routes.py` |
| DB connection | `get_db()`/`close_db()` | `app/models.py` |

### Algorithm (Memorize)
```
clean_text() → strip URLs, keep [a-z0-9/+#.], lowercase
predict_role() → count keyword hits per role (25 roles) → argmax
                  → "General / Other" if all 0
compute_score() → 7 checks: email(15) phone(15) skills(20) education(15)
                   experience(15) 250+words(10) projects(10) = 100 max
extract_skills() → found vs missing keywords for predicted role
```

### Challenges (Real Bugs You Can Cite)
- Duplicate `"Data Science"` key in `ROLE_KEYWORDS` → second silently wins.
- Substring matching → "java" false-positives inside "javascript".
- `MAX(predicted_role)` in `get_upload_stats()` ≠ most recent role.
- `get_user_uploads()` has no `LIMIT` — dashboard over-fetches then slices `[:5]`.
- Only 10/25 roles have interview questions.
- `.docx` tables not read (only paragraphs).
- No OCR for scanned PDFs (handled gracefully with a flash message).

### Scalability (Priority Order for 1M Users)
1. Connection pooling.
2. Add `LIMIT`/index to upload queries.
3. Gunicorn + load balancer (already stateless — cookie sessions).
4. Redis caching for dashboard stats.
5. Read replicas / Alembic migrations / CDN for static assets.

### Security Status
| Control | Status |
|---|---|
| Password hashing | ✅ scrypt |
| SQL injection defense | ✅ parameterized queries |
| XSS defense | ✅ Jinja2 auto-escape (⚠️ one `innerHTML` caveat, low risk) |
| File-disk risk | ✅ N/A — files never saved to disk |
| CSRF protection | ❌ missing |
| Rate limiting | ❌ missing |
| HTTPS config | ❌ missing |
| Email verification | ❌ missing |
| Google OAuth | ❌ not implemented (env vars only) |

### Most-Asked Interview Questions (Rapid Fire)
1. "Is this AI?" → No — rule-based keyword counting, chosen for full explainability.
2. "Why Flask over Django?" → Lightweight, only needed routing/templates/sessions; wanted my own SQL/auth.
3. "Why no ORM?" → Two tables, raw SQL kept it transparent and simple to explain.
4. "SQL injection?" → Not vulnerable — every query uses `%s` parameterized placeholders.
5. "Biggest weakness in your algorithm?" → Substring matching (java/javascript false positive) + the duplicate dict-key bug.
6. "Where are uploaded files stored?" → Nowhere — parsed in-memory, never written to disk.
7. "CSRF protection?" → No, known gap, would add Flask-WTF.
8. "How would this scale to 1M users?" → Pooling + query limits first, then horizontal scaling (already stateless), then caching/replicas.
9. "Tests?" → None currently — would start with `app/ml/predict.py`'s pure functions.
10. "What's the `predictions` table?" → Mentioned in a stale docstring, never actually created.

### 30-Second Pitch
"JobCatch is a Flask app where you upload a resume and it instantly predicts your best-fit job role out of 25 categories, scores your resume out of 100, and shows what skills you have versus what's missing. The matching engine isn't a black-box AI model — it's a transparent keyword-counting algorithm, so I can explain exactly why it made every prediction."

---

*This guide is grounded entirely in the code at the time of writing. If the codebase changes (new routes, fixed bugs, added tests), re-verify the relevant sections before relying on them in an interview.*
