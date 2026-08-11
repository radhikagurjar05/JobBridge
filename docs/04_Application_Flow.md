# 04 — Application Flow (Feature by Feature)

Every flow below is traced directly from the code — file names and function names are exact.

---

## Feature 1: User Registration

**Purpose**: Let a new user create an account so their resume uploads can be tracked.

**Flow diagram**
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

**Files involved**: [templates/register.html](../templates/register.html), [app/auth/routes.py](../app/auth/routes.py), [app/models.py](../app/models.py).

**Function calls**: `register()` → `get_user_by_email()` → `generate_password_hash()` → `create_user()`.

**Database interaction**: one `SELECT` (duplicate-email check) + one `INSERT INTO users`.

**Response**: redirect to `/dashboard` with the new user already logged in (registration auto-logs-in — there is no separate "please verify your email" step).

---

## Feature 2: User Login

**Purpose**: Authenticate a returning user and start their session.

**Flow diagram**
```
User Login
   ↓
GET /login → templates/login.html
   ↓
User submits email + password (POST /login)
   ↓
app/auth/routes.py :: login()
   ↓
get_user_by_email(email) → app/models.py → SELECT * FROM users WHERE email = %s
   ↓
user found? → check_password_hash(user['password_hash'], password)
   ↓ (fail → flash "Incorrect email or password", re-render login.html)
Success
   ↓
session['user_id'] = user['id']
session['user_name'] = user['name']
session['user_email'] = user['email']
   ↓
flash("Welcome back, {name}!")
   ↓
redirect → /dashboard
```

**Files involved**: [templates/login.html](../templates/login.html), [app/auth/routes.py](../app/auth/routes.py), [app/models.py](../app/models.py).

**Function calls**: `login()` → `get_user_by_email()` → `check_password_hash()`.

**Database interaction**: one `SELECT` by email (no `UPDATE` — there is no "last login time" tracking).

**Note**: the same email/password error message is shown whether the email doesn't exist or the password is wrong. This is a deliberate (or at least correct) security practice — it avoids "user enumeration" (telling an attacker whether an email is registered).

---

## Feature 3: Logout

**Purpose**: End the session.

**Flow diagram**
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
**Files involved**: [app/auth/routes.py](../app/auth/routes.py).
**Note**: this is a `GET` request that changes state (logs the user out). That's a minor CSRF-style smell (a malicious `<img src="/logout">` on another page could log a user out), though the *impact* here is low (it only logs out, doesn't do anything destructive).

---

## Feature 4: Resume Upload & Analysis (the core feature)

**Purpose**: Take a resume file, extract its text, predict the best-fit job role, score it, and show a skills gap analysis.

**Flow diagram**
```
User Resume Upload
   ↓
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
results = { predicted_role, score, score_details, found_skills,
            missing_skills, suggested_skills }
   ↓
secure_filename(file.filename) → filename
   ↓
save_upload(user_id, filename, predicted_role, score) → app/models.py
   ↓ INSERT INTO resume_uploads (...)
   ↓
render_template('upload.html', results=results, filename=filename)
   ↓
Response: same upload page, now showing:
   - predicted role + score ring (SVG)
   - score breakdown (7 checks, pass/fail, points)
   - found skills / missing skills tag lists
   - suggested skills to learn next
   - CTA buttons → Interview Prep for this role / Upload another resume
```

**Files involved**: [templates/upload.html](../templates/upload.html), [app/resume/routes.py](../app/resume/routes.py), [app/ml/predict.py](../app/ml/predict.py), [app/ml/data.py](../app/ml/data.py), [app/models.py](../app/models.py).

**Function calls**: `upload()` → `allowed_file()` → `extract_text()` → `analyze_resume()` → (`predict_role`, `compute_score`, `extract_skills`, `get_suggested_skills`) → `save_upload()`.

**Database interaction**: one `INSERT INTO resume_uploads`.

**Response**: HTML page re-rendered with the `results` dict passed into the template (no redirect — this is a **POST-then-render**, not **POST-Redirect-GET**, so refreshing the results page will re-submit the form in some browsers — a known, minor UX gap).

---

## Feature 5: Dashboard

