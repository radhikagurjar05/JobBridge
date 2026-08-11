# 13 — Scalability (If JobCatch Had 1 Million Users)

This is a forward-looking design discussion. Everything in this document is a **proposed change**, clearly distinguished from what's actually implemented today (which is documented in [03_Architecture.md](03_Architecture.md)).

## Current Bottlenecks (Given Today's Actual Code)

1. **One MySQL connection opened per request** (`get_db()` in `app/models.py`) — no connection pooling. At high concurrency, opening/tearing down a raw TCP + MySQL handshake per request is expensive and would exhaust MySQL's `max_connections` limit quickly.
2. **`get_user_uploads()` has no `LIMIT`** — both `/history` and the dashboard's "recent uploads" (which fetches *everything* and Python-slices `[:5]`) pull the user's entire upload history from the database every time. For a power user with thousands of uploads, this wastes both DB and network bandwidth on every dashboard page load.
3. **Synchronous, in-request resume analysis** — `extract_text()` + `analyze_resume()` run inline inside the `/upload` request/response cycle. Today this is fine because keyword matching is fast pure-Python string work, but if the analysis ever became more expensive (a real ML model, OCR for scanned PDFs, an external API call), it would block the request thread and degrade response times under load.
4. **No caching layer at all** — `ROLE_KEYWORDS`, `INTERVIEW_QUESTIONS`, and `SUGGESTED_SKILLS` are static Python dictionaries loaded once at import time (effectively already "cached" in memory, which is good), but dynamic data like dashboard stats is recomputed from scratch on every request with no caching.
5. **Single Flask process, single server** — `app.run(debug=True)` is Flask's built-in development server, explicitly documented as unsuitable for production and incapable of handling concurrent load or multiple worker processes.
6. **No CDN** — CSS/JS/images are served directly by the Flask app itself from `static/`, meaning every static asset request also hits the application server.
7. **No read replicas / no horizontal DB scaling** — a single MySQL instance handles every read and write.

## Practical Improvements, in Priority Order

### 1. Caching
- **What to cache**: dashboard stats (`get_upload_stats`) per user, since they don't need to be recomputed on every single page view — a short TTL cache (e.g. 30–60 seconds) in Redis would dramatically cut repeated `COUNT`/`AVG` queries for active users.
- **What NOT to cache naively**: the resume upload result itself is inherently per-request/per-file, so caching wouldn't apply there — but the *static* role/keyword/question data (`app/ml/data.py`) is already effectively cached in application memory since it's just Python module-level constants; at real scale you'd keep this as-is (it's tiny, ~a few KB) rather than moving it into Redis, since round-tripping to a cache server for data this small and static would be slower than an in-process dict lookup.

### 2. Database Scaling
- **Add explicit indexes**: a composite index on `resume_uploads(user_id, upload_time DESC)` would make both `/history` and dashboard queries faster as row counts grow, instead of relying only on the implicit FK index on `user_id`.
- **Connection pooling**: switch from "one connection per request via `get_db()`" to a pooled setup — `mysql-connector-python` supports `mysql.connector.pooling.MySQLConnectionPool`, or move to SQLAlchemy's engine-level pooling. This alone would meaningfully cut latency and MySQL load under concurrent traffic.
- **Read replicas**: at real scale, read-heavy queries (`get_user_uploads`, `get_upload_stats`, dashboard reads) could be routed to one or more read replicas, while writes (`create_user`, `save_upload`) go to the primary — classic read/write splitting.
- **Pagination**: add `LIMIT`/`OFFSET` (or better, keyset/cursor pagination) to `get_user_uploads()` so `/history` never returns unbounded result sets.
- **Migrations**: introduce a real migration tool (Alembic, or Flyway if moving away from Python-only tooling) instead of `CREATE TABLE IF NOT EXISTS` in `init_db()`, so schema changes can be applied safely and incrementally across environments without hand-editing a running production database.

