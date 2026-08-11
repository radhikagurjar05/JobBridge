# 06 — Technology Stack

Every technology listed here is actually present in [requirements.txt](../requirements.txt) or the codebase — nothing speculative is included.

---

## Python 3
**What it is**: A general-purpose, interpreted, dynamically-typed programming language. The `venv/pyvenv.cfg` and shebang usage in this project target Python 3.12 (README asks for 3.9+).
**Why used here**: Flask is a Python framework; Python's simplicity and huge library ecosystem (`PyPDF2`, `python-docx`, `mysql-connector-python`) made it a natural fit for a student project that needed file parsing + a web server quickly.
**Advantages**: Readable syntax, huge ecosystem, fast to prototype in, great for text/string processing (which is most of what `app/ml/predict.py` does — regex and substring checks).
**Disadvantages**: Slower raw execution than compiled languages (Java, Go, C++); the GIL limits true multi-core parallelism within a single process (not a real concern for this app's workload, which is I/O- and string-bound, not CPU-bound).
**Alternatives**: Node.js/JavaScript, Java, Go, Ruby.
**Why chosen over alternatives**: Python has the richest resume-parsing library ecosystem (`PyPDF2`, `python-docx`) and is typically the first language taught in Indian engineering colleges, making it a natural choice for a student capstone project like this one.

---

## Flask (3.0.2)
**What it is**: A lightweight, unopinionated ("micro") web framework for Python. Provides routing, request/response handling, templating (via Jinja2), and sessions out of the box, but leaves things like database access and forms entirely up to you.
**Why used here**: The entire app is built on Flask — `Flask(__name__, ...)`, `Blueprint`, `render_template`, `session`, `request`, `flash`, `jsonify` are used throughout `app/`.
**Advantages**: Minimal boilerplate, easy to understand end-to-end (you can read every line that runs for a request), huge community, flexible enough to add only what you need.
**Disadvantages**: Because it's unopinionated, you must make your own decisions about structure, ORM, auth, and forms — and it's easy to end up with an insecure or messy app if those decisions are skipped (which is partly true here — no CSRF protection, no ORM).
**Alternatives**: Django, FastAPI.
**Why chosen over Django**: Django is "batteries-included" (ORM, admin panel, auth system, forms with built-in CSRF protection all ship by default) — great for larger apps, but heavier and more opinionated than a project of this scope needed. JobCatch's author explicitly chose to write raw SQL and a hand-rolled auth flow instead of adopting Django's conventions.
**Why chosen over FastAPI**: FastAPI is async-first and designed around typed request/response models (Pydantic) for building APIs — excellent for high-performance JSON APIs, but this project is primarily server-rendered HTML pages, which is Flask's sweet spot, not FastAPI's.
**Trade-off summary**: Flask = maximum flexibility + you own more decisions. Django = more built-in but more opinionated/heavier. FastAPI = best for pure async JSON APIs, not HTML-rendering apps.

---

## Werkzeug (3.0.1)
**What it is**: The WSGI utility library Flask is built on top of (Flask literally wraps Werkzeug + Jinja2). It provides the actual HTTP request/response objects, routing engine, and — importantly for this project — the `werkzeug.security` module.
**Why used here**: Two functions from `werkzeug.security` are the entire password-security story of this app: `generate_password_hash()` (used in `app/auth/routes.py::register()`) and `check_password_hash()` (used in `login()`). Also `werkzeug.utils.secure_filename()` sanitizes uploaded filenames before they're stored.
**Advantages**: Comes bundled with Flask (no extra dependency to reason about), uses scrypt by default for password hashing (a memory-hard, brute-force-resistant algorithm), and `secure_filename()` strips path-traversal-dangerous characters automatically.
**Disadvantages**: It's a low-level utility library, not a full auth *system* — there's no session-lifetime management, no password-reset flow, no account lockout built in; the app has to build all of that itself (and mostly hasn't).
**Alternatives for password hashing**: `bcrypt`, `argon2` (via `argon2-cffi`), Django's built-in `PBKDF2`.
**Why Werkzeug's hasher was fine here**: Since Flask already depends on Werkzeug, using its hashing functions means zero extra dependencies for a very standard, well-reviewed hashing scheme.

---

## mysql-connector-python (8.3.0)
**What it is**: MySQL's official, pure-Python (no C extension required) database driver.
**Why used here**: `app/models.py` uses `mysql.connector.connect(...)` to open connections and raw `cursor.execute("...", (%s, %s))` calls for every query.
**Advantages**: Officially maintained by Oracle/MySQL, no external C library needed to install, supports parameterized queries (`%s` placeholders) which is what prevents SQL injection in this app.
**Disadvantages**: No ORM convenience (no auto-generated models, no relationship traversal, no automatic migrations); slightly more verbose than `PyMySQL` for simple cases; connection pooling isn't used here (a new TCP connection is opened per request, per `get_db()`).
**Alternatives**: `PyMySQL` (pure Python, popular alternative), `SQLAlchemy` (ORM, can sit on top of either driver), `asyncpg`/`psycopg2` if using PostgreSQL instead.
**Why chosen over an ORM like SQLAlchemy**: For a small, two-table schema, raw SQL is easier to read start-to-finish and easier to explain line-by-line in an interview than ORM query-building syntax — a deliberate simplicity trade-off appropriate for this project's size.

---

## MySQL (Database Engine)
**What it is**: A relational (SQL) database management system.
**Why used here**: Two tables (`users`, `resume_uploads`) with a clear foreign-key relationship, fixed schema, and simple aggregate queries (`COUNT`, `AVG`, `MAX`) — a textbook relational use case.
**Advantages**: ACID transactions, foreign key constraints with `ON DELETE CASCADE` (used here so deleting a user automatically deletes their uploads), mature tooling, widely taught/used (a safe, recognizable choice for an academic project).
**Disadvantages**: Requires a running server process (not embedded like SQLite); vertical scaling has limits; schema changes need explicit migrations at scale (this project has none — see [07_Database.md](07_Database.md)).
**Alternatives**: PostgreSQL (more advanced SQL features, still relational), SQLite (embedded, zero-config, but not ideal for concurrent multi-user web apps), MongoDB (NoSQL — see below).
**Why MySQL over PostgreSQL here**: Both would work equally well for this schema; MySQL is extremely common in Indian college curricula and bootcamps (which lines up with this being a student project), so it's the more "expected" choice pedagogically, not because of a specific technical requirement Postgres couldn't meet.
**Why not MongoDB (NoSQL)**: The data here is inherently relational — users *own* resume uploads, and reporting queries (`AVG(resume_score) WHERE user_id = ...`) are natural SQL aggregations. A document store doesn't offer an advantage for this shape of data, and you'd lose the enforced foreign-key `ON DELETE CASCADE` behavior.

---

## PyPDF2 (3.0.1)
**What it is**: A pure-Python library for reading and manipulating PDF files.
**Why used here**: `app/resume/routes.py::extract_text()` uses `PdfReader(io.BytesIO(file.read()))` and loops `reader.pages`, calling `.extract_text()` on each page to build the resume's full text.
**Advantages**: Pure Python (easy to install, no system dependencies), simple API for basic text extraction.
**Disadvantages**: Cannot extract text from **scanned/image-only PDFs** (no OCR) — the app handles this gracefully by flashing "Could not extract text... Make sure it is not a scanned image PDF," but it's still a real functional gap. Text extraction quality can also vary with complex PDF layouts (multi-column resumes, tables).
**Alternatives**: `pdfplumber` (better layout/table handling), `pymupdf`/`fitz` (faster, more robust), OCR tools like `pytesseract` (for scanned documents).
**Why chosen**: It's the simplest, most widely-documented option for "just get the text out of a PDF" without extra system dependencies — appropriate for the project's scope.

---

## python-docx (1.1.0)
**What it is**: A library for reading/writing Microsoft Word `.docx` files.
**Why used here**: `extract_text()` uses `docx.Document(io.BytesIO(file.read()))` and joins the text of every paragraph.
**Advantages**: Simple, well-documented API for `.docx` specifically.
**Disadvantages**: Only supports the modern `.docx` XML format, **not** the legacy binary `.doc` format; text inside tables or text boxes in the Word document may not be captured by a simple paragraph loop (this app only reads `doc.paragraphs`, not `doc.tables`).
**Alternatives**: `docx2txt`, `textract` (aggregates many formats), Apache Tika (via a server, heavier).
**Why chosen**: Same reasoning as PyPDF2 — minimal, pure-Python, does exactly the one thing needed (paragraph text extraction) without extra complexity.

---

## python-dotenv (1.0.1)
**What it is**: A library that loads key=value pairs from a `.env` file into `os.environ`.
**Why used here**: `app/config.py` calls `load_dotenv()` at import time, so `Config` can read `os.environ.get('SECRET_KEY', ...)` etc. without the developer needing to `export` variables manually in their shell.
**Advantages**: Keeps secrets out of source code and out of version control (`.env` is gitignored) while still being effortless for local development.
**Disadvantages**: Not meant for production secret management (no encryption, no access control) — production should use a proper secrets manager (AWS Secrets Manager, HashiCorp Vault, or at least platform-level environment variables).
**Alternatives**: Direct OS environment variables, `python-decouple`, cloud-native secret managers.

---

## requests (2.31.0) — *listed but unused*
**What it is**: The most popular Python HTTP client library.
**Why it's in `requirements.txt`**: Likely added in anticipation of the (never-implemented) Google OAuth flow, which would need to call Google's token/userinfo endpoints. Grepping the `app/` folder shows **no actual `import requests` anywhere in the current codebase** — this is confirmed by inspection, not a guess. If asked about it, the honest answer is: "it's an unused dependency, probably left over from planning the OAuth feature that never got built."

---

## Jinja2 (via Flask)
**What it is**: Python's default templating engine, bundled with Flask.
**Why used here**: Every `.html` file in `templates/` uses Jinja2 syntax (`{% extends %}`, `{% block %}`, `{% for %}`, `{{ variable }}`).
**Advantages**: Auto-escapes variables by default (a real XSS defense — see [12_Security.md](12_Security.md)), supports template inheritance (`base.html` + child blocks) which keeps the navbar/footer DRY.
**Disadvantages**: Server must re-render the full page on every navigation (no partial/SPA updates) unless you deliberately add AJAX (which this app does, once, for the interview questions API).
**Alternatives**: Mako, Django Templates (if using Django).

---

## HTML5, CSS3 (Vanilla), JavaScript (Vanilla)
**What it is**: Standard web technologies, hand-written with no framework or build tool.
**Why used here**: `static/css/style.css` uses CSS custom properties (`--primary`, etc.) for theming, and `static/js/main.js` plus small inline scripts handle just three behaviors: hamburger menu, dark mode toggle, and drag-and-drop/AJAX for two specific pages.
**Advantages**: Zero build step, zero framework learning curve, tiny total payload, easy for any developer to read directly.
**Disadvantages**: No component reusability system, no state management, would not scale well to a much more interactive UI (e.g. real-time updates, complex client-side forms).
**Alternatives**: React, Vue, Svelte, Alpine.js (a lightweight middle ground between vanilla JS and a full framework).
**Why chosen**: The app's interactivity needs are genuinely small (toggle a class, fetch one JSON endpoint) — pulling in a full frontend framework would be over-engineering for what's fundamentally a server-rendered CRUD app.

---

## Font Awesome & Google Fonts (CDN)
**What it is**: Icon font library and web font service, loaded via `<link>` tags in `base.html` pointing at `cdnjs.cloudflare.com` and `fonts.googleapis.com`.
**Why used here**: Purely cosmetic — icons throughout the navbar, buttons, and cards; the "Inter" font family for typography.
**Disadvantages**: Introduces an external network dependency for page rendering (if the CDN is down or blocked, icons/fonts silently fail to load, though the page still functions).
**Alternative**: Self-host the font/icon files to remove the external dependency entirely.

---

## Explicitly NOT Used (worth knowing so you don't get caught out)
| Technology | Status |
|---|---|
| SQLAlchemy / any ORM | Not used — raw SQL only |
| JWT | Not used — session cookies only |
| Docker | Not used — no `Dockerfile` in the repo |
| Any cloud provider (AWS/Azure/GCP) SDK | Not used |
| Celery / RQ / any task queue | Not used — analysis runs synchronously in-request |
| Redis / Memcached | Not used — no caching layer |
| React / Vue / Angular | Not used — server-rendered Jinja2 only |
| pytest / unittest | Not used — no test suite exists despite `pytest` appearing as an example *keyword* inside `ROLE_KEYWORDS["Python Developer"]` (that's just resume-matching data, not a project dependency) |
| Google OAuth (`google-auth`, `authlib`, etc.) | Not used — only placeholder env vars exist |

Being able to say "here's what I used, and here's what I deliberately did *not* use, and why" is exactly the kind of answer that shows engineering judgment in a TCS Digital interview.
