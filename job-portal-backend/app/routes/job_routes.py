# app/routes/job_routes.py — Job Routes
#
# Handles all HTTP requests for job listings.
# This layer parses request inputs, checks session credentials,
# and calls job_service.py for the actual business logic.
#
# URL prefix: /api/jobs
# Endpoints:
#   GET    /api/jobs              → list all jobs (public, with optional filters)
#   GET    /api/jobs/<id>         → get one job's full details (public)
#   POST   /api/jobs              → create a new job listing (company only)
#   PUT    /api/jobs/<id>         → edit an existing job listing (owning company only)
#   DELETE /api/jobs/<id>         → delete a job listing (owning company or admin)
#   GET    /api/jobs/<id>/applications → list all applicants for a job (company only)

from flask import Blueprint, request, jsonify, session
from app.services import job_service
from app.utils.decorators import role_required

job_bp = Blueprint('jobs', __name__)


# GET /api/jobs — public list and search endpoint
@job_bp.route('/', methods=['GET'])
def get_all_jobs():
    """
    Return all job listings, with optional filtering by keyword, location, category, or type.
    Anyone can call this — no login required.
    Supports pagination so large result sets are returned in manageable pages.

    Query Parameters:
        ?keyword=python       → search in job title, description, or skills
        ?location=London      → filter by job location
        ?category=Engineering → filter by job category
    """
    keyword = request.args.get('keyword')
    location = request.args.get('location')
    category = request.args.get('category')
    job_type = request.args.get('job_type')
    page     = request.args.get('page',     1)
    per_page = request.args.get('per_page', 10)

    # Pass all optional filters to the service layer, which queries the database
    result, status_code = job_service.get_all_jobs(
        keyword=keyword,
        location=location,
        category=category,
        job_type=job_type,
        page=page,
        per_page=per_page
    )
    return jsonify(result), status_code


# GET /api/jobs/<id> — public single job lookup
@job_bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """
    Return full details for one job listing by its ID.
    Anyone can call this — no login required.

    Path parameter:
        job_id (int): The numeric ID of the job listing.
    """
    result, status_code = job_service.get_job_by_id(job_id)
    return jsonify(result), status_code


# POST /api/jobs — create a new job listing (approved companies only)
@job_bp.route('/', methods=['POST'])
@role_required('company')
def create_job():
    """
    Post a new job listing. Only approved company accounts can do this.
    The company ID is read from the current session — companies cannot post on behalf of others.

    Expected JSON body:
        {
            "title":       "Senior Python Developer",
            "description": "Build backend APIs and microservices...",
            "location":    "Remote",
            "category":    "Engineering",
            "salary":      "£50,000 - £60,000"
        }
    """
    # The logged-in company's ID is stored in the session during login
    company_id = session.get('company_id') or session.get('user_id')

    # Parse the request body
    data = request.get_json(silent=True) or {}

    # Basic checks: title, description, and location are the minimum required fields
    title = data.get('title')
    description = data.get('description')
    location = data.get('location')

    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({'error': 'Title is required and must be a non-empty string'}), 400

    if not description or not isinstance(description, str) or not description.strip():
        return jsonify({'error': 'Description is required and must be a non-empty string'}), 400

    if not location or not isinstance(location, str) or not location.strip():
        return jsonify({'error': 'Location is required and must be a non-empty string'}), 400

    # Service layer also checks that the company is approved before creating the listing
    result, status_code = job_service.create_job(company_id=company_id, title=data)
    return jsonify(result), status_code


# PUT /api/jobs/<id> — update a job listing (owning company only)
@job_bp.route('/<int:job_id>', methods=['PUT'])
@role_required('company')
def update_job(job_id):
    """
    Edit an existing job listing. Only the company that originally posted the job can edit it.
    Send only the fields you want to change — unchanged fields stay as they are.

    Expected JSON body (any updatable fields):
        {
            "title":    "Lead Python Developer",
            "salary":   "£65,000 - £75,000"
        }
    """
    company_id = session.get('company_id') or session.get('user_id')
    data = request.get_json(silent=True) or {}

    updatable_fields = ['title', 'description', 'location', 'category', 'job_type', 'salary', 'closing_date', 'skills']
    provided_updates = {k: v for k, v in data.items() if k in updatable_fields}

    if not provided_updates:
        return jsonify({
            'error': 'No valid fields provided for update. Allowed fields: title, description, location, category, salary, skills'
        }), 400

    # Service layer verifies the company owns this job before applying any changes
    result, status_code = job_service.update_job(
        job_id=job_id,
        company_id=company_id,
        updated_fields=provided_updates
    )
    return jsonify(result), status_code


# DELETE /api/jobs/<id> — delete a job listing (owning company or admin)
@job_bp.route('/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """
    Delete a job listing. Either the company that posted it, or an admin, can delete it.
    A company can only delete their own jobs; admins can delete any job.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id or not role:
        return jsonify({
            'error': 'Authentication required. Please log in to access this resource.'
        }), 401

    if role not in ['company', 'admin']:
        return jsonify({
            'error': f'Access denied. Required role: company or admin, your role: {role}'
        }), 403

    is_admin = (role == 'admin')
    company_id = (session.get('company_id') or user_id) if role == 'company' else None

    # Service layer enforces ownership rules before deleting
    result, status_code = job_service.delete_job(
        job_id=job_id,
        company_id=company_id,
        is_admin=is_admin
    )
    return jsonify(result), status_code


# GET /api/jobs/<id>/applications — list applicants for a job (company only)
@job_bp.route('/<int:job_id>/applications', methods=['GET'])
@role_required('company')
def get_job_applications(job_id):
    """
    Return all applications submitted for a specific job listing.
    Only the company that posted the job can see its applicants.
    """
    from app.services import application_service
    company_id = session.get('company_id') or session.get('user_id')
    result, status_code = application_service.get_applicants_for_job(
        job_id=job_id,
        company_id=company_id
    )
    return jsonify(result), status_code
