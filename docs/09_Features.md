# 09 — Features (Deep Dive)

## Feature: Authentication (Register / Login / Logout)

**Purpose**: Identify users so their uploads and stats can be tracked individually.

**Business logic**: A user is a name + unique email + hashed password. Registration doubles as login (no email verification step). Session state (`user_id`, `user_name`, `user_email`) is the only thing that distinguishes "logged in" from "logged out" anywhere in the app.

**Files involved**: `app/auth/routes.py`, `app/models.py`, `templates/login.html`, `templates/register.html`.

**Important functions**: `register()`, `login()`, `logout()`, `get_user_by_email()`, `create_user()`.

**Execution flow**: see [04_Application_Flow.md](04_Application_Flow.md) Features 1–3.

**Edge cases**:
- Two users racing to register the same email simultaneously — the app checks for a duplicate *before* inserting, but doesn't wrap the insert in a `try/except` for the `UNIQUE` constraint, so a true race condition would surface as an unhandled `mysql.connector.IntegrityError` (500 error), not a friendly flash message.
- No password complexity rules beyond a 6-character minimum — `"aaaaaa"` is a valid password.
- No account lockout / rate limiting on login attempts — a script could brute-force a password with unlimited attempts.
- Logging out is a `GET` request (see [08_APIs.md](08_APIs.md)) — theoretically forgeable via a cross-site request, though the impact (forced logout) is low-severity.

**Future improvements**: email verification (send a confirmation link before allowing login), password strength meter, "forgot password" flow, rate-limiting on `/login` (e.g. via Flask-Limiter), converting `/logout` to a `POST` with CSRF protection.

---

## Feature: Resume Upload & Text Extraction

**Purpose**: Accept a PDF or DOCX resume and turn it into plain text the analysis engine can work with.

**Business logic**: Only two file types are accepted; files are read entirely in memory (never written to disk); a 5 MB size ceiling is enforced by Flask config; if no text can be extracted (e.g., the PDF is a scanned image with no text layer), the user is told rather than silently getting a broken/empty analysis.

**Files involved**: `app/resume/routes.py` (`allowed_file`, `extract_text`, `upload`), `templates/upload.html`.

**Important functions**: `allowed_file(filename)`, `extract_text(file)`.

**Execution flow**: see [04_Application_Flow.md](04_Application_Flow.md) Feature 4.

**Edge cases**:
- A `.pdf` file that's actually corrupted/not a real PDF → `PdfReader` would raise an exception, caught by the surrounding `try/except Exception as e` in `upload()`, shown as a flash message including the raw exception text (a minor information-disclosure smell, but not exploitable for injection since Jinja auto-escapes it).
- A password-protected PDF → `PdfReader` would likely raise or return unreadable content; same generic catch-all handles it, though the message wouldn't specifically say "this PDF is password-protected."
- A `.docx` file with all its content inside **tables** rather than paragraphs → `extract_text()` only reads `doc.paragraphs`, so table content would be silently missed, potentially causing an inaccurate (lower) score/prediction with no warning to the user.
- File extension spoofing (e.g., renaming a `.exe` to `.pdf`) → `allowed_file()` only checks the extension string, not the actual file content/MIME type; a spoofed file would still fail at `PdfReader`/`Document` parsing and be caught by the generic exception handler, so it wouldn't be *executed*, just rejected with a generic error — no real security risk since the file is never saved or executed, only parsed as text.

**Future improvements**: OCR fallback for scanned PDFs (e.g. `pytesseract`), reading `.docx` tables too, real MIME-type sniffing (e.g. `python-magic`) in addition to extension checking, more specific error messages per failure type.

---

## Feature: Role Prediction Engine

**Purpose**: Guess which of 25 job roles best matches a resume's content, using a fully transparent algorithm.

**Business logic**: Each role has a hand-curated list of ~15 lowercase keywords/phrases (`ROLE_KEYWORDS` in `app/ml/data.py`). The resume text is cleaned (URLs stripped, non-alphanumeric characters removed except `/+#.` which matter for tokens like `c#`, `.net`, `node.js`-style terms) and lowercased. For each role, the algorithm counts how many of its keywords appear anywhere as a substring of the cleaned text, and the role with the highest count wins (`max(scores, key=scores.get)`). If every role scores zero, the result falls back to `"General / Other"`.

