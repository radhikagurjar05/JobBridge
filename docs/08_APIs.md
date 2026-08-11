# 08 — APIs

JobCatch is mostly a server-rendered app (HTML responses), but every route is documented below as if it were an API endpoint, since interviewers will ask about "endpoints" generically. Only **one** route (`/api/questions`) returns pure JSON; the rest return rendered HTML pages, and that distinction is called out explicitly.

---

## `GET /`
**Purpose**: Landing/marketing page.
**Blueprint**: `main_bp` — [app/main/routes.py](../app/main/routes.py) `home()`
**Input**: none.
**Output**: renders `templates/index.html` (hero section, "how it works," features, testimonials, team).
**Validation**: none needed (static content).
**Error handling**: none needed.
**Auth required**: No.

---

## `GET /contact`
**Purpose**: Re-renders the home page (used to scroll to the contact/about section).
**Blueprint**: `main_bp` — `contact()`
**Input**: none.
**Output**: `render_template('index.html', scroll_to='contact')`.
**Note (real gap)**: the `scroll_to` variable is passed into the template, but inspecting `templates/index.html` shows it is **never referenced** anywhere in that template (no `{{ scroll_to }}` and no JS reading a query param for it). So `/contact` today behaves identically to `/` — it does not actually auto-scroll to any section. This is a genuine dead/unfinished parameter, good to acknowledge if asked "what does the contact page do?"
**Auth required**: No.

---

## `GET, POST /register`
**Purpose**: Create a new user account.
**Blueprint**: `auth_bp` — [app/auth/routes.py](../app/auth/routes.py) `register()`
**Input (POST form fields)**: `name`, `email`, `password`, `confirm_password`.
**Output**:
  - `GET` → renders `register.html`.
  - `POST` success → `302 redirect` to `/dashboard`, with a flash message queued.
  - `POST` failure → re-renders `register.html` with a flash error (`error` category), same page, `200` status.
**Validation** (in order, first failure wins):
  1. All of name/email/password non-empty.
  2. `password == confirm_password`.
  3. `len(password) >= 6`.
  4. Email not already registered (`get_user_by_email`).
**Internal flow**: validate → `generate_password_hash(password)` → `create_user(name, email, hash)` → `INSERT INTO users` → set 3 session keys → redirect.
**Error handling**: all validation failures are user-facing flash messages, not exceptions; there is no `try/except` here because none of these operations are expected to throw under normal conditions (a genuinely duplicate email is checked explicitly before insert, so the `UNIQUE` constraint should never actually fire — though if a race condition caused two simultaneous registrations with the same email, MySQL's unique constraint would raise an unhandled exception since there's no `try/except` around `create_user()`; this is a real edge case worth mentioning under [18_Weak_Areas.md](18_Weak_Areas.md)).
**Related files**: `templates/register.html`, `app/models.py` (`get_user_by_email`, `create_user`).
**Auth required**: No (if already logged in, redirects straight to `/dashboard` instead of showing the form again).

---

## `GET, POST /login`
**Purpose**: Authenticate an existing user.
**Blueprint**: `auth_bp` — `login()`
**Input (POST form fields)**: `email`, `password`.
**Output**:
  - `GET` → renders `login.html`.
  - `POST` success → `302 redirect` to `/dashboard`.
  - `POST` failure → re-renders `login.html` with a generic `"Incorrect email or password. Please try again."` flash error.
**Validation**: `get_user_by_email(email)` must return a row **and** `user['password_hash']` must be truthy **and** `check_password_hash(hash, password)` must return `True`. All three are checked in a single `if` so failure at any point produces the exact same generic error — deliberately avoiding leaking *which* part failed (a genuine security-conscious choice, whether intentional or accidental).
**Internal flow**: lookup by email → verify hash → set session → redirect.
**Error handling**: no exceptions expected in the normal path; a database connectivity failure would surface as an unhandled `mysql.connector.Error`, resulting in Flask's default 500 error page (no custom error handler exists for this).
**Related files**: `templates/login.html`, `app/models.py::get_user_by_email`.
**Auth required**: No (redirects to dashboard if already logged in).

---

## `GET /logout`
**Purpose**: End the session.
**Blueprint**: `auth_bp` — `logout()`
**Input**: none.
**Output**: `302 redirect` to `/` with a flash info message.
**Internal flow**: `session.clear()` → flash → redirect.
**Note**: This is a state-changing action performed via `GET`, which is a minor deviation from REST/HTTP semantics (state-changing actions are conventionally `POST`), and a mild CSRF surface (see [12_Security.md](12_Security.md)).
**Auth required**: No explicit check — calling `/logout` while not logged in just clears an already-empty session harmlessly.

---

## `GET /dashboard`
**Purpose**: Show the logged-in user's summary stats.
**Blueprint**: `main_bp` — `dashboard()`
**Input**: none (reads `session['user_id']`).
**Output**: renders `dashboard.html` with `user`, `stats` (`total_uploads`, `avg_score`, `last_role`, `last_upload`), and `recent_uploads` (first 5, newest first).
**Internal flow**: `get_user_by_id()` → `get_upload_stats()` → `get_user_uploads()[:5]` → render.
**Error handling**: none explicit; if `user_id` in session refers to a deleted user, `get_user_by_id` would return `None` and the template would fail trying to read `user.name` (an unhandled `AttributeError`/Jinja `UndefinedError` → 500). This edge case (stale session after account deletion) has no code path in this project since there's no account-deletion feature yet.
**Auth required**: **Yes** — protected by `@login_required`.

---

