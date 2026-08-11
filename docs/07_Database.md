# 07 — Database

All schema definitions below are copied directly from [app/models.py](../app/models.py) `init_db()` — this is the actual, executable source of truth (there is no separate `.sql` schema file or migration tool in this project).

## ER Overview (ASCII)

```
┌───────────────────────────────┐
│            users               │
├───────────────────────────────┤
│ PK  id             INT AUTO_INC│
│     name           VARCHAR(150)│
│ UQ  email          VARCHAR(150)│
│     password_hash  VARCHAR(256)│
│     created_at     DATETIME     │
└───────────────┬───────────────┘
                │ 1
                │
                │ has many
                │
                │ N
┌───────────────▼───────────────┐
│        resume_uploads          │
├───────────────────────────────┤
│ PK  id             INT AUTO_INC│
│ FK  user_id  ───────► users.id │
│     filename       VARCHAR(255)│
│     upload_time    DATETIME     │
│     predicted_role VARCHAR(100)│
│     resume_score   INT          │
└───────────────────────────────┘
        ON DELETE CASCADE
```

There are only **two tables**. This is a simple **one-to-many relationship**: one user has many resume uploads.

> **Discrepancy to flag proactively in an interview**: the docstring at the top of `app/models.py` says *"Tables: users, resume_uploads, predictions — every ML prediction made for a user"* — but `init_db()` only actually issues `CREATE TABLE IF NOT EXISTS` for `users` and `resume_uploads`. **There is no `predictions` table in the running database.** The prediction (`predicted_role`) is instead stored directly as a column on `resume_uploads`. If an interviewer says "tell me about your `predictions` table," the correct, honest answer is: "That was mentioned in an early comment/plan, but in the actual implementation the prediction result is stored as a column on `resume_uploads` — there's no separate table for it." Being able to spot and explain this kind of comment-vs-code drift is itself a good signal in an interview.

## Tables

### `users`
| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` | Unique surrogate key for each user |
| `name` | `VARCHAR(150)` | `NOT NULL` | Display name shown on dashboard ("Hello, {name}!") |
| `email` | `VARCHAR(150)` | `UNIQUE NOT NULL` | Login identifier; uniqueness enforced at the DB level, not just in app code |
| `password_hash` | `VARCHAR(256)` | nullable | Scrypt hash string from `generate_password_hash()`, e.g. `scrypt:32768:8:1$...$...` |
| `created_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | Auto-set registration timestamp |

**Why `password_hash` is nullable**: this is a small but deliberate hint that the original design anticipated a second signup method (e.g. Google OAuth, where there'd be no local password) — consistent with the unused OAuth env vars — even though that path isn't implemented. In the current code, every user created through `create_user()` in `register()` always supplies a hash, so in practice this column is never actually left null.

### `resume_uploads`
| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` | Unique surrogate key for each upload event |
| `user_id` | `INT` | `NOT NULL`, `FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE` | Owner of this upload |
| `filename` | `VARCHAR(255)` | `NOT NULL` | Sanitized original filename (via `secure_filename()`) — **not** a path to a stored file, since the file itself is never saved to disk |
| `upload_time` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | When the upload happened; used for `ORDER BY upload_time DESC` in history/dashboard |
| `predicted_role` | `VARCHAR(100)` | nullable | The role string returned by `predict_role()`, e.g. `"Python Developer"` or `"General / Other"` |
| `resume_score` | `INT` | nullable | The 0–100 score from `compute_score()` |

## Primary Keys
Both tables use a simple auto-incrementing surrogate integer key (`id`). This is the standard, simplest choice — no natural key (like email) is used as the primary key, which is good practice since natural keys (emails) can theoretically change, while surrogate keys never do.

## Foreign Keys
Exactly one: `resume_uploads.user_id → users.id`, declared with `ON DELETE CASCADE`. This means **deleting a user automatically deletes all of their resume upload records** — the database enforces referential integrity itself, rather than relying on application code to remember to clean up child rows. (Note: there is currently no "delete account" feature in the app that would actually trigger this cascade — but the schema is ready for one.)

## Indexes
- Both `id` columns are indexed automatically (as the `PRIMARY KEY`).
- `users.email` has an implicit unique index because of the `UNIQUE` constraint — this is what makes `get_user_by_email()` lookups efficient.
- `resume_uploads.user_id`, being a foreign key column under InnoDB (MySQL's default engine), automatically gets an index created for it by MySQL itself (InnoDB requires an index on the referencing column for foreign keys) — so `WHERE user_id = %s` lookups in `get_user_uploads()` and `get_upload_stats()` are index-backed even without an explicit `CREATE INDEX` statement in the code.
- **No explicit index exists on `upload_time`.** Every history/dashboard query does `ORDER BY upload_time DESC`; at very large row counts per user this would benefit from a composite index like `(user_id, upload_time DESC)`. At the current scale (a student project) this doesn't matter, but it's a valid scalability talking point (see [13_Scalability.md](13_Scalability.md)).

## Constraints Summary
| Constraint | Where |
|---|---|
| `NOT NULL` | `users.name`, `users.email`, `resume_uploads.user_id`, `resume_uploads.filename` |
| `UNIQUE` | `users.email` |
| `PRIMARY KEY` | `users.id`, `resume_uploads.id` |
| `FOREIGN KEY ... ON DELETE CASCADE` | `resume_uploads.user_id → users.id` |
| `DEFAULT CURRENT_TIMESTAMP` | `users.created_at`, `resume_uploads.upload_time` |

There are **no `CHECK` constraints** (e.g. nothing in the database itself enforces `resume_score BETWEEN 0 AND 100` — that range is only guaranteed by the application logic in `compute_score()`, since the checks sum to a hard-coded maximum of 100 points). This is worth mentioning if asked "how do you guarantee the score never exceeds 100?" — the honest answer is "by construction in `compute_score()` (the point values are designed to sum to exactly 100), not by a database-level constraint."

## Normalization
The schema is effectively in **Third Normal Form (3NF)**:
- **1NF**: every column holds a single, atomic value (no comma-separated lists stored in a single field, for instance).
- **2NF**: there's no composite primary key, so partial-dependency issues don't apply.
- **3NF**: no column depends on a non-key column. For example, `predicted_role` and `resume_score` depend only on the upload's own `id`, not transitively on some other non-key attribute.

**Why the schema is designed this way**: two tables is the minimum needed to model "a user can have many uploads, and we need to remember details about each upload individually" without duplicating user information on every upload row. An alternative (bad) design would have been to flatten everything into one `users` table with columns like `last_upload_score` — but that would lose history (only the most recent value could be kept) and violate normalization by mixing user identity with upload-event data. The current two-table design correctly separates "who the user is" from "what happened during each of their upload events," which is exactly why a `dashboard`/`history` feature is possible at all — you can't show upload *history* if you only ever kept the latest value.

## What a `predictions` Table *Would* Have Looked Like (if it existed)
Since the docstring mentions this table but it isn't implemented, here's the natural extension were it to be built — useful if an interviewer asks "how would you refactor this?":
```
predictions
├── PK id
├── FK upload_id  → resume_uploads.id
├── role           VARCHAR(100)
├── keyword_score  INT            -- raw count of matched keywords
├── created_at     DATETIME
```
This would let a single upload have multiple prediction attempts recorded over time (e.g., if the algorithm changed), separating "the file that was uploaded" from "the specific prediction run against it" — a cleaner separation of concerns than cramming `predicted_role`/`resume_score` directly onto `resume_uploads`. This is a good, low-risk answer to "what would you improve about your schema?"
