# 12 — Security Analysis

This is an honest audit of what is and isn't implemented, based only on what's actually in the code. Interviewers at TCS Digital frequently probe security fundamentals — this document is meant to make you comfortable saying "yes, implemented, here's how" or "no, not implemented, here's what I'd add" instead of guessing.

## Authentication
**Implemented**: Email + password login using Flask sessions. `app/auth/routes.py` handles `register`/`login`/`logout`.
**Not implemented**: email verification, "forgot password" / password reset flow, multi-factor authentication, account lockout after repeated failed attempts, Google OAuth (despite `.env.example` placeholders `GOOGLE_OAUTH_CLIENT_ID`/`SECRET` and a docstring mentioning `/login/google` — no such route exists in code).

## Authorization
**Implemented**: route-level protection via the `login_required` decorator (`app/main/routes.py`), applied to `/dashboard`, `/upload`, `/history`. Every protected route also implicitly scopes its data queries to `session['user_id']` — e.g. `get_user_uploads(session['user_id'])` — so one logged-in user can never see another user's data through the normal UI.
**Not implemented**: there is only **one** user role in this system (no admin/staff distinction) — every registered user has identical permissions. There's also no object-level ownership check beyond "the query itself is scoped by user_id" — i.e., there's no separate `if upload.user_id != session['user_id']: abort(403)` check anywhere, because no route currently accepts an upload ID directly from the client (all upload lookups always go through the session's own `user_id`). This is good by *omission* (no such vulnerable endpoint exists yet) rather than by explicit design.

## Password Storage
**Implemented correctly**: `werkzeug.security.generate_password_hash()` at registration (scrypt algorithm by default in modern Werkzeug versions), `check_password_hash()` at login. Passwords are **never** stored or logged in plaintext, and the `password_hash` column is `VARCHAR(256)`, sized appropriately for a scrypt hash string like `scrypt:32768:8:1$salt$hash`.
**Gap**: minimum password length is only 6 characters (`app/auth/routes.py::register`), with no complexity requirement (no uppercase/digit/symbol requirement) and no check against common/breached password lists.

## JWT
**Not used at all.** Authentication state lives entirely in Flask's server-signed session cookie, not a bearer token. If asked "how would JWT fit here," the honest answer is: JWT would make more sense if this app exposed its API to a separate mobile app or SPA frontend that couldn't rely on cookies — for a same-origin, server-rendered app like this, session cookies are the simpler, appropriate choice.

## Sessions
**Implemented**: Flask's built-in client-side session, signed (not encrypted) using `SECRET_KEY` (`app/config.py`). It stores `user_id`, `user_name`, `user_email` — note that these values are **visible** (base64-decodable) to anyone who has the cookie, even though they can't be *tampered with* without knowing `SECRET_KEY` (Flask uses `itsdangerous` to sign, not to encrypt).
**Gap**: no `session.permanent = True` / `PERMANENT_SESSION_LIFETIME` is configured, so sessions default to expiring when the browser closes (not necessarily a bug, but worth knowing precisely rather than guessing "sessions never expire"). There's also no server-side session store (e.g. Redis-backed sessions) — everything lives in the cookie itself, which is fine at this data volume (3 small values) but wouldn't scale if session data grew large.

## Cookies
The session cookie's security flags (`SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE`) are **not explicitly set** in `app/config.py` — Flask's defaults apply (`HttpOnly=True` by default, `Secure=False` by default, `SameSite=Lax` by default in modern Flask). Because `SESSION_COOKIE_SECURE` isn't explicitly forced to `True`, the cookie **could** be sent over plain HTTP if the app were ever deployed without HTTPS enforced elsewhere (e.g., at a reverse proxy) — a real, fixable gap for production.

## HTTPS
**Not configured anywhere in this codebase** — there's no Flask-Talisman, no HSTS header, no redirect-to-HTTPS middleware. The app runs via `app.run(debug=True)`, Flask's plain development server, which doesn't support TLS termination itself. In a real deployment, HTTPS would be handled by a reverse proxy (Nginx) or a PaaS's built-in TLS — this is standard practice, but it's worth being able to say plainly that **this repository has zero HTTPS configuration of its own**.

## Input Validation
**Implemented**:
- Registration: non-empty fields, password match, minimum length, duplicate-email check (`app/auth/routes.py`).
- Upload: file-presence check, extension allow-list (`allowed_file()`), file-size cap (`MAX_CONTENT_LENGTH = 5MB` in `Config`, enforced by Werkzeug automatically).
**Gaps**:
- No server-side validation of email *format* beyond the HTML5 `type="email"` input (client-side only — trivially bypassed by posting directly to `/register` with curl).
- No `413` (file too large) custom error handler — Flask shows its default error page rather than a friendly message.
- `allowed_file()` only checks the file extension string, not the actual file content/MIME type.

## SQL Injection
**Not vulnerable, as far as the code shows.** Every single SQL statement in `app/models.py` uses `%s` placeholders with the value passed as a separate tuple argument to `cursor.execute()` — this is the `mysql-connector-python` equivalent of a parameterized/prepared statement, which is the correct defense. There is **no string concatenation or f-string interpolation building SQL anywhere in the codebase** (verified by reading every query in `app/models.py`). This is a strong, demonstrable "what did you do right" talking point.

## XSS (Cross-Site Scripting)
**Mostly protected by default**: Jinja2 auto-escapes all `{{ variable }}` output by default, so any user-controlled data rendered into a template (e.g. a user's `name`, an upload's `filename`) is HTML-escaped automatically — a stored-XSS payload in a resume filename like `<script>...</script>.pdf` would be rendered as inert escaped text, not executed.
**One real caveat**: `templates/interview_prep.html`'s inline JavaScript builds question cards using `card.innerHTML = \`...${item.q}...${item.a}...\`` — this bypasses Jinja's auto-escaping because it's client-side JS setting `innerHTML` directly from JSON data. In *this specific case* the risk is theoretical/low because `item.q`/`item.a` come from the hardcoded `INTERVIEW_QUESTIONS` dictionary in `app/ml/data.py`, not from any user-submitted input — there is no code path where a user's own text ends up in this `innerHTML` call. But it's worth recognizing the *pattern* as something that would become a real vulnerability the moment this endpoint's data source ever became user-editable (e.g., if you added a "submit your own interview question" feature later without also switching this rendering to `textContent` or an escaping helper).

## CSRF (Cross-Site Request Forgery)
**Not implemented.** There is no CSRF token on any form (`login.html`, `register.html`, `upload.html`) and no library like Flask-WTF providing one. Combined with session-cookie-based auth, this means a malicious third-party site could, in theory, trick a logged-in user's browser into submitting a form to this app (e.g., forcing a resume upload, or hitting `/logout`). The **practical impact is low** here — there's no destructive action like "delete account" or "change password" exposed, so the worst realistic outcome is an unwanted logout or an unwanted resume upload, not account takeover or data loss. Still, this is a gap worth naming directly if asked, along with the fix: add Flask-WTF's `CSRFProtect` and `{{ form.csrf_token }}` to every form.

## Secrets Management
**Implemented correctly for local dev**: `SECRET_KEY` and MySQL credentials are read from environment variables via `python-dotenv`, never hardcoded in `app/config.py` (only insecure *fallback defaults* are hardcoded, clearly intended for local development only — e.g. `'jobcatch-dev-secret-key-change-in-production'`, whose very name warns you not to use it in production). `.env` is gitignored; `.env.example` documents the required keys without real values.
**Gap for production**: no integration with a real secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.) — acceptable for a student project, a real requirement before production use.

