# 17 — Resume Questions (50+ Questions an Interviewer Could Ask If This Is On Your Resume)

If your resume has a line like *"Built JobBridge — a Flask-based resume analysis platform with MySQL, achieving resume scoring and 25-role prediction"*, expect questions like these. Answers are short and resume-defense-oriented — pair with the deeper docs referenced for follow-up depth.

### Project Scope & Ownership
1. **Did you build this alone?** — Yes, solo project (per the "Meet the Team" section listing a single developer, Radhika Gurjar, and the README's "Developer" credit).
2. **How long did it take you to build?** — (Answer based on your own actual timeline — the git history shows two commits, so be ready to explain your real development process, e.g. local iteration before committing.)
3. **What was the hardest part to build?** — A strong, honest answer: getting reliable text extraction across both PDF and DOCX formats, and designing a scoring rubric that felt fair without a labeled dataset to validate against.
4. **What would you do differently if you started over?** — Add tests from day one, especially for `app/ml/predict.py`, to catch issues like the duplicate `"Data Science"` dictionary key immediately.
5. **Is this project deployed anywhere live?** — No — there's no deployment configuration (no Dockerfile, no cloud config) in the repository; it currently only runs locally via `python run.py`.

### Architecture & Design Decisions
6. **Why did you structure the app with blueprints?** — To separate auth, main pages, and resume features into independently readable modules as the app grew past a handful of routes.
7. **What is the Application Factory pattern and why use it?** — `create_app()` builds the Flask app on demand instead of at import time, supporting different configs (e.g., testing vs. production) without side effects.
8. **Why no ORM?** — Two tables, simple queries — raw SQL kept everything transparent and avoided ORM overhead/learning curve for a project this size.
9. **How is your code organized?** — Feature-folder blueprints (`auth/`, `main/`, `resume/`) plus two shared layers: `models.py` (data access) and `ml/` (business logic), see [05_Folder_Structure.md](05_Folder_Structure.md).
10. **What design pattern does your `login_required` decorator use?** — The decorator pattern — wraps a view function to inject an authentication check before it runs, using `functools.wraps` to preserve the original function's identity for Flask's routing.

### The Core "AI" Feature
11. **Explain your resume-matching algorithm in detail.** — See [09_Features.md](09_Features.md) "Role Prediction Engine" — keyword-counting against a 25-role dictionary, highest count wins, `"General / Other"` fallback if nothing matches.
12. **Is this real machine learning?** — No, and I'm upfront about that — it's rule-based and 100% explainable, a deliberate choice over an opaque model.
13. **How accurate is your prediction algorithm?** — Honestly, this has never been formally measured against a labeled dataset — there's no accuracy metric computed anywhere in the project. If asked to improve it, I'd build a labeled test set first.
14. **What's a known weakness of your algorithm?** — Substring matching causes false positives (e.g., "java" matches inside "javascript").
15. **How many job roles do you support, and how did you choose them?** — 25 roles, covering a broad mix of tech and non-tech careers (e.g., Python Developer, HR, Civil Engineer, Sales) — a broad net rather than a narrow tech-only focus.
16. **Why only 10 of 25 roles have interview questions?** — Time constraints during development — the interview-prep content set is intentionally incomplete today, and the app handles the gap gracefully (empty state message) rather than erroring.
17. **How do you score a resume?** — Seven weighted structural checks (email, phone, skills, education, experience, length, projects) summing to 100 — see [09_Features.md](09_Features.md).
18. **Could someone game your scoring system?** — Yes — since checks are substring/regex based (e.g., just including the literal word "skill" anywhere), a resume could technically pad itself with trigger words without real substance and still score well. This is a known limitation of any keyword-based rubric.

### Database
19. **What database did you use and why?** — MySQL, chosen for its relational fit (users → many uploads) and familiarity/support.
20. **Describe your schema.** — Two tables: `users` and `resume_uploads`, linked by a foreign key with `ON DELETE CASCADE` — see [07_Database.md](07_Database.md).
21. **How do you prevent SQL injection?** — Parameterized queries (`%s` placeholders) everywhere, no string-built SQL.
22. **How do you manage the database connection lifecycle?** — Request-scoped via Flask's `g` object, opened lazily and closed via `teardown_appcontext`.
23. **Do you use migrations?** — No — `init_db()` uses `CREATE TABLE IF NOT EXISTS`, which is fine for a fresh database but not a substitute for versioned migrations if the schema needed to evolve against a populated production database.
24. **What indexes exist on your tables?** — Primary keys on both `id` columns, a unique index on `users.email`, and an implicit index on `resume_uploads.user_id` from the foreign key (InnoDB requires this). No explicit index on `upload_time` yet.

### Authentication & Security
25. **How do you handle authentication?** — Session-based, with Werkzeug-hashed passwords (scrypt) and a custom `login_required` decorator.
26. **Do you use JWT?** — No — session cookies, appropriate for this same-origin server-rendered app.
27. **Is there CSRF protection?** — No, a known gap — I'd add Flask-WTF's `CSRFProtect`.
28. **How are passwords stored?** — Hashed via `werkzeug.security.generate_password_hash()`, never plaintext.
29. **What happens on failed login?** — A generic "incorrect email or password" message — deliberately not revealing which part was wrong, to avoid user enumeration.
30. **Is there rate limiting on login attempts?** — No — a real gap I'd close with Flask-Limiter.
31. **What security review would you do before shipping this to production?** — See [12_Security.md](12_Security.md) — CSRF, rate limiting, HTTPS enforcement, and secure cookie flags would be the top priorities.

### File Handling
32. **How do you handle file uploads?** — Accepted in-memory only (never saved to disk), parsed via PyPDF2/python-docx, and discarded after text extraction.
33. **What file types and size limits do you support?** — PDF and DOCX, up to 5MB, enforced via Flask's `MAX_CONTENT_LENGTH`.
34. **What happens with a scanned/image-only PDF?** — No text can be extracted (PyPDF2 has no OCR), so the user gets a clear flash message rather than a broken result.
35. **Do you validate file content, not just the extension?** — No — only the extension is checked; a real fix would add MIME-type sniffing (e.g., `python-magic`).

### Testing & Quality
36. **Do you have automated tests?** — No, honestly — a real gap I'd prioritize fixing, starting with the pure functions in `app/ml/predict.py` since they have no external dependencies and are easy to unit test.
37. **How did you verify correctness without tests?** — Manual testing through the UI during development (be ready to describe your actual manual testing process).
38. **What's a bug you found while reviewing your own code for this interview?** — The duplicate `"Data Science"` key in `ROLE_KEYWORDS` — Python silently keeps only the second occurrence, meaning part of the intended keyword list was dead code.
39. **How would you catch that kind of bug automatically in the future?** — A simple test asserting `len(ROLE_KEYWORDS) == 25` (the expected unique role count) would fail immediately if a duplicate key silently reduced that count.

### Frontend
40. **What frontend framework did you use?** — None — vanilla HTML/CSS/JS with Jinja2 server-rendered templates, deliberately, since the app's interactivity needs are small.
41. **How does dark mode work?** — CSS custom properties toggled via a `data-theme` attribute, persisted in `localStorage`.
42. **Is any part of your frontend using AJAX/fetch?** — Yes, exactly one place — the interview-prep page's role dropdown fetches `/api/questions` as JSON without a full page reload.
43. **Why didn't you use React/Vue?** — The app is fundamentally server-rendered CRUD pages with minimal client interactivity — a full frontend framework would be unnecessary complexity for this scope.

### Scalability & Deployment
44. **Is this deployed anywhere?** — No — local development only (`python run.py`), no Dockerfile, no cloud config.
45. **How would you deploy this to production?** — Gunicorn behind Nginx (or a managed platform), managed MySQL (e.g., RDS), environment-based secrets, HTTPS termination at the proxy layer.
46. **How would this scale to many concurrent users?** — See [13_Scalability.md](13_Scalability.md) — connection pooling and query/indexing fixes first, then horizontal scaling (the app is already stateless thanks to cookie-based sessions), then caching/read replicas as needed.
47. **What's the biggest performance bottleneck today?** — No connection pooling (a new MySQL connection per request) and an unbounded `get_user_uploads()` query used by both `/history` and the dashboard.

### Honesty / Self-Awareness Checks
48. **What does your README claim that isn't fully true in the code?** — It references Google OAuth login and a `predictions` table (via code comments/env vars) that don't actually exist in the implementation — I'd flag this drift and either build them or update the docs.
49. **What's the single thing you're least confident about in this project?** — Being upfront here is the right move — e.g., "the resume-scoring rubric's point values were chosen by intuition, not validated against real recruiter judgments, so I can't claim it's empirically accurate."
50. **If I opened your code right now, what's the first thing that would embarrass you?** — A strong, senior-sounding answer: "Probably the lack of tests, and the duplicate `Data Science` dictionary key — both are things I'd fix first, and both are things I found by re-reading my own code carefully rather than something a reviewer had to catch for me."
51. **Would you put this project on your resume again, knowing its gaps?** — Yes — it demonstrates full-stack fundamentals (auth, file processing, database design, a from-scratch matching algorithm) end-to-end, and being able to discuss its real limitations honestly is itself valuable interview material.
52. **What did you learn building this that you'd apply to your next project?** — A genuine, personal answer works best here — e.g., "the value of writing tests alongside features, not after," or "how much a small data bug (the duplicate key) can silently change behavior without any error being raised."
