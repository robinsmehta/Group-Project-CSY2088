# ============================================================
# app/routes/auth_routes.py — Authentication Routes (Presentation Layer)
#
# This file is the PRESENTATION LAYER for authentication.
# Its job is ONLY to:
#   1. Receive HTTP requests
#   2. Extract and validate request input (presence of required JSON fields)
#   3. Pass the data to the Business Logic layer (auth_service.py)
#   4. Return an HTTP response with appropriate status code
#
# Blueprint: auth_bp
# URL Prefix (set in app/__init__.py): /api/auth
# Endpoints:
#   POST /api/auth/register/user
#   POST /api/auth/register/company
#   POST /api/auth/login
#   POST /api/auth/logout
#   GET  /api/auth/company/test (protected test route demonstrating @role_required)
# ============================================================

from flask import Blueprint, request, jsonify, session
from app.services import auth_service
from app.utils.decorators import role_required

auth_bp = Blueprint('auth', __name__)


# ============================================================
# POST /api/auth/register/user
# ============================================================
@auth_bp.route('/register/user', methods=['POST'])
def register_user():
    """
    Register a new job-seeker account.

    Expected JSON body:
        {
            "name":     "Jane Doe",
            "email":    "jane@example.com",
            "password": "securepassword123"
        }

    Response Statuses:
        201 Created — User registered successfully
        400 Bad Request — Missing required fields
        409 Conflict — Email already registered
    """
    data = request.get_json(silent=True) or {}

    # Basic route-level input validation
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({
            'error': 'Missing required fields: name, email, and password are required.'
        }), 400

    # Delegate business logic to auth_service layer
    result, status_code = auth_service.register_user(name=name, email=email, password=password)
    return jsonify(result), status_code


# ============================================================
# POST /api/auth/register/company
# ============================================================
@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    """
    Register a new employer/company account.

    Expected JSON body:
        {
            "company_name": "Acme Corp",
            "email":        "hr@acme.com",
            "password":     "securepassword456",
            "description":  "We make software."
        }

    Response Statuses:
        201 Created — Company registered (pending approval)
        400 Bad Request — Missing required fields
        409 Conflict — Email already registered
    """
    data = request.get_json(silent=True) or {}

    company_name = data.get('company_name')
    email = data.get('email')
    password = data.get('password')
    description = data.get('description')

    if not company_name or not email or not password:
        return jsonify({
            'error': 'Missing required fields: company_name, email, and password are required.'
        }), 400

    # Delegate business logic to auth_service layer
    result, status_code = auth_service.register_company(
        company_name=company_name,
        email=email,
        password=password,
        description=description
    )
    return jsonify(result), status_code


# ============================================================
# POST /api/auth/login
# ============================================================
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user, company, or admin and establish a session.

    Expected JSON body:
        {
            "email":    "jane@example.com",
            "password": "securepassword123",
            "role":     "user"    # 'user', 'company', or 'admin'
        }

    Response Statuses:
        200 OK — Authentication successful, session initialized
        400 Bad Request — Missing required fields or invalid role format
        401 Unauthorized — Invalid email or password
    """
    data = request.get_json(silent=True) or {}

    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not email or not password:
        return jsonify({
            'error': 'Missing required fields: email and password are required.'
        }), 400

    # Delegate business logic to auth_service layer
    result, status_code = auth_service.login(email=email, password=password, role=role)
    return jsonify(result), status_code


# ============================================================
# POST /api/auth/logout
# ============================================================
@auth_bp.route('/me', methods=['GET'])
def current_user():
    """Return the currently authenticated user from the server-side session."""
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id or not role:
        return jsonify({
            'error': 'Authentication required. Please log in to access this resource.'
        }), 401

    user = {
        'id': user_id,
        'role': role,
        'name': session.get('name') or session.get('company_name') or '',
        'email': session.get('email') or '',
        'status': session.get('status')
    }

    if role == 'company':
        user['company_id'] = session.get('company_id', user_id)
        user['company_name'] = session.get('company_name') or user['name'] or ''

    return jsonify({'user': user}), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Log out the currently authenticated user/company/admin.

    Clears server-side session data.

    Response Statuses:
        200 OK — Logout successful
    """
    result, status_code = auth_service.logout()
    return jsonify(result), status_code


# ============================================================
# TASK-009 — Add "update my own profile" routes (User / Company / Admin)
# ============================================================
#
# PROBLEM:
# Right now, once someone registers, there is NO way for them to change
# their own name, email, password (or, for companies, their description)
# afterwards. This file has routes for registering and logging in, but
# nothing for "update my account while I'm logged in."
#
# There are actually THREE separate small tasks hiding here, one per
# account type — each assigned to a different team member, because each
# person already owns that account type elsewhere in the app:
#
#   • Job seeker (User)  → Reeju      (E7) → update name, email, password
#   • Company             → Simrika   (D4) → update company_name, email,
#                                              password, AND description
#   • Admin                → Ugeesha  (C3) → update name, email, password
#
# WHAT YOU NEED TO DO (same pattern for all three — copy this shape):
# 1. Add a new route in this file, for example:
#        @auth_bp.route('/me/user', methods=['PUT'])       (Reeju)
#        @auth_bp.route('/me/company', methods=['PUT'])    (Simrika)
#        @auth_bp.route('/me/admin', methods=['PUT'])      (Ugeesha)
#    Protect it with @role_required('user') / ('company') / ('admin')
#    (see how other routes in this file and in job_routes.py use it).
# 2. Read the logged-in person's id from the session, the same way
#    `session.get('user_id')` / `session.get('company_id')` is used
#    elsewhere in this file.
# 3. Read the new values (name/email/password, +description for company)
#    from the JSON request body — look at how `register_company()` above
#    reads `data.get(...)` for an example.
# 4. Call a new function you'll add in auth_service.py (e.g.
#    `update_user_profile(...)`, `update_company_profile(...)`,
#    `update_admin_profile(...)`) that actually updates the database
#    record. IMPORTANT: if a new password is provided, it must be
#    hashed the same way `register_user`/`register_company` already
#    hash passwords in auth_service.py — never save a plain-text password.
# 5. Return the updated (safe — no password) profile info as JSON.
#
# HOW THIS PART CONNECTS:
# Member B (Sagar) is building ONE shared popover (in shared.js) that opens
# from the little circle icon in the navbar on every page. Once you've
# built your route above, Sagar's popover code will call it. You do NOT
# need to build any frontend for this — just the backend route + service
# function. Member A (Robins) is building what the popover LOOKS like.
#
# WHAT "DONE" LOOKS LIKE:
# You can send a PUT request with a new password to your route, and the
# next time that account logs in, the new password works.
#
# ASSIGNED TASK:
# TASK-009a — Reeju (E7): Job seeker profile editing route.
# TASK-009b — Simrika (D4): Company profile editing route (incl. description).
# TASK-009c — Ugeesha (C3): Admin's own profile editing route.
# ============================================================


# ============================================================
# GET /api/auth/company/test — Protected Route Example
# ============================================================
@auth_bp.route('/company/test', methods=['GET'])
@role_required('company')
def company_test_route():
    """
    Demonstration protected endpoint requiring 'company' role.

    Response Statuses:
        200 OK — Session valid & role matches 'company'
        401 Unauthorized — User not logged in
        403 Forbidden — User logged in with non-company role
    """
    return jsonify({
        'message': 'Access granted to protected company test endpoint!',
        'company_id': session.get('user_id'),
        'role': session.get('role'),
        'approval_status': session.get('status')
    }), 200
