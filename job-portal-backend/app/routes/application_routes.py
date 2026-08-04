# ============================================================
# app/routes/application_routes.py — Application Routes (Presentation Layer)
#
# Handles job application submissions, candidate retrieval,
# application status updates, and secure resume file serving.
#
# Blueprint: application_bp (URL prefix: /api/applications)
# Endpoints:
#   POST /api/applications                    → Apply to job with resume upload (user)
#   GET  /api/applications/mine               → View my submitted applications (user)
#   GET  /api/applications/job/<job_id>       → View applicants for a job (company)
#   PUT  /api/applications/<id>/status        → Update application status (company)
#   GET  /api/applications/resumes/<filename> → Serve/download uploaded resume file
# ============================================================

import os
from flask import Blueprint, request, jsonify, session, send_from_directory, current_app
from app.services import application_service
from app.utils.decorators import role_required

application_bp = Blueprint('applications', __name__)


# ============================================================
# 1. POST /api/applications
# ============================================================
@application_bp.route('/', methods=['POST'])
@role_required('user')
def submit_application():
    """
    Submit a new job application with a résumé file upload.
    Only authenticated USERS (job seekers) can apply.

    Accepts multipart/form-data:
        job_id (form field): ID of the job listing.
        resume  (file field): Résumé file (.pdf, .doc, .docx).

    Returns:
        201 Created — Application submitted successfully
        400 Bad Request — Missing job_id or invalid file type
        403 Forbidden — User role missing
        404 Not Found — Job does not exist
        409 Conflict — User already applied to this job
    """
    user_id = session.get('user_id')

    # Parse job_id from multipart form-data or fallback to JSON payload
    job_id = None
    if request.form:
        job_id = request.form.get('job_id')
    elif request.is_json:
        data = request.get_json(silent=True) or {}
        job_id = data.get('job_id')

    # Get resume file from request.files
    resume_file = request.files.get('resume')

    # Call service layer business logic
    result, status_code = application_service.apply_to_job(
        user_id=user_id,
        job_id=job_id,
        resume_file=resume_file
    )

    return jsonify(result), status_code


# ============================================================
# 2. GET /api/applications/mine
# ============================================================
@application_bp.route('/mine', methods=['GET'])
@role_required('user')
def get_my_applications():
    """
    Retrieve all applications submitted by the logged-in user.

    Returns:
        200 OK — List of applications with job title and company details
        401 Unauthorized — User not logged in
        403 Forbidden — Requires 'user' role
    """
    user_id = session.get('user_id')
    result, status_code = application_service.get_my_applications(user_id)
    return jsonify(result), status_code


# ============================================================
# 3. GET /api/applications/job/<job_id>
# ============================================================
@application_bp.route('/job/<int:job_id>', methods=['GET'])
@role_required('company')
def get_applications_for_job(job_id):
    """
    Retrieve all applications for a specific job listing.
    Only the COMPANY THAT POSTED THE JOB can view its applicants.

    Returns:
        200 OK — List of applicants with user details and resume links
        403 Forbidden — Requesting company does not own the job
        404 Not Found — Job not found
    """
    company_id = session.get('company_id') or session.get('user_id')
    result, status_code = application_service.get_applicants_for_job(
        job_id=job_id,
        company_id=company_id
    )
    return jsonify(result), status_code


# ============================================================
# 4. PUT /api/applications/<id>/status
# ============================================================
@application_bp.route('/<int:application_id>/status', methods=['PUT'])
@role_required('company')
def update_application_status(application_id):
    """
    Update the review status of an application.
    Only the COMPANY THAT POSTED THE JOB can update applicant status.

    Expected JSON payload:
        { "status": "shortlisted" }  # valid: applied, under_review, shortlisted, rejected

    Returns:
        200 OK — Application status updated successfully
        400 Bad Request — Invalid status value
        403 Forbidden — Requesting company does not own the application's job
        404 Not Found — Application not found
    """
    company_id = session.get('company_id') or session.get('user_id')

    data = request.get_json(silent=True) or {}
    new_status = data.get('status') or data.get('new_status')

    result, status_code = application_service.update_application_status(
        application_id=application_id,
        company_id=company_id,
        new_status=new_status
    )
    return jsonify(result), status_code


# ============================================================
# 5. GET /api/applications/resumes/<filename> — Secure Resume File Serving
# ============================================================
@application_bp.route('/resumes/<filename>', methods=['GET'])

def download_resume(filename):
    """
    Securely serve/download an uploaded resume file.

    SECURITY & PATH TRAVERSAL PROTECTION:
    Flask's `send_from_directory()` function ensures that files are strictly served from
    the configured UPLOAD_FOLDER directory. It automatically sanitizes filenames and rejects
    any path traversal attempts (such as '../../etc/passwd' or encoded slashes) by returning
    a 404 or 400 error if the resulting path escapes the target directory.

    Path parameter:
        filename (str): Sanitized unique filename stored in DB.
    """
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')

    # Convert relative path to absolute directory for send_from_directory
    abs_upload_folder = os.path.abspath(upload_folder)

    try:
        return send_from_directory(
            abs_upload_folder,
            filename,
            as_attachment=False
        )
    except FileNotFoundError:
        return jsonify({'error': 'Resume file not found'}), 404