### 3. Load Balancing
Run multiple stateless Flask app instances (via gunicorn/uWSGI workers, or multiple containers/VMs) behind a load balancer (Nginx, AWS ALB, etc.). This is straightforward **because the app is already stateless at the process level** — all session state lives in the signed client cookie, not in server-side memory, so any instance can serve any request without "sticky sessions." This is a genuine architectural strength worth calling out: the current session design (cookie-based, not server-memory-based) is *already* horizontally-scalable-friendly, even though nothing else about the deployment is set up for it yet.

### 4. Async Jobs / Queues
If resume analysis ever became slow (e.g., adding OCR for scanned PDFs, or swapping the keyword engine for a real ML model that needs GPU inference), the right move would be:
```
User uploads resume
   → Flask saves the file reference + enqueues a job (Celery + Redis/RabbitMQ, or AWS SQS)
   → Flask immediately responds "Analyzing... check back shortly" (or uses websockets/polling)
   → A background worker picks up the job, runs analyze_resume() (or a heavier model)
   → Result written to resume_uploads once ready
   → Frontend polls or gets pushed the result
```
Today's synchronous design (analyze inline, return the page immediately) is *appropriate for the current workload* — introducing a queue prematurely would be over-engineering for pure keyword matching, which typically completes in milliseconds.

### 5. CDN
Serve `static/css/style.css`, `static/js/main.js`, and `static/images/*.jpg` from a CDN (CloudFront, Cloudflare) instead of directly from the Flask app, freeing the application servers to only handle dynamic requests. Font Awesome/Google Fonts are already CDN-hosted (external), but the app's own static assets are not.

### 6. Horizontal Scaling
Because there's no server-side session store or in-memory application state (again, thanks to cookie-based sessions), horizontally scaling this app is mostly a matter of: containerize it (add a `Dockerfile`, currently missing), put it behind a load balancer, and point every instance at the same MySQL host (and eventually a connection-pooled/read-replica setup as above).

### 7. Microservices
At 1 million users, it's reasonable to ask "would you split this into microservices?" A defensible answer: **not yet, and maybe never fully** — this app's actual computational hot path (resume analysis) is cheap and synchronous, and the domain is small (auth + one core feature + a content page). The more valuable "service boundary" to consider is separating the **resume-analysis engine** (`app/ml/`) into its own internal service *only if* it evolves into something heavier (a trained model needing dedicated hardware) — at that point, extracting it behind an internal API (still callable from the same Flask app) would let it scale independently (e.g., GPU-backed instances) from the rest of the CRUD app. Splitting auth or dashboard into separate services wouldn't buy much given how lightweight those paths are.

### 8. Monitoring & Logging
Currently there is **no structured logging and no monitoring** anywhere in the codebase — the only console output is a single `print("[JobCatch] Database tables are ready.")` in `init_db()`. At scale you would add:
- Structured application logging (Python's `logging` module configured with JSON output) for request tracing, errors, and slow-query detection.
- An APM/monitoring tool (Datadog, New Relic, or open-source Prometheus + Grafana) tracking request latency, error rates, and database query times.
- Centralized log aggregation (ELK stack / CloudWatch Logs) so logs from many horizontally-scaled instances are searchable in one place.
- Alerting on error-rate spikes, slow queries, and MySQL connection-pool exhaustion.

### 9. Cloud Improvements
- Move MySQL to a managed service (AWS RDS, Azure Database for MySQL, GCP Cloud SQL) for automated backups, failover, and read replicas without operational overhead.
- Use managed secrets (AWS Secrets Manager / Parameter Store) instead of a `.env` file.
- Auto-scaling groups / Kubernetes HPA for the Flask app tier, scaling worker count based on CPU/request-latency metrics.
- Object storage (S3) *if* the design ever changes to persist actual resume files (it currently doesn't) rather than only extracted text/metadata.

## What Would NOT Need to Change
- The **relational schema** itself (`users` + `resume_uploads`) is already well-normalized and would scale fine with proper indexing — no need for a NoSQL rewrite.
- The **stateless session design** is already scale-friendly and wouldn't need re-architecting for horizontal scaling.
- The **keyword-matching "ML" engine** itself is computationally trivial (string operations over a small dictionary) and would remain fast even at very high request volume — the bottleneck at scale is the database and infrastructure layer, not this logic.
