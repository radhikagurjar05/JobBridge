"""
app/ml/predict.py — Resume analysis using pure Python (no ML libraries).

Three functions you can easily explain in an interview:

1. predict_role(text)    — counts keyword matches per role; highest count wins
2. compute_score(text)   — checks for resume sections; awards points per check
3. extract_skills(text, role) — finds which role keywords appear in the resume
"""

import re
from app.ml.data import ROLE_KEYWORDS, SUGGESTED_SKILLS


# ----------------------------------------------------------------
# Helper: Clean resume text before analysis
# ----------------------------------------------------------------
def clean_text(text):
    """
    Removes URLs, special characters, and extra whitespace from text.
    Makes keyword matching more reliable.
    """
    text = re.sub(r'http\S+', ' ', text)           # remove URLs
    text = re.sub(r'[^a-zA-Z0-9\s/+#.]', ' ', text)  # keep letters, numbers, /+#.
    text = re.sub(r'\s+', ' ', text)               # collapse multiple spaces
    return text.lower().strip()


# ----------------------------------------------------------------
# 1. Predict the most suitable job role
# ----------------------------------------------------------------
def predict_role(resume_text):
    """
    Algorithm (simple and explainable):
      - We have a dictionary: role → list of keywords.
      - We count how many keywords from each role appear in the resume.
      - The role with the highest count is our prediction.

    Returns a tuple: (predicted_role, scores_dict)
      predicted_role — string, e.g. "Python Developer"
      scores_dict    — dict of all roles and their keyword match counts (for debugging)
    """
    cleaned = clean_text(resume_text)

    scores = {}
    for role, keywords in ROLE_KEYWORDS.items():
        # Count how many keywords from this role appear in the cleaned resume
        count = sum(1 for kw in keywords if kw in cleaned)
        scores[role] = count

    # Pick the role with the maximum keyword matches
    predicted_role = max(scores, key=scores.get)

    # Edge case: if ALL scores are 0, we cannot predict
    if scores[predicted_role] == 0:
        predicted_role = "General / Other"

    return predicted_role, scores


# ----------------------------------------------------------------
# 2. Compute a resume quality score (0–100)
# ----------------------------------------------------------------
def compute_score(resume_text):
    """
    Rule-based scoring. Each check awards points.
    Total maximum = 100 points.

    Returns a dict with:
      'score'   — integer 0-100
      'details' — list of (check_name, passed, points) tuples
    """
    text_lower = resume_text.lower()
    word_count = len(resume_text.split())

    # Define checks: (label, did_it_pass, points_awarded_if_true)
    checks = [
        ("Has email address",        bool(re.search(r'[\w.-]+@[\w.-]+\.\w+', resume_text)),   15),
        ("Has phone number",         bool(re.search(r'(\+?\d[\d\s\-]{8,}\d)', resume_text)),  15),
        ("Has Skills section",       'skill' in text_lower,                                    20),
        ("Has Education section",    any(w in text_lower for w in ['education', 'degree', 'university', 'college', 'bachelor', 'master']), 15),
        ("Has Experience section",   any(w in text_lower for w in ['experience', 'work history', 'employment', 'internship']),             15),
        ("Sufficient length (250+ words)", word_count >= 250,                                 10),
        ("Has Projects / Achievements",    any(w in text_lower for w in ['project', 'achievement', 'built', 'developed', 'designed']),     10),
    ]

    total_score = sum(pts for _, passed, pts in checks if passed)
    details = [{"label": label, "passed": passed, "points": pts} for label, passed, pts in checks]

    return {"score": total_score, "details": details}


# ----------------------------------------------------------------
# 3. Extract skills found in the resume for the predicted role
# ----------------------------------------------------------------
def extract_skills(resume_text, role):
    """
    Looks at the keyword list for the given role.
    Returns two lists:
      found   — keywords that DO appear in the resume
      missing — keywords that DO NOT appear in the resume
    """
    if role not in ROLE_KEYWORDS:
        return [], []

    cleaned = clean_text(resume_text)
    role_keywords = ROLE_KEYWORDS[role]

    found   = [kw for kw in role_keywords if kw in cleaned]
    missing = [kw for kw in role_keywords if kw not in cleaned]

    return found, missing


# ----------------------------------------------------------------
# 4. Get suggested (future) skills for a role
# ----------------------------------------------------------------
def get_suggested_skills(role):
    """Returns a list of recommended skills to learn for career growth."""
    return SUGGESTED_SKILLS.get(role, [])


# ----------------------------------------------------------------
# 5. Full analysis in one call (used by the upload route)
# ----------------------------------------------------------------
def analyze_resume(resume_text):
    """
    Runs all analysis steps and returns a single result dictionary.
    This is what the Flask route calls.
    """
    predicted_role, _scores = predict_role(resume_text)
    score_info              = compute_score(resume_text)
    found_skills, missing_skills = extract_skills(resume_text, predicted_role)
    suggested               = get_suggested_skills(predicted_role)

    return {
        "predicted_role":  predicted_role,
        "score":           score_info["score"],
        "score_details":   score_info["details"],
        "found_skills":    found_skills,
        "missing_skills":  missing_skills,
        "suggested_skills": suggested,
    }
