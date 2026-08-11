# 15 — TCS Digital Interview Q&A (100+ Questions)

Format for every question: **Ideal Answer**, **Reasoning** (why this is asked / what it tests), **Interview Tip**.

---

# BASIC (Q1–Q36)

### Q1. What does JobCatch do, in one sentence?
**Ideal Answer**: It's a Flask web app where you upload a resume (PDF/DOCX) and it instantly predicts your best-fit job role out of 25 categories, scores your resume out of 100, and shows which skills you have and which you're missing.
**Reasoning**: Tests whether you can summarize your own project crisply.
**Tip**: Say this in under 15 seconds — don't let it become a monologue.

### Q2. What tech stack did you use?
**Ideal Answer**: Python + Flask for the backend, MySQL for the database (via `mysql-connector-python`, no ORM), Jinja2 + vanilla HTML/CSS/JS for the frontend, PyPDF2 and python-docx for file parsing.
**Reasoning**: Baseline check that you know what you built.
**Tip**: Mention "no ORM, raw SQL" proactively — it shows precision.

### Q3. Why did you use Flask instead of Django?
**Ideal Answer**: Flask is a micro-framework — I only needed routing, templating, and sessions, and I wanted to write my own SQL and auth logic rather than adopt Django's full ORM/admin/conventions for a project this size.
**Reasoning**: Classic framework-choice justification question.
**Tip**: Don't say "Django is bad" — say it's heavier than this project needed.

### Q4. What is the Application Factory pattern, and where did you use it?
**Ideal Answer**: Instead of a global `app = Flask(__name__)`, I wrote a `create_app()` function in `app/__init__.py` that builds and configures the app when called. `run.py` calls it to get the actual app instance.
**Reasoning**: Tests Flask fundamentals.
**Tip**: Mention it avoids import-time side effects and supports multiple configs (dev/test/prod).

### Q5. What is a Flask Blueprint?
**Ideal Answer**: A way to group related routes together. I have three: `auth_bp` (login/register/logout), `main_bp` (home/dashboard), and `resume_bp` (upload/history/interview-prep).
**Reasoning**: Basic Flask structure knowledge.
**Tip**: Name the actual blueprint variables from your code — shows you're not guessing.

### Q6. How do you handle passwords securely?
**Ideal Answer**: I never store plaintext passwords. `werkzeug.security.generate_password_hash()` hashes the password at registration (scrypt algorithm), and `check_password_hash()` verifies it at login by comparing hashes, not raw text.
**Reasoning**: Universal security basics question.
**Tip**: Say "scrypt" if you remember it — shows depth beyond "I used hashing."

### Q7. What database did you use and why?
**Ideal Answer**: MySQL, because the data is naturally relational — users have many resume uploads, a clean one-to-many relationship — and MySQL is widely used and well-supported.
**Reasoning**: Basic data-modeling justification.
**Tip**: Be ready to say why NOT MongoDB (data is relational, not document-shaped).

### Q8. Do you use an ORM like SQLAlchemy?
**Ideal Answer**: No — I used `mysql-connector-python` directly with raw parameterized SQL queries in `app/models.py`. I chose this for transparency and simplicity given the small schema (two tables).
**Reasoning**: Tests honesty and understanding of trade-offs.
**Tip**: Don't apologize for this choice — explain it as deliberate.

### Q9. How many tables does your database have? Name them.
**Ideal Answer**: Two — `users` (id, name, email, password_hash, created_at) and `resume_uploads` (id, user_id, filename, upload_time, predicted_role, resume_score), linked by a foreign key.
**Reasoning**: Basic schema recall.
**Tip**: Mention the FK has `ON DELETE CASCADE`.

### Q10. What file types can users upload?
**Ideal Answer**: PDF and DOCX only, validated by checking the file extension against an allow-list in `app/config.py`.
**Reasoning**: Basic feature recall.
**Tip**: Mention the 5MB size cap too.

### Q11. How do you extract text from a PDF?
**Ideal Answer**: Using PyPDF2's `PdfReader` — I loop through every page and call `.extract_text()`, concatenating the results.
**Reasoning**: Tests understanding of your own file-parsing code.
**Tip**: Mention the limitation: it can't read scanned/image PDFs (no OCR).

### Q12. How do you extract text from a DOCX file?
**Ideal Answer**: Using `python-docx`'s `Document` class, joining the `.text` of every paragraph with newlines.
**Reasoning**: Same as above, for the other format.
**Tip**: Mention the known gap: table content isn't extracted, only paragraphs.

### Q13. How does your app predict a job role from a resume?
**Ideal Answer**: I have a dictionary mapping 25 job roles to ~15 keywords each. I count how many keywords from each role appear in the cleaned resume text, and the role with the highest count is the prediction.
**Reasoning**: The core "algorithm" question — very likely to be asked.
**Tip**: Say explicitly "it's not machine learning, it's rule-based keyword counting" — honesty here builds trust.

### Q14. Is this a machine learning model?
**Ideal Answer**: No. It's a transparent, rule-based keyword-matching algorithm — no training data, no neural network. I chose this deliberately because it's 100% explainable: I can always say exactly why a prediction happened.
**Reasoning**: Interviewers specifically probe AI/ML buzzwords to check honesty.
**Tip**: Never overclaim "AI" if it isn't ML — this is one of the most important honesty checks in the whole project.

### Q15. How is the resume score calculated?
**Ideal Answer**: Seven rule-based checks — has email, has phone, has a skills section, has education, has experience, is at least 250 words, and has projects/achievements — each worth 10-20 points, summing to 100.
**Reasoning**: Tests recall of a specific, important function (`compute_score`).
**Tip**: Have the point values roughly memorized (15/15/20/15/15/10/10).

### Q16. What happens if no keywords match any role?
**Ideal Answer**: The predicted role falls back to `"General / Other"`.
**Reasoning**: Tests edge-case awareness.
**Tip**: Mention this is a deliberate fallback in `predict_role()`, not a bug.

### Q17. How do users log in?
**Ideal Answer**: Email + password form. The backend looks up the user by email, then uses `check_password_hash()` to verify the password against the stored hash, and if valid, stores `user_id`, `user_name`, `user_email` in the Flask session.
**Reasoning**: Basic auth flow recall.
**Tip**: Mention the same error message is shown for wrong email OR wrong password (avoids leaking which one failed).

### Q18. How do you protect routes that require login?
**Ideal Answer**: A custom `login_required` decorator checks `session.get('user_id')` and redirects to `/login` if it's missing; it's applied to `/dashboard`, `/upload`, and `/history`.
**Reasoning**: Tests understanding of decorators and route protection.
**Tip**: Mention it's reused across two different blueprints (`main` and `resume`).

### Q19. What is a Python decorator?
**Ideal Answer**: A function that wraps another function to add behavior without changing its code. `login_required` is a decorator that wraps view functions to add an authentication check before they run.
**Reasoning**: General Python fundamentals, tied to your own code.
**Tip**: Mention `@functools.wraps` and why it's needed (preserves the original function's name for Flask's `url_for`).

