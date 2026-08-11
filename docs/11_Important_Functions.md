# 11 — Important Functions

Every function below actually exists in the codebase at the file/line described. This is the "function-level cheat sheet."

---

### `create_app()`
**File**: `app/__init__.py`
**Purpose**: Build and return a fully configured Flask application (the Application Factory pattern).
**Input**: none.
**Output**: a `Flask` app instance.
**Logic**: create `Flask()` object → load `Config` → register `close_db` teardown → register 3 blueprints → call `init_db()`.
**Why it exists**: avoids a module-level global `app`, which makes the app safer to configure differently for different contexts (dev/test/prod) without side effects at import time.
**Called by**: `run.py`.
**Calls**: `app.config.from_object`, `app.teardown_appcontext`, `app.register_blueprint` (×3), `init_db`.

---

### `get_db()`
**File**: `app/models.py`
**Purpose**: Return a MySQL connection scoped to the current request, creating it lazily on first use.
**Input**: none (implicitly reads `flask.g` and `flask.current_app.config`).
**Output**: a `mysql.connector` connection object.
**Logic**: `if 'db' not in g: g.db = mysql.connector.connect(...)`; return `g.db`.
**Why it exists**: prevents opening a new database connection every time any query function runs within the *same* request — all queries in one request share one connection.
**Called by**: every query helper in `app/models.py` (`get_user_by_email`, `get_user_by_id`, `create_user`, `save_upload`, `get_user_uploads`, `get_upload_stats`).
**Calls**: `mysql.connector.connect`.

---

