# 19 — Revision Notes (20-Minute Read Before the Interview)

## What Is JobCatch?
A Flask web app: upload a resume (PDF/DOCX) → get an instant predicted job role (out of 25), a resume quality score (0–100), found/missing skills for that role, and suggested skills to learn. Also has login/register, upload history, a dashboard, and an interview-prep Q&A page (10 of 25 roles have questions).

## Tech Stack (One Line Each)
- **Python 3 + Flask 3.0.2** — backend web framework, app factory pattern (`create_app()` in `app/__init__.py`).
- **MySQL + mysql-connector-python** — raw SQL, no ORM, two tables (`users`, `resume_uploads`).
- **Werkzeug** — password hashing (`generate_password_hash`/`check_password_hash`, scrypt) and `secure_filename()`.
- **PyPDF2 / python-docx** — extract text from PDF / DOCX, entirely in-memory (`io.BytesIO`), files never saved to disk.
- **Jinja2** — server-rendered templates, one shared `base.html`, auto-escapes output (XSS defense).
- **Vanilla CSS/JS** — no framework; dark mode via CSS variables + `data-theme` attribute + `localStorage`.
- **python-dotenv** — loads `.env` into environment variables for config.
- **`requests`** — listed in `requirements.txt` but unused anywhere in the code (leftover from planned OAuth).

## Architecture in One Diagram
```
Browser → Flask (blueprints: auth, main, resume) → app/models.py (raw SQL) → MySQL
                                                  → app/ml/predict.py + data.py (keyword engine)
```
No microservices, no ORM, no message queue, no Docker, no deployment config — a single monolithic Flask process.

## The Three Blueprints
| Blueprint | Routes |
|---|---|
| `auth_bp` | `/register`, `/login`, `/logout` |
| `main_bp` | `/`, `/dashboard` (protected), `/contact` |
| `resume_bp` | `/upload` (protected), `/history` (protected), `/interview-prep`, `/api/questions` (JSON) |

## The Two Database Tables
```
users(id PK, name, email UNIQUE, password_hash, created_at)
resume_uploads(id PK, user_id FK→users.id ON DELETE CASCADE,
                filename, upload_time, predicted_role, resume_score)
```
No `predictions` table despite a stale docstring mentioning one.

## The Core Algorithm (Memorize This Flow)
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

## Known Bugs / Gaps (Say These Proactively — They Build Trust)
1. **Duplicate `"Data Science"` key** in `ROLE_KEYWORDS` (`app/ml/data.py`) — Python silently keeps only the second definition.
2. **Substring matching, not word-boundary** — "java" matches inside "javascript."
3. **No `predictions` table** despite a docstring in `app/models.py` mentioning one.
4. **No Google OAuth** despite `.env.example` placeholders and a docstring mentioning `/login/google`.
5. **No CSRF protection** on any form.
6. **No rate limiting** on login (brute-force possible).
7. **No connection pooling** — one MySQL connection per request.
8. **No `LIMIT`** on `get_user_uploads()` — dashboard fetches all rows then slices `[:5]` in Python.
9. **No tests, no Docker, no CI/CD, no migrations** anywhere in the repo.
10. **`MAX(predicted_role)`** in `get_upload_stats()` returns the alphabetically largest role string, not necessarily the most recent one.
11. **Only 10 of 25 roles** have interview questions (`INTERVIEW_QUESTIONS`).
12. **`.docx` tables aren't read** — only `doc.paragraphs`.
13. **Scanned/image PDFs** produce no extractable text (no OCR) — handled with a flash message, not a crash.
14. **`/logout` is a GET request** — a minor CSRF surface.
15. **`/contact`** passes `scroll_to='contact'` to the template but the template never uses it — dead parameter.

## Security Cheat Facts
- Passwords: hashed (scrypt via Werkzeug), never plaintext, never encrypted-and-decrypted.
- SQL: 100% parameterized queries (`%s` placeholders) — no injection risk found.
- XSS: Jinja2 auto-escapes by default; one caveat is `innerHTML` usage in interview-prep JS (low risk, data source is static, not user input).
- Sessions: signed (via `SECRET_KEY`), not encrypted — readable but not forgeable without the key.
- Files: never written to disk — parsed fully in memory, discarded after use.
- Missing: CSRF tokens, rate limiting, HTTPS config, explicit secure cookie flags, email verification.

## Scalability — What You'd Fix First (In Order)
1. Connection pooling (`mysql.connector.pooling.MySQLConnectionPool`).
2. Add `LIMIT` to `get_user_uploads()`; add composite index `(user_id, upload_time DESC)`.
3. Move off Flask's dev server to gunicorn/uWSGI + load balancer (app is already stateless — cookie-based sessions require no sticky sessions).
4. Caching (Redis) for dashboard stats.
5. Read replicas / migrations (Alembic) / CDN for static assets — only once the above is done and still insufficient.

## Your Elevator Pitch (30 Seconds — Memorize This)
"JobCatch is a Flask app where you upload a resume and it instantly predicts your best-fit job role out of 25 categories, scores your resume out of 100, and shows what skills you have versus what's missing. The matching engine isn't a black-box AI model — it's a transparent keyword-counting algorithm, so I can explain exactly why it made every prediction."

## If Asked "Is This AI?"
Say **no** immediately and calmly: "It's rule-based keyword counting, not a trained model — a deliberate choice for full explainability." Do not get defensive. This is a trust test, not a technical test.

## The One Sentence to Start Any Code Walkthrough With
"Start with `app/__init__.py`'s `create_app()` function — it names every other important file in the project in about 30 lines."

## Files Map (Quick Reference)
```
run.py                     → entry point
app/__init__.py            → create_app() — app factory
app/config.py               → Config (env vars)
app/models.py               → all SQL, get_db/close_db/init_db
app/auth/routes.py          → register, login, logout
app/main/routes.py          → home, dashboard, contact, login_required
app/resume/routes.py        → upload, history, interview_prep, get_questions
app/ml/data.py               → ROLE_KEYWORDS, INTERVIEW_QUESTIONS, SUGGESTED_SKILLS
app/ml/predict.py            → clean_text, predict_role, compute_score,
                                extract_skills, get_suggested_skills, analyze_resume
templates/base.html          → shared layout
static/css/style.css         → all styling (~1078 lines)
static/js/main.js            → hamburger menu + dark mode toggle
```

## Last-Minute Confidence Boosters (What You Did Right)
- Files are never saved to disk — a real, deliberate security strength.
- Aggregate stats (`get_upload_stats`) computed in one SQL query, not pulled into Python.
- Every SQL query is parameterized — zero injection risk.
- `predict.py` has zero Flask dependencies — clean separation of business logic from web framework.
- The app is honest by design: unmatched resumes fall back to `"General / Other"` instead of forcing a wrong guess.