### Q20. What is session management, and how does Flask do it?
**Ideal Answer**: Flask stores session data in a cookie signed with `SECRET_KEY`. It's not encrypted, just tamper-evident — the browser can read it, but can't modify it without invalidating the signature.
**Reasoning**: Core web fundamentals.
**Tip**: Be precise: "signed, not encrypted" is a common point of confusion — get it right.

### Q21. What is the purpose of `SECRET_KEY`?
**Ideal Answer**: It's used by Flask to cryptographically sign session cookies and flash messages, so they can be verified as untampered but aren't necessarily hidden from the user.
**Reasoning**: Config fundamentals.
**Tip**: Mention it's loaded from an environment variable, not hardcoded, for security.

### Q22. What is `.env` and why do you use it?
**Ideal Answer**: A file holding environment-specific secrets (SECRET_KEY, DB credentials) that's read via `python-dotenv`, kept out of version control via `.gitignore`, so secrets never get committed to Git.
**Reasoning**: Secrets management basics.
**Tip**: Mention `.env.example` is the committed template with no real values.

### Q23. What is a foreign key, and where do you use one?
**Ideal Answer**: A column that references another table's primary key to enforce a relationship. `resume_uploads.user_id` references `users.id`, with `ON DELETE CASCADE` so deleting a user also deletes their uploads.
**Reasoning**: Basic relational DB concept.
**Tip**: Explain `ON DELETE CASCADE` clearly — it's a common follow-up.

