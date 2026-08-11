"""
app/resume/routes.py — Resume Blueprint.

Routes:
    GET/POST  /upload           — Upload a resume and see analysis results
    GET       /history          — View all past uploads for the logged-in user
    GET       /interview-prep   — Interview questions by role (JSON + page)
    GET       /api/questions    — Returns interview Q&A as JSON (called by JS)
"""

import io
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, jsonify, current_app
)
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document

from app.ml.predict import analyze_resume
from app.ml.data import INTERVIEW_QUESTIONS, ROLE_KEYWORDS
from app.models import save_upload, get_user_uploads
from app.main.routes import login_required

resume_bp = Blueprint('resume', __name__)


# ----------------------------------------------------------------
# Helper: Extract text from uploaded file
# ----------------------------------------------------------------
def allowed_file(filename):
    """Check if the file extension is PDF or DOCX."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def extract_text(file):
    """
    Extract plain text from a PDF or DOCX file object.
    Returns the text as a string.
    """
    filename = secure_filename(file.filename)

    if filename.lower().endswith('.pdf'):
        reader = PdfReader(io.BytesIO(file.read()))
        text = ''
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
        return text

    elif filename.lower().endswith('.docx'):
        doc = Document(io.BytesIO(file.read()))
        paragraphs = [p.text for p in doc.paragraphs if p.text]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        paragraphs.append(cell.text.strip())
        return '\n'.join(paragraphs)

    return ''


# ----------------------------------------------------------------
# Upload Route
# ----------------------------------------------------------------
@resume_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template('upload.html')

    # --- Handle file upload ---
    if 'resume' not in request.files:
        flash('No file selected. Please choose a PDF or DOCX file.', 'error')
        return render_template('upload.html')

    file = request.files['resume']

    if file.filename == '':
        flash('No file selected.', 'error')
        return render_template('upload.html')

    if not allowed_file(file.filename):
        flash('Only PDF and DOCX files are supported.', 'error')
        return render_template('upload.html')

    # --- Extract text ---
    try:
        resume_text = extract_text(file)
    except Exception as e:
        flash(f'Could not read the file. Error: {str(e)}', 'error')
        return render_template('upload.html')

    if not resume_text.strip():
        flash('Could not extract text from the file. Make sure it is not a scanned image PDF.', 'error')
        return render_template('upload.html')

    # --- Run analysis (pure Python — no ML library) ---
    results = analyze_resume(resume_text)

    # --- Save to database ---
    filename = secure_filename(file.filename)
    save_upload(
        user_id       = session['user_id'],
        filename      = filename,
        predicted_role = results['predicted_role'],
        resume_score  = results['score']
    )

    return render_template('upload.html', results=results, filename=filename)


# ----------------------------------------------------------------
# History Route
# ----------------------------------------------------------------
@resume_bp.route('/history')
@login_required
def history():
    uploads = get_user_uploads(session['user_id'])
    return render_template('history.html', uploads=uploads)


# ----------------------------------------------------------------
# Interview Prep Page
# ----------------------------------------------------------------
@resume_bp.route('/interview-prep')
def interview_prep():
    # Pass all available roles so the dropdown can be populated
    roles = list(INTERVIEW_QUESTIONS.keys())
    return render_template('interview_prep.html', roles=roles)


# ----------------------------------------------------------------
# API: Return interview questions for a selected role (called by JS)
# ----------------------------------------------------------------
@resume_bp.route('/api/questions')
def get_questions():
    role = request.args.get('role', '')
    questions = INTERVIEW_QUESTIONS.get(role, [])
    return jsonify(questions)
