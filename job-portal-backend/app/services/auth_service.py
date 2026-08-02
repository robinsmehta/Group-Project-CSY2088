# ============================================================
# app/services/auth_service.py — Authentication Business Logic
#
# This is the BUSINESS LOGIC LAYER for authentication.
# Routes in auth_routes.py call functions defined here.
#
# Responsibilities:
#   - Check for duplicate emails in the database BEFORE password hashing
#   - Hash passwords with bcrypt before storing (never store plain text)
#   - Verify passwords on login using bcrypt.check_password_hash
#   - Manage session state (store user_id, role, company approval status)
#   - Return sanitized response dicts and HTTP status codes (never return password hashes)
# ============================================================

from flask import session
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.company import Company
from app.models.admin import Admin


def register_user(name, email=None, password=None):
    """
    Register a new job-seeker account.

    Args:
        name (str or dict): Full name or dict containing name, email, password.
        email (str, optional): User email address.
        password (str, optional): Plain text password to hash.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # Accept both positional arguments and dictionary input for flexibility
    if isinstance(name, dict):
        data = name
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

    name = (name or '').strip()
    email = (email or '').strip().lower()
    password = password or ''

    if not name or not email or not password:
        return {'error': 'Name, email, and password are required fields'}, 400

    # -------------------------------------------------------------------------
    # 1. DUPLICATE EMAIL CHECK (BEFORE HASHING)
    #
    # WHY CHECK BEFORE HASHING?
    # Password hashing using bcrypt is deliberately computationally expensive (work factor 12)
    # to resist brute-force attacks. Running bcrypt hashing BEFORE checking if the email exists
    # would allow malicious users to launch a Denial of Service (DoS) attack by spamming
    # duplicate registration requests to consume CPU resources.
    # -------------------------------------------------------------------------
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return {'error': 'Email is already registered'}, 409

    # -------------------------------------------------------------------------
    # 2. SECURE PASSWORD HASHING
    #
    # WHY BCRYPT?
    # Plain text passwords must NEVER be saved in the database. Flask-Bcrypt generates
    # a salt automatically and hashes the password securely. We decode it to utf-8
    # so it can be stored as a String in MySQL.
    # -------------------------------------------------------------------------
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # 3. Create new User record and commit to database
    new_user = User(
        name=name,
        email=email,
        password_hash=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()

    # -------------------------------------------------------------------------
    # 4. RETURN SUCCESS RESPONSE (SANITISED)
    #
    # WHY PASSWORD HASH IS EXCLUDED:
    # Even though bcrypt hashes are secure, returning password hashes in API responses
    # exposes them to network sniffers, client logs, or XSS attacks. We only return
    # essential user details (id, name, email).
    # -------------------------------------------------------------------------
    return {
        'message': 'User registered successfully',
        'user': {
            'id': new_user.id,
            'name': new_user.name,
            'email': new_user.email
        }
    }, 201


def register_company(company_name, email=None, password=None, description=None):
    """
    Register a new company/employer account.

    Args:
        company_name (str or dict): Company name or dict with fields.
        email (str, optional): Company contact/login email.
        password (str, optional): Plain text password to hash.
        description (str, optional): Optional description of the company.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    if isinstance(company_name, dict):
        data = company_name
        company_name = data.get('company_name')
        email = data.get('email')
        password = data.get('password')
        description = data.get('description')

    company_name = (company_name or '').strip()
    email = (email or '').strip().lower()
    password = password or ''
    description = (description or '').strip() if description else None

    if not company_name or not email or not password:
        return {'error': 'Company name, email, and password are required fields'}, 400

    # 1. Duplicate email check in companies table before hashing
    existing_company = Company.query.filter_by(email=email).first()
    if existing_company:
        return {'error': 'Email is already registered'}, 409

    # 2. Securely hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # 3. Create Company record (default status='pending')
    # Companies default to 'pending' and require admin approval before they can post jobs.
    new_company = Company(
        company_name=company_name,
        email=email,
        password_hash=hashed_password,
        description=description,
        status='pending'
    )
    db.session.add(new_company)
    db.session.commit()

    # 4. Return success response with note about admin approval
    return {
        'message': 'Company registered successfully. Account is pending admin approval.',
        'note': 'Your account is pending admin approval before you can post jobs.',
        'company': {
            'id': new_company.id,
            'company_name': new_company.company_name,
            'email': new_company.email,
            'status': new_company.status
        }
    }, 201


def login(email, password=None, role=None):
    """
    Authenticate a user, company, or admin account and establish a session.

    Args:
        email (str or dict): Email address or dictionary of login credentials.
        password (str, optional): Password to verify.
        role (str, optional): Account role ('user', 'company', or 'admin').

    Returns:
        tuple: (response_dict, http_status_code)
    """
    if isinstance(email, dict):
        data = email
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

    email = (email or '').strip().lower()
    password = password or ''
    role = (role or '').strip().lower()

    if not email or not password or not role:
        return {'error': 'Email, password, and role are required fields'}, 400

    # 1. Query the corresponding database model based on the requested role
    if role == 'user':
        account = User.query.filter_by(email=email).first()
    elif role == 'company':
        account = Company.query.filter_by(email=email).first()
    elif role == 'admin':
        account = Admin.query.filter_by(email=email).first()
    else:
        return {'error': 'Invalid role. Role must be user, company, or admin.'}, 400

    # 2. Check if account exists
    # SECURITY: Return generic error message ("Invalid email or password") to prevent email enumeration
    if not account:
        return {'error': 'Invalid email or password'}, 401

    # -------------------------------------------------------------------------
    # 3. VERIFY PASSWORD WITH BCRYPT
    #
    # WHY NOT STRING EQUALITY (==)?
    # Bcrypt produces a random salt for every password hash. Comparing plain text
    # password against stored hash using `==` will always fail and is insecure.
    # `bcrypt.check_password_hash` extracts the salt from stored hash and re-hashes
    # the candidate password in constant time to prevent timing attacks.
    # -------------------------------------------------------------------------
    if not bcrypt.check_password_hash(account.password_hash, password):
        return {'error': 'Invalid email or password'}, 401

    # -------------------------------------------------------------------------
    # 4. STORE IDENTITY AND ROLE IN FLASK SESSION
    #
    # WHY SESSION STORAGE?
    # Flask sessions use cryptographically signed HTTP cookies. Storing user_id, role,
    # and approval status in the session allows server-side decorators like @role_required
    # to authenticate subsequent requests instantly without database lookups.
    # -------------------------------------------------------------------------
    session.clear()  # Clear any stale session data
    session['user_id'] = account.id
    session['role'] = role

    approval_status = None
    if role == 'company':
        approval_status = account.status
        session['status'] = approval_status
        session['company_id'] = account.id  # Set company_id for consistency

    account_name = getattr(account, 'name', getattr(account, 'company_name', ''))

    return {
        'message': 'Login successful',
        'role': role,
        'user': {
            'id': account.id,
            'name': account_name,
            'email': account.email,
            'role': role,
            'status': approval_status
        }
    }, 200


def logout():
    """
    Log out the active account by clearing the Flask session.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # session.clear() removes user_id, role, and all stored credentials
    session.clear()
    return {'message': 'Logged out successfully'}, 200