**Files involved**: `app/ml/predict.py` (`clean_text`, `predict_role`), `app/ml/data.py` (`ROLE_KEYWORDS`).

**Important functions**: `predict_role(resume_text)`.

**Execution flow**:
```
resume_text
   ↓
clean_text() — strip URLs, keep [a-zA-Z0-9\s/+#.], collapse whitespace, lowercase
   ↓
for each of 25 roles:
     count = number of that role's keywords found as substrings in cleaned text
   ↓
predicted_role = role with max(count)
   ↓
if max count == 0 → "General / Other"
```

**Edge cases**:
- **Substring matching, not word-boundary matching**: `"java"` as a keyword would also match inside `"javascript"` (since `"java" in "javascript resume"` is `True` in Python). This means a JavaScript-heavy resume with no actual Java experience could contribute a false-positive point toward "Java Developer." This is a real, demonstrable limitation of the algorithm and a *very* likely interview question.
- **Ties**: if two roles have the exact same keyword count, `max()` deterministically returns the **first** one in dictionary insertion order (Python dicts preserve insertion order since 3.7) — not randomly, but also not by any deeper "confidence" logic.
- **Duplicate dictionary key**: `ROLE_KEYWORDS` literally contains the key `"Data Science"` **twice** in `app/ml/data.py` (once around line 23 with `jupyter` in its keyword list, once around line 60 with `nlp`, `deep learning`, `neural network` instead). In a Python dict literal, the **second occurrence silently overwrites the first** at parse time — so the actual runtime keyword list for "Data Science" is the second block; the first block's keywords (including `jupyter`) are effectively dead code and never used for matching. This is a genuine bug/oversight in the source data, and a great "what would you fix" answer for [14_Challenges_and_Improvements.md](14_Challenges_and_Improvements.md).
- No weighting by keyword importance or resume section (a keyword found in a "Skills" heading counts the same as one found in a random sentence).

**Future improvements**: word-boundary-aware regex matching (`\bjava\b` instead of substring `in`) to fix the Java/JavaScript problem, TF-IDF or embedding-based similarity instead of raw counting, confidence scores shown to the user (not just the winning role), de-duplicating the `"Data Science"` key.

---

## Feature: Resume Scoring (0–100)

**Purpose**: Give an objective, structural quality score independent of which role is predicted.

**Business logic**: Seven independent checks, each worth a fixed number of points that sum to exactly 100:
| Check | Points | How it's detected |
|---|---|---|
| Has email address | 15 | regex `[\w.-]+@[\w.-]+\.\w+` |
| Has phone number | 15 | regex `(\+?\d[\d\s\-]{8,}\d)` |
| Has Skills section | 20 | substring `'skill'` present |
| Has Education section | 15 | any of `education, degree, university, college, bachelor, master` |
| Has Experience section | 15 | any of `experience, work history, employment, internship` |
| Sufficient length (250+ words) | 10 | `len(resume_text.split()) >= 250` |
| Has Projects/Achievements | 10 | any of `project, achievement, built, developed, designed` |

**Files involved**: `app/ml/predict.py::compute_score`.

**Execution flow**: run all 7 checks independently on the raw (uncleaned — note this uses `resume_text.lower()`, not the URL-stripped `clean_text()` used elsewhere) text → sum points for passed checks → return `{"score": total, "details": [...]}` for the UI's pass/fail breakdown.

**Edge cases**:
- A resume that says "no experience yet, currently a fresher" would still score the 15 "Has Experience section" points, because the check only looks for the *word* "experience," not actual work history content — a false positive by design of simple keyword matching.
- The "Skills" check triggers on the substring `'skill'` anywhere — even inside an unrelated sentence like "I want to upskill my abilities" — again a substring-matching limitation, not a semantic one.
- Phone regex requires at least 10 digits total (`{8,}` between the first and last digit means at least 10 digits overall) — an unusually short or oddly formatted number could fail to match even if a human would recognize it as a phone number.

