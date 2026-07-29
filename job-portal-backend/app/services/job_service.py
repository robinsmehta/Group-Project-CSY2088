# ============================================================
# app/services/job_service.py — Job Business Logic Layer
#
# This file contains the core business rules for job operations:
#   1. Creating job listings (with company approval verification)
#   2. Searching/retrieving job listings (with optional dynamic filters)
#   3. Fetching single job listing details
#   4. Updating job listings (with company ownership verification)
#   5. Deleting job listings (with company ownership & admin override rules)
#
# Architectural Notes & Security Design:
#
# 1. WHY THE APPROVAL CHECK HAPPENS BEFORE JOB CREATION:
#    Checking company.status == 'approved' before creating a job ensures that
#    unapproved, pending, or rejected companies cannot post job listings on the platform.
#    This enforces administrative authorization at the backend database boundary,
#    preventing unverified accounts from publishing content even if client-side controls are bypassed.
#
# 2. WHY OWNERSHIP IS CHECKED IN THE SERVICE LAYER RATHER THAN TRUSTING THE FRONTEND:
#    Ownership validation (job.company_id == company_id) MUST be enforced in the service layer.
#    Frontend inputs and HTTP request headers/payloads can be forged or manipulated (e.g. via Postman,
#    cURL, or browser dev tools). Validating ownership in the service layer ensures complete security,
#    preventing one company from modifying or deleting another company's job postings.
#
# 3. WHY SEARCH/FILTER USES OPTIONAL QUERY PARAMETERS RATHER THAN SEPARATE ENDPOINTS PER FILTER TYPE:
#    Using optional query parameters (e.g., GET /api/jobs?keyword=...&location=...&category=...)
#    follows RESTful API design principles. It allows clients to combine any dynamic set of filters
#    (e.g., keyword + location, or category only) within a single unified endpoint handler rather than
#    creating individual, redundant routes for every filter permutation (e.g. /jobs/category, /jobs/location).
# ============================================================

from app.extensions import db
from app.models.job import Job
from app.models.company import Company


def create_job(company_id: int, title=None, description=None, location=None, category=None, salary=None):
    """
    Create a new job listing for an approved company.

    Accepts parameters individually or as a single dictionary passed in the 'title' argument.

    Args:
        company_id (int): Primary key of the requesting company.
        title (str or dict): Job title, or dict containing job details.
        description (str, optional): Detailed job description.
        location (str, optional): Job location.
        category (str, optional): Job category.
        salary (str, optional): Salary range / string representation.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # Support receiving a dictionary as the second argument (data dict)
    if isinstance(title, dict):
        data = title
        title = data.get('title')
        description = data.get('description')
        location = data.get('location')
        category = data.get('category')
        salary = data.get('salary')

    # Basic input checks
    title = (title or '').strip()
    description = (description or '').strip()
    location = (location or '').strip()
    category = (category or '').strip() if category else None
    salary = (salary or '').strip() if salary else None

    if not title or not description or not location:
        return {'error': 'Title, description, and location are required fields'}, 400

    # Look up the company by company_id
    company = Company.query.get(company_id)
    if not company:
        return {'error': 'Company not found'}, 404

    # -------------------------------------------------------------------------
    # APPROVAL CHECK BEFORE JOB CREATION:
    # We verify that the company's account status is 'approved'.
    # Pending or rejected companies cannot post job listings.
    # -------------------------------------------------------------------------
    if company.status != 'approved':
        return {
            'error': 'Your company account is pending admin approval and cannot post jobs yet.'
        }, 403

    # Create new Job record linked to this company
    new_job = Job(
        company_id=company_id,
        title=title,
        description=description,
        location=location,
        category=category,
        salary=salary
    )

    db.session.add(new_job)
    db.session.commit()

    return {
        'message': 'Job created successfully',
        'job': new_job.to_dict()
    }, 201


def get_all_jobs(keyword=None, location=None, category=None):
    """
    Retrieve all job listings, optionally filtered by keyword, location, and/or category.
    Joins with the companies table to include company information.

    Args:
        keyword (str, optional): Search string to match in title or description.
        location (str, optional): Location string filter.
        category (str, optional): Category string filter.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # Query the jobs table and join with companies
    query = Job.query.join(Company)

    # -------------------------------------------------------------------------
    # OPTIONAL SEARCH & FILTERING:
    # Filter by category, location, and/or keyword (searches title and description).
    # -------------------------------------------------------------------------
    if category and category.strip():
        query = query.filter(Job.category.ilike(f'%{category.strip()}%'))

    if location and location.strip():
        query = query.filter(Job.location.ilike(f'%{location.strip()}%'))

    if keyword and keyword.strip():
        search_pattern = f'%{keyword.strip()}%'
        query = query.filter(
            db.or_(
                Job.title.ilike(search_pattern),
                Job.description.ilike(search_pattern)
            )
        )

    # Order by creation date (newest first)
    jobs = query.order_by(Job.created_at.desc()).all()

    # to_dict() includes company_name via the relationship
    return {
        'count': len(jobs),
        'jobs': [j.to_dict() for j in jobs]
    }, 200


