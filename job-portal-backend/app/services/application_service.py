# ============================================================
# app/services/application_service.py — Application Business Logic
#
# This is the BUSINESS LOGIC LAYER for job applications.
# Called by routes in application_routes.py.
#
# Responsibilities:
#   - Prevent duplicate applications (same user applying to same job twice)
#   - Check that the job exists and is from an approved company
#   - Verify company ownership before status updates
#   - Save and retrieve Application records
# ============================================================

from app.extensions import db
from app.models.application import Application
from app.models.job         import Job


def submit_application(user_id: int, job_id: int, resume_path: str = None):
    """
    Submit a new job application from a user.

    Args:
        user_id     (int): ID of the authenticated user applying.
        job_id      (int): ID of the job being applied for.
        resume_path (str, optional): Filesystem path to the uploaded résumé.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Check that the job exists
    # job = Job.query.get(job_id)
    # if not job:
    #     return {'error': 'Job not found'}, 404

    # TODO: Check that the user hasn't already applied to this job
    # existing = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
    # if existing:
    #     return {'error': 'You have already applied to this job'}, 409

    # TODO: Create and save the Application record
    # new_application = Application(
    #     user_id     = user_id,
    #     job_id      = job_id,
    #     resume_path = resume_path,
    #     status      = 'applied',   # default, but explicit for clarity
    # )
    # db.session.add(new_application)
    # db.session.commit()
    # return {'message': 'Application submitted successfully', 'application': new_application.to_dict()}, 201

    return {'message': 'submit_application service stub — not yet implemented'}, 200


def get_applications_by_user(user_id: int):
    """
    Get all applications submitted by a specific user.

    Args:
        user_id (int): ID of the user.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Query applications for this user
    # applications = Application.query.filter_by(user_id=user_id).all()

    # TODO: Optionally include related job/company info for richer responses
    # result = []
    # for app in applications:
    #     app_dict = app.to_dict()
    #     app_dict['job_title'] = app.job.title           # access via relationship
    #     app_dict['company']   = app.job.company.company_name
    #     result.append(app_dict)

    # return {'applications': result}, 200

    return {'message': 'get_applications_by_user service stub — not yet implemented'}, 200


def get_applications_for_job(job_id: int, company_id: int):
    """
    Get all applications for a specific job (company view).

    Args:
        job_id     (int): The job whose applications to retrieve.
        company_id (int): Must match job.company_id (ownership check).

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Find the job (404 if missing)
    # job = Job.query.get(job_id)
    # if not job:
    #     return {'error': 'Job not found'}, 404

    # TODO: Verify the company owns this job
    # if job.company_id != company_id:
    #     return {'error': 'Access denied'}, 403

    # TODO: Retrieve and return applications
    # applications = Application.query.filter_by(job_id=job_id).all()
    # return {'applications': [a.to_dict() for a in applications]}, 200

    return {'message': 'get_applications_for_job service stub — not yet implemented'}, 200


def update_status(application_id: int, company_id: int, new_status: str):
    """
    Update the review status of an application.

    Args:
        application_id (int): The application to update.
        company_id     (int): Must be the company that posted the job.
        new_status     (str): One of: 'applied', 'under_review', 'shortlisted', 'rejected'.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # Define the allowed status values (must match the ENUM in the model)
    VALID_STATUSES = ['applied', 'under_review', 'shortlisted', 'rejected']

    # TODO: Validate new_status
    # if new_status not in VALID_STATUSES:
    #     return {'error': f'Invalid status. Must be one of: {VALID_STATUSES}'}, 400

    # TODO: Find the application (404 if missing)
    # application = Application.query.get(application_id)
    # if not application:
    #     return {'error': 'Application not found'}, 404

    # TODO: Verify that the application's job belongs to this company
    # if application.job.company_id != company_id:
    #     return {'error': 'You do not have permission to update this application'}, 403

    # TODO: Update status and commit
    # application.status = new_status
    # db.session.commit()
    # return {'message': 'Application status updated', 'application': application.to_dict()}, 200

    return {'message': f'update_status({application_id}) service stub — not yet implemented'}, 200
