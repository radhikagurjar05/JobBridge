# 18 — Weak Areas (Topics You MUST Understand Before the Interview)

This document ranks the topics most likely to expose a shallow understanding if you didn't build this project yourself. Study these in order.

## Tier 1 — Non-Negotiable (Will Almost Certainly Come Up)

### 1. The Keyword-Matching Algorithm, Including Its Flaws
**Why risky**: This is the "headline feature" of the project — any interviewer will ask about it, and a shallow answer ("it checks keywords") will invite immediate follow-ups you need to survive.
**What to actually know**: The exact flow in `predict_role()` (`clean_text` → count per role → `max()` → `"General / Other"` fallback), the substring-matching false-positive problem (java/javascript), and the duplicate `"Data Science"` dictionary key bug.
**Why it matters**: Being able to name a specific, real flaw in your own algorithm — unprompted — is one of the highest-signal things you can do in this interview. See [09_Features.md](09_Features.md) and [15_TCS_Digital_Interview_QA.md](15_TCS_Digital_Interview_QA.md) Q40–42.

### 2. "Is This AI?" — The Honesty Question
**Why risky**: The README calls it "AI-Powered." Interviewers specifically probe buzzword projects to see if the candidate overclaims. Getting defensive here is the single most damaging thing you can do.
**What to actually know**: It's rule-based keyword counting, not a trained model. Say this plainly and immediately, then pivot to *why* that was a deliberate, defensible choice (explainability). See [16_Cross_Questions.md](16_Cross_Questions.md) Chain 2.
**Why it matters**: This tests intellectual honesty, not technical depth — and it's an easy trap if you haven't rehearsed the honest answer out loud beforehand.

### 3. SQL Injection Defense (Parameterized Queries)
**Why risky**: Any project touching a database gets asked this. You need to point at *actual code*, not recite the concept abstractly.
**What to actually know**: Every query in `app/models.py` uses `%s` placeholders with values passed as a separate tuple to `cursor.execute()` — never string concatenation or f-strings. Be ready to contrast this with what an unsafe version would look like.
**Why it matters**: This is one of the few areas where the code is unambiguously *correct* — a confident, precise answer here builds credibility for the rest of the interview.

### 4. Password Hashing (Not Encryption)
**Why risky**: Candidates often confuse "hashing" and "encryption," which is an instant red flag to a technical interviewer.
**What to actually know**: `generate_password_hash()`/`check_password_hash()` from Werkzeug, scrypt-based, one-way (not reversible) — hashing, never encryption. Passwords are never decrypted for comparison; the *input* password is re-hashed and the hashes are compared.
**Why it matters**: Getting this exactly right (one-way hash vs. reversible encryption) is a basic but frequently-botched security fundamental.

### 5. What Is and Isn't Actually Implemented
**Why risky**: The codebase itself contains misleading signals — a docstring mentioning a `predictions` table that was never created, comments and `.env.example` entries referencing Google OAuth that was never built, and README language ("AI-Powered") that overstates the engine. If you haven't internalized these gaps, an interviewer who has read the code (or asks you to `grep` live) will catch you claiming something that isn't there.
**What to actually know**: The exact list — no `predictions` table, no Google OAuth routes, no CSRF protection, no tests, no Docker/deployment config, no rate limiting. See [01_Project_Overview.md](01_Project_Overview.md) "Honesty note" and [12_Security.md](12_Security.md) summary table.
**Why it matters**: Confidently and accurately stating what's *missing* is more impressive than vaguely implying everything works — it proves you actually read the code rather than memorized a description of it.

## Tier 2 — Very Likely to Come Up

### 6. Session Management: Signed vs. Encrypted
**Why risky**: A subtle distinction that's easy to get backwards under pressure.
**What to know**: Flask's session cookie is *signed* (tamper-evident, using `SECRET_KEY`) but *not encrypted* — its contents (`user_id`, `user_name`, `user_email`) are readable by anyone with the cookie, but can't be forged without the secret key. See [12_Security.md](12_Security.md) "Sessions."

