# ============================================================
# app/services/application_service.py — Application Business Logic
#
# This is the BUSINESS LOGIC LAYER for job applications.
# Called by routes in application_routes.py.
#
# Responsibilities:
#   - Prevent duplicate applications (same user applying to same job twice)
#   - Check that the job exists
#   - Save and validate uploaded résumé files securely
#   - Verify company ownership before listing applicants or updating statuses
#   - Save and update Application database records
# ============================================================

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
    Submit a new job application with an uploaded résumé.

    Args:
        user_id (int): ID of the authenticated user applying.
        job_id (int or str): ID of the job being applied for.
        resume_file (FileStorage, optional): Uploaded file from request.files['resume'].

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # 1. Validate job_id input
    if not job_id:
        return {'error': 'job_id is required'}, 400

    try:
        job_id = int(job_id)
    except (ValueError, TypeError):
        return {'error': 'Invalid job_id format'}, 400

    # 2. Check that the job exists in the database
    job = Job.query.get(job_id)
    if not job:
        return {'error': 'Job not found'}, 404

    # -------------------------------------------------------------------------
    # WHY THE DUPLICATE-APPLICATION CHECK HAPPENS BEFORE SAVING THE FILE:
    #
    # Performance & Storage Efficiency:
    # If a user attempts to apply to the same job twice, checking the database first
    # allows us to reject duplicate submissions instantly before performing any disk I/O.
    # Saving a file to disk is a relatively expensive operation. If we saved the file
    # before checking for duplicates, a rejected request would waste server storage
    # and leave orphaned files on disk that require cleanup scripts.
    # -------------------------------------------------------------------------
    existing_app = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
    if existing_app:
        return {'error': 'you have already applied to this job'}, 409

    # 3. Validate and save the uploaded résumé file using upload_helper
    resume_path = None
    if resume_file:
        saved_path, upload_error = save_resume_file(resume_file)
        if upload_error:
            return {'error': upload_error}, 400
        resume_path = saved_path
    else:
        # Prompt specifies resume file upload, return 400 if missing
        return {'error': 'Resume file upload is required (.pdf, .doc, .docx)'}, 400

    # 4. Create new Application record with default status='applied'
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
    Retrieve all job applications submitted by the currently authenticated user.

    Args:
        user_id (int): ID of the user.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    applications = Application.query.filter_by(user_id=user_id).all()

    result = []
    for app in applications:
        app_data = app.to_dict()

        # Join with jobs and company details
        if app.job:
            app_data['job_title'] = app.job.title
            app_data['location']  = app.job.location
            app_data['category']  = app.job.category
            app_data['company_name'] = app.job.company.company_name if app.job.company else 'N/A'

        # Build download link if resume file is present
        if app.resume_path:
            filename = app.resume_path.rsplit('/', 1)[-1]
            app_data['resume_url'] = f"/api/applications/resumes/{filename}"

        result.append(app_data)

    return {'applications': result}, 200


def get_applicants_for_job(job_id: int, company_id: int):
    """
    Get all applicant submissions for a specific job listing owned by a company.

    Args:
        job_id (int): ID of the job listing.
        company_id (int): ID of the authenticated company making the request.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    job = Job.query.get(job_id)
    if not job:
        return {'error': 'Job not found'}, 404

    # Confirm job ownership
    if job.company_id != company_id:
        return {'error': 'You do not have permission to view applicants for this job'}, 403

    applications = Application.query.filter_by(job_id=job_id).all()

    result = []
    for app in applications:
        app_data = app.to_dict()

        # Join with user details (applicant name & email)
        if app.user:
            app_data['applicant_name']  = app.user.name
            app_data['applicant_email'] = app.user.email

        # Build accessible download link for the resume file
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
    Retrieve all job application submissions across all job listings owned by a company.

    Args:
        company_id (int): ID of the authenticated company.

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


STATUS_SYNONYMS = {
    'reviewing': 'under_review',
    'interview': 'shortlisted',
    'pending': 'applied'
}


def update_application_status(application_id: int, company_id: int, new_status: str):
    """
    Update the review status of an application.

    Args:
        application_id (int): ID of the application record to update.
        company_id (int): ID of the requesting company.
        new_status (str): New status value ('applied', 'under_review', 'shortlisted', 'rejected').

    Returns:
        tuple: (response_dict, http_status_code)
    """
    if new_status and new_status in STATUS_SYNONYMS:
        new_status = STATUS_SYNONYMS[new_status]

    # 1. Validate new_status input against allowed values
    if not new_status or new_status not in ALLOWED_STATUSES:
        return {
            'error': f"Invalid status. Must be one of: {', '.join(sorted(ALLOWED_STATUSES))}"
        }, 400

    # 2. Look up the application record
    application = Application.query.get(application_id)
    if not application:
        return {'error': 'Application not found'}, 404

    # -------------------------------------------------------------------------
    # WHY STATUS UPDATES ARE RESTRICTED TO THE OWNING COMPANY ONLY:
    #
    # Multi-Tenant Security & Ownership Authorization:
    # Applications contain candidate submissions for specific job listings. Allowing
    # any company to modify application statuses would introduce critical authorization
    # flaws where competing employers could alter candidates' review statuses.
    # Verifying that application.job.company_id matches company_id ensures strict
    # ownership controls and data isolation across company accounts.
    # -------------------------------------------------------------------------
    if not application.job or application.job.company_id != company_id:
        return {'error': 'You do not have permission to update this application'}, 403

    # 3. Update status and commit changes
    application.status = new_status
    db.session.commit()

    return {
        'message': 'Application status updated successfully',
        'application': application.to_dict()
    }, 200


# ============================================================
# TASK-007 — Build the "application stats" feature for the User Dashboard
# ============================================================
#
# PROBLEM:
# The new User Dashboard design shows 4 numbers at the top of the page:
# Total Applied, In Review (i.e. under_review), Shortlisted, and Rejected.
# This counting logic does not exist anywhere in the backend yet — there is
# no function here, and no route in application_routes.py, that returns
# these counts.
#
# (Note: This is NOT the same as the old "platform-wide admin stats" idea —
# this only counts ONE job seeker's own applications, so it's simpler.)
#
# WHAT YOU NEED TO DO:
# 1. Add a new function in this file, e.g. `get_my_application_stats(user_id)`,
#    that looks a lot like `get_my_applications()` above it, except instead
#    of returning the full list of applications, it counts how many of that
#    user's applications currently have each status.
#    Example return shape:
#        {
#          'total': 10,
#          'applied': 4,
#          'under_review': 3,
#          'shortlisted': 2,
#          'rejected': 1
#        }
# 2. Add a new route in application_routes.py, something like:
#        GET /api/applications/mine/stats
#    protected the same way as `get_my_applications` (role_required('user')),
#    that calls your new function and returns the counts as JSON.
# 3. On the frontend, the User Dashboard (job-portal-frontend/user/dashboard.html)
#    needs to call this new endpoint and put the numbers into the 4 stat boxes
#    at the top of the page — see the matching TODO in that file.
#
# WHAT "DONE" LOOKS LIKE:
# If a job seeker has applied to 10 jobs and 3 of them are "shortlisted",
# calling this new endpoint returns shortlisted: 3, and the dashboard shows
# "3" in the Shortlisted box — and it updates correctly every time you check.
#
# ASSIGNED TASK:
# Reeju (E4) — Build the User Dashboard's stat numbers.
# ============================================================


# Alias method names for backwards compatibility if needed
submit_application = apply_to_job
get_applications_by_user = get_my_applications
get_applications_for_job = get_applicants_for_job
get_company_applications = get_applications_for_company
update_status = update_application_status

