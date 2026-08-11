# 20 — Cheat Sheet (Compact Reference)

## Project Summary
Flask app: upload resume (PDF/DOCX) → predicts 1 of 25 job roles via keyword counting → scores resume 0–100 (7 checks) → shows found/missing skills → suggests next skills → saves to MySQL → dashboard/history tracks it over time → separate interview-prep page (10/25 roles have Q&A).

## Architecture
```
Browser → Flask (auth_bp, main_bp, resume_bp) → app/models.py (raw SQL) → MySQL
                                               → app/ml/{data,predict}.py (keyword engine)
```
App Factory pattern (`create_app()`). No ORM. No microservices. No Docker. Dev server only (`python run.py`).

## Tech Stack
| Layer | Tech |
|---|---|
| Backend | Python 3, Flask 3.0.2, Werkzeug |
| DB | MySQL, `mysql-connector-python` (raw SQL) |
| File parsing | PyPDF2 (PDF), python-docx (DOCX) |
| Templates | Jinja2 |
| Frontend | Vanilla HTML/CSS/JS, no framework |
| Config | `python-dotenv` + `.env` |
| Auth | Session cookies + Werkzeug password hashing (scrypt) |

## Database
```
users(id PK, name, email UNIQUE, password_hash, created_at)
   │ 1:N (ON DELETE CASCADE)
resume_uploads(id PK, user_id FK, filename, upload_time,
                predicted_role, resume_score)
```
No `predictions` table (despite a stale docstring). No migrations. No explicit index on `upload_time`.

## APIs
| Method | Path | Auth | Returns |
|---|---|---|---|
| GET/POST | `/register`, `/login` | No | HTML |
| GET | `/logout` | No | Redirect |
| GET | `/dashboard` | Yes | HTML |
| GET/POST | `/upload` | Yes | HTML |
| GET | `/history` | Yes | HTML |
| GET | `/interview-prep` | No | HTML |
| GET | `/api/questions?role=` | No | **JSON** (only real API) |

## Authentication
- Register/Login → `werkzeug.security` scrypt hash → Flask session (`user_id`, `user_name`, `user_email`), signed not encrypted.
- `login_required` decorator (in `main/routes.py`, reused in `resume/routes.py`) guards `/dashboard`, `/upload`, `/history`.
- No JWT, no OAuth (despite env var placeholders), no CSRF, no rate limiting.

## Major Features & Core Functions
| Feature | Function | File |
|---|---|---|
| Role prediction | `predict_role()` | `app/ml/predict.py` |
| Resume scoring | `compute_score()` | `app/ml/predict.py` |
| Skill gap | `extract_skills()` | `app/ml/predict.py` |
| Suggested skills | `get_suggested_skills()` | `app/ml/predict.py` |
| Orchestrator | `analyze_resume()` | `app/ml/predict.py` |
| Text extraction | `extract_text()` | `app/resume/routes.py` |
| DB connection | `get_db()`/`close_db()` | `app/models.py` |

## Algorithm (Memorize)
```
clean_text() → strip URLs, keep [a-z0-9/+#.], lowercase
predict_role() → count keyword hits per role (25 roles) → argmax
                  → "General / Other" if all 0
compute_score() → 7 checks: email(15) phone(15) skills(20) education(15)
                   experience(15) 250+words(10) projects(10) = 100 max
extract_skills() → found vs missing keywords for predicted role
```

## Challenges (Real Bugs You Can Cite)
- Duplicate `"Data Science"` key in `ROLE_KEYWORDS` → second silently wins.
- Substring matching → "java" false-positives inside "javascript".
- `MAX(predicted_role)` in `get_upload_stats()` ≠ most recent role (alphabetical max, not latest).
- `get_user_uploads()` has no `LIMIT` — dashboard over-fetches then slices `[:5]` in Python.
- Only 10/25 roles have interview questions.
- `.docx` tables not read (only paragraphs).
- No OCR for scanned PDFs (handled gracefully with a flash message).

## Scalability (Priority Order for 1M Users)
1. Connection pooling.
2. Add `LIMIT`/index to upload queries.
3. Gunicorn + load balancer (already stateless — cookie sessions).
4. Redis caching for dashboard stats.
5. Read replicas / Alembic migrations / CDN for static assets.

## Security Status
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

## Most-Asked Interview Questions (Rapid Fire)
1. "Is this AI?" → No — rule-based keyword counting, chosen for full explainability.
2. "Why Flask over Django?" → Lightweight, only needed routing/templates/sessions; I wanted my own SQL/auth.
3. "Why no ORM?" → Two tables, raw SQL kept it transparent and simple to explain.
4. "SQL injection?" → Not vulnerable — every query uses `%s` parameterized placeholders.
5. "Biggest weakness in your algorithm?" → Substring matching (java/javascript false positive) + the duplicate dict-key bug.
6. "Where are uploaded files stored?" → Nowhere — parsed in-memory, never written to disk.
7. "CSRF protection?" → No, known gap, would add Flask-WTF.
8. "How would this scale to 1M users?" → Pooling + query limits first, then horizontal scaling (already stateless), then caching/replicas.
9. "Tests?" → None currently — would start with `app/ml/predict.py`'s pure functions.
10. "What's the `predictions` table?" → Mentioned in a stale docstring, never actually created — prediction lives as a column on `resume_uploads` instead.

## 30-Second Pitch
"JobCatch is a Flask app where you upload a resume and it instantly predicts your best-fit job role out of 25 categories, scores your resume out of 100, and shows what skills you have versus what's missing. The matching engine isn't a black-box AI model — it's a transparent keyword-counting algorithm, so I can explain exactly why it made every prediction."
