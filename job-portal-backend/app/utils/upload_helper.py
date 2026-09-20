# app/utils/upload_helper.py — File Upload Helpers
#
# Provides helper functions to validate, sanitize, and save resume uploads securely.

import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


def allowed_file(filename: str) -> bool:
    """
    Check if the uploaded file has an allowed extension (.pdf, .doc, .docx).

    Args:
        filename (str): The original filename.

    Returns:
        bool: True if extension is allowed, False otherwise.
    """
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', ALLOWED_EXTENSIONS)
    return ext in allowed


def generate_unique_filename(filename: str) -> str:
    """
    Generate a unique, safe filename using a UUID.

    Why randomize filenames?
    1. Avoids overwriting existing files when users upload files with the same name (like resume.pdf).
    2. Prevents unsafe characters or invalid path formats in file names.

    Args:
        filename (str): Original filename submitted by client.

    Returns:
        str: Unique filename formatted as "<uuid>_<sanitized_name>".
    """
    clean_name = secure_filename(filename)
    if not clean_name:
        clean_name = "file"
    unique_id = uuid.uuid4().hex
    return f"{unique_id}_{clean_name}"


def save_resume_file(file, upload_folder: str = None):
    """
    Validate and save an uploaded resume file to disk.

    Args:
        file (FileStorage): Uploaded file object from request.files['resume'].
        upload_folder (str, optional): Destination directory. Defaults to app config UPLOAD_FOLDER.

    Returns:
        tuple: (file_path: str, error_message: str)
               If successful, returns (relative_path, None).
               If failed, returns (None, error_message).
    """
    if not file or file.filename == '':
        return None, 'No file selected for upload'

    if not allowed_file(file.filename):
        return None, 'Invalid file type. Only PDF, DOC, and DOCX files are allowed.'

    if not upload_folder:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')

    # Ensure destination folder exists automatically
    os.makedirs(upload_folder, exist_ok=True)

    filename = generate_unique_filename(file.filename)
    full_path = os.path.join(upload_folder, filename)
    file.save(full_path)

    # Return relative path for database storage (standardised with forward slashes)
    relative_path = os.path.join(upload_folder, filename).replace('\\', '/')
    return relative_path, None
