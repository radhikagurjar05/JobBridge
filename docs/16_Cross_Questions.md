# 16 — Cross-Questions (Follow-Up Chains)

Real interviews rarely stop at one question — they drill down. Below are realistic follow-up chains for the most important topics in JobBridge. Practice going down each chain out loud without notes.

---

## Chain 1: Framework Choice
```
Why Flask?
   ↓
"Because it's lightweight and I only needed routing, templating, and sessions —
 I wanted control over my own SQL and auth logic."
   ↓
Why not Django then, since Django gives you all that for free?
   ↓
"Django's ORM, admin panel, and built-in CSRF/auth are great, but they come with
 conventions I'd have to learn and follow. For a 2-table schema and 10 routes,
 that's more structure than the problem needed."
   ↓
Why not FastAPI — isn't it faster and more modern?
   ↓
"FastAPI is async-first and built around typed JSON APIs with Pydantic —
 excellent for a pure API backend, but this app is server-rendered HTML pages
 with Jinja2, which is exactly Flask's use case, not FastAPI's."
   ↓
So what are the actual trade-offs between the three?
   ↓
"Flask = flexibility, you own more decisions (and more risk of skipping
 something important, like CSRF, which I did). Django = batteries included,
 faster to get security/admin right, less flexible. FastAPI = best-in-class
 for async JSON APIs and auto-generated docs, not built for server-rendered
 HTML."
   ↓
Given you skipped CSRF protection, doesn't that prove Django would have been
safer for you specifically?
   ↓
"Fair point — Django's forms come with CSRF tokens by default, so choosing
 Django might have prevented this gap by convention. My answer isn't 'Flask
 was strictly better,' it's that I traded some default safety for
 flexibility and transparency, and CSRF is exactly the kind of thing that
 trade-off cost me here. I'd add Flask-WTF to close that gap."
```
**Lesson**: don't just defend your original choice reflexively — when a follow-up exposes a real cost of that choice, acknowledge it honestly. That's a stronger answer than doubling down.

---

## Chain 2: The "AI" Claim
```
Is this AI?
   ↓
"No — it's a rule-based keyword-counting engine, not a trained model."
   ↓
Then why call it "AI-Powered" in the README/hero section?
   ↓
"That's marketing language on the landing page — in a technical discussion
 I'd always describe it accurately as rule-based. I think that's a fair
 critique of the README/marketing copy, not of the underlying engineering,
 and I'd be careful not to make that overstatement in a professional
 context."
   ↓
If it's not AI, what would you need to add to honestly call it AI?
   ↓
"A model trained on labeled data — for example, resumes labeled with their
 correct role — using something like TF-IDF + logistic regression, or
 embeddings + a classifier, learned from data rather than hand-written
 keyword lists."
   ↓
Would you actually recommend replacing the current system with that model?
   ↓
"Not replace — augment. I'd keep the rule-based system as an explainable
 baseline/fallback, and only add a learned model where it demonstrably
 outperforms keyword counting, because the current system's biggest strength
 is that every prediction is fully explainable, and a black-box model would
 lose that."
   ↓
How would you even measure whether the learned model "outperforms" the rule-based one?
   ↓
"Same labeled test set, measure accuracy of both systems side by side,
 and specifically look at cases where they disagree to understand why."
```
**Lesson**: this chain tests honesty under pressure. The winning move is agreeing immediately with any fair critique ("marketing language," "not technically AI") rather than getting defensive.

---

