# 10 — Code Walkthrough (How to Learn This Codebase From Scratch)

If you did not write this project, read the files in **this exact order**. Each step builds on the previous one.

## Step 1: Start at the Entry Point — `run.py`
```python
from app import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True)
```
Two lines that matter. Everything else in the project exists to make `create_app()` return a fully configured Flask app. Read this file first so you know **where execution literally begins**.

## Step 2: The App Factory — `app/__init__.py`
This is the "table of contents" of the whole backend. Reading `create_app()` top to bottom tells you:
1. A `Flask` instance is created, pointed at `../templates` and `../static` (one directory above `app/`).
2. Config is loaded from `app/config.py`.
3. `close_db` is registered to run after every request.
4. Three blueprints are imported and registered: `auth_bp`, `main_bp`, `resume_bp`.
5. `init_db(app)` runs once, creating tables if missing.

**Why start here**: this function is a map. Once you've read it, you know exactly which other files to open next and in what order — it names every blueprint and both database-init functions explicitly.

## Step 3: Configuration — `app/config.py`
Small file, quick read. Shows you every environment variable the app depends on (`SECRET_KEY`, `MYSQL_*`, `MAX_CONTENT_LENGTH`, `ALLOWED_EXTENSIONS`) and their local-dev fallback defaults. Cross-reference with `.env.example` to see the intended production values.

## Step 4: The Database Layer — `app/models.py`
Read this before any blueprint, because every blueprint calls into it. Notice the three-part structure:
1. **Connection management** (`get_db`, `close_db`) — the request-scoped connection pattern using Flask's `g`.
2. **Schema setup** (`init_db`) — the two `CREATE TABLE IF NOT EXISTS` statements; this *is* the schema documentation for this project (no separate `.sql` file exists).
3. **Query helpers** (`get_user_by_email`, `get_user_by_id`, `create_user`, `save_upload`, `get_user_uploads`, `get_upload_stats`) — every one of these is a small, single-purpose function wrapping one SQL statement. Once you've read this file, you know the entire data-access API available to the rest of the app.

## Step 5: Routing — Blueprints, in Feature Order

### 5a. `app/auth/routes.py`
Read `register()`, then `login()`, then `logout()`. This is the simplest blueprint and teaches you the standard route pattern used everywhere else in this app:
```python
@blueprint.route('/path', methods=['GET', 'POST'])
def view():
    if request.method == 'POST':
        # read request.form
        # validate
        # call app/models.py function(s)
        # update session and/or flash a message
        # redirect or re-render
    return render_template('template.html')
```
Every route in this project — auth, main, resume — follows this exact shape.

### 5b. `app/main/routes.py`
Read the `login_required` decorator definition first — it's short (10 lines) and it's reused by the `resume` blueprint later, so understanding it now saves you a detour. Then read `home()`, `dashboard()`, `contact()`.

### 5c. `app/resume/routes.py` — the most important blueprint
This is where the project's actual "product" lives. Read in this order:
1. `allowed_file()` and `extract_text()` — the file-handling helpers, used only by `upload()`.
2. `upload()` — the core feature. Notice it imports `analyze_resume` from `app/ml/predict.py` and `login_required` from `app/main/routes.py` — this is the one place two blueprints are coupled.
3. `history()` — a thin wrapper around `get_user_uploads()`.
4. `interview_prep()` and `get_questions()` — the two routes that serve the Q&A feature, one HTML, one JSON.

## Step 6: The "ML" Engine — `app/ml/data.py` then `app/ml/predict.py`
**Read `data.py` first**, even though `predict.py` is the "logic" file, because `predict.py` is meaningless without knowing the shape of `ROLE_KEYWORDS`, `INTERVIEW_QUESTIONS`, and `SUGGESTED_SKILLS`. `data.py` is pure data — three Python dictionaries, no functions.

Then read `predict.py` top to bottom — it's short (about 140 lines) and every function has a docstring explaining exactly what it does:
1. `clean_text()` — text normalization used by prediction and skill extraction.
2. `predict_role()` — the keyword-counting algorithm.
3. `compute_score()` — the 7-check scoring rubric.
4. `extract_skills()` — found vs. missing skill lists.
5. `get_suggested_skills()` — a one-line dictionary lookup.
6. `analyze_resume()` — the single function the Flask route actually calls, which composes all of the above into one result dict.

