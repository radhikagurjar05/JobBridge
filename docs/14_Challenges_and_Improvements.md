# 14 — Challenges & Improvements

## Realistic Technical Challenges (Grounded in the Actual Code)

### Challenge 1: Substring Keyword Matching Produces False Positives
**Problem**: `predict_role()` and `extract_skills()` both check `kw in cleaned_text` — plain Python substring membership. The keyword `"java"` matches inside `"javascript"`; the keyword `"skill"` (used in `compute_score`) matches inside `"upskill"`.
**Cause**: the simplest possible implementation of "does this keyword appear" is substring search, not word-boundary-aware matching. It was likely chosen for speed of development and easy explainability.
**Solution**: use regex with word boundaries, e.g. `re.search(r'\bjava\b', text)` instead of `'java' in text`, for every keyword check across `predict_role`, `extract_skills`, and the `compute_score` substring checks.
**Learning**: "simple" and "correct" aren't the same thing — a naive string-matching approach can look like it works in demos (most test resumes won't happen to contain "javascript" when checking for "java") while silently being wrong in edge cases. This is a great example to discuss when asked about testing/edge-case thinking.

### Challenge 2: Duplicate Dictionary Key Silently Overwrites Data
**Problem**: `ROLE_KEYWORDS` in `app/ml/data.py` defines `"Data Science"` twice (once near the top of the dict with `jupyter` in its keyword list, once later with `nlp`, `deep learning`, `neural network` instead). Python dict literals silently keep only the **last** assignment for a repeated key — no error, no warning.
**Cause**: likely a copy-paste or merge mistake while iteratively adding roles to the dictionary, that was never caught because Python doesn't error on duplicate literal keys.
**Solution**: merge both keyword lists into one canonical `"Data Science"` entry (dedup the union of both keyword lists), and consider adding a small startup check (e.g., asserting `len(ROLE_KEYWORDS) == <expected count>`, or writing the dict from a validated list-of-tuples) to catch this class of mistake automatically in the future.
**Learning**: shows the value of **static analysis / linting** — a tool like `pylint` (with `W0130`-type duplicate-key checks) or even a simple unit test asserting the count of unique roles would have caught this immediately. It's a good, honest answer to "did you write any tests?" — "no, and this exact kind of bug is why I should have."

### Challenge 3: Scanned/Image-Only PDFs Produce No Extractable Text
**Problem**: `PyPDF2.PdfReader.extract_text()` can only read text that exists as actual text objects in the PDF — it cannot read text baked into an image (a scanned resume).
**Cause**: PyPDF2 has no OCR capability; this is a fundamental limitation of the library choice, not a bug.
**Solution**: the app **does** handle this gracefully today — `if not resume_text.strip(): flash('Could not extract text... Make sure it is not a scanned image PDF.')` — so the user isn't silently given a wrong/empty analysis. A deeper fix would integrate OCR (e.g. `pytesseract` + `pdf2image`) as a fallback when direct text extraction returns nothing.
**Learning**: good defensive coding doesn't always mean "solve the underlying limitation" — sometimes the right first step is "detect the failure clearly and tell the user," which is exactly what was done here, before deciding whether the deeper fix (OCR) is worth the added complexity/dependency weight.

### Challenge 4: `.docx` Table Content Is Never Extracted
**Problem**: `extract_text()`'s DOCX branch only reads `doc.paragraphs` — any resume content placed inside a Word **table** (a common way to lay out a two-column resume) is invisible to the algorithm.
**Cause**: `python-docx`'s simplest API (`.paragraphs`) doesn't recurse into tables by default; you have to explicitly also iterate `doc.tables`.
**Solution**: extend `extract_text()` to also loop `doc.tables`, iterating each table's rows/cells and extracting their paragraph text too.
**Learning**: library APIs often have a "simple/obvious" method that covers the common case but silently misses valid document structures — reading the library's docs fully (not just the first example) matters.