## Chain 3: Database Choice
```
Why MySQL and not MongoDB?
   ↓
"The data is inherently relational — a user has many resume uploads, a
 classic one-to-many — and I need aggregate queries like AVG(resume_score).
 That's a natural fit for SQL, not a document store."
   ↓
But couldn't you model that in MongoDB too, with an array of uploads embedded
in the user document?
   ↓
"Yes, technically — but then updating/appending to that array on every
 upload, plus doing aggregate math across potentially thousands of embedded
 uploads, becomes awkward compared to a simple SQL JOIN/aggregate. Also, I'd
 lose the database-enforced foreign key and ON DELETE CASCADE behavior I get
 for free in MySQL."
   ↓
Why not PostgreSQL instead of MySQL, then, since Postgres has more advanced
SQL features?
   ↓
"For this schema, MySQL and PostgreSQL are functionally equivalent — I don't
 use any Postgres-specific feature (like JSONB columns or window functions)
 that would make Postgres meaningfully better here. MySQL is just the more
 commonly taught/used option in the environment I built this in."
   ↓
If you DID need a JSON-like flexible field later — say, storing arbitrary
extracted resume metadata — how would you add that in MySQL?
   ↓
"MySQL supports a native JSON column type since 5.7, so I could add a
 `metadata JSON` column to resume_uploads without needing to switch
 databases at all."
```
**Lesson**: know the escape hatch — if asked "what if you needed X," always know whether your current stack already supports it before assuming you'd need to switch technologies entirely.

---

## Chain 4: No ORM
```
Why didn't you use an ORM like SQLAlchemy?
   ↓
"For two tables and a handful of queries, raw SQL is easier to read
 end-to-end and easier to explain line-by-line — every query in models.py
 is fully visible, nothing is generated for me."
   ↓
Isn't that going to become unmaintainable as the schema grows?
   ↓
"Yes — this is explicitly a small-scale trade-off. If I added five more
 tables with complex relationships, I'd likely introduce SQLAlchemy at that
 point, both for migration support (Alembic) and to avoid hand-writing
 increasingly complex JOINs."
   ↓
How do you currently handle schema changes without an ORM or migration tool?
   ↓
"Honestly, I don't have a real migration story today — init_db() only runs
 CREATE TABLE IF NOT EXISTS, which works for a fresh database but doesn't
 handle altering an existing populated table safely. That's a real gap I'd
 fix with Alembic before this went to production."
   ↓
Walk me through how Alembic would solve that.
   ↓
"Alembic tracks schema versions as incremental Python migration scripts —
 each one has an `upgrade()` and `downgrade()` function. You'd run
 `alembic upgrade head` to apply pending migrations in order, and it keeps
 a version table in the database so it always knows the current state,
 unlike my current CREATE TABLE IF NOT EXISTS approach which has no concept
 of 'versions' at all."
```
**Lesson**: "I don't have a real answer for X today, here's what I'd add" is a completely acceptable and often *better* answer than pretending a solution already exists.

---

## Chain 5: Passwords & Session Security
```
How are passwords stored?
   ↓
"Hashed with Werkzeug's generate_password_hash(), scrypt-based, never
 plaintext."
   ↓
Why scrypt over bcrypt?
   ↓
"I didn't choose scrypt explicitly — it's Werkzeug's current default
 algorithm. Both scrypt and bcrypt are memory-hard, brute-force-resistant
 hashing schemes; the important property either way is that hashing is slow
 and salted, unlike a fast hash like plain SHA-256 which would be unsuitable
 for passwords."
   ↓
What's stored in the session — is it safe if someone steals the cookie?
   ↓
"user_id, user_name, and user_email — signed with SECRET_KEY, so it can't be
 tampered with, but it's not encrypted, so anyone who obtains the cookie
 (e.g. via XSS, or a shared computer) can read that data in plaintext. They
 couldn't forge a DIFFERENT user's session without knowing SECRET_KEY,
 but they could read this user's info."
   ↓
So what's the actual worst-case impact of a stolen session cookie here?
   ↓
"The attacker could act as that logged-in user for as long as the cookie
 is valid — uploading resumes on their behalf, viewing their history and
 dashboard. There's no password change or destructive action gated only by
 session (no account deletion feature exists), so the blast radius is
 'impersonate this user's resume activity,' not 'take over their account
 permanently' — since the attacker still doesn't gain the password itself."
   ↓
How would you reduce that impact further?
   ↓
"Set SESSION_COOKIE_HTTPONLY (already Flask's default) and
 SESSION_COOKIE_SECURE=True explicitly once served over HTTPS, add a session
 expiry, and consider re-authentication before any future sensitive action
 like changing account details."
```
**Lesson**: security follow-ups often ask you to reason about *actual blast radius*, not just name the vulnerability. Precise, bounded answers beat vague alarm.

---

