# ============================================================
# app/routes/job_routes.py — Job Listing Routes (Presentation Layer)
#
# This file is the PRESENTATION LAYER for job-related endpoints.
# It receives HTTP requests, delegates to job_service.py (Business Logic),
# and returns JSON responses.
#
# Blueprint: job_bp
# URL Prefix (set in app/__init__.py): /api/jobs
# Full endpoint URLs:
#   GET    /api/jobs              → list all jobs (with optional filters)
#   GET    /api/jobs/<id>         → get a specific job by ID
#   POST   /api/jobs              → create a new job listing (company only)
#   PUT    /api/jobs/<id>         → update a job listing (owning company only)
#   DELETE /api/jobs/<id>         → delete a job listing (owning company only)
# ============================================================

from flask import Blueprint, request, jsonify
from app.services import job_service
from app.utils.decorators import role_required  # Role-based access control decorator

job_bp = Blueprint('jobs', __name__)


# ============================================================
# GET /api/jobs
# ============================================================
@job_bp.route('/', methods=['GET'])
def get_all_jobs():
    """
    Retrieve all approved job listings.

    Optional query parameters for filtering/searching:
        ?category=Engineering
        ?location=London
        ?keyword=python

    Success response (200 OK):
        { "jobs": [ { job1 }, { job2 }, ... ] }
    """
    # TODO: Read optional query params from the URL
    # category = request.args.get('category')
    # location  = request.args.get('location')
    # keyword   = request.args.get('keyword')

    # TODO: Call job_service.get_all_jobs(filters) which will:
    #         - Build a SQLAlchemy query with optional WHERE clauses
    #         - Return a list of Job objects from approved companies only
    # result, status_code = job_service.get_all_jobs(category, location, keyword)
    # return jsonify(result), status_code

    return jsonify({'message': 'get_all_jobs route stub — not yet implemented'}), 200


# ============================================================
# GET /api/jobs/<id>
# ============================================================
@job_bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """
    Retrieve a single job listing by its ID.

    Path parameter:
        job_id (int): The primary key of the job.

    Success response (200 OK):
        { "job": { id, title, description, ... } }

    Error response:
        404 — Job not found
    """
    # TODO: Call job_service.get_job_by_id(job_id) which will:
    #         - Query Job.query.get(job_id)
    #         - Return 404 if not found
    # result, status_code = job_service.get_job_by_id(job_id)
    # return jsonify(result), status_code

    return jsonify({'message': f'get_job({job_id}) route stub — not yet implemented'}), 200


# ============================================================
# POST /api/jobs
# ============================================================
@job_bp.route('/', methods=['POST'])
# @role_required('company')  # TODO: Uncomment once role_required decorator is implemented
def create_job():
    """
    Create a new job listing.
    Only an APPROVED company should be able to call this.

    Expected JSON body:
        {
            "title":       "Python Developer",
            "description": "Build backend APIs...",
            "location":    "Remote",
            "category":    "Software Engineering",
            "salary":      "£40,000 - £50,000"
        }

    Success response (201 Created):
        { "message": "Job created successfully", "job": { ... } }

    Error responses:
        400 — Missing required fields
        401 — Not logged in
        403 — Not a company, or company not approved
    """
    # TODO: Get the logged-in company's ID from the session
    # company_id = session.get('company_id')

    # TODO: Extract JSON body
    # data = request.get_json()

    # TODO: Call job_service.create_job(company_id, data) which will:
    #         - Validate required fields (title, description, location)
    #         - Confirm company status is 'approved'
    #         - Create a new Job record and save to DB
    # result, status_code = job_service.create_job(company_id, data)
    # return jsonify(result), status_code

    return jsonify({'message': 'create_job route stub — not yet implemented'}), 200


# ============================================================
# PUT /api/jobs/<id>
# ============================================================
@job_bp.route('/<int:job_id>', methods=['PUT'])
# @role_required('company')  # TODO: Uncomment once role_required decorator is implemented
def update_job(job_id):
    """
    Update an existing job listing.
    Only the COMPANY THAT POSTED THIS JOB can update it.

    Path parameter:
        job_id (int): The primary key of the job to update.

    Expected JSON body (any updatable fields):
        {
            "title":    "Senior Python Developer",
            "salary":   "£55,000"
        }

    Success response (200 OK):
        { "message": "Job updated", "job": { ... } }

    Error responses:
        400 — No valid fields to update
        401 — Not authenticated
        403 — Not the owning company
        404 — Job not found
    """
    # TODO: Get logged-in company_id from session
    # company_id = session.get('company_id')

    # TODO: Extract JSON body
    # data = request.get_json()

    # TODO: Call job_service.update_job(job_id, company_id, data) which will:
    #         - Find the Job by ID (404 if missing)
    #         - Verify job.company_id == company_id (403 if mismatch)
    #         - Update only the provided fields
    #         - Commit changes to DB
    # result, status_code = job_service.update_job(job_id, company_id, data)
    # return jsonify(result), status_code

    return jsonify({'message': f'update_job({job_id}) route stub — not yet implemented'}), 200


# ============================================================
# DELETE /api/jobs/<id>
# ============================================================
@job_bp.route('/<int:job_id>', methods=['DELETE'])
# @role_required('company')  # TODO: Uncomment once role_required decorator is implemented
def delete_job(job_id):
    """
    Delete a job listing.
    Only the COMPANY THAT POSTED THIS JOB can delete it
    (admins can also delete via /api/admin/jobs/<id>).

    Path parameter:
        job_id (int): The primary key of the job to delete.

    Success response (200 OK):
        { "message": "Job deleted successfully" }

    Error responses:
        401 — Not authenticated
        403 — Not the owning company
        404 — Job not found
    """
    # TODO: Get logged-in company_id from session
    # company_id = session.get('company_id')

    # TODO: Call job_service.delete_job(job_id, company_id) which will:
    #         - Find the Job (404 if not found)
    #         - Verify ownership (403 if not owning company)
    #         - Delete the Job (cascade deletes its Applications too)
    #         - Commit to DB
    # result, status_code = job_service.delete_job(job_id, company_id)
    # return jsonify(result), status_code

    return jsonify({'message': f'delete_job({job_id}) route stub — not yet implemented'}), 200