**Future improvements**: section-header detection (looking for text that's actually formatted like a heading, not just any occurrence of a keyword), configurable point weights, more nuanced length/format checks (e.g. bullet point density, consistent date formats).

---

## Feature: Skill Gap Analysis (Found vs. Missing Skills)

**Purpose**: Once a role is predicted, tell the user exactly which of that role's expected keywords are present in their resume and which are absent.

**Business logic**: Reuses the same `ROLE_KEYWORDS[role]` list used for prediction — `found` = keywords present in the cleaned text, `missing` = the rest. This is a direct, honest consequence of the same keyword list driving both prediction *and* gap analysis — the two features are not independent, which is worth pointing out if asked how prediction and skill-gap analysis relate.

**Files involved**: `app/ml/predict.py::extract_skills`.

**Execution flow**: `clean_text(resume_text)` → for each keyword in the predicted role's list, check substring membership → split into `found`/`missing` lists, preserving the original keyword order from `ROLE_KEYWORDS`.

**Edge cases**: if the predicted role is `"General / Other"` (not a key in `ROLE_KEYWORDS`), `extract_skills` returns `([], [])` — no found/missing skills are shown, and the template correctly falls back to its "no matching skills found" message.

**Future improvements**: show found/missing skills for the *second-best* role too (in case the top prediction was close), let the user manually pick a different target role to see a gap analysis against it instead of only the auto-predicted one.

---

## Feature: Suggested Skills

**Purpose**: Recommend forward-looking, "next skills to learn" for the predicted role — distinct from the *current* keyword requirements, aimed at career growth.

**Business logic**: A static dictionary, `SUGGESTED_SKILLS` in `app/ml/data.py`, maps each of the 25 roles to 4–5 trending skill names (e.g., "Python Developer" → `FastAPI, Docker, PostgreSQL, Redis, AWS Lambda`). Unlike `ROLE_KEYWORDS`, these are **not** cross-checked against the resume at all — they are shown unconditionally for the predicted role.

**Files involved**: `app/ml/predict.py::get_suggested_skills`, `app/ml/data.py::SUGGESTED_SKILLS`.

**Edge cases**: `"General / Other"` has no entry in `SUGGESTED_SKILLS`, so `.get(role, [])` returns an empty list, and the template's `{% if results.suggested_skills %}` correctly hides the whole section.

**Future improvements**: keep this list current (these are hand-curated and will age — e.g., today's "trending" skill list will look dated in a couple of years without maintenance).

---

## Feature: Dashboard & Upload History

**Purpose**: Let a user see aggregate stats (total uploads, average score, latest role, last upload date) and browse every past upload.

**Business logic**: Purely derived from `resume_uploads` rows for the logged-in user — no separate caching or pre-computed aggregate table; every dashboard load runs a fresh `COUNT`/`AVG`/`MAX` SQL query.

**Files involved**: `app/main/routes.py::dashboard`, `app/resume/routes.py::history`, `app/models.py` (`get_upload_stats`, `get_user_uploads`), `templates/dashboard.html`, `templates/history.html`.

**Edge cases**: A brand-new user with zero uploads — `get_upload_stats()` still returns a row (from `COUNT(*)` which is `0` for no matches, but `MAX`/`AVG` over zero rows return `NULL`) — the template handles this with `{{ stats.avg_score or 0 }}` and `{{ stats.last_role or '—' }}` fallbacks, so the dashboard renders cleanly rather than crashing on `None`.

**Future improvements**: pagination on `/history` (currently returns *all* rows, unbounded), a chart of score trend over time, ability to delete individual upload records.

---

## Feature: Interview Prep

**Purpose**: Let anyone (not just logged-in users) study curated interview Q&A for a specific role.

**Business logic**: `INTERVIEW_QUESTIONS` (in `app/ml/data.py`) only covers **10 of the 25** roles with 5 Q&A pairs each. The page fetches questions asynchronously via `/api/questions` rather than server-rendering them, so switching roles doesn't require a full page reload.

**Files involved**: `app/resume/routes.py` (`interview_prep`, `get_questions`), `templates/interview_prep.html`.

**Edge cases**: selecting one of the 15 roles *without* curated questions returns `[]` and the UI shows "No questions available for this role yet." gracefully — this is handled correctly in the frontend JS (`if (questions.length === 0) { ... }`), so it's not a bug, just an intentionally incomplete content set.

**Future improvements**: fill in Q&A for the remaining 15 roles, let users mark questions as "mastered," track which questions a user has practiced (would need a new DB table linking `user_id` + `question_id`).