## Chain 6: The Keyword-Matching Algorithm's Weaknesses
```
How does role prediction work?
   ↓
"Count keyword matches per role from a fixed dictionary, highest count wins."
   ↓
What's a concrete case where that fails?
   ↓
"'java' as a keyword matches as a substring inside 'javascript', so a pure
 JavaScript resume could get a false-positive point toward Java Developer."
   ↓
How would you actually fix that, in code?
   ↓
"Switch from `kw in text` substring checks to word-boundary regex, like
 `re.search(r'\bjava\b', text)`, for every keyword comparison in both
 predict_role and extract_skills."
   ↓
Would that fix introduce any new problems?
   ↓
"Possibly — some keywords contain special regex characters, like 'c#' or
 '.net' or 'ci/cd'. I'd need re.escape() around each keyword before building
 the regex pattern, otherwise '.' or '#' would be interpreted as regex
 syntax instead of literal characters."
   ↓
Are there keywords in your actual data that would hit that exact problem?
   ↓
"Yes — 'c#' under DotNet Developer, '.net' under DotNet Developer, and
 'ci/cd' under DevOps Engineer and Automation Testing are all in
 ROLE_KEYWORDS today, so re.escape() wouldn't be optional, it'd be required
 for the fix to work correctly."
```
**Lesson**: the strongest signal here is being able to name the *specific* keywords in your *actual* data (`c#`, `.net`, `ci/cd`) that would break a naive fix — proving you've actually read `app/ml/data.py`, not just described the algorithm abstractly.

---

## Chain 7: Scalability Depth
```
What's the biggest scalability bottleneck today?
   ↓
"No connection pooling — a new MySQL connection opens per request."
   ↓
Why does that matter specifically — what breaks first under load?
   ↓
"MySQL has a max_connections limit (often a few hundred by default). Each
 concurrent request holding open its own connection for the request's
 duration means you'd hit that ceiling far sooner than with pooling, where
 connections are reused and a fixed, smaller pool serves many more
 concurrent requests."
   ↓
Besides pooling, what's the second thing you'd fix?
   ↓
"The unbounded get_user_uploads() query — no LIMIT, used both for /history
 and (worse) for the dashboard's 'recent 5,' which fetches everything and
 slices in Python."
   ↓
Would adding an index alone fix that, or do you also need to change the
query itself?
   ↓
"Both — an index on (user_id, upload_time DESC) makes the ORDER BY faster,
 but it doesn't stop the dashboard from fetching every row; I'd also need to
 add LIMIT 5 directly in the SQL for that specific call, or better, give
 get_user_uploads() an optional limit parameter."
   ↓
At what point would you introduce a read replica instead of just tuning the
primary?
   ↓
"Once read query volume (dashboard/history) meaningfully outpaces write
 volume (uploads) AND vertical scaling of the single primary is no longer
 cost-effective — I wouldn't introduce replica complexity before those two
 conditions are both true, since replication lag adds real operational
 complexity I don't want to pay for prematurely."
```
**Lesson**: scalability chains reward *ordering* — fix the cheap, high-impact things (pooling, indexes, LIMIT) before reaching for heavier infrastructure (replicas, microservices).

---

## Chain 8: "What Would You Improve" (Generic Closer)
```
What would you improve about this project if you had another week?
   ↓
"Fix the duplicate 'Data Science' key bug, add CSRF protection, and add
 LIMIT to the unbounded history query — those are the highest-impact,
 lowest-effort fixes."
   ↓
If you had another month instead of a week?
   ↓
"Add a real test suite starting with the pure functions in predict.py, add
 word-boundary keyword matching, build out interview questions for the
 remaining 15 roles, and add connection pooling."
   ↓
If you had another year and a full team?
   ↓
"Evolve the prediction engine toward a real (still explainable, hybrid)
 ML model trained on labeled resumes, add OCR support for scanned PDFs, add
 proper migrations (Alembic), containerize and deploy behind a load
 balancer with monitoring, and add account management features (password
 reset, email verification, account deletion)."
```
**Lesson**: this three-horizon structure (a week / a month / a year) is a great way to answer any open-ended "what would you improve" question — it shows prioritization at every timescale instead of one flat wishlist.
