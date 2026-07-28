# ============================================================
# app/routes/application_routes.py — Application Routes (Presentation Layer)
#
# Handles job application submissions and status management.
#
# Blueprint: application_bp
# URL Prefix (set in app/__init__.py): /api/applications
# Full endpoint URLs:
#   POST /api/applications                        → submit a new application
#   GET  /api/applications/mine                   → get all my applications (user)
#   GET  /api/jobs/<id>/applications              → get all applicants for a job (company)
#   PUT  /api/applications/<id>/status            → update application status (company)
#
# NOTE: GET /api/jobs/<id>/applications is defined in job_routes.py
#       to keep job-related sub-resources together — or here, your choice.
#       We define it here for clarity.
# ============================================================

from flask import Blueprint, request, jsonify
from app.services import application_service
from app.utils.decorators import role_required

application_bp = Blueprint('applications', __name__)


# ============================================================
# POST /api/applications
# ============================================================
@application_bp.route('/', methods=['POST'])
# @role_required('user')  # TODO: Uncomment once role_required decorator is implemented
def submit_application():
    """
    Submit a new job application with an optional résumé file upload.
    Only authenticated USERS (job seekers) can apply.

    Expected request (multipart/form-data to support file upload):
        job_id (int, form field): The ID of the job to apply for.
        resume  (file, optional): The résumé PDF to upload.

    Or as JSON (if not uploading a file):
        { "job_id": 5 }

    Success response (201 Created):
        { "message": "Application submitted", "application": { ... } }

    Error responses:
        400 — Missing job_id, or already applied to this job
        401 — Not logged in as a user
        404 — Job not found
    """
    # TODO: Get the logged-in user's ID from the session
    # user_id = session.get('user_id')

    # TODO: Get job_id from form data or JSON body
    # job_id = request.form.get('job_id') or request.get_json().get('job_id')

    # TODO: Handle file upload (if a résumé was attached)
    # resume_file = request.files.get('resume')
    # If file exists:
    #   - Use werkzeug.utils.secure_filename() to sanitise the filename
    #   - Save it to app.config['UPLOAD_FOLDER']
    #   - Store the file path in resume_path variable

    # TODO: Call application_service.submit_application(user_id, job_id, resume_path)
    #         - Check the job exists
    #         - Check user hasn't already applied to this job (prevent duplicates)
    #         - Create and save Application record
    # result, status_code = application_service.submit_application(user_id, job_id, resume_path)
    # return jsonify(result), status_code

    return jsonify({'message': 'submit_application route stub — not yet implemented'}), 200


# ============================================================
# GET /api/applications/mine
# ============================================================
@application_bp.route('/mine', methods=['GET'])
# @role_required('user')  # TODO: Uncomment once role_required decorator is implemented
def get_my_applications():
    """
    Retrieve all applications submitted by the currently logged-in user.
    Useful for the "My Applications" dashboard page.

    Success response (200 OK):
        { "applications": [ { app1 }, { app2 }, ... ] }

    Error responses:
        401 — Not logged in as a user
    """
    # TODO: Get user_id from session
    # user_id = session.get('user_id')

    # TODO: Call application_service.get_applications_by_user(user_id) which will:
    #         - Query Application.query.filter_by(user_id=user_id).all()
    #         - Optionally include job title/company info in each result
    # result, status_code = application_service.get_applications_by_user(user_id)
    # return jsonify(result), status_code

    return jsonify({'message': 'get_my_applications route stub — not yet implemented'}), 200


# ============================================================
# GET /api/jobs/<id>/applications
# (technically a sub-resource of jobs, but managed here)
# ============================================================
@application_bp.route('/job/<int:job_id>', methods=['GET'])
# @role_required('company')  # TODO: Uncomment once role_required is implemented
def get_applications_for_job(job_id):
    """
    Retrieve all applications for a specific job listing.
    Only the COMPANY THAT POSTED THIS JOB can view its applications.

    Path parameter:
        job_id (int): The ID of the job.

    Success response (200 OK):
        { "applications": [ { app1 }, { app2 }, ... ] }

    Error responses:
        401 — Not logged in as a company
        403 — Not the job's owning company
        404 — Job not found
    """
    # TODO: Get logged-in company_id from session
    # company_id = session.get('company_id')

    # TODO: Call application_service.get_applications_for_job(job_id, company_id) which will:
    #         - Find the Job (404 if not found)
    #         - Verify job.company_id == company_id (403 if mismatch)
    #         - Return all Application records for this job
    # result, status_code = application_service.get_applications_for_job(job_id, company_id)
    # return jsonify(result), status_code

    return jsonify({'message': f'get_applications_for_job({job_id}) stub — not yet implemented'}), 200


# ============================================================
# PUT /api/applications/<id>/status
# ============================================================
@application_bp.route('/<int:application_id>/status', methods=['PUT'])
# @role_required('company')  # TODO: Uncomment once role_required is implemented
def update_application_status(application_id):
    """
    Update the review status of a job application.
    Only the COMPANY that posted the job can change an application's status.

    Path parameter:
        application_id (int): The ID of the application to update.

    Expected JSON body:
        { "status": "shortlisted" }
        # Valid values: "applied", "under_review", "shortlisted", "rejected"

    Success response (200 OK):
        { "message": "Status updated", "application": { ... } }

    Error responses:
        400 — Invalid status value
        401 — Not logged in as a company
        403 — This application's job does not belong to your company
        404 — Application not found
    """
    # TODO: Get logged-in company_id from session
    # company_id = session.get('company_id')

    # TODO: Extract new status from request body
    # data = request.get_json()
    # new_status = data.get('status')

    # TODO: Call application_service.update_status(application_id, company_id, new_status) which will:
    #         - Find Application by ID (404 if not found)
    #         - Verify the application's job belongs to this company (403 if not)
    #         - Validate new_status is one of the allowed enum values
    #         - Update application.status and commit to DB
    # result, status_code = application_service.update_status(application_id, company_id, new_status)
    # return jsonify(result), status_code

    return jsonify({'message': f'update_application_status({application_id}) stub — not yet implemented'}), 200
