# app/services/job_service.py — Job Business Logic Layer
#
# Contains the core rules for all job listing operations:
#   1. Creating job listings (only allowed for approved companies)
#   2. Searching and listing jobs (with optional filters and pagination)
#   3. Fetching a single job's full details
#   4. Updating job listings (only the company that owns the job may edit it)
#   5. Deleting job listings (owning company or any admin may delete)
#
# Why ownership checks live here and not in the route:
#   The route layer only checks that the person is logged in with the right role.
#   Checking that a company actually owns a specific job must happen here,
#   because a malicious user could forge requests from any tool — the frontend
#   cannot be trusted to enforce this rule on its own.

from datetime import datetime, timezone
from math import ceil

from app.extensions import db
from app.models.job import Job
from app.models.company import Company
from sqlalchemy import text


def refresh_job_statuses():
    """Mark any jobs whose closing date has passed as 'closed' in the database."""
    now = datetime.now(timezone.utc)
    # Use a direct SQL update for efficiency rather than loading every job into Python
    try:
        sql = text("UPDATE jobs SET status='closed' WHERE closing_date IS NOT NULL AND closing_date <= :now AND status != 'closed'")
        db.session.execute(sql, {'now': now})
        db.session.commit()
    except Exception:
        db.session.rollback()


def create_job(company_id: int, title=None, description=None, location=None, category=None, salary=None, job_type=None, skills=None):
    """
    Post a new job listing for an approved company.
    Rejects the request if the company's account has not been approved by an admin yet.

    Accepts parameters individually or as a single dictionary passed in the 'title' argument.

    Args:
        company_id (int): Primary key of the requesting company.
        title (str or dict): Job title, or a dict containing all job details.
        description (str, optional): Detailed job description.
        location (str, optional): Job location.
        category (str, optional): Job category.
        salary (str, optional): Salary range or description.
        job_type (str, optional): Employment type (e.g. Full-time, Part-time).
        skills (str, optional): Comma-separated list of required skills.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # Support receiving all fields packed into a dict as the second argument
    data = None
    if isinstance(title, dict):
        data = title
        title = data.get('title')
        description = data.get('description')
        location = data.get('location')
        category = data.get('category')
        salary = data.get('salary')
        job_type = data.get('job_type')
        skills = data.get('skills')

    # Clean up whitespace and treat empty strings as missing
    title = (title or '').strip()
    description = (description or '').strip()
    location = (location or '').strip()
    category = (category or '').strip() if category else None
    salary = (salary or '').strip() if salary else None
    job_type = (job_type or '').strip() if job_type else None
    skills = (skills or '').strip() if skills else None

    if not title or not description or not location:
        return {'error': 'Title, description, and location are required fields'}, 400

    # Look up the company by ID
    company = Company.query.get(company_id)
    if not company:
        return {'error': 'Company not found'}, 404

    # Only approved companies may post jobs — pending or rejected accounts are blocked here
    if company.status != 'approved':
        return {
            'error': 'Your company account is pending admin approval and cannot post jobs yet.'
        }, 403

    closing_date = None
    if isinstance(title, dict):
        closing_date_raw = data.get('closing_date')
    else:
        closing_date_raw = None

    if closing_date_raw:
        try:
            closing_date = datetime.fromisoformat(closing_date_raw)
            if closing_date.tzinfo is None:
                closing_date = closing_date.replace(tzinfo=timezone.utc)
        except ValueError:
            closing_date = None

    # Create the job record and link it to the company
    new_job = Job(
        company_id=company_id,
        title=title,
        description=description,
        location=location,
        category=category,
        job_type=job_type,
        salary=salary,
        skills=skills,
        closing_date=closing_date
    )

    db.session.add(new_job)
    # Set the initial status based on whether the closing date has already passed
    new_job.status = 'closed' if new_job.is_closed else 'active'
    db.session.commit()

    return {
        'message': 'Job created successfully',
        'job': new_job.to_dict()
    }, 201


def get_all_jobs(keyword=None, location=None, category=None, job_type=None, page=1, per_page=10):
    """
    Return a paginated list of job listings, with optional filters.
    All filters are optional — leaving them all blank returns every active job.

    Args:
        keyword (str, optional): Search term matched against title, description, or skills.
        location (str, optional): Filter to jobs in a specific location.
        category (str, optional): Filter to jobs in a specific category.
        job_type (str, optional): Filter by employment type (e.g. Full-time).
        page (int): Which page of results to return (starts at 1).
        per_page (int): How many results to include per page (default 10, max 100).

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # Clamp pagination values to safe ranges
    try:
        page = max(1, int(page))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = max(1, min(100, int(per_page)))
    except (TypeError, ValueError):
        per_page = 10

    # Make sure any jobs whose deadline has passed are marked closed before we return them
    refresh_job_statuses()

    # Start building the database query, joining with companies so we can include company names
    query = Job.query.join(Company)

    # Apply any filters the caller passed — each one narrows the results further
    if category and category.strip():
        query = query.filter(Job.category.ilike(f'%{category.strip()}%'))

    if job_type and job_type.strip():
        query = query.filter(Job.job_type.ilike(f'%{job_type.strip()}%'))

    if location and location.strip():
        query = query.filter(Job.location.ilike(f'%{location.strip()}%'))

    if keyword and keyword.strip():
        search_pattern = f'%{keyword.strip()}%'
        query = query.filter(
            db.or_(
                Job.title.ilike(search_pattern),
                Job.description.ilike(search_pattern),
                Job.skills.ilike(search_pattern)
            )
        )

    # Show newest jobs first
    query = query.order_by(Job.created_at.desc())

    # Count total results before slicing so callers know how many pages exist
    total_count = query.count()
    total_pages = ceil(total_count / per_page) if total_count > 0 else 1

    jobs = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        'count': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'jobs': [j.to_dict() for j in jobs]
    }, 200