### 7. The Request Lifecycle and `flask.g`
**Why risky**: Tests whether you understand Flask internals or just copied the pattern.
**What to know**: `get_db()` checks `g` before opening a new connection (reused within one request); `close_db()` runs via `app.teardown_appcontext` after every request, success or failure. Practice explaining *why* teardown functions matter (guaranteed cleanup even on exceptions).

### 8. CSRF: What It Is, and Why This App Lacks It
**Why risky**: A common, expected security gap question — don't be caught not knowing the term or the fix.
**What to know**: No form in this app has a CSRF token; the fix is Flask-WTF's `CSRFProtect`. Also know the practical (low) severity here — no destructive action is exposed today, but that's a mitigating factor, not an excuse.

### 9. Why Files Are Never Saved to Disk
**Why risky**: A candidate who assumes "of course uploaded files get saved somewhere" will be caught flat-footed if asked to point to where.
**What to know**: `extract_text()` reads the file into `io.BytesIO` in memory; only the sanitized filename string and extracted analysis results are persisted to MySQL. This is a genuine architectural strength (removes a whole class of file-storage vulnerabilities) — know it well enough to explain it as a deliberate benefit, not just "oh, I guess it doesn't save files."

### 10. The Two-Table Schema and the FK Cascade
**Why risky**: Basic but must be fluent, since it's the foundation of every data question.
**What to know**: `users` ← `resume_uploads` (`user_id` FK, `ON DELETE CASCADE`). Know what `ON DELETE CASCADE` actually does operationally (auto-deletes child rows) even though no "delete account" feature exists yet to trigger it.

## Tier 3 — Good to Have Ready (Depth Questions)

### 11. Scalability Priorities, In Order
**Why risky**: A vague "I'd add caching and load balancers" answer sounds memorized. You need a *prioritized*, code-grounded list.
**What to know**: Connection pooling and the missing `LIMIT` on `get_user_uploads()` come before load balancers/microservices — see [13_Scalability.md](13_Scalability.md) and [16_Cross_Questions.md](16_Cross_Questions.md) Chain 7.

### 12. Why No Tests Exist, and What You'd Test First
**Why risky**: "I didn't have time" is a weak answer alone. Pair it with a concrete testing plan.
**What to know**: `app/ml/predict.py`'s pure functions (no Flask/DB dependency) are the easiest and most valuable place to start, and the duplicate-key bug is a perfect, concrete example of what a simple test would have caught.

### 13. The One Cross-Blueprint Coupling (`login_required`)
**Why risky**: Tests whether you understand the actual dependency graph of your own code, not just "I used blueprints."
**What to know**: `login_required` is defined in `app/main/routes.py` and imported into `app/resume/routes.py` — the only place two blueprints directly depend on each other.

### 14. The `MAX(predicted_role)` Subtlety in `get_upload_stats()`
**Why risky**: A genuinely subtle correctness issue (`MAX()` on a string column returns the alphabetically largest value, not necessarily the most recent one) that only shows up if you've read the SQL very carefully. A sharp interviewer might present this as a puzzle.
**What to know**: See [15_TCS_Digital_Interview_QA.md](15_TCS_Digital_Interview_QA.md) Q95 for the full explanation and fix (subquery or `ORDER BY ... LIMIT 1` instead of independent `MAX()`).

### 15. Comment/Docstring Drift as a Concept
**Why risky**: Being asked "does your code match your documentation?" is a values question about engineering discipline, not just a project-specific fact.
**What to know**: You have two concrete, real examples ready (the `predictions` table, the Google OAuth routes) — use them, and use the broader lesson ("stale comments mislead more than no comments") as your framing.

## How to Use This Document
Read Tier 1 the night before, out loud, without notes. Skim Tier 2 the morning of. Keep Tier 3 as a mental "if they push deeper" reserve — you don't need to lead with it, but you should never be caught not knowing it if asked directly.