**Why this order matters**: `analyze_resume()` is the "public API" of this module (it's the only function imported by `app/resume/routes.py`), but reading it *first* would be confusing without knowing what `predict_role`/`compute_score`/`extract_skills` individually return. Read bottom-up in terms of abstraction, but top-down in terms of file position (the file happens to be ordered exactly this way already).

## Step 7: Templates — Read `base.html` First, Then Whichever Page You Care About
`templates/base.html` defines the shared shell (navbar, flash messages, footer) every other template extends. Once you understand its `{% block %}` names (`title`, `content`, `extra_head`, `extra_scripts`), every other template becomes readable in isolation — you don't need to read all 8 templates in sequence, just `base.html` plus whichever specific page you're investigating.

## Step 8: Static Assets (Only If You Need Them)
`static/css/style.css` and `static/js/main.js` are large-ish but self-contained; you only need to open them if you're debugging a visual/interactive behavior (e.g., dark mode, drag-and-drop). They have no bearing on backend logic.

---

## "Where Do I Start Reading?" — One-Line Answer
**Start at `run.py` → `app/__init__.py` → `app/models.py` → then whichever blueprint matches the feature you're asked about → `app/ml/predict.py` + `app/ml/data.py` if it's the resume-analysis feature.**

## Entry Point → Routing → "Controllers" → "Services" → Models — Mapped to This Project's Real Names
This project doesn't use MVC terminology explicitly, but the layers map cleanly:

| MVC-style Layer | This Project's Equivalent |
|---|---|
| Entry point | `run.py` |
| App bootstrap | `app/__init__.py :: create_app()` |
| Configuration | `app/config.py :: Config` |
| Routing + Controllers (combined) | `app/auth/routes.py`, `app/main/routes.py`, `app/resume/routes.py` — Flask blueprints double as both the URL router *and* the controller/view-function logic; there's no separate "controller" class |
| Services / Business Logic | `app/ml/predict.py` (pure functions, no Flask dependency — this is the closest thing to a "service layer" in this codebase) |
| Data / Models | `app/models.py` (raw SQL — there is no `models/` directory with one class per table, just query functions) |
| Views (templates) | `templates/*.html` |
| Static config data | `app/ml/data.py` |

## Execution Order for a Real Request (Concrete Example: Uploading a Resume)
```
1. python run.py                     → Flask dev server starts, listening on :5000
2. Browser: POST /upload (file attached)
3. Flask's router matches resume_bp's /upload rule
4. app/resume/routes.py :: upload() begins executing
5.   → allowed_file() checks extension
6.   → extract_text() called
7.        → PyPDF2.PdfReader / docx.Document parses the in-memory file
8.   → app/ml/predict.py :: analyze_resume(text) called
9.        → predict_role() reads app/ml/data.py :: ROLE_KEYWORDS
10.       → compute_score() runs its 7 regex/substring checks
11.       → extract_skills() reads ROLE_KEYWORDS again, for the winning role
12.       → get_suggested_skills() reads app/ml/data.py :: SUGGESTED_SKILLS
13.  → app/models.py :: save_upload() called
14.       → get_db() opens (or reuses) a MySQL connection stored in flask.g
15.       → INSERT INTO resume_uploads ... ; db.commit()
16.  → render_template('upload.html', results=..., filename=...)
17. Flask finishes the response
18. app.teardown_appcontext fires → close_db() closes the MySQL connection
19. HTML sent back to the browser
```

## Configuration Files to Know About
- `.env` (local secrets, gitignored) / `.env.example` (template) — read together with `app/config.py`.
- `requirements.txt` — the complete dependency list; if a library is imported anywhere in `app/`, it must appear here (this was verified — every import in the codebase maps to a line in `requirements.txt`, except the standard library, e.g. `re`, `io`, `functools`).
- `.gitignore` — tells you what's deliberately excluded from version control (`venv/`, `__pycache__/`, `.env`, IDE folders, logs).

## Tips for Explaining This Codebase Live in an Interview
1. If asked to "walk through the code," follow the exact order above — it mirrors how the request actually executes, which is the most defensible way to present it.
2. If asked "what would you show me first," say `app/__init__.py` — it's genuinely the best single file to read to understand the whole app's shape in under a minute.
3. If asked to demo a feature, run `python run.py`, open `http://127.0.0.1:5000`, and walk through Register → Upload → Dashboard → History → Interview Prep in that order — it exercises every blueprint and every table.