### `close_db(e=None)`
**File**: `app/models.py`
**Purpose**: Close the request-scoped MySQL connection when the request ends.
**Input**: `e` — an optional exception object Flask passes to teardown functions (unused here, present only because Flask's teardown API always passes it).
**Output**: `None`.
**Logic**: `g.pop('db', None)` (removes and returns it, or `None` if never opened) → if it exists and `is_connected()`, call `.close()`.
**Why it exists**: guarantees no MySQL connection ever leaks past a single request, even on error, because `app.teardown_appcontext` runs regardless of whether the request succeeded or an exception was raised.
**Called by**: Flask itself, via `app.teardown_appcontext(close_db)` registered in `create_app()`.

---

### `init_db(app)`
**File**: `app/models.py`
**Purpose**: Ensure the required tables exist before the app serves any traffic.
**Input**: the Flask `app` object (used for `app.app_context()` and `app.config`).
**Output**: `None` (side effect: creates tables in MySQL).
**Logic**: opens its **own** separate connection (not via `get_db()`, since this runs outside a request), runs two `CREATE TABLE IF NOT EXISTS` statements (`users`, `resume_uploads`), commits, closes, prints a confirmation line to the console.
**Why it exists**: makes the app "self-provisioning" — a fresh MySQL database with no tables will automatically get the correct schema the first time `python run.py` runs, with no separate migration step needed.
**Called by**: `create_app()`.

---

### `get_user_by_email(email)` / `get_user_by_id(user_id)`
**File**: `app/models.py`
**Purpose**: Look up a single user row by email (used at login/registration) or by ID (used to populate the dashboard).
**Input**: a string email, or an integer ID.
**Output**: a dict (`cursor(dictionary=True)`) with all `users` columns, or `None` if no match.
**Logic**: a single parameterized `SELECT * FROM users WHERE ... = %s` + `fetchone()`.
**Why parameterized (`%s`) queries matter**: this is exactly what prevents SQL injection — user input is never string-concatenated into the SQL text.
**Called by**: `auth/routes.py` (`register`, `login`), `main/routes.py` (`dashboard`).

---

### `create_user(name, email, password_hash=None)`
**File**: `app/models.py`
**Purpose**: Insert a new user row.
**Input**: name (str), email (str), password_hash (str or None).
**Output**: the new row's auto-incremented `id` (`cursor.lastrowid`).
**Logic**: parameterized `INSERT`, `db.commit()`, read `lastrowid`.
**Called by**: `auth/routes.py::register()`.

---

### `save_upload(user_id, filename, predicted_role, resume_score)`
**File**: `app/models.py`
**Purpose**: Persist one resume-upload event.
**Input**: the logged-in user's ID, the sanitized filename, the predicted role string, the integer score.
**Output**: the new upload row's `id`.
**Logic**: parameterized `INSERT INTO resume_uploads`, commit, return `lastrowid`.
**Called by**: `resume/routes.py::upload()`, immediately after `analyze_resume()` produces its result dict.

---

### `get_user_uploads(user_id)`
**File**: `app/models.py`
**Purpose**: Fetch every upload row belonging to a user, most recent first.
**Input**: user ID.
**Output**: a list of dicts, each with `id, filename, upload_time, predicted_role, resume_score`.
**Logic**: `SELECT ... WHERE user_id = %s ORDER BY upload_time DESC` + `fetchall()`.
**Called by**: `resume/routes.py::history()` (uses the full list) and `main/routes.py::dashboard()` (uses only `[:5]` of it — see the scalability note in [04_Application_Flow.md](04_Application_Flow.md)).

---

### `get_upload_stats(user_id)`
**File**: `app/models.py`
**Purpose**: Compute the aggregate numbers shown on the dashboard in a single query.
**Input**: user ID.
**Output**: one dict with `total_uploads`, `last_upload`, `last_role`, `avg_score`.
**Logic**: one `SELECT COUNT(*), MAX(upload_time), MAX(predicted_role), ROUND(AVG(resume_score)) FROM resume_uploads WHERE user_id = %s`.
**Why this matters**: this is a good example of **pushing aggregation down to the database** instead of pulling all rows into Python and computing the average in application code — the correct, efficient pattern, and a good thing to point out proactively as a "what did you do right" answer.
**Called by**: `main/routes.py::dashboard()`.

---

### `register()`
**File**: `app/auth/routes.py`
**Purpose**: Handle both showing the registration form (`GET`) and processing a new signup (`POST`).
**Input**: `request.form` fields `name, email, password, confirm_password` on `POST`.
**Output**: rendered HTML (form or error) or a redirect to `/dashboard`.
**Logic**: see [08_APIs.md](08_APIs.md) `/register` section for the full validation order.
**Calls**: `get_user_by_email`, `generate_password_hash`, `create_user`.

---

### `login()`
**File**: `app/auth/routes.py`
**Purpose**: Authenticate a user and start their session.
**Logic**: `get_user_by_email` → `check_password_hash` → set 3 session keys → redirect.
**Calls**: `get_user_by_email`, `check_password_hash`.

---

### `login_required(f)`
**File**: `app/main/routes.py`
**Purpose**: A decorator factory that wraps any view function to require a logged-in session.
**Input**: `f`, the view function being decorated.
**Output**: `decorated`, a wrapper function that either redirects to `/login` or calls `f(*args, **kwargs)`.
**Why `functools.wraps(f)` is used**: without it, Flask would see every decorated view function as having the same name (`decorated`), which breaks Flask's URL-building (`url_for`) since Flask indexes view functions by their `__name__`. `@wraps(f)` preserves the original function's metadata.
**Called by / reused by**: `main/routes.py::dashboard()`, and imported directly into `resume/routes.py` to protect `upload()` and `history()` — this is the one cross-blueprint import in the whole codebase.

---

### `allowed_file(filename)`
**File**: `app/resume/routes.py`
**Purpose**: Check whether an uploaded file's extension is permitted.
**Input**: filename string.
**Output**: boolean.
**Logic**: `'.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']`.
**Edge case**: a filename with no extension at all (`'.' not in filename`) correctly short-circuits to `False` before ever calling `.rsplit()` — avoiding an `IndexError`.

---

### `extract_text(file)`
**File**: `app/resume/routes.py`
**Purpose**: Convert an uploaded PDF or DOCX file object into plain text.
**Input**: a Flask `FileStorage` object (`request.files['resume']`).
**Output**: a string (possibly empty if extraction fails or the file has no extractable text).
**Logic**: branch on file extension → `PyPDF2.PdfReader` (loop pages, concatenate `.extract_text()`) or `docx.Document` (join paragraph `.text`).
**Why it reads into `io.BytesIO(file.read())` instead of saving to disk first**: both `PdfReader` and `Document` accept file-like objects, so there's no need to ever touch the filesystem — this is what keeps the app's storage footprint at zero for uploaded files (see [03_Architecture.md](03_Architecture.md) "Storage").
**Called by**: `upload()`.

---

### `upload()`
**File**: `app/resume/routes.py`
**Purpose**: The full end-to-end resume analysis feature — the most important route in the app.
**Logic**: see [04_Application_Flow.md](04_Application_Flow.md) Feature 4 for the complete flow.
**Calls**: `allowed_file`, `extract_text`, `analyze_resume`, `secure_filename`, `save_upload`.

---

### `clean_text(text)`
**File**: `app/ml/predict.py`
**Purpose**: Normalize raw resume text so keyword matching is reliable.
**Input**: raw string.
**Output**: cleaned, lowercased string.
**Logic**: three `re.sub()` passes — strip URLs (`http\S+`), strip everything except letters/digits/whitespace/`/+#.` (kept because tokens like `c#`, `.net`, `ci/cd` need those characters), collapse whitespace runs → `.lower().strip()`.
**Why `/+#.` are specifically preserved**: without keeping them, keywords like `"c#"`, `".net"`, and `"ci/cd"` in `ROLE_KEYWORDS` could never match anything in the cleaned text, since those characters would otherwise be stripped from both the keyword list *and* the resume text inconsistently. (Note: the keywords themselves in `data.py` are never run through `clean_text()` — they're already written in lowercase with these characters, so cleaning only needs to preserve them on the resume-text side to keep both sides comparable.)
**Called by**: `predict_role()`, `extract_skills()`.

---

### `predict_role(resume_text)`
**File**: `app/ml/predict.py`
**Purpose**: The core "AI" of the app — pick the best-fit job role.
**Input**: raw resume text.
**Output**: a tuple `(predicted_role: str, scores: dict[str, int])`.
**Logic**: see [09_Features.md](09_Features.md) "Role Prediction Engine" for the full breakdown, including the substring-matching and duplicate-key caveats.
**Called by**: `analyze_resume()`.
**Calls**: `clean_text()`.

---

### `compute_score(resume_text)`
**File**: `app/ml/predict.py`
**Purpose**: Produce the 0–100 resume quality score and its breakdown.
**Input**: raw resume text.
**Output**: `{"score": int, "details": [{"label": str, "passed": bool, "points": int}, ...]}`.
**Logic**: 7 independent boolean checks (regex + substring), each contributing points only if passed; sum = score.
**Called by**: `analyze_resume()`.

---

### `extract_skills(resume_text, role)`
**File**: `app/ml/predict.py`
**Purpose**: Split a role's keyword list into found-in-resume vs. missing.
**Input**: raw resume text, the predicted role string.
**Output**: tuple `(found: list[str], missing: list[str])`.
**Logic**: guard clause returns `([], [])` if `role` isn't a known key; otherwise `clean_text()` then list-comprehension membership tests against `ROLE_KEYWORDS[role]`.
**Called by**: `analyze_resume()`.
**Calls**: `clean_text()`.

---

### `get_suggested_skills(role)`
**File**: `app/ml/predict.py`
**Purpose**: One-line dictionary lookup for the "skills to learn next" list.
**Input**: role string.
**Output**: list of strings (empty if role unknown).
**Called by**: `analyze_resume()`.

---

### `analyze_resume(resume_text)`
**File**: `app/ml/predict.py`
**Purpose**: The single entry point the web layer calls — composes all four analysis functions into one dict.
**Input**: raw resume text.
**Output**: `{predicted_role, score, score_details, found_skills, missing_skills, suggested_skills}`.
**Why it exists**: this is the **only** function from `app/ml/predict.py` that `app/resume/routes.py` imports — it's the deliberate "public API surface" of the ML module, hiding the internal composition of `predict_role`/`compute_score`/`extract_skills`/`get_suggested_skills` from the web layer. This is a textbook example of encapsulation: the route doesn't need to know or care how the analysis is composed internally.
**Called by**: `resume/routes.py::upload()`.
**Calls**: `predict_role`, `compute_score`, `extract_skills`, `get_suggested_skills`.

---

### `get_questions()`
**File**: `app/resume/routes.py`
**Purpose**: Serve interview Q&A as JSON for a requested role.
**Input**: query param `role`.
**Output**: `jsonify(list[{"q": str, "a": str}])`.
**Logic**: `INTERVIEW_QUESTIONS.get(role, [])` — a single, safe dictionary lookup with a default, meaning this function can never raise an error from bad/unknown input.
**Called by**: client-side `fetch()` in `templates/interview_prep.html`.
