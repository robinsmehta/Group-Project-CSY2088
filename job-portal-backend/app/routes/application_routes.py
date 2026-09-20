# app/routes/application_routes.py — Application Routes
#
# Handles job application submissions, candidate retrieval,
# application status updates, and secure resume file serving.
#
# URL prefix: /api/applications
# Endpoints:
#   POST /api/applications                    → apply to a job with a resume upload (user)
#   GET  /api/applications/mine               → view my own submitted applications (user)
#   GET  /api/applications/company            → view all applicants across all company jobs (company)
#   GET  /api/applications/job/<job_id>       → view applicants for one specific job (company)
#   PUT  /api/applications/<id>/status        → update an application's review status (company)
#   GET  /api/applications/resumes/<filename> → download an uploaded resume file (authenticated)

import os
from flask import Blueprint, request, jsonify, session, send_from_directory, current_app
from app.models.application import Application
from app.services import application_service
from app.utils.decorators import role_required

application_bp = Blueprint('applications', __name__)


# POST /api/applications — submit a job application
@application_bp.route('/', methods=['POST'])
@role_required('user')
def submit_application():
    """
    Submit a new job application with a résumé file upload.
    Only logged-in job seekers can apply. One user can only apply to the same job once.

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

    # Accept the job ID from either a form field or a JSON body
    job_id = None
    if request.form:
        job_id = request.form.get('job_id')
    elif request.is_json:
        data = request.get_json(silent=True) or {}
        job_id = data.get('job_id')

    # Get the uploaded resume file from the request
    resume_file = request.files.get('resume')

    # Service layer handles duplicate checking, file saving, and record creation
    result, status_code = application_service.apply_to_job(
        user_id=user_id,
        job_id=job_id,
        resume_file=resume_file
    )

    return jsonify(result), status_code


# GET /api/applications/mine — view the logged-in user's own applications
@application_bp.route('/mine', methods=['GET'])
@role_required('user')
def get_my_applications():
    """
    Return all job applications submitted by the currently logged-in job seeker,
    including the job title, company name, and current review status for each.
    """
    user_id = session.get('user_id')
    result, status_code = application_service.get_my_applications(user_id)
    return jsonify(result), status_code


# GET /api/applications/company — view all applicants across all of a company's jobs
@application_bp.route('/company', methods=['GET'])
@role_required('company')
def get_company_applications():
    """
    Return all applications across every job listing the logged-in company has posted.
    Useful for getting an overview of all incoming candidates in one place.
    """
    company_id = session.get('company_id') or session.get('user_id')
    result, status_code = application_service.get_applications_for_company(company_id)
    return jsonify(result), status_code


# GET /api/applications/job/<job_id> — view applicants for one specific job
@application_bp.route('/job/<int:job_id>', methods=['GET'])
@role_required('company')
def get_applications_for_job(job_id):
    """
    Return all applications submitted for a specific job listing.
    Only the company that posted the job can view its applicants.
    """
    company_id = session.get('company_id') or session.get('user_id')
    result, status_code = application_service.get_applicants_for_job(
        job_id=job_id,
        company_id=company_id
    )
    return jsonify(result), status_code


# PUT /api/applications/<id>/status — update an application's review status
@application_bp.route('/<int:application_id>/status', methods=['PUT'])
@role_required('company')
def update_application_status(application_id):
    """
    Change the review status of an application (e.g., move it from "applied" to "shortlisted").
    Only the company that posted the job can update the status of its applications.

    Expected JSON payload:
        { "status": "shortlisted" }  # valid: applied, under_review, shortlisted, rejected
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


# GET /api/applications/resumes/<filename> — securely download a resume file

@application_bp.route('/resumes/<filename>', methods=['GET'])
def download_resume(filename):
    """
    Serve an uploaded resume file for download.
    The requester must be logged in and must either own the resume (job seeker)
    or own the job it was submitted for (company). Flask's send_from_directory
    prevents path traversal attacks by restricting files to the uploads folder.

    Path parameter:
        filename (str): The stored filename of the resume.
    """
    user_id = session.get('user_id')
    user_role = session.get('role')
    if not user_id or not user_role:
        return jsonify({
            'error': 'Authentication required. Please log in to access this resource.'
        }), 401

    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    stored_paths = {
        filename,
        os.path.join(upload_folder, filename).replace(os.sep, '/'),
    }
    application = Application.query.filter(
        Application.resume_path.in_(stored_paths)
    ).first()

    if not application:
        return jsonify({'error': 'Resume file not found'}), 404

    is_applicant = user_role == 'user' and application.user_id == user_id
    company_id = session.get('company_id') or user_id
    is_job_company = (
        user_role == 'company'
        and application.job is not None
        and application.job.company_id == company_id
    )
    if not (is_applicant or is_job_company):
        return jsonify({'error': 'Not allowed to access this resume'}), 403

    # Convert relative path to absolute so send_from_directory can find the file
    abs_upload_folder = os.path.abspath(upload_folder)

    try:
        return send_from_directory(
            abs_upload_folder,
            filename,
            as_attachment=False
        )
    except FileNotFoundError:
        return jsonify({'error': 'Resume file not found'}), 404
