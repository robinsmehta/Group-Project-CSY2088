# app/routes/admin_routes.py — Admin Routes
#
# Handles all platform administration actions.
# Every route in this file is protected with @role_required('admin') so only
# logged-in admins can access them.
#
# URL prefix: /api/admin
# Endpoints:
#   GET    /api/admin/companies/pending         → list companies waiting for approval
#   PUT    /api/admin/companies/<id>/approve    → approve a company
#   PUT    /api/admin/companies/<id>/reject     → reject a company
#   DELETE /api/admin/jobs/<id>                → remove any job listing
#   DELETE /api/admin/users/<id>               → remove a user account
#   DELETE /api/admin/companies/<id>           → remove a company account
#   PUT    /api/admin/profile                  → update the logged-in admin's profile
#   GET    /api/admin/stats                    → platform-wide counts for the dashboard
#   GET    /api/admin/users                    → paginated list of all users and companies
#   POST   /api/admin/admins                   → create a new admin account
#   PUT    /api/admin/users/<id>/revoke        → suspend a user account
#   PUT    /api/admin/users/<id>/restore       → restore a suspended user account
#   PUT    /api/admin/companies/<id>/revoke    → suspend a company account
#   PUT    /api/admin/companies/<id>/restore   → restore a suspended company account

from flask import Blueprint, jsonify, request, session
from app.services import admin_service
from app.utils.decorators import role_required

admin_bp = Blueprint('admin', __name__)


# GET /api/admin/companies/pending
@admin_bp.route('/companies/pending', methods=['GET'])
@role_required('admin')
def get_pending_companies():
    """
    Return all company accounts that are still waiting for approval.
    Admins use this to see which employers need to be reviewed.

    Success response (200 OK):
        { "companies": [ { company1 }, { company2 }, ... ] }
    """
    search = request.args.get('search') or None
    result, status_code = admin_service.get_pending_companies(search=search)
    return jsonify(result), status_code


# PUT /api/admin/companies/<id>/approve
@admin_bp.route('/companies/<int:company_id>/approve', methods=['PUT'])
@role_required('admin')
def approve_company(company_id):
    """
    Approve a company's account. Once approved, the company can log in and post job listings.

    Path parameter:
        company_id (int): The ID of the company to approve.
    """
    result, status_code = admin_service.approve_company(company_id)
    return jsonify(result), status_code


# PUT /api/admin/companies/<id>/reject
@admin_bp.route('/companies/<int:company_id>/reject', methods=['PUT'])
@role_required('admin')
def reject_company(company_id):
    """
    Reject a company's account. The company will not be allowed to log in or post jobs.

    Path parameter:
        company_id (int): The ID of the company to reject.
    """
    result, status_code = admin_service.reject_company(company_id)
    return jsonify(result), status_code


# DELETE /api/admin/jobs/<id>
@admin_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
@role_required('admin')
def delete_job(job_id):
    """
    Permanently delete any job listing from the platform.
    Admins can remove inappropriate or fraudulent job postings.
    All applications submitted for this job are also deleted.

    Path parameter:
        job_id (int): The ID of the job to delete.
    """
    result, status_code = admin_service.delete_job(job_id)
    return jsonify(result), status_code


# DELETE /api/admin/users/<id>
@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    """
    Permanently delete a job-seeker account.
    All applications submitted by this user are also deleted.

    Path parameter:
        user_id (int): The ID of the user to delete.
    """
    result, status_code = admin_service.delete_user(user_id)
    return jsonify(result), status_code


# DELETE /api/admin/companies/<id>
@admin_bp.route('/companies/<int:company_id>', methods=['DELETE'])
@role_required('admin')
def delete_company(company_id):
    """
    Permanently delete a company account.
    All jobs posted by this company and all applications for those jobs are also deleted.

    Path parameter:
        company_id (int): The ID of the company to delete.
    """
    result, status_code = admin_service.delete_company(company_id)
    return jsonify(result), status_code


# GET /api/admin/stats
@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def get_stats():
    """
    Return platform-wide totals for the admin dashboard: total users, companies, jobs,
    applications, and how many companies are still pending approval.
    """
    result, status_code = admin_service.get_admin_stats()
    return jsonify(result), status_code


# PUT /api/admin/profile
@admin_bp.route('/profile', methods=['PUT'])
@role_required('admin')
def update_profile():
    """
    Allow the currently logged-in admin to update their own name, email, or password.
    Leave any field blank (or omit it) to keep the existing value.

    Request body (JSON):
        {
            "name": "New Name",           (optional)
            "email": "new@example.com",   (optional)
            "password": "newpassword123"  (optional)
        }
    """
    admin_id = session.get('user_id')
    if not admin_id:
        return jsonify({'error': 'Admin not found in session'}), 401

    data = request.get_json() or {}

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    result, status_code = admin_service.update_admin_profile(
        admin_id=admin_id,
        name=name,
        email=email,
        password=password
    )
    return jsonify(result), status_code


# GET /api/admin/users
@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def get_users():
    """
    Return a paginated, searchable list of all users and companies for the admin directory.

    Query params:
        page (int, optional): page number, starting at 1 (default 1)
        per_page (int, optional): how many results per page (default 10)
        search (str, optional): filter by name or email (case-insensitive)
    """
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)
    search = request.args.get('search') or None

    result, status_code = admin_service.get_users(page=page, per_page=per_page, search=search)
    return jsonify(result), status_code


# POST /api/admin/admins
@admin_bp.route('/admins', methods=['POST'])
@role_required('admin')
def create_admin_route():
    """
    Create a new administrator account. Only existing admins can do this.
    Request body must include JSON: { name, email, password }
    """
    data = None
    try:
        data = request.get_json(force=True)
    except Exception:
        data = None

    if not data:
        return jsonify({'error': 'Invalid JSON body'}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    result, status_code = admin_service.create_admin(name=name, email=email, password=password)
    return jsonify(result), status_code


# PUT /api/admin/users/<id>/revoke — suspend a user account
@admin_bp.route('/users/<int:user_id>/revoke', methods=['PUT'])
@role_required('admin')
def revoke_user(user_id):
    """Suspend a user account so they cannot log in. Does not delete their data."""
    result, status_code = admin_service.revoke_user(user_id)
    return jsonify(result), status_code


# PUT /api/admin/users/<id>/restore — reinstate a suspended user account
@admin_bp.route('/users/<int:user_id>/restore', methods=['PUT'])
@role_required('admin')
def restore_user(user_id):
    """Restore a previously suspended user account, allowing them to log in again."""
    result, status_code = admin_service.restore_user(user_id)
    return jsonify(result), status_code


# PUT /api/admin/companies/<id>/revoke — suspend a company account
@admin_bp.route('/companies/<int:company_id>/revoke', methods=['PUT'])
@role_required('admin')
def revoke_company(company_id):
    """Suspend a company account so they cannot log in or post new jobs."""
    result, status_code = admin_service.revoke_company(company_id)
    return jsonify(result), status_code


# PUT /api/admin/companies/<id>/restore — reinstate a suspended company account
@admin_bp.route('/companies/<int:company_id>/restore', methods=['PUT'])
@role_required('admin')
def restore_company(company_id):
    """Restore a previously suspended company account, allowing them to log in again."""
    result, status_code = admin_service.restore_company(company_id)
    return jsonify(result), status_code