def get_job_by_id(job_id: int):
    """
    Retrieve full details for a single job listing by ID.

    Args:
        job_id (int): Primary key of the job.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    job = Job.query.get(job_id)
    if not job:
        return {'error': 'Job not found'}, 404

    return {
        'job': job.to_dict()
    }, 200


def update_job(job_id: int, company_id: int, updated_fields: dict = None, **kwargs):
    """
    Update an existing job listing. Only the owning company can update its jobs.

    Args:
        job_id (int): Primary key of the job to update.
        company_id (int): Primary key of the requesting company (from session).
        updated_fields (dict, optional): Dictionary containing updated fields.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    if updated_fields is None:
        updated_fields = kwargs

    job = Job.query.get(job_id)
    if not job:
        return {'error': 'Job not found'}, 404

    # -------------------------------------------------------------------------
    # OWNERSHIP CHECK IN SERVICE LAYER:
    # Ensure job.company_id matches the requesting company_id.
    # -------------------------------------------------------------------------
    if job.company_id != company_id:
        return {'error': 'You do not own this job'}, 403

    # Update only fields provided
    if 'title' in updated_fields and updated_fields['title'] is not None:
        job.title = updated_fields['title'].strip()
    if 'description' in updated_fields and updated_fields['description'] is not None:
        job.description = updated_fields['description'].strip()
    if 'location' in updated_fields and updated_fields['location'] is not None:
        job.location = updated_fields['location'].strip()
    if 'category' in updated_fields and updated_fields['category'] is not None:
        job.category = updated_fields['category'].strip()
    if 'salary' in updated_fields and updated_fields['salary'] is not None:
        job.salary = updated_fields['salary'].strip()

    db.session.commit()

    return {
        'message': 'Job updated successfully',
        'job': job.to_dict()
    }, 200


def delete_job(job_id: int, company_id: int = None, is_admin: bool = False):
    """
    Delete a job listing.
    - If is_admin is True: deletion is allowed regardless of ownership.
    - If is_admin is False: company_id must match job.company_id.

    Args:
        job_id (int): Primary key of the job to delete.
        company_id (int, optional): ID of requesting company (required if not admin).
        is_admin (bool): Flag indicating if request comes from an administrator.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    job = Job.query.get(job_id)
    if not job:
        return {'error': 'Job not found'}, 404

    # -------------------------------------------------------------------------
    # OWNERSHIP & ADMIN DELETION CHECK:
    # -------------------------------------------------------------------------
    if not is_admin:
        if not company_id or job.company_id != company_id:
            return {'error': 'You do not have permission to delete this job'}, 403

    db.session.delete(job)
    db.session.commit()

    return {
        'message': 'Job deleted successfully'
    }, 200
