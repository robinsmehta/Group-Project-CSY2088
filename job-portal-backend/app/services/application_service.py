# app/services/application_service.py — Application Business Logic
#
# Called by routes in application_routes.py.
#
# What this file handles:
#   - Checking that a user hasn't already applied to the same job twice
#   - Verifying the job exists before accepting any file uploads
#   - Saving the uploaded résumé file securely to disk
#   - Creating and updating Application records in the database
#   - Ensuring companies can only see and change applications for their own jobs

from flask import current_app
from app.extensions import db
from app.models.application import Application
from app.models.job         import Job
from app.models.user        import User
from app.models.company     import Company
from app.utils.upload_helper import save_resume_file


ALLOWED_STATUSES = {'applied', 'under_review', 'shortlisted', 'rejected'}


def apply_to_job(user_id: int, job_id, resume_file=None):
    """
    Submit a new job application, including a résumé file.
    Rejects the request if the user has already applied to this job,
    or if the résumé file is missing or the wrong format.

    Args:
        user_id (int): ID of the authenticated user applying.
        job_id (int or str): ID of the job being applied for.
        resume_file (FileStorage, optional): Uploaded file from request.files['resume'].

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # Validate that a job ID was actually provided
    if not job_id:
        return {'error': 'job_id is required'}, 400

    try:
        job_id = int(job_id)
    except (ValueError, TypeError):
        return {'error': 'Invalid job_id format'}, 400

    # Make sure the job still exists in the database
    job = Job.query.get(job_id)
    if not job:
        return {'error': 'Job not found'}, 404

    # Check for a duplicate application BEFORE saving the résumé file.
    # Uploading a file to disk is slow — rejecting duplicates here avoids doing
    # that work only to throw it away if the application is rejected anyway.
    existing_app = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
    if existing_app:
        return {'error': 'you have already applied to this job'}, 409

    # Validate and save the uploaded résumé file
    resume_path = None
    if resume_file:
        saved_path, upload_error = save_resume_file(resume_file)
        if upload_error:
            return {'error': upload_error}, 400
        resume_path = saved_path
    else:
        return {'error': 'Resume file upload is required (.pdf, .doc, .docx)'}, 400

    # Create the application record with a default status of 'applied'
    new_application = Application(
        job_id=job_id,
        user_id=user_id,
        resume_path=resume_path,
        status='applied'
    )

    db.session.add(new_application)
    db.session.commit()

    return {
        'message': 'Application submitted successfully',
        'application': new_application.to_dict()
    }, 201


def get_my_applications(user_id: int):
    """
    Return all applications the currently logged-in job seeker has submitted,
    including the job title, company name, and a download link for their résumé.

    Args:
        user_id (int): ID of the user whose applications to retrieve.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    applications = Application.query.filter_by(user_id=user_id).all()

    result = []
    for app in applications:
        app_data = app.to_dict()

        # Add job and company details alongside the application record
        if app.job:
            app_data['job_title'] = app.job.title
            app_data['location']  = app.job.location
            app_data['category']  = app.job.category
            app_data['company_name'] = app.job.company.company_name if app.job.company else 'N/A'

        # Build a URL the user can click to download their uploaded résumé
        if app.resume_path:
            filename = app.resume_path.rsplit('/', 1)[-1]
            app_data['resume_url'] = f"/api/applications/resumes/{filename}"

        result.append(app_data)

    return {'applications': result}, 200


def get_applicants_for_job(job_id: int, company_id: int):
    """
    Return all applications submitted for a specific job listing.
    Only the company that posted the job can view its applicants.

    Args:
        job_id (int): ID of the job listing.
        company_id (int): ID of the company making the request.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    job = Job.query.get(job_id)
    if not job:
        return {'error': 'Job not found'}, 404

    # Make sure the company requesting this list actually owns the job
    if job.company_id != company_id:
        return {'error': 'You do not have permission to view applicants for this job'}, 403

    applications = Application.query.filter_by(job_id=job_id).all()

    result = []
    for app in applications:
        app_data = app.to_dict()

        # Add the applicant's name and email so companies can identify candidates
        if app.user:
            app_data['applicant_name']  = app.user.name
            app_data['applicant_email'] = app.user.email

        # Add a download link for the applicant's résumé
        if app.resume_path:
            filename = app.resume_path.rsplit('/', 1)[-1]
            app_data['resume_url'] = f"/api/applications/resumes/{filename}"

        result.append(app_data)

    return {
        'job_id': job.id,
        'job_title': job.title,
        'total_applicants': len(result),
        'applications': result
    }, 200


def get_applications_for_company(company_id: int):
    """
    Return all applications submitted across every job a company has posted.
    Useful for companies that want to see all incoming candidates in one place.

    Args:
        company_id (int): ID of the company.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    company_jobs = Job.query.filter_by(company_id=company_id).all()
    job_ids = [j.id for j in company_jobs]

    if not job_ids:
        return {
            'total_applications': 0,
            'applications': []
        }, 200

    applications = Application.query.filter(Application.job_id.in_(job_ids)).order_by(Application.applied_at.desc()).all()

    result = []
    for app in applications:
        app_data = app.to_dict()
        app_data['created_at'] = app.applied_at.isoformat() if app.applied_at else None

        if app.user:
            app_data['applicant_name']  = app.user.name
            app_data['applicant_email'] = app.user.email

        if app.job:
            app_data['job_title'] = app.job.title

        if app.resume_path:
            filename = app.resume_path.rsplit('/', 1)[-1]
            app_data['resume_url'] = f"/api/applications/resumes/{filename}"

        result.append(app_data)

    return {
        'total_applications': len(result),
        'applications': result
    }, 200


# Friendly aliases for common status strings that users might type
STATUS_SYNONYMS = {
    'reviewing': 'under_review',
    'interview': 'shortlisted',
    'pending': 'applied'
}


def update_application_status(application_id: int, company_id: int, new_status: str):
    """
    Change the review status of a job application (e.g., from 'applied' to 'shortlisted').
    Only the company that posted the job can update its applications.
    This prevents companies from interfering with each other's candidate pipelines.

    Args:
        application_id (int): ID of the application to update.
        company_id (int): ID of the requesting company.
        new_status (str): New status value. Allowed: applied, under_review, shortlisted, rejected.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # Translate any friendly alias to the canonical status string
    if new_status and new_status in STATUS_SYNONYMS:
        new_status = STATUS_SYNONYMS[new_status]

    # Reject invalid status values
    if not new_status or new_status not in ALLOWED_STATUSES:
        return {
            'error': f"Invalid status. Must be one of: {', '.join(sorted(ALLOWED_STATUSES))}"
        }, 400

    application = Application.query.get(application_id)
    if not application:
        return {'error': 'Application not found'}, 404

    # Ensure the company owns the job that this application was submitted for
    if not application.job or application.job.company_id != company_id:
        return {'error': 'You do not have permission to update this application'}, 403

    application.status = new_status
    db.session.commit()

    return {
        'message': 'Application status updated successfully',
        'application': application.to_dict()
    }, 200

# Alias method names for backwards compatibility
submit_application = apply_to_job
get_applications_by_user = get_my_applications
get_applications_for_job = get_applicants_for_job
get_company_applications = get_applications_for_company
update_status = update_application_status
