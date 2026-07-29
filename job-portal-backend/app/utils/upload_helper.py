# ============================================================
# app/utils/upload_helper.py — File Upload Helper Utilities
#
# Provides file validation and secure file saving logic for
# user resume uploads.
# ============================================================

import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


def allowed_file(filename: str) -> bool:
    """
    Validate whether an uploaded filename has an allowed file extension.

    Allowed extensions: .pdf, .doc, .docx (case-insensitive).

    Args:
        filename (str): The original name of the uploaded file.

    Returns:
        bool: True if file extension is allowed, False otherwise.
    """
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', ALLOWED_EXTENSIONS)
    return ext in allowed


def generate_unique_filename(filename: str) -> str:
    """
    Generate a safe, unique filename for an uploaded file using UUID.

    SECURITY & DESIGN RATIONALE FOR RANDOMIZING FILENAMES:
    1. Prevents File Overwriting (Collisions):
       Many job seekers name their file 'resume.pdf' or 'cv.pdf'. Using original
       filenames would cause subsequent uploads to overwrite existing candidate files.
    2. Path Traversal & Injection Prevention:
       Original filenames may contain malicious path traversal vectors (e.g. '../../etc/passwd')
       or dangerous control characters. Combining werkzeug's secure_filename() with a UUID4
       guarantees a safe, collision-free filename on disk.

    Args:
        filename (str): Original filename submitted by client.

    Returns:
        str: Sanitised, unique filename in format "<uuid>_<sanitised_name>".
    """
    clean_name = secure_filename(filename)
    if not clean_name:
        clean_name = "file"
    unique_id = uuid.uuid4().hex
    return f"{unique_id}_{clean_name}"


def save_resume_file(file, upload_folder: str = None) -> str:
    """
    Validate, sanitize, and save an uploaded resume file to disk.

    Args:
        file (FileStorage): Flask FileStorage object from request.files['resume'].
        upload_folder (str, optional): Target directory. Defaults to app config UPLOAD_FOLDER.

    Returns:
        tuple: (file_path: str, error_message: str)
               If successful, returns (relative_path, None).
               If failed, returns (None, error_str).
    """
    if not file or file.filename == '':
        return None, 'No file selected for upload'

    if not allowed_file(file.filename):
        return None, 'Invalid file type. Only PDF, DOC, and DOCX files are allowed.'

    if not upload_folder:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/resumes')

    # Ensure destination folder exists automatically
    os.makedirs(upload_folder, exist_ok=True)

    filename = generate_unique_filename(file.filename)
    full_path = os.path.join(upload_folder, filename)
    file.save(full_path)

    # Return relative path for database storage (standardised with forward slashes)
    relative_path = os.path.join(upload_folder, filename).replace('\\', '/')
    return relative_path, None