def get_job_by_id(job_id: int):
    """
    Return full details for a single job listing.
    Also updates any expired listings to 'closed' before returning.

    Args:
        job_id (int): Primary key of the job.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # Ensure the job's status is up to date before returning it
    refresh_job_statuses()

    job = Job.query.get(job_id)
    if not job:
        return {'error': 'Job not found'}, 404

    return {
        'job': job.to_dict()
    }, 200


def update_job(job_id: int, company_id: int, updated_fields: dict = None, **kwargs):
    """
    Edit an existing job listing. Only the company that posted the job can make changes.

    Args:
        job_id (int): Primary key of the job to update.
        company_id (int): Primary key of the company making the request.
        updated_fields (dict, optional): Dictionary of fields to change.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    if updated_fields is None:
        updated_fields = kwargs

    job = Job.query.get(job_id)
    if not job:
        return {'error': 'Job not found'}, 404

    # Make sure the company asking for the change actually owns this job
    if job.company_id != company_id:
        return {'error': 'You do not own this job'}, 403

    # Update only the fields that were provided — leave everything else unchanged
    if 'title' in updated_fields and updated_fields['title'] is not None:
        job.title = updated_fields['title'].strip()
    if 'description' in updated_fields and updated_fields['description'] is not None:
        job.description = updated_fields['description'].strip()
    if 'location' in updated_fields and updated_fields['location'] is not None:
        job.location = updated_fields['location'].strip()
    if 'category' in updated_fields and updated_fields['category'] is not None:
        job.category = updated_fields['category'].strip()
    if 'job_type' in updated_fields and updated_fields['job_type'] is not None:
        job.job_type = updated_fields['job_type'].strip()
    if 'salary' in updated_fields and updated_fields['salary'] is not None:
        job.salary = updated_fields['salary'].strip()
    if 'skills' in updated_fields and updated_fields['skills'] is not None:
        job.skills = updated_fields['skills'].strip()
    if 'closing_date' in updated_fields:
        closing_date_raw = updated_fields.get('closing_date')
        if closing_date_raw:
            try:
                closing_date = datetime.fromisoformat(closing_date_raw)
                if closing_date.tzinfo is None:
                    closing_date = closing_date.replace(tzinfo=timezone.utc)
            except ValueError:
                closing_date = None
        else:
            closing_date = None
        job.closing_date = closing_date

    # Re-evaluate the job's open/closed status after changes
    job.status = 'closed' if job.is_closed else 'active'

    db.session.commit()

    return {
        'message': 'Job updated successfully',
        'job': job.to_dict()
    }, 200


def delete_job(job_id: int, company_id: int = None, is_admin: bool = False):
    """
    Delete a job listing.
    Admins can delete any job. Companies can only delete their own jobs.

    Args:
        job_id (int): Primary key of the job to delete.
        company_id (int, optional): ID of the requesting company (required if not admin).
        is_admin (bool): True if the request comes from an admin account.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    job = Job.query.get(job_id)
    if not job:
        return {'error': 'Job not found'}, 404

    # If this is not an admin request, verify the company owns the job before deleting
    if not is_admin:
        if not company_id or job.company_id != company_id:
            return {'error': 'You do not have permission to delete this job'}, 403

    db.session.delete(job)
    db.session.commit()

    return {
        'message': 'Job deleted successfully'
    }, 200
