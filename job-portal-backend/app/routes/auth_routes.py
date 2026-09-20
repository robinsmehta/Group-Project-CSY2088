# app/routes/auth_routes.py — Authentication Routes
#
# Handles all user login, logout, and registration requests.
# This layer receives HTTP requests, checks that required fields are present,
# then passes the work to auth_service.py which contains the actual logic.
#
# URL prefix: /api/auth
# Endpoints:
#   POST /api/auth/register/user     → create a new job-seeker account
#   POST /api/auth/register/company  → create a new employer account
#   POST /api/auth/login             → log in as user, company, or admin
#   POST /api/auth/logout            → end the current session
#   GET  /api/auth/me                → return info about who is logged in
#   PUT  /api/auth/me/user           → job seeker updates their own profile
#   PUT  /api/auth/me/company        → company updates their own profile
#   GET  /api/auth/company/test      → protected test route for company role

from flask import Blueprint, request, jsonify, session
from app.services import auth_service
from app.utils.decorators import role_required

auth_bp = Blueprint('auth', __name__)


# POST /api/auth/register/user
@auth_bp.route('/register/user', methods=['POST'])
def register_user():
    """
    Create a new job-seeker account.
    Anyone can call this endpoint — no login required.

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

    # Check that all required fields were sent before doing anything else
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({
            'error': 'Missing required fields: name, email, and password are required.'
        }), 400

    # Hand off to the service layer which handles password hashing and database saving
    result, status_code = auth_service.register_user(name=name, email=email, password=password)
    return jsonify(result), status_code


# POST /api/auth/register/company
@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    """
    Create a new employer/company account.
    New company accounts start as "pending" and cannot post jobs until an admin approves them.

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

    # Hand off to the service layer for the actual registration logic
    result, status_code = auth_service.register_company(
        company_name=company_name,
        email=email,
        password=password,
        description=description
    )
    return jsonify(result), status_code


# POST /api/auth/login
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Log in as a user, company, or admin and start a session.
    After a successful login the caller's browser will hold a session cookie
    that keeps them logged in for future requests.

    Expected JSON body:
        {
            "email":    "jane@example.com",
            "password": "securepassword123",
            "role":     "user"    # 'user', 'company', or 'admin'
        }

    Response Statuses:
        200 OK — Login successful, session started
        400 Bad Request — Missing required fields or invalid role format
        401 Unauthorized — Wrong email or password
    """
    data = request.get_json(silent=True) or {}

    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not email or not password:
        return jsonify({
            'error': 'Missing required fields: email and password are required.'
        }), 400

    # Service layer verifies the password and sets up the session
    result, status_code = auth_service.login(email=email, password=password, role=role)
    return jsonify(result), status_code


# GET /api/auth/me — return info about the currently logged-in account
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
    elif role == 'user':
        user_obj = db.session.get(User, user_id)
        if user_obj:
            user['skills'] = user_obj.skills

    return jsonify({'user': user}), 200


# POST /api/auth/logout
@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Log out the currently authenticated user, company, or admin.
    Clears the server-side session so the browser cookie is no longer valid.

    Response Statuses:
        200 OK — Logout successful
    """
    result, status_code = auth_service.logout()
    return jsonify(result), status_code


# PUT /api/auth/me/user — job seeker updates their own profile
@auth_bp.route('/me/user', methods=['PUT'])
@role_required('user')
def update_user_profile():
    """
    Let the currently logged-in job seeker update their name, email, password, or skills.
    Only users with the 'user' role can call this endpoint.
    """
    user_id = session.get('user_id')
    data = request.get_json(silent=True) or {}

    result, status_code = auth_service.update_user_profile(
        user_id=user_id,
        name=data.get('name'),
        email=data.get('email'),
        password=data.get('password'),
        skills=data.get('skills')
    )
    return jsonify(result), status_code


# PUT /api/auth/me/company — company updates their own profile
@auth_bp.route('/me/company', methods=['PUT'])
@role_required('company')
def update_company_profile():
    """
    Let the currently logged-in company update their name, email, password, or description.
    Only accounts with the 'company' role can call this endpoint.
    """
    company_id = session.get('company_id') or session.get('user_id')
    data = request.get_json(silent=True) or {}

    result, status_code = auth_service.update_company_profile(
        company_id=company_id,
        company_name=data.get('company_name') or data.get('name'),
        email=data.get('email'),
        password=data.get('password'),
        description=data.get('description')
    )
    return jsonify(result), status_code


# GET /api/auth/company/test — protected test route demonstrating @role_required
@auth_bp.route('/company/test', methods=['GET'])
@role_required('company')
def company_test_route():
    """
    A protected test endpoint that only an approved company can reach.
    Useful for verifying that the session and role-checking middleware work correctly.

    Response Statuses:
        200 OK — Session valid and role matches 'company'
        401 Unauthorized — User not logged in
        403 Forbidden — Logged in with a different role
    """
    return jsonify({
        'message': 'Access granted to protected company test endpoint!',
        'company_id': session.get('user_id'),
        'role': session.get('role'),
        'approval_status': session.get('status')
    }), 200