**Purpose**: Give the logged-in user a summary view: total uploads, average score, latest predicted role, last upload date, and a preview of the 5 most recent uploads.

**Flow diagram**
```
User Dashboard
   ↓
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
render_template('dashboard.html', user=user, stats=stats,
                 recent_uploads=recent_uploads)
   ↓
Response: HTML dashboard with stat cards + recent uploads table
```
**Files involved**: [app/main/routes.py](../app/main/routes.py), [app/models.py](../app/models.py), [templates/dashboard.html](../templates/dashboard.html).

**Note on efficiency**: `get_user_uploads()` fetches **all** uploads for the user and only *then* Python-slices `[:5]`. For a user with thousands of uploads this is wasteful — a `LIMIT 5` in the SQL query would be the correct fix at scale (see [13_Scalability.md](13_Scalability.md) and [14_Challenges_and_Improvements.md](14_Challenges_and_Improvements.md)).

---

## Feature 6: Upload History

**Purpose**: Show every past upload for the logged-in user, not just the last 5.

**Flow diagram**
```
User History
   ↓
GET /history (login_required)
   ↓
app/resume/routes.py :: history()
   ↓
get_user_uploads(session['user_id']) → app/models.py
   ↓ SELECT id, filename, upload_time, predicted_role, resume_score
     FROM resume_uploads WHERE user_id = %s ORDER BY upload_time DESC
   ↓
render_template('history.html', uploads=uploads)
   ↓
Response: full table of all uploads, with a colored score bar
          (green ≥70, orange ≥40, red <40)
```
**Files involved**: [app/resume/routes.py](../app/resume/routes.py), [app/models.py](../app/models.py), [templates/history.html](../templates/history.html).

---

## Feature 7: Interview Prep

**Purpose**: Let any visitor (logged in or not — this route has no `login_required`) pick a job role and read curated interview Q&A for it.

**Flow diagram**
```
User Interview Prep
   ↓
GET /interview-prep
   ↓
app/resume/routes.py :: interview_prep()
   ↓
roles = list(INTERVIEW_QUESTIONS.keys())   [from app/ml/data.py]
   ↓
render_template('interview_prep.html', roles=roles)
   ↓
Browser shows a <select> dropdown of roles
   ↓
User picks a role → JS 'change' event fires (interview_prep.html inline script)
   ↓
fetch('/api/questions?role=<role>')
   ↓
app/resume/routes.py :: get_questions()
   ↓
role = request.args.get('role', '')
questions = INTERVIEW_QUESTIONS.get(role, [])
   ↓
return jsonify(questions)
   ↓
JS receives JSON array of {q, a} objects
   ↓
JS builds question-card DOM elements (click to expand/collapse the answer)
```
**Files involved**: [app/resume/routes.py](../app/resume/routes.py), [app/ml/data.py](../app/ml/data.py), [templates/interview_prep.html](../templates/interview_prep.html).

**Important gap to know**: `INTERVIEW_QUESTIONS` in `app/ml/data.py` only has entries for **10 of the 25** roles (Python Developer, Data Science, Web Designing, Java Developer, DevOps Engineer, Testing, HR, Business Analyst, Sales, Network Security Engineer). For the other 15 roles, `/api/questions` returns an empty JSON array `[]`, and the frontend correctly shows "No questions available for this role yet." — this is handled gracefully, but it's an obvious follow-up question an interviewer might ask ("what happens if I pick 'Civil Engineer'?").

---

## Cross-Cutting Flow: Route Protection (`login_required`)

```
Any protected route (/dashboard, /upload, /history)
   ↓
@login_required decorator (app/main/routes.py) runs BEFORE the view function
   ↓
session.get('user_id') present?
   ├── No  → redirect(url_for('auth.login'))
   └── Yes → call the actual view function
```
This decorator is defined once in `app/main/routes.py` and imported into `app/resume/routes.py` (`from app.main.routes import login_required`) — a small but real example of cross-blueprint code reuse worth mentioning if asked "how did you avoid duplicating the login check?".

## Cross-Cutting Flow: Database Connection Per Request
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
This guarantees a MySQL connection never leaks past a single request — it opens at most once per request (subsequent calls to `get_db()` within the same request reuse `g.db`) and always closes at the end.
