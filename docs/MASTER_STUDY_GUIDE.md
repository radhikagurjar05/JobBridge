# MASTER STUDY GUIDE — JobBridge TCS Digital Interview Prep

## Project Summary

**JobBridge** is a Flask-based, MySQL-backed web application that lets a user upload a resume (PDF or DOCX) and instantly receive: a predicted job role (1 of 25 categories, via a transparent rule-based keyword-counting engine — deliberately **not** a trained ML model), a resume quality score out of 100 (7 structural checks), a found-vs-missing skills breakdown for the predicted role, and suggested skills to learn next. Registered users get a dashboard and full upload history; a separate interview-prep page offers curated Q&A for 10 of the 25 roles. The whole app is a single monolithic Flask process using the Application Factory pattern, three blueprints (`auth`, `main`, `resume`), raw SQL (no ORM) against a two-table MySQL schema, and server-rendered Jinja2 templates with a vanilla CSS/JS frontend (including a dark-mode toggle). There is no deployment configuration, no automated tests, and several honestly-documented gaps (no CSRF protection, no Google OAuth despite placeholder env vars, a stale docstring referencing a `predictions` table that was never built) — all catalogued precisely throughout this guide so you can discuss them with confidence rather than being caught by them.

This guide (and every document it indexes) is based **only** on what's actually implemented in the codebase at `/home/nikhil/Sudh/JobBridge` — nothing here is speculative or invented.

---

## Table of Contents & Suggested Study Order

| # | Document | What It Covers | Est. Reading Time |
|---|---|---|---|
| 1 | [01_Project_Overview.md](01_Project_Overview.md) | Problem statement, purpose, features, use cases | 8 min |
| 2 | [02_Elevator_Pitch.md](02_Elevator_Pitch.md) | 30-sec / 1-min / 2-min / 5-min spoken explanations | 10 min |
| 3 | [03_Architecture.md](03_Architecture.md) | Layers, diagrams, request lifecycle | 12 min |
| 4 | [04_Application_Flow.md](04_Application_Flow.md) | Every feature's end-to-end flow with diagrams | 15 min |
| 5 | [05_Folder_Structure.md](05_Folder_Structure.md) | Every folder/file, why it exists, dependency flow | 10 min |
| 6 | [06_Technology_Stack.md](06_Technology_Stack.md) | Every technology: what/why/pros/cons/alternatives | 15 min |
| 7 | [07_Database.md](07_Database.md) | Full schema, ER diagram, normalization, constraints | 10 min |
| 8 | [08_APIs.md](08_APIs.md) | Every route documented like an API endpoint | 12 min |
| 9 | [09_Features.md](09_Features.md) | Deep dive per feature: logic, edge cases, improvements | 15 min |
| 10 | [10_Code_Walkthrough.md](10_Code_Walkthrough.md) | Reading order for a new engineer, execution trace | 10 min |
| 11 | [11_Important_Functions.md](11_Important_Functions.md) | Every key function: input/output/logic/callers | 12 min |
| 12 | [12_Security.md](12_Security.md) | Full security audit — implemented vs. missing | 12 min |
| 13 | [13_Scalability.md](13_Scalability.md) | Design for 1 million users | 10 min |
| 14 | [14_Challenges_and_Improvements.md](14_Challenges_and_Improvements.md) | Real bugs found, root cause, fix, lesson | 10 min |
| 15 | [15_TCS_Digital_Interview_QA.md](15_TCS_Digital_Interview_QA.md) | 104 Q&A: Basic/Intermediate/Advanced | 35 min |
| 16 | [16_Cross_Questions.md](16_Cross_Questions.md) | Realistic interviewer follow-up chains | 15 min |
| 17 | [17_Resume_Questions.md](17_Resume_Questions.md) | 52 questions if this is on your resume | 15 min |
| 18 | [18_Weak_Areas.md](18_Weak_Areas.md) | Ranked list of what you MUST know cold | 10 min |
| 19 | [19_Revision_Notes.md](19_Revision_Notes.md) | Full 20-minute pre-interview revision | 20 min |
| 20 | [20_Cheat_Sheet.md](20_Cheat_Sheet.md) | Ultra-compact final reference | 5 min |

**Total first-pass reading time: ~4.5 hours** (spread across the 7-day plan below — you are not meant to read this in one sitting).