### Challenge 5: No Database Connection Pooling
**Problem**: `get_db()` opens a brand-new `mysql.connector.connect()` for every request that touches the database (once per request, reused within that request via `flask.g`, but never across requests).
**Cause**: this is the simplest correct pattern for a small app and was likely chosen for clarity over performance, which is a reasonable trade-off at this project's scale.
**Solution**: introduce `mysql.connector.pooling.MySQLConnectionPool` (or move to SQLAlchemy's engine, which pools by default) so connections are reused across requests instead of opened/closed constantly.
**Learning**: the right complexity level depends on scale — pooling would be premature optimization for a project handling a handful of concurrent users, but it's the *first* infrastructure change needed before this app could handle real production traffic (see [13_Scalability.md](13_Scalability.md)).

### Challenge 6: Comment/Docstring Drift From Actual Implementation
**Problem**: two places in the codebase have comments describing functionality that doesn't actually exist: (1) `app/models.py`'s module docstring mentions a `predictions` table that `init_db()` never creates; (2) `app/auth/routes.py`'s module docstring mentions `/login/google` and `/login/google/callback` routes that don't exist anywhere in the file.
**Cause**: these were likely planned features, documented in a comment while the author was thinking through the design, and then either descoped or never got to before the project was submitted/shared.
**Solution**: either implement the missing pieces, or update the docstrings to match reality — stale comments are worse than no comments because they actively mislead the next reader.
**Learning**: this is exactly the kind of drift a senior engineer is trained to notice, and calling it out proactively (rather than letting an interviewer discover it and ask "wait, where's this table?") is a strong signal of code-reading discipline.

### Challenge 7: `/upload`'s POST Handler Re-renders Instead of Redirecting (No PRG Pattern)
**Problem**: a successful `POST /upload` re-renders `upload.html` directly with the results, rather than redirecting to a separate results URL (the "Post/Redirect/Get" pattern). This means refreshing the results page in some browsers will prompt to resubmit the form.
**Cause**: simplest way to pass the `results` dict to the template without inventing a way to persist it between a redirect and the next GET (e.g., flashing a complex object, or storing an upload ID in the URL and re-querying by ID).
**Solution**: after `save_upload()` returns the new row's ID, redirect to something like `/upload/results/<upload_id>`, which re-queries and re-renders using that ID — avoiding resubmission-on-refresh entirely.
**Learning**: a good example of a small UX rough edge that doesn't affect correctness but would come up in a "how would you improve this" conversation.

## Future Improvements (Beyond the Challenges Above)

### Optimization Ideas
- Add the composite index `(user_id, upload_time DESC)` on `resume_uploads` for faster history/dashboard queries.
- Push the "recent 5 uploads" `LIMIT` into SQL instead of fetching all rows and slicing in Python (`get_user_uploads(user_id)[:5]` in `dashboard()`).
- Cache dashboard aggregate stats briefly (Redis, short TTL) for frequently-visited dashboards.

### Performance Improvements
- Move to connection pooling (see Challenge 5).
- Serve static assets via a CDN instead of directly from Flask.
- Self-host Font Awesome/Google Fonts to remove the external CDN round-trip on every page load.

### Maintainability Improvements
- Add a test suite (currently **zero** automated tests exist) — start with unit tests for the pure functions in `app/ml/predict.py` (easiest to test since they have no Flask/DB dependency), then integration tests for the routes using Flask's test client.
- Fix the duplicate `"Data Science"` key and add a simple assertion/test guarding against future duplicate-key regressions.
- Reconcile docstrings with actual implemented routes/tables (Challenge 6).
- Add type hints to function signatures in `app/ml/predict.py` and `app/models.py` for clearer contracts (e.g. `def predict_role(resume_text: str) -> tuple[str, dict[str, int]]:`).
- Introduce a proper migration tool instead of `CREATE TABLE IF NOT EXISTS`.

### Feature-Level Future Improvements
- Fill in `INTERVIEW_QUESTIONS` for the remaining 15 of 25 roles.
- Add word-boundary-aware matching to fix the Java/JavaScript-style false positives.
- Add a "forgot password" flow and email verification.
- Add pagination to `/history`.
- Add CSRF protection (Flask-WTF) and rate limiting (Flask-Limiter) — see [12_Security.md](12_Security.md).
