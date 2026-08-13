# 01 — Project Overview

## Project Name
**JobBridge** — "Your AI-Powered Career Companion"

Source of truth for this claim: [README.md](../README.md) and the hero section in [templates/index.html](../templates/index.html).

## Problem Statement
Most freshers and job seekers do not know:
1. Which job role their resume is actually best suited for.
2. Whether their resume is "good enough" in terms of structure (does it have contact info, an education section, a skills section, enough content, etc.).
3. Which specific technical skills they are missing for the role they want.
4. What kind of questions they will actually be asked in an interview for that role.

Today this feedback normally only comes from a mentor, a senior, or a paid resume-review service. JobBridge tries to give an **instant, free, first-pass answer** to all four questions the moment a user uploads their resume.

## Purpose
JobBridge is a Flask web application that:
- Accepts a resume file (PDF or DOCX).
- Extracts the raw text from it.
- Runs it through a **rule-based keyword-matching engine** (not a trained ML/AI model — this is important and explained in [06_Technology_Stack.md](06_Technology_Stack.md)) to guess the most likely job role out of 25 predefined categories.
- Scores the resume out of 100 based on structural checks.
- Shows which of that role's key skills are present and which are missing.
- Suggests additional trending skills for that role.
- Stores the result in a MySQL database against the logged-in user so they can see history and dashboard stats.
- Offers a separate "Interview Prep" page with curated question-and-answer pairs for a subset of the 25 roles.

## Target Users
- **Final-year students / freshers** applying for their first job (this project itself was built by a student — see the "Meet the Team" section in `index.html`, which lists "Radhika Gurjar — Developer" and mentions "Students at Medicaps University").
- **Job seekers** who want a quick, free sanity check on their resume before applying.
- **Anyone preparing for interviews** who wants role-specific practice questions.

## Main Features
All of these are backed by real code — nothing here is a wishlist:

| Feature | Where it lives |
|---|---|
| Register / Login / Logout (session-based auth) | [app/auth/routes.py](../app/auth/routes.py) |
| Resume upload (PDF/DOCX) + text extraction | [app/resume/routes.py](../app/resume/routes.py) |
| Role prediction (25 categories, keyword counting) | [app/ml/predict.py](../app/ml/predict.py), [app/ml/data.py](../app/ml/data.py) |
| Resume score (0–100, 7 rule-based checks) | [app/ml/predict.py](../app/ml/predict.py) `compute_score()` |
| Found vs. missing skill extraction | [app/ml/predict.py](../app/ml/predict.py) `extract_skills()` |
| Suggested "next skills to learn" | [app/ml/data.py](../app/ml/data.py) `SUGGESTED_SKILLS` |
| Upload history table | [app/resume/routes.py](../app/resume/routes.py) `history()`, [templates/history.html](../templates/history.html) |
| Dashboard (totals, average score, last role) | [app/main/routes.py](../app/main/routes.py) `dashboard()`, [templates/dashboard.html](../templates/dashboard.html) |
| Interview Prep page + JSON API | [app/resume/routes.py](../app/resume/routes.py) `interview_prep()`, `get_questions()` |
| Dark mode toggle (frontend only, localStorage) | [static/js/main.js](../static/js/main.js) |

## Real-world Use Cases
- A student about to apply to TCS uploads their resume before submitting it, sees they are missing "REST API" and "JUnit" for a Java Developer role, adds those to their resume, and re-uploads to confirm.
- A bootcamp graduate is unsure if their resume "counts" as a Data Science resume or a Python Developer resume — JobBridge tells them objectively based on keyword density.
- Someone practices the curated Q&A for "Python Developer" the night before an interview.

## Why This Project Is Useful (for an interview discussion)
- It is a **complete, working, full-stack CRUD + auth + file-processing application** — a good vehicle to demonstrate backend fundamentals (Flask, blueprints, MySQL, sessions, password hashing, file parsing).
- It deliberately avoids "black box" AI: the matching logic is transparent keyword counting, which is **explainable** — every prediction can be justified by listing which keywords matched. This is a strong talking point for an interview: you can explain exactly *why* a resume got a particular label, unlike a neural network.
- It touches many topics interviewers probe: authentication security, file upload handling, database design, request lifecycle, session management, template rendering, and a home-grown "AI" feature explained honestly as rule-based rather than pretending to be deep learning.

## High-Level Overview
```
                     ┌───────────────────────────────┐
                     │        Browser (Client)        │
                     │  HTML + CSS + Vanilla JS        │
                     └───────────────┬────────────────┘
                                      │  HTTP (forms / fetch)
                                      ▼
                     ┌───────────────────────────────┐
                     │   Flask Application (run.py)    │
                     │   App Factory: app/__init__.py │
                     │                                 │
                     │   Blueprints:                   │
                     │     auth_bp    → /login /register│
                     │     main_bp    → / /dashboard    │
                     │     resume_bp  → /upload /history│
                     └───────────────┬────────────────┘
                                      │
                        ┌─────────────┼─────────────────┐
                        ▼             ▼                 ▼
                 ┌─────────────┐ ┌───────────┐   ┌────────────────┐
                 │ app/models.py│ │ app/ml/    │   │ PyPDF2 /       │
                 │ (raw SQL)    │ │ predict.py │   │ python-docx     │
                 │              │ │ + data.py  │   │ (text extraction)│
                 └──────┬──────┘ └───────────┘   └────────────────┘
                        │
                        ▼
                 ┌─────────────┐
                 │   MySQL DB   │
                 │ jobbridge_db  │
                 │ users,       │
                 │ resume_uploads│
                 └─────────────┘
```

This project is intentionally **simple and monolithic** — a single Flask app, no microservices, no external AI API, no containerization. That simplicity is a feature for an interview: you can explain every single line of the request path, which is exactly what an interviewer wants to verify.

> **Honesty note (things NOT implemented, even though hinted at in comments/README):**
> - Google OAuth login (`GOOGLE_OAUTH_CLIENT_ID`/`SECRET` exist in `.env.example`, and the docstring in [app/auth/routes.py](../app/auth/routes.py) mentions `/login/google` routes) is **not implemented** — there is no such route in the code.
> - The docstring in [app/models.py](../app/models.py) mentions a `predictions` table, but `init_db()` only actually creates `users` and `resume_uploads`. There is no third table.
> - There are no automated tests, no Docker setup, and no deployment/CI configuration anywhere in the repository.