## `GET, POST /upload`
**Purpose**: Upload a resume and receive a full analysis.
**Blueprint**: `resume_bp` — [app/resume/routes.py](../app/resume/routes.py) `upload()`
**Input**:
  - `GET`: none.
  - `POST`: `multipart/form-data` with a file field named `resume`.
**Output**:
  - `GET` → renders empty `upload.html` form.
  - `POST` success → renders `upload.html` **with** `results` (dict) and `filename` — same URL, `200` status, no redirect.
  - `POST` failure (missing file / bad extension / unreadable / empty text) → re-renders `upload.html` with a flash error, no `results`.
**Validation**:
  1. `'resume' in request.files`.
  2. `file.filename != ''`.
  3. `allowed_file(filename)` → extension must be `pdf` or `docx` (from `Config.ALLOWED_EXTENSIONS`).
  4. `extract_text()` must not raise (wrapped in `try/except Exception`).
  5. Extracted text must not be blank after `.strip()`.
**`results` payload shape** (this is the closest thing to a JSON API contract in this app, even though it's rendered into HTML, not returned as JSON):
```json
{
  "predicted_role": "Python Developer",
  "score": 82,
  "score_details": [
    {"label": "Has email address", "passed": true, "points": 15},
    "... 6 more checks ..."
  ],
  "found_skills": ["python", "flask", "rest api"],
  "missing_skills": ["django", "celery", "..."],
  "suggested_skills": ["FastAPI", "Docker", "PostgreSQL", "Redis", "AWS Lambda"]
}
```
**Internal flow**: validate → `extract_text()` (PyPDF2 or python-docx) → `analyze_resume()` (`app/ml/predict.py`) → `secure_filename()` → `save_upload()` (`INSERT INTO resume_uploads`) → render with results.
**Error handling**: file-read errors are caught and shown as a flash message (`f'Could not read the file. Error: {str(e)}'` — note this leaks the raw exception string to the user, a minor information-disclosure smell worth flagging).
**Related files**: `templates/upload.html`, `app/ml/predict.py`, `app/ml/data.py`, `app/models.py::save_upload`.
**Auth required**: **Yes** — `@login_required`.
**File size limit**: enforced globally by Flask via `MAX_CONTENT_LENGTH = 5 * 1024 * 1024` (5 MB) in `Config` — if exceeded, Werkzeug raises a `413 Request Entity Too Large` **before the route function even runs**, and since there's no custom error handler registered for `413`, the user sees Flask's default error page rather than a friendly flash message. This is a real, demonstrable gap.

---

## `GET /history`
**Purpose**: Show every past upload for the logged-in user.
**Blueprint**: `resume_bp` — `history()`
**Input**: none.
**Output**: renders `history.html` with `uploads` (full list, newest first, **no pagination**).
**Internal flow**: `get_user_uploads(session['user_id'])` → render.
**Auth required**: **Yes** — `@login_required`.
**Scalability note**: no `LIMIT`/`OFFSET` — a user with thousands of uploads would get every row rendered in one page load. See [13_Scalability.md](13_Scalability.md).

---

## `GET /interview-prep`
**Purpose**: Show the role picker page for interview practice.
**Blueprint**: `resume_bp` — `interview_prep()`
**Input**: none.
**Output**: renders `interview_prep.html` with `roles` = `list(INTERVIEW_QUESTIONS.keys())` (only the **10** roles that actually have curated questions, not all 25 `ROLE_KEYWORDS` roles).
**Auth required**: No — this page is publicly accessible even to logged-out visitors (unlike `/upload`, `/history`, `/dashboard`).

---

## `GET /api/questions?role=<role>` — **the one true JSON API**
**Purpose**: Return interview Q&A for a given role, consumed by client-side JavaScript (`fetch`) on the interview-prep page.
**Blueprint**: `resume_bp` — `get_questions()`
**HTTP Method**: `GET`
**Input**: query string parameter `role` (a string, e.g. `Python Developer` — URL-encoded by the frontend with `encodeURIComponent`).
**Output**: `200 OK`, `Content-Type: application/json`, body = a JSON array of `{ "q": "...", "a": "..." }` objects (`jsonify(questions)`), or `[]` if the role isn't found or has no questions.
**Validation**: none explicit — `INTERVIEW_QUESTIONS.get(role, [])` safely defaults to an empty list for any unknown/missing/mistyped role string; there is no `400 Bad Request` ever returned by this endpoint, by design (it's impossible to "misuse" it into an error).
**Error handling**: none needed given the safe `.get()` default; the frontend JS has its own `.catch()` for network-level failures, showing `"Failed to load questions. Please try again."`.
**Related files**: `templates/interview_prep.html` (the `fetch()` call and DOM-building JS), `app/ml/data.py::INTERVIEW_QUESTIONS`.
**Auth required**: No.
**Request lifecycle example**:
```
Browser: fetch('/api/questions?role=Python%20Developer')
   ↓
Flask routes to resume_bp.get_questions
   ↓
request.args.get('role', '') → "Python Developer"
   ↓
INTERVIEW_QUESTIONS.get("Python Developer", [])
   → list of 5 {q, a} dicts (hardcoded in app/ml/data.py)
   ↓
jsonify(questions) → HTTP 200, JSON body
   ↓
Browser JS parses JSON → builds <div class="question-card"> per item
```

---

## Endpoints Summary Table

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

**Not implemented, despite being referenced elsewhere in the project**: `/login/google`, `/login/google/callback` (mentioned only in the `app/auth/routes.py` module docstring, no actual route decorators exist for them).
