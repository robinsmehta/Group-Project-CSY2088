# ============================================================
# app/routes/admin_routes.py — Admin Routes (Presentation Layer)
#
# Handles all platform administration actions.
# EVERY route in this file is protected with @role_required('admin') so only
# authenticated Admins can access them.
#
# Blueprint: admin_bp
# URL Prefix (set in app/__init__.py): /api/admin
# Full endpoint URLs:
#   GET    /api/admin/companies/pending       → list companies awaiting approval
#   PUT    /api/admin/companies/<id>/approve  → approve a company
#   PUT    /api/admin/companies/<id>/reject   → reject a company
#   DELETE /api/admin/jobs/<id>              → remove any job listing
#   DELETE /api/admin/users/<id>             → remove a user account
#   DELETE /api/admin/companies/<id>         → remove a company account
# ============================================================

from flask import Blueprint, jsonify
from app.services import admin_service
from app.utils.decorators import role_required

admin_bp = Blueprint('admin', __name__)


# ============================================================
# GET /api/admin/companies/pending
# ============================================================
@admin_bp.route('/companies/pending', methods=['GET'])
@role_required('admin')
def get_pending_companies():
    """
    Retrieve all company accounts with status = 'pending'.
    Used by admins to see which companies are waiting for approval.

    Success response (200 OK):
        { "companies": [ { company1 }, { company2 }, ... ] }

    Error responses:
        401 — Not logged in
        403 — Not an admin
    """
    result, status_code = admin_service.get_pending_companies()
    return jsonify(result), status_code


# ============================================================
# PUT /api/admin/companies/<id>/approve
# ============================================================
@admin_bp.route('/companies/<int:company_id>/approve', methods=['PUT'])
@role_required('admin')
def approve_company(company_id):
    """
    Approve a pending company account.
    Once approved, the company can log in and post job listings.

    Path parameter:
        company_id (int): The ID of the company to approve.

    Success response (200 OK):
        { "message": "Company approved successfully", "company": { ... } }

    Error responses:
        401 — Not logged in
        403 — Not an admin
        404 — Company not found
    """
    result, status_code = admin_service.approve_company(company_id)
    return jsonify(result), status_code


# ============================================================
# PUT /api/admin/companies/<id>/reject
# ============================================================
@admin_bp.route('/companies/<int:company_id>/reject', methods=['PUT'])
@role_required('admin')
def reject_company(company_id):
    """
    Reject a pending company account.
    The company will not be able to log in or post jobs.

    Path parameter:
        company_id (int): The ID of the company to reject.

    Success response (200 OK):
        { "message": "Company rejected successfully", "company": { ... } }

    Error responses:
        401 — Not logged in
        403 — Not an admin
        404 — Company not found
    """
    result, status_code = admin_service.reject_company(company_id)
    return jsonify(result), status_code


# ============================================================
# DELETE /api/admin/jobs/<id>
# ============================================================
@admin_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
@role_required('admin')
def delete_job(job_id):
    """
    Permanently delete any job listing from the platform.
    Admins can remove inappropriate or fraudulent job postings.
    Cascades deletion to all Applications submitted for this job.

    Path parameter:
        job_id (int): The ID of the job to delete.

    Success response (200 OK):
        { "message": "Job deleted successfully" }

    Error responses:
        401 — Not logged in
        403 — Not an admin
        404 — Job not found
    """
    result, status_code = admin_service.delete_job(job_id)
    return jsonify(result), status_code


# ============================================================
# DELETE /api/admin/users/<id>
# ============================================================
@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    """
    Permanently delete a user (job seeker) account.
    Cascades deletion to all Applications submitted by this user.

    Path parameter:
        user_id (int): The ID of the user to delete.

    Success response (200 OK):
        { "message": "User deleted successfully" }

    Error responses:
        401 — Not logged in
        403 — Not an admin
        404 — User not found
    """
    result, status_code = admin_service.delete_user(user_id)
    return jsonify(result), status_code


# ============================================================
# DELETE /api/admin/companies/<id>
# ============================================================
@admin_bp.route('/companies/<int:company_id>', methods=['DELETE'])
@role_required('admin')
def delete_company(company_id):
    """
    Permanently delete a company account.
    Cascades deletion to all Jobs posted by the company and their Applications.

    Path parameter:
        company_id (int): The ID of the company to delete.

    Success response (200 OK):
        { "message": "Company deleted successfully" }

    Error responses:
        401 — Not logged in
        403 — Not an admin
        404 — Company not found
    """
    result, status_code = admin_service.delete_company(company_id)
    return jsonify(result), status_code


# ============================================================
# GET /api/admin/stats
# ============================================================
@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def get_stats():
    """
    Get platform statistics for admin dashboard.

    Success response (200 OK):
        {
            "stats": {
                "total_users": 10,
                "total_companies": 5,
                "total_jobs": 20,
                "total_applications": 15,
                "pending_companies": 2
            }
        }

    Error responses:
        401 — Not logged in
        403 — Not an admin
    """
    result, status_code = admin_service.get_admin_stats()
    return jsonify(result), status_code
