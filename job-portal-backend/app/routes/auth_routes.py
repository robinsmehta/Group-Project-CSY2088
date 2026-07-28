# ============================================================
# app/routes/auth_routes.py — Authentication Routes (Presentation Layer)
#
# This file is the PRESENTATION LAYER for authentication.
# Its job is ONLY to:
#   1. Receive HTTP requests
#   2. Extract and lightly validate the request data
#   3. Pass the data to the Business Logic layer (auth_service.py)
#   4. Return an HTTP response
#
# It should NOT contain any business logic itself.
#
# Blueprint: auth_bp
# URL Prefix (set in app/__init__.py): /api/auth
# Full endpoint URLs:
#   POST /api/auth/register/user
#   POST /api/auth/register/company
#   POST /api/auth/login
#   POST /api/auth/logout
# ============================================================

from flask import Blueprint, request, jsonify
from app.services import auth_service  # Business logic lives here

# Create a Blueprint named 'auth'.
# A Blueprint is a mini Flask app — a group of related routes.
# 'auth' is the internal name; __name__ is used to locate templates/static files.
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

    Success response (201 Created):
        { "message": "User registered successfully", "user": { ... } }

    Error responses:
        400 — Missing fields or invalid data
        409 — Email already exists
    """
    # TODO: Extract JSON data from request body
    # data = request.get_json()

    # TODO: Check that required fields (name, email, password) exist in data
    # if not data or not data.get('name') or ...:
    #     return jsonify({'error': 'Missing required fields'}), 400

    # TODO: Call auth_service.register_user(data) to:
    #         - Check for duplicate email
    #         - Hash the password
    #         - Save the new User to the DB
    # result, status_code = auth_service.register_user(data)
    # return jsonify(result), status_code

    # Placeholder response — remove once logic is implemented
    return jsonify({'message': 'register_user route stub — not yet implemented'}), 200


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
            "description":  "We make everything."
        }

    Success response (201 Created):
        { "message": "Company registered. Pending admin approval.", "company": { ... } }

    Error responses:
        400 — Missing fields
        409 — Email already registered
    """
    # TODO: Extract JSON from request
    # data = request.get_json()

    # TODO: Validate required fields (company_name, email, password)

    # TODO: Call auth_service.register_company(data) to:
    #         - Check for duplicate email
    #         - Hash the password
    #         - Save Company with status='pending'
    # result, status_code = auth_service.register_company(data)
    # return jsonify(result), status_code

    return jsonify({'message': 'register_company route stub — not yet implemented'}), 200


# ============================================================
# POST /api/auth/login
# ============================================================
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user, company, or admin and start a session.

    Expected JSON body:
        {
            "email":    "jane@example.com",
            "password": "securepassword123",
            "role":     "user"    # one of: "user", "company", "admin"
        }

    Success response (200 OK):
        { "message": "Login successful", "role": "user", "data": { ... } }

    Error responses:
        400 — Missing fields
        401 — Invalid credentials
        403 — Company not yet approved by admin
    """
    # TODO: Extract JSON from request
    # data = request.get_json()

    # TODO: Get role from request to know which table to query
    # role = data.get('role')  # 'user', 'company', or 'admin'

    # TODO: Call auth_service.login(email, password, role) which will:
    #         - Look up the account in the right table
    #         - Verify the password with bcrypt.check_password_hash()
    #         - If company, check status == 'approved'
    #         - Store user info in Flask session (or generate a JWT token)
    # result, status_code = auth_service.login(data)
    # return jsonify(result), status_code

    return jsonify({'message': 'login route stub — not yet implemented'}), 200


# ============================================================
# POST /api/auth/logout
# ============================================================
@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Log out the currently authenticated user/company/admin.

    Clears the server-side session (or invalidates JWT token).

    Success response (200 OK):
        { "message": "Logged out successfully" }
    """
    # TODO: Call auth_service.logout() which will:
    #         - Clear session data: session.clear()
    #         - Or if using JWT: add token to a blacklist / tell client to discard it
    # result, status_code = auth_service.logout()
    # return jsonify(result), status_code

    return jsonify({'message': 'logout route stub — not yet implemented'}), 200