## Environment Variables
All of: `SECRET_KEY`, `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, and the unused `GOOGLE_OAUTH_CLIENT_ID`/`GOOGLE_OAUTH_CLIENT_SECRET` are defined in `.env.example`. `app/config.py` reads all of the *used* ones with `os.environ.get(key, default)`.

## File Upload Security (extra, project-specific)
- Uploaded files are **never saved to disk** — parsed entirely in memory via `io.BytesIO`. This eliminates an entire category of risk (path traversal via a malicious filename, arbitrary file write, an attacker uploading an executable to a web-accessible directory) that a naive "save the file to `/uploads/<filename>`" implementation would have to defend against explicitly.
- `secure_filename()` is still applied before the filename is stored in the database, which is good defense-in-depth even though the file itself isn't written anywhere.
- File size is capped at 5MB via Flask config, mitigating trivial denial-of-service-by-large-upload.

## Summary Table

| Control | Status | Notes |
|---|---|---|
| Password hashing | ✅ Implemented | Werkzeug scrypt |
| SQL injection defense | ✅ Implemented | Parameterized queries throughout |
| XSS defense (server-rendered) | ✅ Implemented | Jinja2 auto-escaping |
| XSS defense (client-side JS) | ⚠️ Partial | `innerHTML` used in interview-prep JS, low risk given static data source |
| File upload validation | ⚠️ Partial | Extension allow-list + size cap; no MIME sniffing |
| Login rate limiting | ❌ Missing | No brute-force protection |
| CSRF protection | ❌ Missing | No tokens on any form |
| Email verification | ❌ Missing | Registration = instant login |
| HTTPS enforcement | ❌ Missing | No config in this codebase |
| Secure cookie flags | ⚠️ Partial | Flask defaults only, not explicitly hardened |
| Secrets in env vars | ✅ Implemented | `.env` + `python-dotenv` |
| Authorization (data scoping) | ✅ Implemented | All queries scoped to `session['user_id']` |
| Google OAuth | ❌ Not implemented | Env vars exist, no route code |

**How to talk about this in an interview**: don't hide the gaps — naming them accurately and explaining the fix (e.g., "I'd add Flask-WTF for CSRF, Flask-Limiter for rate limiting, and Flask-Talisman for HTTPS/security headers") demonstrates more engineering maturity than pretending everything is already secure.
