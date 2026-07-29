# ============================================================
# app/routes/job_routes.py — Job Routes (Presentation Layer)
#
# This file handles all HTTP requests for job listings.
# It acts as the PRESENTATION LAYER:
#   - Parses request URLs, query parameters, and JSON payloads
#   - Performs route-level input validation
#   - Checks session credentials and enforces role authorization
#   - Calls job_service.py for core business logic execution
#   - Formats JSON responses with proper HTTP status codes
#
# Blueprint: job_bp (URL prefix: /api/jobs)
# Endpoints:
#   GET    /api/jobs              → List all jobs (public, optional filters)
#   GET    /api/jobs/<id>         → Get specific job details (public)
#   POST   /api/jobs              → Create new job listing (company role required)
#   PUT    /api/jobs/<id>         → Update job listing (company role required)
#   DELETE /api/jobs/<id>         → Delete job listing (owning company or admin allowed)
# ============================================================

from flask import Blueprint, request, jsonify, session
from app.services import job_service
from app.utils.decorators import role_required

job_bp = Blueprint('jobs', __name__)


# ============================================================
# 1. GET /api/jobs — Public list & search endpoint
# ============================================================
@job_bp.route('/', methods=['GET'])
def get_all_jobs():
    """
    Retrieve all job listings with optional filtering and search.
    Public access — no authentication required.

    Query Parameters:
        ?keyword=python       → Search in job title or description
        ?location=London      → Filter by job location
        ?category=Engineering → Filter by job category

    Why search/filter uses optional query parameters rather than separate endpoints:
    Query parameters allow clients to dynamically combine optional filters (e.g. keyword + location)
    in a single, RESTful GET endpoint without needing separate routes per filter combination.
    """
    keyword = request.args.get('keyword')
    location = request.args.get('location')
    category = request.args.get('category')

    # Forward query parameters to service layer for SQL filtering
    result, status_code = job_service.get_all_jobs(
        keyword=keyword,
        location=location,
        category=category
    )
    return jsonify(result), status_code


# ============================================================
# 2. GET /api/jobs/<id> — Public single job lookup
# ============================================================
@job_bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """
    Retrieve full details for a single job listing by ID.
    Public access — no authentication required.

    Path parameter:
        job_id (int): Primary key of the job listing.
    """
    result, status_code = job_service.get_job_by_id(job_id)
    return jsonify(result), status_code


# ============================================================
# 3. POST /api/jobs — Create job listing (Approved Company only)
# ============================================================
@job_bp.route('/', methods=['POST'])
@role_required('company')
def create_job():
    """
    Create a new job listing for the authenticated company.

    Protected: Requires 'company' role.
    Extracts company_id from active session.

    Expected JSON body:
        {
            "title":       "Senior Python Developer",
            "description": "Build backend APIs and microservices...",
            "location":    "Remote",
            "category":    "Engineering",
            "salary":      "£50,000 - £60,000"
        }
    """
    # Company ID is stored in session during login (session['user_id'])
    company_id = session.get('company_id') or session.get('user_id')

    # Parse JSON payload
    data = request.get_json(silent=True) or {}

    # Route-level input validation
    title = data.get('title')
    description = data.get('description')
    location = data.get('location')

    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({'error': 'Title is required and must be a non-empty string'}), 400

    if not description or not isinstance(description, str) or not description.strip():
        return jsonify({'error': 'Description is required and must be a non-empty string'}), 400

    if not location or not isinstance(location, str) or not location.strip():
        return jsonify({'error': 'Location is required and must be a non-empty string'}), 400

    # Call service layer to perform approval check & creation
    result, status_code = job_service.create_job(company_id=company_id, title=data)
    return jsonify(result), status_code


# ============================================================
# 4. PUT /api/jobs/<id> — Update job listing (Owning Company only)
# ============================================================
@job_bp.route('/<int:job_id>', methods=['PUT'])
@role_required('company')
def update_job(job_id):
    """
    Update an existing job listing.

    Protected: Requires 'company' role.
    Service layer enforces that company_id matches job.company_id.

    Expected JSON body (any updatable fields):
        {
            "title":    "Lead Python Developer",
            "salary":   "£65,000 - £75,000"
        }
    """
    company_id = session.get('company_id') or session.get('user_id')
    data = request.get_json(silent=True) or {}

    updatable_fields = ['title', 'description', 'location', 'category', 'salary']
    provided_updates = {k: v for k, v in data.items() if k in updatable_fields}

    if not provided_updates:
        return jsonify({
            'error': 'No valid fields provided for update. Allowed fields: title, description, location, category, salary'
        }), 400

    # Delegate to service layer for ownership check and database update
    result, status_code = job_service.update_job(
        job_id=job_id,
        company_id=company_id,
        updated_fields=provided_updates
    )
    return jsonify(result), status_code


# ============================================================
# 5. DELETE /api/jobs/<id> — Delete job (Owning Company or Admin)
# ============================================================
@job_bp.route('/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """
    Delete a job listing.

    Protected: Accessible by either:
      - The owning company (session['role'] == 'company' and job.company_id matches session company_id)
      - An administrator (session['role'] == 'admin', is_admin=True)
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

    # Delegate deletion logic to service layer
    result, status_code = job_service.delete_job(
        job_id=job_id,
        company_id=company_id,
        is_admin=is_admin
    )
    return jsonify(result), status_code


# ============================================================
# 6. GET /api/jobs/<id>/applications — Get applicants for a job (Company)
# ============================================================
@job_bp.route('/<int:job_id>/applications', methods=['GET'])
@role_required('company')
def get_job_applications(job_id):
    """
    Retrieve all applications for a specific job listing (sub-resource route).
    Only the COMPANY THAT POSTED THE JOB can view its applicants.
    """
    from app.services import application_service
    company_id = session.get('company_id') or session.get('user_id')
    result, status_code = application_service.get_applicants_for_job(
        job_id=job_id,
        company_id=company_id
    )
    return jsonify(result), status_code