### Suggested Study Order (Not Just Numerical)
1. **Understand it** (Docs 1–5): what it is, how to say it, how it's architected, how features flow, how it's organized.
2. **Know it cold** (Docs 6–11): every technology choice, the database, every API, every feature's edge cases, every important function.
3. **Defend it** (Docs 12–14): security posture, scalability posture, and the real bugs/challenges you can speak to with authority.
4. **Rehearse it** (Docs 15–17): 100+ direct Q&A, realistic follow-up chains, resume-specific questions.
5. **Cram it** (Docs 18–20): weak-areas ranking, 20-minute revision notes, and the final cheat sheet.

---

## 7-Day Interview Preparation Plan

### Day 1 — Foundation (Understand the "What" and "Why")
- Read: [01_Project_Overview.md](01_Project_Overview.md), [02_Elevator_Pitch.md](02_Elevator_Pitch.md), [03_Architecture.md](03_Architecture.md).
- Do: Practice the 30-second and 1-minute pitches out loud, 5 times each, without notes.
- Goal by end of day: you can describe what JobBridge is and why it exists in under 30 seconds, confidently.

### Day 2 — How It's Built
- Read: [04_Application_Flow.md](04_Application_Flow.md), [05_Folder_Structure.md](05_Folder_Structure.md), [10_Code_Walkthrough.md](10_Code_Walkthrough.md).
- Do: Open the actual codebase side-by-side and trace the `/upload` flow file-by-file as you read Doc 4 and Doc 10.
- Goal by end of day: you can whiteboard the request lifecycle for resume upload from memory.

### Day 3 — Technology & Data
- Read: [06_Technology_Stack.md](06_Technology_Stack.md), [07_Database.md](07_Database.md), [08_APIs.md](08_APIs.md).
- Do: Write out the two-table schema from memory, then check it against Doc 7. Recite why Flask/MySQL/no-ORM were chosen, unprompted.
- Goal by end of day: you can answer any "why did you choose X technology" question with a reasoned trade-off, not just a preference.

### Day 4 — Features & Functions
- Read: [09_Features.md](09_Features.md), [11_Important_Functions.md](11_Important_Functions.md).
- Do: For each of the 7 major features, say out loud: purpose → flow → files → one edge case. Time yourself — aim for under 90 seconds per feature.
- Goal by end of day: no feature surprises you if asked to explain it cold.

### Day 5 — Security, Scale, and Honest Self-Critique
- Read: [12_Security.md](12_Security.md), [13_Scalability.md](13_Scalability.md), [14_Challenges_and_Improvements.md](14_Challenges_and_Improvements.md).
- Do: Write your own one-paragraph answer to "what's the biggest security gap?" and "what's the biggest scalability bottleneck?" without looking, then compare to the docs.
- Goal by end of day: you can name real gaps (CSRF, no pooling, duplicate dict key) proactively and calmly, with a fix for each.

### Day 6 — Full Mock Interview
- Read: [15_TCS_Digital_Interview_QA.md](15_TCS_Digital_Interview_QA.md) (all tiers), [16_Cross_Questions.md](16_Cross_Questions.md).
- Do: Have someone (or yourself, reading questions out loud) fire questions at you from Doc 15 in random order, including at least 2 full follow-up chains from Doc 16 (Chain 2 "Is this AI?" and Chain 6 "keyword-matching weaknesses" are the highest-value ones to rehearse).
- Goal by end of day: you don't freeze on any Basic or Intermediate question, and you can hold your own through at least 3 Advanced follow-up chains.

### Day 7 — Resume Defense & Final Cram
- Read: [17_Resume_Questions.md](17_Resume_Questions.md), [18_Weak_Areas.md](18_Weak_Areas.md), then finish with [19_Revision_Notes.md](19_Revision_Notes.md) and [20_Cheat_Sheet.md](20_Cheat_Sheet.md).
- Do: Read Doc 19 once, slowly, the night before. Read Doc 20 once, quickly, the morning of the interview — nothing new, just activation of what you already know.
- Goal by end of day: total recall of the project's shape, its honest gaps, and your elevator pitch — calm, not cramming anything new.

---

## The Three Things to Never Forget
1. **It's not AI — it's rule-based keyword counting, and that's a deliberate, defensible choice for explainability.** Say this immediately and calmly if asked; never get defensive about it.
2. **You know your own bugs** — the duplicate `"Data Science"` key, the java/javascript substring false-positive, and the stale `predictions`/Google-OAuth references. Naming these unprompted is the single highest-signal thing you can do in this interview.
3. **Files are never saved to disk** — parsed entirely in memory and discarded. This is a genuine architectural strength; know it well enough to say so with pride, not just as a passing fact.

Good luck.
