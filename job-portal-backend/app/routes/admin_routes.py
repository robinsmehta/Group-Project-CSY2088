# ============================================================
# app/routes/admin_routes.py — Admin Routes (Presentation Layer)
#
# Handles all platform administration actions.
# EVERY route in this file should be protected so only Admins can access them.
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
# @role_required('admin')  # TODO: Uncomment once role_required is implemented
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
    # TODO: Call admin_service.get_pending_companies() which will:
    #         - Query Company.query.filter_by(status='pending').all()
    #         - Return the list serialised as dicts
    # result, status_code = admin_service.get_pending_companies()
    # return jsonify(result), status_code

    return jsonify({'message': 'get_pending_companies route stub — not yet implemented'}), 200


# ============================================================
# PUT /api/admin/companies/<id>/approve
# ============================================================
@admin_bp.route('/companies/<int:company_id>/approve', methods=['PUT'])
# @role_required('admin')  # TODO: Uncomment once role_required is implemented
def approve_company(company_id):
    """
    Approve a pending company account.
    Once approved, the company can log in and post job listings.

    Path parameter:
        company_id (int): The ID of the company to approve.

    Success response (200 OK):
        { "message": "Company approved", "company": { ... } }

    Error responses:
        401 — Not an admin
        404 — Company not found
    """
    # TODO: Call admin_service.update_company_status(company_id, 'approved') which will:
    #         - Find Company by ID (404 if not found)
    #         - Set company.status = 'approved'
    #         - Commit to DB
    #         - Optionally: send an approval email to the company
    # result, status_code = admin_service.update_company_status(company_id, 'approved')
    # return jsonify(result), status_code

    return jsonify({'message': f'approve_company({company_id}) stub — not yet implemented'}), 200


# ============================================================
# PUT /api/admin/companies/<id>/reject
# ============================================================
@admin_bp.route('/companies/<int:company_id>/reject', methods=['PUT'])
# @role_required('admin')  # TODO: Uncomment once role_required is implemented
def reject_company(company_id):
    """
    Reject a pending company account.
    The company will not be able to log in or post jobs.

    Path parameter:
        company_id (int): The ID of the company to reject.

    Success response (200 OK):
        { "message": "Company rejected", "company": { ... } }

    Error responses:
        401 — Not an admin
        404 — Company not found
    """
    # TODO: Call admin_service.update_company_status(company_id, 'rejected')
    # Same as approve but sets status to 'rejected'
    # result, status_code = admin_service.update_company_status(company_id, 'rejected')
    # return jsonify(result), status_code

    return jsonify({'message': f'reject_company({company_id}) stub — not yet implemented'}), 200


# ============================================================
# DELETE /api/admin/jobs/<id>
# ============================================================
@admin_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
# @role_required('admin')  # TODO: Uncomment once role_required is implemented
def delete_job(job_id):
    """
    Permanently delete any job listing from the platform.
    Admins can remove inappropriate or fraudulent job postings.

    Path parameter:
        job_id (int): The ID of the job to delete.

    Success response (200 OK):
        { "message": "Job deleted by admin" }

    Error responses:
        401 — Not an admin
        404 — Job not found
    """
    # TODO: Call admin_service.delete_job(job_id) which will:
    #         - Find Job by ID (404 if not found)
    #         - Delete it (cascade removes its Applications too)
    #         - Commit to DB
    # result, status_code = admin_service.delete_job(job_id)
    # return jsonify(result), status_code

    return jsonify({'message': f'admin_delete_job({job_id}) stub — not yet implemented'}), 200


# ============================================================
# DELETE /api/admin/users/<id>
# ============================================================
@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
# @role_required('admin')  # TODO: Uncomment once role_required is implemented
def delete_user(user_id):
    """
    Permanently delete a user (job seeker) account.
    Also removes all their applications (via cascade).

    Path parameter:
        user_id (int): The ID of the user to delete.

    Success response (200 OK):
        { "message": "User deleted by admin" }

    Error responses:
        401 — Not an admin
        404 — User not found
    """
    # TODO: Call admin_service.delete_user(user_id) which will:
    #         - Find User by ID (404 if not found)
    #         - Delete user (cascade removes their Applications)
    #         - Commit to DB
    # result, status_code = admin_service.delete_user(user_id)
    # return jsonify(result), status_code

    return jsonify({'message': f'admin_delete_user({user_id}) stub — not yet implemented'}), 200


# ============================================================
# DELETE /api/admin/companies/<id>
# ============================================================
@admin_bp.route('/companies/<int:company_id>', methods=['DELETE'])
# @role_required('admin')  # TODO: Uncomment once role_required is implemented
def delete_company(company_id):
    """
    Permanently delete a company account.
    Also removes all their job listings and associated applications.

    Path parameter:
        company_id (int): The ID of the company to delete.

    Success response (200 OK):
        { "message": "Company deleted by admin" }

    Error responses:
        401 — Not an admin
        404 — Company not found
    """
    # TODO: Call admin_service.delete_company(company_id) which will:
    #         - Find Company by ID (404 if not found)
    #         - Delete company (cascade removes all Jobs and their Applications)
    #         - Commit to DB
    # result, status_code = admin_service.delete_company(company_id)
    # return jsonify(result), status_code

    return jsonify({'message': f'admin_delete_company({company_id}) stub — not yet implemented'}), 200