### Q24. What does `ON DELETE CASCADE` mean?
**Ideal Answer**: If the parent row (a user) is deleted, all child rows referencing it (that user's resume_uploads) are automatically deleted too, enforced by the database itself.
**Reasoning**: Direct follow-up to Q23.
**Tip**: Contrast with `ON DELETE RESTRICT` (would block the delete) or `SET NULL`.

### Q25. How do you prevent SQL injection?
**Ideal Answer**: Every query uses parameterized placeholders (`%s`) with values passed separately to `cursor.execute()`, never string-concatenated into the SQL text.
**Reasoning**: Universal security basics.
**Tip**: Say this confidently — it's genuinely true in this codebase, verified by reading every query.

### Q26. What is Jinja2?
**Ideal Answer**: Flask's default templating engine. It lets you embed Python-like expressions (`{{ }}`, `{% %}`) inside HTML, and supports template inheritance so `base.html` can be extended by every page.
**Reasoning**: Frontend/templating basics.
**Tip**: Mention Jinja2 auto-escapes variables by default — a real XSS defense.

### Q27. What is template inheritance, and how did you use it?
**Ideal Answer**: `base.html` defines the shared layout (navbar, flash messages, footer) with `{% block content %}` placeholders; every other page `{% extends "base.html" %}` and fills in just its unique content.
**Reasoning**: Basic templating pattern.
**Tip**: Mention this keeps the navbar/footer DRY — one change updates every page.

### Q28. What does `secure_filename()` do?
**Ideal Answer**: A Werkzeug utility that sanitizes a filename by stripping dangerous characters (like `../` path traversal sequences), used before storing the uploaded file's name in the database.
**Reasoning**: File-upload security basics.
**Tip**: Mention that in this app the actual file is never saved to disk — only the sanitized name is stored, so this is defense-in-depth rather than strictly necessary today.

### Q29. Where are uploaded resume files actually stored?
**Ideal Answer**: They're not stored anywhere on disk. The file is read into memory (`io.BytesIO`), text is extracted, and only the extracted analysis results plus the filename string are saved to the database.
**Reasoning**: Tests whether you actually understand your own storage design (a common wrong assumption is "the file must be saved somewhere").
**Tip**: This is a strong, memorable fact — call it out proactively as a design decision that removes a whole class of file-storage security risk.

### Q30. What is the maximum file upload size, and how is it enforced?
**Ideal Answer**: 5 MB, enforced by Flask's `MAX_CONTENT_LENGTH` config setting — Werkzeug rejects larger uploads automatically before the route function even runs.
**Reasoning**: Config/validation basics.
**Tip**: Mention the honest gap: there's no custom error page for this (413), so the user sees Flask's default error page.

### Q31. What is the `/api/questions` endpoint?
**Ideal Answer**: A JSON API that takes a `role` query parameter and returns a list of `{q, a}` interview question objects for that role, used by client-side JavaScript on the interview-prep page.
**Reasoning**: Tests knowledge of the one true JSON API in the app.
**Tip**: Mention it safely defaults to an empty list for unknown roles — no error is possible.

### Q32. How many job roles does your app support?
**Ideal Answer**: 25 roles for prediction/skill-matching (`ROLE_KEYWORDS`), but only 10 of those 25 currently have curated interview questions (`INTERVIEW_QUESTIONS`).
**Reasoning**: Tests precise recall, not just "a lot."
**Tip**: Get this exact distinction right — it's a very likely follow-up ("do all 25 have interview questions?").

### Q33. What happens when a user picks a role with no interview questions?
**Ideal Answer**: The API returns an empty list, and the frontend shows "No questions available for this role yet." — handled gracefully, not a crash.
**Reasoning**: Tests edge-case awareness for a real gap in the app.
**Tip**: Frame this as "known content gap, gracefully handled" rather than "bug."

### Q34. What is `flash()` used for in Flask?
**Ideal Answer**: To queue a one-time message (like "Login successful" or "Incorrect password") that survives a redirect and is shown once on the next rendered page.
**Reasoning**: Basic Flask UX pattern.
**Tip**: Mention the categories (`success`, `error`, `info`) used for different message styling.

### Q35. What is `render_template()`?
**Ideal Answer**: A Flask function that renders a Jinja2 template file, optionally passing in variables (e.g. `render_template('dashboard.html', user=user, stats=stats)`) that the template can reference.
**Reasoning**: Absolute basics check.
**Tip**: Keep this answer short — it's a warm-up question, not a deep one.

### Q36. What is `redirect()` and `url_for()`?
**Ideal Answer**: `redirect()` sends an HTTP redirect response; `url_for('blueprint.endpoint')` generates the correct URL for a given view function by name, so URLs aren't hardcoded as strings anywhere.
**Reasoning**: Basic Flask routing mechanics.
**Tip**: Mention `url_for` is why templates use `{{ url_for('main.dashboard') }}` instead of hardcoded `/dashboard` — safer if routes ever change.

---

# INTERMEDIATE (Q37–Q72)

### Q37. Walk me through what happens, step by step, when a user uploads a resume.
**Ideal Answer**: Walk the flow: form POST → validate file presence/extension → `extract_text()` (PyPDF2/python-docx) → `analyze_resume()` (predict role, compute score, extract skills, suggest skills) → `save_upload()` inserts a DB row → template re-rendered with results.
**Reasoning**: The single most likely "explain your project" deep-dive question.
**Tip**: Practice this out loud until it's fluent — see [04_Application_Flow.md](04_Application_Flow.md) for the exact flow.

### Q38. Why did you separate `app/ml/data.py` from `app/ml/predict.py`?
**Ideal Answer**: `data.py` is pure static data (dictionaries); `predict.py` is pure logic operating on that data, with zero Flask dependencies. This separation means the data can be extended (new roles, new questions) without touching logic, and the logic is independently testable.
**Reasoning**: Tests understanding of separation of concerns.
**Tip**: Mention "single responsibility" explicitly if comfortable with the terminology.

### Q39. Why does `predict.py` have no Flask imports?
**Ideal Answer**: To keep the analysis logic framework-agnostic — it takes a string in, returns a dict out, so it could be unit-tested or reused outside a web context without needing a running Flask app or request context.
**Reasoning**: Tests architectural reasoning, not just recall.
**Tip**: Acknowledge honestly that no tests currently exist, but explain this design specifically enables adding them easily.

### Q40. What's a real bug or limitation you know about in your own keyword-matching logic?
**Ideal Answer**: It uses substring matching, not word-boundary matching — so `"java"` as a keyword also matches inside `"javascript"`, which could cause a JavaScript-heavy resume to get a false-positive point toward "Java Developer."
**Reasoning**: Directly tests self-awareness / code-reading depth — a very strong signal question.
**Tip**: This is one of the best answers you can give in the whole interview — it shows you actually read and understood your own algorithm's weaknesses.

### Q41. You mentioned a duplicate key bug — explain it.
**Ideal Answer**: `ROLE_KEYWORDS` in `data.py` defines `"Data Science"` twice with different keyword lists; Python dict literals silently keep only the last one, so the first block's keywords (including "jupyter") are dead code that never actually gets used at runtime.
**Reasoning**: Tests whether you found this yourself or are just repeating a memorized fact — be ready to explain *why* Python behaves this way.
**Tip**: Mention how you'd catch this going forward: a test asserting the expected number of unique roles, or linting for duplicate keys.

### Q42. How would you fix the substring-matching problem?
**Ideal Answer**: Replace `kw in cleaned_text` with a regex word-boundary check, e.g. `re.search(r'\b' + re.escape(kw) + r'\b', cleaned_text)`, for both `predict_role` and `extract_skills`.
**Reasoning**: Tests whether you can propose a concrete fix, not just identify the problem.
**Tip**: Mention `re.escape()` specifically — some keywords contain special regex characters like `.` and `+` (e.g. `.net`, `c#`) that would break a naive regex without escaping.

### Q43. Why is `resume_score` capped at exactly 100, and is that enforced by the database?
**Ideal Answer**: The 7 check point-values (15+15+20+15+15+10+10) are hand-designed to sum to exactly 100 — this is enforced by construction in `compute_score()`, not by any database constraint like `CHECK (resume_score <= 100)`. There's no DB-level guarantee.
**Reasoning**: Tests understanding of where business rules live vs. where they're enforced.
**Tip**: This is a good "what would you add" answer — a CHECK constraint would add defense-in-depth.

### Q44. Explain the request-scoped database connection pattern you used.
**Ideal Answer**: `get_db()` opens a MySQL connection and stores it on Flask's `g` object only if one doesn't already exist for the current request; `close_db()`, registered via `app.teardown_appcontext`, closes it automatically after every request, success or failure.
**Reasoning**: Tests understanding of Flask's request lifecycle and the `g` object.
**Tip**: Emphasize "teardown runs even on exceptions" — that's the key correctness property.

### Q45. Why didn't you use connection pooling?
**Ideal Answer**: For a small student project with low concurrent traffic, opening one connection per request is simple and correct; pooling would be the first infrastructure improvement needed before handling real production load, since opening/closing a fresh MySQL connection per request doesn't scale well under high concurrency.
**Reasoning**: Tests whether you understand trade-offs, not just "pooling is better."
**Tip**: Reference `mysql.connector.pooling.MySQLConnectionPool` as the concrete upgrade path.

### Q46. How does `get_upload_stats()` compute the dashboard numbers efficiently?
**Ideal Answer**: It's a single SQL query using `COUNT(*)`, `MAX(upload_time)`, `MAX(predicted_role)`, and `ROUND(AVG(resume_score))`, all filtered by `user_id` — the aggregation happens inside MySQL, not by pulling every row into Python and computing manually.
**Reasoning**: Tests whether you understand *why* this is the efficient approach.
**Tip**: Contrast this explicitly with the *inefficient* pattern used elsewhere in the same file (see Q47) — showing you can spot both good and bad examples in your own code is a strong signal.

### Q47. Is there anywhere in your code that does the opposite — fetches too much data?
**Ideal Answer**: Yes — the dashboard's "recent uploads" section calls `get_user_uploads(user_id)[:5]`, which fetches **all** of a user's uploads from MySQL and only then slices the first 5 in Python. The correct fix would be adding `LIMIT 5` to the SQL query itself.
**Reasoning**: Tests genuine self-critical code review ability.
**Tip**: This is a great, specific, low-risk "here's a real inefficiency I'd fix" answer.

### Q48. How do you scope data so users can't see each other's uploads?
**Ideal Answer**: Every query that reads uploads (`get_user_uploads`, `get_upload_stats`) takes `user_id` as a required parameter and filters `WHERE user_id = %s`, and every route always passes `session['user_id']` — never a client-supplied ID — so there's no way to request another user's data through the current UI.
**Reasoning**: Tests authorization understanding, specifically IDOR (Insecure Direct Object Reference) awareness.
**Tip**: Note that this is safe *only because* no route currently accepts an upload ID from the client — if one were added later (e.g. "view a specific past upload's full detail by ID"), an explicit ownership check would become necessary.

### Q49. What would happen if two users tried to register with the same email at the exact same time?
**Ideal Answer**: The app checks for an existing email before inserting, but doesn't wrap the `INSERT` in a try/except for the database's `UNIQUE` constraint — so in a true race condition, the second insert could raise an unhandled `IntegrityError`, resulting in a 500 error rather than a friendly message.
**Reasoning**: Tests deep understanding of race conditions, a favorite "gotcha" topic.
**Tip**: Propose the fix: wrap `create_user()`'s call in a try/except catching the integrity error and showing a friendly duplicate-email message.

### Q50. Why is the same error message shown for wrong email and wrong password at login?
**Ideal Answer**: To avoid "user enumeration" — if the app said "no account with that email" vs. "wrong password" separately, an attacker could use that distinction to discover which emails are registered.
**Reasoning**: Security-awareness question, testing whether you understand *why* generic errors matter.
**Tip**: Mention this specific term, "user enumeration" — it signals real security vocabulary.

### Q51. Your `/logout` route is a GET request. What's the concern with that?
**Ideal Answer**: State-changing actions are conventionally done via POST; a GET-based logout is a mild CSRF surface (e.g. an `<img src="/logout">` on another site could force a logout), though the actual impact here is low since logout isn't destructive.
**Reasoning**: Tests whether you understand HTTP method semantics and CSRF at a basic level.
**Tip**: Immediately connect it to "and here's a bigger CSRF gap" (Q52) — shows you see the pattern, not just one instance.

### Q52. Does your app have CSRF protection?
**Ideal Answer**: No — none of the forms (login, register, upload) include CSRF tokens, and no library like Flask-WTF is used. I'd add `CSRFProtect` from Flask-WTF as the fix.
**Reasoning**: Very common security question; also tests honesty.
**Tip**: Don't try to argue it's not needed — just state the gap and the fix plainly.

### Q53. Is your app vulnerable to XSS?
**Ideal Answer**: Mostly no, because Jinja2 auto-escapes all `{{ }}` output by default. The one caveat is the interview-prep page's client-side JavaScript, which builds question cards using `innerHTML` directly from JSON — bypassing Jinja's escaping. The risk is low today because that data comes from a hardcoded dictionary, not user input, but the *pattern* would become dangerous if that data source ever became user-editable.
**Reasoning**: Tests nuanced security understanding — not just "yes/no" but "where exactly, and why is the current risk low."
**Tip**: This layered answer (mostly protected, one specific caveat, explained precisely) is exactly the depth TCS Digital interviewers reward.

### Q54. How would you add rate limiting to prevent brute-force login attempts?
**Ideal Answer**: Add Flask-Limiter, applying a per-IP or per-email rate limit decorator (e.g. `@limiter.limit("5 per minute")`) to the `/login` route, returning a 429 response when exceeded.
**Reasoning**: Tests whether you know a concrete real-world library/solution, not just the concept.
**Tip**: Naming "Flask-Limiter" specifically shows you've researched beyond the current code.

### Q55. Explain the difference between session-based auth and JWT-based auth. Which did you use, and why?
**Ideal Answer**: Session-based auth keeps a small identifier in a cookie and the actual data server-side (or, in Flask's default case, signed directly in the cookie); JWT is a self-contained signed token holding claims, verified statelessly without a server-side lookup. I used Flask sessions because this is a same-origin, server-rendered app — no separate API client (mobile app, SPA) needed statelessness.
**Reasoning**: Classic architecture comparison question.
**Tip**: Be precise that Flask's default session actually *is* self-contained in the cookie too (signed via `SECRET_KEY`) — so the real distinguishing factor here is more about "designed for server-rendered vs. API clients" than "stateless vs. stateful," which is a subtlety worth having ready.

### Q56. How would you implement "forgot password"?
**Ideal Answer**: Generate a time-limited, signed token (e.g. using `itsdangerous`, which Flask already depends on) tied to the user's email, email a reset link containing that token, verify the token's validity and expiry on the reset page, then let the user set a new password via `generate_password_hash()`.
**Reasoning**: Tests ability to design a feature not yet built, using tools already in your stack.
**Tip**: Mentioning `itsdangerous` (already a Flask dependency) shows resourcefulness — you don't need a new library for token signing.

### Q57. How would you add email verification at registration?
**Ideal Answer**: Add an `is_verified` boolean column to `users`, send a signed verification link on registration, don't allow login (or restrict features) until the link is clicked, which flips `is_verified` to true.
**Reasoning**: Tests schema-design-on-the-fly ability.
**Tip**: Note this requires an email-sending mechanism (e.g. Flask-Mail + an SMTP provider) not currently in the stack.

### Q58. What is the purpose of the `login_required` decorator being defined in `main/routes.py` but used in `resume/routes.py` too?
**Ideal Answer**: It's cross-blueprint code reuse — rather than duplicating the same session check in every blueprint, `resume/routes.py` imports the one decorator already defined in `main/routes.py`. It's the one deliberate coupling point between two blueprints in this codebase.
**Reasoning**: Tests whether you understand the actual dependency graph of your own code, not just "it's imported somewhere."
**Tip**: If asked "would you refactor this," a reasonable answer is moving `login_required` into a shared `app/utils.py` or `app/auth/decorators.py` so no blueprint "owns" a decorator another blueprint depends on.

### Q59. What is the significance of `analyze_resume()` being the *only* function imported from `predict.py`?
**Ideal Answer**: It's the deliberate public API of the ML module — encapsulating `predict_role`, `compute_score`, `extract_skills`, and `get_suggested_skills` behind one function means the web layer doesn't need to know how analysis is internally composed, and that internal composition could change without touching `app/resume/routes.py` at all.
**Reasoning**: Tests understanding of encapsulation/abstraction as an architectural principle, using a concrete example from your own code.
**Tip**: This is a great answer to a generic "what is encapsulation, give an example" question — you have a real one ready.

### Q60. Why does `clean_text()` preserve `/+#.` characters instead of stripping all non-alphanumeric characters?
**Ideal Answer**: Because keywords like `"c#"`, `".net"`, and `"ci/cd"` in `ROLE_KEYWORDS` rely on those specific characters — stripping them from the resume text would make those keywords permanently unmatchable.
**Reasoning**: Tests close reading of a specific, non-obvious implementation detail.
**Tip**: This shows genuine familiarity with the code rather than a generic understanding of "text cleaning."

### Q61. What's the difference between `compute_score()`'s text processing and `predict_role()`'s?
**Ideal Answer**: `compute_score()` uses `resume_text.lower()` directly (no URL-stripping or character filtering), while `predict_role()` and `extract_skills()` run the fuller `clean_text()` pipeline (URL removal, character filtering, whitespace collapsing) before lowercasing.
**Reasoning**: Tests very close reading — a good "have you actually read every line" check.
**Tip**: You can add: "this is a minor inconsistency — ideally both would share the exact same normalization step, though in practice it doesn't cause incorrect results since `compute_score`'s checks are simple substring/regex checks that don't depend on URL-stripping."

### Q62. How would you add pagination to the upload history page?
**Ideal Answer**: Modify `get_user_uploads()` to accept `limit`/`offset` (or a page number), add `LIMIT %s OFFSET %s` to its SQL query, and update `history()` to read a `?page=` query parameter and pass "next/previous page" links to the template.
**Reasoning**: Tests ability to extend an existing function without breaking its other caller (the dashboard also uses `get_user_uploads`).
**Tip**: Mention you'd need to make the new parameters optional with sane defaults so `dashboard()`'s existing call (`get_user_uploads(user_id)[:5]`) doesn't break — or better, refactor dashboard to pass `limit=5` directly instead of slicing in Python.

### Q63. What does `MAX_CONTENT_LENGTH` do and where is it set?
**Ideal Answer**: A Flask config value (set to 5MB in `app/config.py`) that makes Werkzeug automatically reject any request body larger than that limit with a 413 error, before your route code even runs.
**Reasoning**: Tests config-level understanding, not just route-level.
**Tip**: Mention the honest gap: no custom error handler exists for 413, so users see Flask's default error page.

### Q64. Why is `allowed_file()` checking only the extension, not the actual file content, considered a weak check?
**Ideal Answer**: A file could be renamed to have a `.pdf`/`.docx` extension while actually containing different content — the extension check alone doesn't verify the real file type/MIME. In this app the impact is limited because such a file would simply fail inside `PdfReader`/`Document` parsing and be caught by the generic exception handler — it's never executed or saved, only parsed as text.
**Reasoning**: Tests whether you understand *both* the theoretical weakness and its actual practical impact in this specific app (not blindly saying "this is a critical vulnerability" when it isn't, given files are never persisted or executed).
**Tip**: Calibrated answers (acknowledging a weakness exists but explaining why the blast radius is small here) show more maturity than alarmism.

### Q65. What would you change about how `upload()` handles a successful analysis?
**Ideal Answer**: Currently it re-renders `upload.html` directly with the results (no redirect), which risks form-resubmission warnings on page refresh. I'd switch to a Post/Redirect/Get pattern — redirect to `/upload/results/<upload_id>` after saving, and have that route re-query and render by ID.
**Reasoning**: Tests knowledge of a named, standard web pattern (PRG) applied to a real gap in your code.
**Tip**: Mention "PRG pattern" by name if comfortable — it's a recognized term interviewers like hearing.

### Q66. How does your app avoid duplicate database connections building up during a single request?
**Ideal Answer**: `get_db()` checks `if 'db' not in g` before opening a new connection, so calling it multiple times within the same request (e.g., once in `dashboard()` for `get_user_by_id`, again for `get_upload_stats`) reuses the same connection stored on `flask.g`.
**Reasoning**: Tests understanding of Flask's `g` object specifically.
**Tip**: Contrast `g` (request-scoped) with `session` (persists across requests, stored in a cookie) — a common point of confusion.

### Q67. Explain how dark mode works in your frontend.
**Ideal Answer**: CSS custom properties are defined in `:root` for light mode and overridden under `[data-theme="dark"]` for dark mode; JavaScript in `main.js` toggles a `data-theme="dark"` attribute on the `<html>` element and persists the choice in `localStorage` so it survives page reloads.
**Reasoning**: Tests basic frontend/CSS variable understanding.
**Tip**: Mention the inline `<script>` in `base.html`'s `<head>` that applies the theme *before* the page renders, to avoid a "flash of wrong theme."

### Q68. How does the interview-prep page load questions without a full page reload?
**Ideal Answer**: JavaScript listens for the `<select>` dropdown's `change` event, then calls `fetch('/api/questions?role=...')`, parses the JSON response, and dynamically builds question-card `<div>` elements in the DOM — a small-scale AJAX pattern, no page navigation involved.
**Reasoning**: Tests understanding of client-server async communication basics.
**Tip**: Mention this is the *only* place in the entire app where JS talks to the backend asynchronously — everywhere else is full-page form submissions.

### Q69. What's the difference between `request.form` and `request.args` in Flask, and where does your app use each?
**Ideal Answer**: `request.form` reads POST body data (used in `register()`/`login()`/`upload()` for form fields); `request.args` reads URL query string parameters (used in `get_questions()` to read `?role=...`).
**Reasoning**: Basic but easy-to-mix-up Flask request object knowledge.
**Tip**: Precise, correct terminology here is an easy way to look sharp.

### Q70. If you had to add unit tests to this project, where would you start and why?
**Ideal Answer**: I'd start with `app/ml/predict.py` — `predict_role`, `compute_score`, `extract_skills` — because they're pure functions with no Flask/DB dependency, so they're trivial to test in isolation with plain `assert` statements or `pytest`, and they contain the actual business logic most worth protecting against regressions (like the duplicate-key bug).
**Reasoning**: Tests testing strategy/prioritization, not just "yes I'd add tests."
**Tip**: Mention you'd follow with Flask test-client integration tests for the routes (`/register`, `/login`, `/upload`) once the pure-function layer is covered.

### Q71. How would you containerize this app with Docker?
**Ideal Answer**: Write a `Dockerfile` based on a `python:3.12-slim` image, `pip install -r requirements.txt`, expose port 5000, and run via gunicorn instead of Flask's dev server (e.g. `gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"`); add a `docker-compose.yml` with a MySQL service so the whole stack runs with `docker-compose up`.
**Reasoning**: Tests deployment knowledge even though nothing currently exists in the repo.
**Tip**: Be upfront that no Dockerfile currently exists — describe exactly what you'd add.

### Q72. Why does `run.py` say "NEVER set debug=True in production"?
**Ideal Answer**: Flask's debug mode enables the interactive debugger and auto-reloader, but the interactive debugger can execute arbitrary Python code if an unhandled exception occurs and an attacker can reach the debugger console — a serious remote-code-execution risk in production. Debug mode also leaks stack traces with source code to end users.
**Reasoning**: Tests understanding of a very common, very real Flask production gotcha.
**Tip**: This is a well-known, high-value security fact — memorize the reason, not just the rule.

---

# ADVANCED (Q73–Q104+)

### Q73. If this app had to serve 1 million users, what would you change first?
**Ideal Answer**: First, connection pooling (currently one raw connection per request) and adding `LIMIT` to unbounded queries like `get_user_uploads`. Second, moving off Flask's dev server to gunicorn/uWSGI behind a load balancer, since the app is already stateless (sessions live in the client cookie) so horizontal scaling is straightforward. Third, adding indexes (`user_id, upload_time`) and considering read replicas for the dashboard's read-heavy queries.
**Reasoning**: Classic scalability deep-dive; tests prioritization under a hypothetical.
**Tip**: Lead with the *cheapest, highest-impact* fixes first (pooling, indexes) before jumping to "microservices" — shows practical judgment. See [13_Scalability.md](13_Scalability.md).

### Q74. Why is this app's session design "already scale-friendly," and what design choice specifically enables that?
**Ideal Answer**: Because all session state (`user_id`, `user_name`, `user_email`) lives in the signed client-side cookie rather than server-side memory, any Flask instance behind a load balancer can serve any request without needing "sticky sessions" — there's no shared server-side session store to keep in sync.
**Reasoning**: Tests whether you can identify an architectural strength, not just weaknesses — shows balanced analysis.
**Tip**: This is a great answer to "what did you get right, architecturally, without realizing it at the time?"

### Q75. Would you introduce microservices for this app? Why or why not?
**Ideal Answer**: Not yet, and maybe not fully ever — the domain is small (auth + one core feature) and the computational hot path (keyword matching) is cheap. The one plausible service boundary worth extracting *later* is the resume-analysis engine itself, but only if it evolves into something requiring dedicated infrastructure (e.g., a real ML model needing GPU inference) — at that point extracting it behind an internal API would let it scale independently from the CRUD parts of the app.
**Reasoning**: Tests whether you default to "microservices are always better" (a red flag) or reason from actual requirements.
**Tip**: A senior answer resists over-engineering — say so explicitly.

### Q76. How would you migrate this schema safely in production without downtime, given there's currently no migration tool?
**Ideal Answer**: Introduce Alembic (or a similar migration tool), write incremental migration scripts instead of relying on `CREATE TABLE IF NOT EXISTS`, and for any breaking schema change (e.g., adding a NOT NULL column to a populated table), use the "expand-contract" pattern: add the new column as nullable first, backfill data, then tighten the constraint in a later migration once all writers are updated.
**Reasoning**: Tests real-world database migration discipline, a common senior-level topic.
**Tip**: Mention `CREATE TABLE IF NOT EXISTS` is fine for a fresh dev database but is not a substitute for versioned migrations once real data exists in production.

### Q77. Explain a scenario where the current keyword-counting algorithm would give a clearly wrong prediction, and how you'd detect that in testing.
**Ideal Answer**: A resume for a "Business Analyst" that happens to mention "sql," "agile," and "jira" heavily (all present in multiple role keyword lists) could tie with or beat a role that's a better semantic fit, since the algorithm has no concept of context or keyword importance — it's a flat count. I'd detect this by building a small labeled test set of real (anonymized) resumes with known correct roles and asserting prediction accuracy against it as a regression test.
**Reasoning**: Tests ability to reason about the algorithm's blind spots at a systems level, plus propose a concrete evaluation methodology.
**Tip**: Mentioning "labeled test set + accuracy metric" borrows correctly from real ML evaluation practice, even though this isn't ML — a good bridge answer.

### Q78. How would you evolve this rule-based engine into a real ML-based classifier, and what would you need to be careful about?
**Ideal Answer**: I'd collect a labeled dataset of resumes and their correct roles, use TF-IDF or embeddings (e.g. sentence-transformers) as features, and train a classifier (logistic regression or a small neural network) — but I'd keep the existing keyword-based system as an explainable fallback/baseline, since one strength of the current design is that predictions are always justifiable. I'd need to be careful about class imbalance (some roles have far more example resumes than others) and about maintaining explainability, since a black-box model would lose the "here's exactly why" trust the current design has.
**Reasoning**: Tests whether you can extend your project thoughtfully rather than just naming ML buzzwords.
**Tip**: Explicitly weigh the trade-off (accuracy vs. explainability) — that tension is the heart of a good answer here.

### Q79. Walk through exactly what happens if the MySQL server is down when a request comes in.
**Ideal Answer**: `get_db()`'s call to `mysql.connector.connect()` would raise an exception (e.g. `InterfaceError`), which isn't caught anywhere in the route or in `models.py`, so Flask would return a 500 Internal Server Error with (in debug mode) a full stack trace, or a generic error page in production. There's no retry logic, circuit breaker, or graceful degradation currently implemented.
**Reasoning**: Tests failure-mode reasoning, a hallmark of production-readiness thinking.
**Tip**: Propose the fix: a `try/except` around `get_db()` returning a friendly "service temporarily unavailable" page, plus health-check-based monitoring to detect DB outages proactively.

### Q80. How would you design a rate limiter that applies per-user rather than per-IP, and why might that matter here?
**Ideal Answer**: Since `/upload` requires login, I could rate-limit based on `session['user_id']` instead of IP — relevant because multiple legitimate users could share a NAT'd IP (e.g., a college network), which per-IP limiting would unfairly penalize. Flask-Limiter supports custom key functions, so I'd pass a function reading `session['user_id']` as the rate-limit key for authenticated routes, falling back to IP for unauthenticated ones like `/login` (where there's no user_id yet to key on).
**Reasoning**: Tests deeper rate-limiting design thinking beyond "just add Flask-Limiter."
**Tip**: The IP-vs-user-id distinction, and why `/login` specifically can't use user-id-based limiting (no session yet), is the key insight here.

### Q81. If `resume_uploads` grew to 500 million rows, what specifically would break first, and how would you fix it?
**Ideal Answer**: `ORDER BY upload_time DESC` on an un-indexed-for-this-purpose table (only the FK-derived index on `user_id` exists) would force expensive sorts/scans at that scale, especially combined with unbounded `get_user_uploads()` calls. I'd add a composite index `(user_id, upload_time DESC)`, enforce pagination everywhere, and consider partitioning the table by date range if historical data needed to be retained but queried less frequently.
**Reasoning**: Tests genuine at-scale database reasoning with specifics, not generic "add an index" hand-waving.
**Tip**: Naming the *exact* composite index and explaining *why* that specific column order matters (equality filter first, then the sort column) shows real depth.

### Q82. What's the security implication of storing `user_name` and `user_email` directly in the session cookie rather than just `user_id`?
**Ideal Answer**: Since Flask sessions are signed but not encrypted, anyone with access to the cookie (e.g., via browser dev tools, or a shared/public computer) can read the user's name and email in plaintext, even though they can't forge a *different* user's session without the server's `SECRET_KEY`. It's a mild information-exposure concern more than an authentication bypass risk — the fix would be storing only `user_id` in the session and re-fetching name/email from the database on each request that needs them.
**Reasoning**: Tests nuanced understanding of "signed vs. encrypted" applied to a specific, real design choice in your code.
**Tip**: This is subtle enough that many candidates get it wrong — getting "signed ≠ encrypted, so it's readable but not forgeable" exactly right is a strong signal.

### Q83. How would you implement "delete my account," and what would the FK cascade do?
**Ideal Answer**: Add a `POST /account/delete` route (with re-authentication or a confirmation step, and CSRF protection), which calls a new `delete_user(user_id)` in `models.py` running `DELETE FROM users WHERE id = %s`. Because `resume_uploads.user_id` has `ON DELETE CASCADE`, MySQL would automatically delete every one of that user's upload rows as part of the same operation — no separate cleanup query needed.
**Reasoning**: Tests whether you understand the *consequence* of a schema decision (the cascade) that was made but never yet exercised by any existing feature.
**Tip**: Mention this is a good example of "the schema was designed with more foresight than the current feature set uses" — a nice callback to Q23-25.

### Q84. Your app currently has one MySQL instance handling all reads and writes. How would you introduce a read replica, and what would change in `app/models.py`?
**Ideal Answer**: I'd stand up a MySQL read replica, then modify `get_db()` (or add a second `get_read_db()`) to route read-only queries (`get_user_by_email`, `get_user_uploads`, `get_upload_stats`) to the replica's connection, while write queries (`create_user`, `save_upload`) stay on the primary. The main complexity to manage is replication lag — a user who just uploaded a resume might not immediately see it in their history if the read replica hasn't caught up yet, so time-sensitive reads right after a write (e.g., the `upload()` route ends by rendering results already in memory, not by re-querying, so this specific case is actually unaffected).
**Reasoning**: Tests read/write-splitting understanding plus awareness of replication lag as a real consequence.
**Tip**: Noting that `upload()` renders results already computed in memory (not re-fetched from DB) means it wouldn't actually be affected by replica lag — a nice, precise detail that shows you're reasoning about *this specific codebase*, not reciting generic scaling advice.

### Q85. What would a proper CI/CD pipeline for this project look like, given none exists today?
**Ideal Answer**: On every push: install dependencies, run linting (flake8/pylint) and the (currently nonexistent, but proposed) pytest suite, build a Docker image, run it against a test MySQL container for integration tests, then on merge to main, push the image to a registry and deploy via a rolling update to whatever hosting platform is used.
**Reasoning**: Tests DevOps/CI-CD fundamentals against a real (currently empty) gap.
**Tip**: Be explicit that none of this exists yet — describe the target state clearly rather than implying it's already there.

### Q86. Explain how you'd add structured logging and monitoring to this app, and what specific events you'd log first.
**Ideal Answer**: Replace the single `print()` statement in `init_db()` with Python's `logging` module configured for structured (JSON) output. I'd prioritize logging: failed login attempts (for security monitoring/brute-force detection), file-upload failures (to spot patterns like a specific PDF format that keeps failing extraction), and slow database queries. I'd pair this with an APM tool (or at minimum Prometheus + Grafana) tracking request latency and error rate per route.
**Reasoning**: Tests observability design thinking, prioritized by actual business value, not a generic "add logging everywhere."
**Tip**: Prioritizing *security-relevant* and *failure-diagnosing* logs first (rather than logging everything indiscriminately) shows signal-vs-noise judgment.

### Q87. If an interviewer asks "prove to me there's no SQL injection risk," how would you demonstrate it using your actual code?
**Ideal Answer**: Point to any query in `models.py`, e.g. `cursor.execute("SELECT * FROM users WHERE email = %s", (email,))` — the `%s` is a placeholder the MySQL driver substitutes safely as a *parameter*, not as string-interpolated SQL text, so even if `email` contained `' OR '1'='1`, it would be treated as a literal string value to match against, never as executable SQL syntax. I'd contrast this with what an *unsafe* version would look like: `f"SELECT * FROM users WHERE email = '{email}'"`, which the codebase never does anywhere.
**Reasoning**: Tests whether you can give a concrete, code-referenced proof rather than a vague "I used parameterized queries" claim.
**Tip**: Actually contrasting safe vs. unsafe syntax side-by-side in your answer is far more convincing than asserting safety abstractly.

### Q88. How would you redesign the `predictions` concept that's mentioned in a docstring but never implemented?
**Ideal Answer**: Introduce a real `predictions` table with its own `id`, a foreign key to `resume_uploads.id`, the predicted role, the raw keyword-match score, and a timestamp — decoupling "the file that was uploaded" from "a specific prediction run against it." This would let the same upload be re-analyzed multiple times (e.g., if the algorithm improves) with a full history of predictions, rather than overwriting `predicted_role`/`resume_score` directly on `resume_uploads` as today.
**Reasoning**: Tests schema design skill and the ability to reconcile stale documentation with a concrete improvement plan.
**Tip**: See [07_Database.md](07_Database.md) for the exact proposed schema — have the column names ready.

### Q89. What testing strategy would give you the most confidence in the keyword-matching engine specifically?
**Ideal Answer**: Table-driven unit tests: a list of (resume_text, expected_role) pairs covering typical cases, boundary cases (a resume with keywords from two roles equally), and known-bad cases (e.g. a JavaScript resume, to explicitly assert the Java false-positive either doesn't happen after a fix, or document that it currently does as a known limitation). I'd also add a regression test asserting `len(ROLE_KEYWORDS) == 25` to catch the duplicate-key class of bug automatically.
**Reasoning**: Tests concrete test-design ability tied to this project's actual known weaknesses.
**Tip**: The `len(ROLE_KEYWORDS) == 25` assertion is a small, precise, memorable answer — say it exactly like that.

### Q90. How would you handle internationalization (i18n) if JobCatch needed to support non-English resumes?
**Ideal Answer**: The keyword lists in `ROLE_KEYWORDS` are entirely English-language-specific technical terms, which mostly transfer across languages as-is (e.g., "python," "docker" are used in resumes worldwide), but section-heading detection in `compute_score()` (looking for words like "education," "experience," "skill") would fail on a resume written in, say, Hindi or Spanish. I'd need language-specific keyword sets for the structural checks, and possibly a language-detection step before choosing which set to apply.
**Reasoning**: Tests whether you can reason about a dimension of the problem not addressed at all in the current code, without over-claiming a solution already exists.
**Tip**: Be honest that i18n isn't handled today at all — the interesting part of the answer is *which specific functions* would break first (structural checks) versus which would mostly survive (technical keyword matching).

### Q91. Explain the trade-off between the app's current "analyze inline, respond immediately" design versus a background-job design, and when you'd switch.
**Ideal Answer**: Inline analysis is simpler and gives instant feedback, appropriate because keyword matching is fast (milliseconds). I'd switch to a background job (Celery + Redis/RabbitMQ) only if the analysis step became slow or unreliable — e.g., adding OCR for scanned PDFs, calling an external ML API, or adding heavier NLP processing — because those introduce latency/failure modes that shouldn't block the HTTP request/response cycle.
**Reasoning**: Tests judgment about *when* added complexity (a job queue) is actually justified, not just "queues are always better."
**Tip**: The phrase "shouldn't block the HTTP request/response cycle" is the precise technical justification interviewers want to hear, not just "it would be faster."

### Q92. If you had to support the Google OAuth login referenced in `.env.example` but never implemented, what would the full flow look like?
**Ideal Answer**: Register the app in Google Cloud Console to get `GOOGLE_OAUTH_CLIENT_ID`/`SECRET` (already placeholder'd in `.env.example`). Add `/login/google` (redirects to Google's OAuth consent URL) and `/login/google/callback` (Google redirects back with an authorization code; exchange it for an access token using the `requests` library — already an unused dependency in `requirements.txt`, which would finally get used — then call Google's userinfo endpoint to get the user's email/name). I'd need a new `users.google_id` column (or reuse `email` to match/create an account) and would leave `password_hash` nullable for OAuth-only accounts, which the schema already supports today.
**Reasoning**: Tests ability to design a real, complete OAuth flow, tied precisely to existing (currently dormant) scaffolding in the codebase — the unused `requests` dependency and the nullable `password_hash` column.
**Tip**: Connecting this answer back to two specific pieces of "evidence" already in the repo (unused `requests` import, nullable `password_hash`) is a memorable, code-grounded way to answer a hypothetical.

### Q93. How would you prevent the `upload()` route's exception handler from leaking internal error details to users?
**Ideal Answer**: Currently `flash(f'Could not read the file. Error: {str(e)}')` includes the raw exception message, which could leak internal details (e.g., a library's internal file path or parsing internals) to the end user. I'd log the full exception server-side (via the `logging` module) and show a generic, safe message to the user instead, like "We couldn't read that file — please make sure it's a valid PDF or DOCX."
**Reasoning**: Tests information-disclosure awareness at a granular, specific code location.
**Tip**: This exact line (`flash(f'... Error: {str(e)}')`) is a genuinely good, small, concrete finding — cite the line directly.

### Q94. Suppose a load test shows `/dashboard` is the slowest route under concurrent load. How would you diagnose and fix it, step by step?
**Ideal Answer**: First, profile which of the three DB calls (`get_user_by_id`, `get_upload_stats`, `get_user_uploads`) is slow — likely `get_user_uploads` since it has no `LIMIT` and full-scans/sorts the user's entire upload history just to slice `[:5]` in Python. Fix: add a dedicated query with `LIMIT 5` directly in SQL instead of over-fetching. Second, check whether connection setup overhead (no pooling) is the bigger factor at high concurrency — if so, pooling would help across all three calls at once, not just this one route.
**Reasoning**: Tests a realistic, ordered diagnostic process rather than jumping straight to a fix.
**Tip**: The "diagnose in priority order, then fix the biggest lever first" structure is what distinguishes a senior-sounding answer from a junior one that just lists everything at once.

### Q95. Why might using `MAX(predicted_role)` in `get_upload_stats()` be semantically wrong, even though it runs without error?
**Ideal Answer**: `MAX(predicted_role)` returns the alphabetically **largest** role string among all of a user's uploads (e.g., "Web Designing" > "Java Developer" alphabetically) — not necessarily their *most recent* prediction, which is what "last_role" implies to the dashboard. The query happens to also select `MAX(upload_time)` in the same row, but `MAX()` is computed independently per column, so there's no guarantee `last_role` actually corresponds to the same row as `last_upload`.
**Reasoning**: This is a genuinely subtle, real correctness bug hiding in a single line of SQL — a great "gotcha" question for someone who has actually read the query carefully.
**Tip**: Propose the fix: use a subquery or `ORDER BY upload_time DESC LIMIT 1` to fetch the most recent row's role specifically, rather than an independent `MAX()` aggregate on a different column.

### Q96. How would you support multiple resumes analyzed against different *target* roles chosen manually by the user, rather than only the auto-predicted role?
**Ideal Answer**: Add an optional `target_role` form field on `/upload`; if provided, call `extract_skills(resume_text, target_role)` (and `get_suggested_skills(target_role)`) using the user's chosen role instead of the auto-predicted one, while still showing the auto-predicted role separately for comparison. `extract_skills()` already accepts a `role` parameter generically, so this requires no changes to `app/ml/predict.py` itself — only to how `upload()` calls it.
**Reasoning**: Tests whether you can extend a feature using the *existing* function signatures without inventing unnecessary new code — a sign of working with the grain of the codebase.
**Tip**: Explicitly noting "`extract_skills()` already supports this, no signature change needed" shows you understand the function's actual flexibility, not just its current single call site.

### Q97. What single change would most improve this project's demonstrable trustworthiness (i.e., "can I trust this prediction") without changing the underlying algorithm at all?
**Ideal Answer**: Show *which specific keywords* drove the prediction directly in the results UI — e.g., "Predicted 'Python Developer' because we found: python, flask, rest api" — since `predict_role()` already computes a full `scores` dict per role internally but currently discards it (the route only uses `predicted_role`, not the `_scores` tuple element). Surfacing that already-computed data would make the "explainable AI" claim tangible to the end user, not just true in the backend.
**Reasoning**: Tests product-thinking layered on top of technical understanding — noticing that explainability data already exists but isn't surfaced.
**Tip**: Pointing out `_scores` is thrown away with the underscore-prefixed variable name in `analyze_resume()` (`predicted_role, _scores = predict_role(resume_text)`) is a nice, precise detail — literally named to be ignored, and you'd un-ignore it.

### Q98. If TCS asked you to make this production-grade in one sprint, what are your top 5 changes, in order?
**Ideal Answer**: (1) Add CSRF protection (Flask-WTF) — highest-impact, lowest-effort security fix. (2) Add connection pooling and the missing `LIMIT`s — biggest performance win for the effort. (3) Add a proper WSGI server (gunicorn) + basic Dockerfile — makes it actually deployable. (4) Add structured logging + a health-check endpoint — baseline observability. (5) Add a pytest suite starting with `app/ml/predict.py`'s pure functions — protects against regressions like the duplicate-key bug going forward.
**Reasoning**: A synthesis question forcing prioritization across security, performance, deployability, observability, and quality — tests whether you can rank, not just list.
**Tip**: Having a crisp, ordered "top 5" ready (not a laundry list) is exactly the kind of answer that ends an interview strong.

### Q99. Your app has zero automated tests. Is that actually a problem for a project at this scale, or are you over-indexing on it?
**Ideal Answer**: For a solo student project at this scale, it's a reasonable (if not ideal) trade-off — the codebase is small enough to reason about manually, and I was optimizing for shipping a complete, working feature set within a timeline. It becomes a real problem the moment more than one person touches the code, or the moment a bug like the duplicate `"Data Science"` key silently changes behavior without anyone noticing — which is exactly what happened here. So: acceptable historically, but the first thing I'd fix before this codebase grows or gets a second contributor.
**Reasoning**: Tests calibrated self-assessment — neither defensive ("tests weren't needed") nor performatively self-flagellating ("this is terrible, I should be ashamed").
**Tip**: Tying the answer back to a *real, already-discovered* bug (the duplicate key) that tests would have caught makes the argument concrete instead of abstract.

### Q100. If an interviewer says "this isn't really AI, it's just `if` statements" — how do you respond?
**Ideal Answer**: "You're right, and that's intentional, not a limitation I'm hiding from — it's a keyword-counting rule engine, not a trained model. I chose that deliberately because every prediction is 100% explainable: I can point to the exact keywords that caused any result. If I were to add a real ML layer later, I'd want to keep this rule-based system as an interpretable baseline/fallback rather than replace it outright, because losing explainability is a real cost, not just a limitation to eventually engineer away."
**Reasoning**: This is the single most likely "gotcha" framing a sharp interviewer will use, specifically to see if you get defensive or oversell your project. It tests intellectual honesty under mild pressure.
**Tip**: Agree with the premise immediately and calmly, then pivot to *why* that was a deliberate choice with a real benefit (explainability) — don't argue that it "is" AI.

### Q101. What's the single most impressive, correctly-implemented thing in this codebase, and why?
**Ideal Answer**: The complete absence of on-disk file storage for uploaded resumes — every upload is parsed entirely in memory via `io.BytesIO` and discarded after text extraction, meaning an entire category of file-upload vulnerabilities (path traversal, arbitrary file write, serving an uploaded file back as executable content) simply doesn't apply here, not because of a clever mitigation, but because the attack surface doesn't exist in the first place.
**Reasoning**: Tests whether you can identify and defend a genuine architectural strength persuasively — interviewers want to see pride backed by reasoning, not just modesty about gaps.
**Tip**: "The vulnerability doesn't apply because the attack surface doesn't exist" is a stronger, more sophisticated security argument than "I added a mitigation" — know the difference and use it here.

### Q102. What's the single riskiest thing in this codebase from a security standpoint, and why?
**Ideal Answer**: The combination of no CSRF protection and no rate limiting on `/login` — individually each is a known, moderate gap, but together they mean there's no protection against automated credential-stuffing/brute-force attempts, and no protection against a forged cross-site request. Neither is catastrophic given the app's current low-stakes data (resumes and scores, not financial data), but both are the first things I'd fix before any real user data was at stake.
**Reasoning**: Forces you to rank risks rather than list them uniformly — a hallmark of security maturity.
**Tip**: Explicitly stating "not catastrophic given the current data sensitivity, but still worth fixing first" shows calibrated risk assessment, not alarmism.

### Q103. How would you validate that your resume-scoring rubric (`compute_score`) is actually correlated with real resume quality, rather than just being "seven checks that sound reasonable"?
**Ideal Answer**: I'd want to validate it empirically — collect a set of resumes with independent human/recruiter quality ratings, compute the rule-based score for each, and check correlation between the two. If correlation were weak, I'd revisit which checks matter most (possibly re-weighting points) or consider that some checks are proxies for quality that don't actually track it well (e.g., "contains the word 'skill'" doesn't really measure skill-section *quality*, just its *presence*).
**Reasoning**: Tests whether you can think about your own metric's validity, not just its implementation — a very senior-level line of questioning.
**Tip**: Acknowledging that the current rubric is *unvalidated* (it was designed by reasonable intuition, not measured against outcomes) is the honest and correct answer — don't claim it's proven to work.

### Q104. In one sentence, what would you tell a new engineer joining this codebase to read first, and why?
**Ideal Answer**: "Start with `app/__init__.py`'s `create_app()` function — it's short, and it literally names every other important file in the project (config, models, and all three blueprints), so it's the fastest way to build a mental map before diving into any one feature."
**Reasoning**: A synthesis/communication question — tests whether you can distill onboarding guidance concisely.
**Tip**: This mirrors [10_Code_Walkthrough.md](10_Code_Walkthrough.md) — keep your answer to one crisp sentence, resist the urge to list all eight steps out loud.
