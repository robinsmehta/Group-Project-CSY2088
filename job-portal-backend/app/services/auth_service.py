# ============================================================
# app/services/auth_service.py — Authentication Business Logic
#
# This is the BUSINESS LOGIC LAYER for authentication.
# Routes in auth_routes.py call functions defined here.
#
# Responsibilities:
#   - Validate data rules (not just "is field present" but "is email valid format?")
#   - Check for duplicate emails in the database before registering
#   - Hash passwords with bcrypt before storing
#   - Verify passwords on login
#   - Manage session state (set/clear session variables)
#   - Return consistent (response_dict, http_status_code) tuples
#
# Each function here follows this return pattern:
#   return {'key': 'value'}, 200   ← success
#   return {'error': 'msg'},  400   ← failure
# ============================================================

from app.extensions import db, bcrypt
from app.models.user    import User
from app.models.company import Company
from app.models.admin   import Admin


def register_user(data: dict):
    """
    Business logic for registering a new job-seeker account.

    Args:
        data (dict): Should contain 'name', 'email', 'password'.

    Returns:
        tuple: (response_dict, http_status_code)

    Steps to implement:
    """
    # TODO: Extract fields from data
    # name     = data.get('name', '').strip()
    # email    = data.get('email', '').strip().lower()
    # password = data.get('password', '')

    # TODO: Validate that fields are not empty
    # if not name or not email or not password:
    #     return {'error': 'Name, email, and password are required'}, 400

    # TODO: Validate email format (optional but recommended)
    # You can use a regex or the 'email-validator' library

    # TODO: Check if email already exists in the users table
    # existing = User.query.filter_by(email=email).first()
    # if existing:
    #     return {'error': 'An account with this email already exists'}, 409

    # TODO: Hash the password using bcrypt
    # password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # TODO: Create a new User object and save to DB
    # new_user = User(name=name, email=email, password_hash=password_hash)
    # db.session.add(new_user)
    # db.session.commit()

    # TODO: Return success response
    # return {'message': 'User registered successfully', 'user': new_user.to_dict()}, 201

    # Placeholder
    return {'message': 'register_user service stub — not yet implemented'}, 200


def register_company(data: dict):
    """
    Business logic for registering a new company account.

    Args:
        data (dict): Should contain 'company_name', 'email', 'password',
                     and optionally 'description'.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Extract and validate fields (company_name, email, password)

    # TODO: Check for duplicate email in the companies table

    # TODO: Hash the password

    # TODO: Create Company with status='pending' (default) and save to DB

    # TODO: Return success response
    # return {'message': 'Company registered. Awaiting admin approval.', 'company': company.to_dict()}, 201

    return {'message': 'register_company service stub — not yet implemented'}, 200


def login(data: dict):
    """
    Business logic for authenticating a user, company, or admin.

    Args:
        data (dict): Should contain 'email', 'password', 'role'.
                     role must be one of: 'user', 'company', 'admin'.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Extract email, password, role from data

    # TODO: Based on role, decide which model to query:
    #   role == 'user'    → User model
    #   role == 'company' → Company model
    #   role == 'admin'   → Admin model

    # TODO: Query the database for an account with matching email
    # account = User.query.filter_by(email=email).first()  # (example for user)

    # TODO: If not found, return 401 Unauthorized
    # if not account:
    #     return {'error': 'Invalid email or password'}, 401

    # TODO: Verify password
    # if not bcrypt.check_password_hash(account.password_hash, password):
    #     return {'error': 'Invalid email or password'}, 401

    # TODO: If role is 'company', check that company status is 'approved'
    # if role == 'company' and account.status != 'approved':
    #     return {'error': 'Your company account is pending admin approval'}, 403

    # TODO: Store identity in Flask session
    # from flask import session
    # session['user_id'] = account.id
    # session['role']    = role

    # TODO: Return success response with account info
    # return {'message': 'Login successful', 'role': role, 'data': account.to_dict()}, 200

    return {'message': 'login service stub — not yet implemented'}, 200


def logout():
    """
    Business logic for logging out.
    Clears the Flask session.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Import session from flask and clear it
    # from flask import session
    # session.clear()
    # return {'message': 'Logged out successfully'}, 200

    return {'message': 'logout service stub — not yet implemented'}, 200
