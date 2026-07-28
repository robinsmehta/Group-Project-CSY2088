# ============================================================
# app/services/job_service.py — Job Business Logic
#
# This is the BUSINESS LOGIC LAYER for job-related operations.
# Called by routes in job_routes.py.
#
# Responsibilities:
#   - Apply validation rules specific to jobs
#   - Check company ownership before allowing edits/deletes
#   - Build database queries (with optional filters)
#   - Create, update, and delete Job records
# ============================================================

from app.extensions import db
from app.models.job     import Job
from app.models.company import Company


def get_all_jobs(category=None, location=None, keyword=None):
    """
    Retrieve all job listings (from approved companies only).
    Supports optional filtering by category, location, or keyword.

    Args:
        category (str, optional): Filter by job category.
        location (str, optional): Filter by job location.
        keyword  (str, optional): Search in job title or description.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Start a base query for all jobs
    # query = Job.query.join(Company).filter(Company.status == 'approved')

    # TODO: Apply filters if provided
    # if category:
    #     query = query.filter(Job.category.ilike(f'%{category}%'))
    # if location:
    #     query = query.filter(Job.location.ilike(f'%{location}%'))
    # if keyword:
    #     query = query.filter(
    #         db.or_(Job.title.ilike(f'%{keyword}%'), Job.description.ilike(f'%{keyword}%'))
    #     )

    # TODO: Execute query and serialise results
    # jobs = query.all()
    # return {'jobs': [j.to_dict() for j in jobs]}, 200

    return {'message': 'get_all_jobs service stub — not yet implemented'}, 200


def get_job_by_id(job_id: int):
    """
    Retrieve a single job listing by its primary key.

    Args:
        job_id (int): The job's primary key.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Query the job from the database
    # job = Job.query.get(job_id)
    # if not job:
    #     return {'error': 'Job not found'}, 404
    # return {'job': job.to_dict()}, 200

    return {'message': f'get_job_by_id({job_id}) service stub — not yet implemented'}, 200


def create_job(company_id: int, data: dict):
    """
    Create a new job listing for the given company.

    Args:
        company_id (int): ID of the authenticated company creating the job.
        data (dict): Job details (title, description, location, category, salary).

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Validate required fields in data
    # if not data.get('title') or not data.get('description') or not data.get('location'):
    #     return {'error': 'Title, description, and location are required'}, 400

    # TODO: Confirm the company exists and is approved
    # company = Company.query.get(company_id)
    # if not company or company.status != 'approved':
    #     return {'error': 'Only approved companies can post jobs'}, 403

    # TODO: Create and save the Job
    # new_job = Job(
    #     company_id  = company_id,
    #     title       = data['title'],
    #     description = data['description'],
    #     location    = data['location'],
    #     category    = data.get('category'),
    #     salary      = data.get('salary'),
    # )
    # db.session.add(new_job)
    # db.session.commit()
    # return {'message': 'Job created successfully', 'job': new_job.to_dict()}, 201

    return {'message': 'create_job service stub — not yet implemented'}, 200


def update_job(job_id: int, company_id: int, data: dict):
    """
    Update a job listing owned by the given company.

    Args:
        job_id     (int): The job to update.
        company_id (int): Must match job.company_id (ownership check).
        data (dict): Fields to update.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Find the job (404 if missing)
    # job = Job.query.get(job_id)
    # if not job:
    #     return {'error': 'Job not found'}, 404

    # TODO: Ownership check — company can only edit their own jobs
    # if job.company_id != company_id:
    #     return {'error': 'You do not have permission to edit this job'}, 403

    # TODO: Update only the fields that were provided
    # if data.get('title'):       job.title       = data['title']
    # if data.get('description'): job.description = data['description']
    # if data.get('location'):    job.location    = data['location']
    # if data.get('category'):    job.category    = data['category']
    # if data.get('salary'):      job.salary      = data['salary']
    # db.session.commit()
    # return {'message': 'Job updated', 'job': job.to_dict()}, 200

    return {'message': f'update_job({job_id}) service stub — not yet implemented'}, 200


def delete_job(job_id: int, company_id: int):
    """
    Delete a job listing (company must own the job).

    Args:
        job_id     (int): The job to delete.
        company_id (int): Must match job.company_id (ownership check).

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Find the job (404 if missing)
    # job = Job.query.get(job_id)
    # if not job:
    #     return {'error': 'Job not found'}, 404

    # TODO: Ownership check
    # if job.company_id != company_id:
    #     return {'error': 'You do not have permission to delete this job'}, 403

    # TODO: Delete and commit
    # db.session.delete(job)
    # db.session.commit()
    # return {'message': 'Job deleted successfully'}, 200

    return {'message': f'delete_job({job_id}) service stub — not yet implemented'}, 200
