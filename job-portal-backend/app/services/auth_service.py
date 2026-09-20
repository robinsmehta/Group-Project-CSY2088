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


# TODO — TASK-009 (see auth_routes.py for full details): the new profile-edit
# routes (update_user_profile / update_company_profile / update_admin_profile)
# should live in this file, following the same pattern as the register_*
# functions below — look up the record by id, update the provided fields,
# and if a new password is given, hash it with
# `bcrypt.generate_password_hash(password).decode('utf-8')` exactly like
# `register_user()` and `register_company()` do a few lines down, before
# saving it. Never save a password that hasn't been hashed.
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

    if not email or not password:
        return {'error': 'Email and password are required fields'}, 400

    # 1. Query the corresponding database model based on the requested role, or auto-detect
    if not role:
        account = Admin.query.filter_by(email=email).first()
        if account:
            role = 'admin'
        if not account:
            account = Company.query.filter_by(email=email).first()
            if account:
                role = 'company'
        if not account:
            account = User.query.filter_by(email=email).first()
            if account:
                role = 'user'
    else:
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

    # Prevent login if account has been suspended (users and companies only)
    if role in ('user', 'company'):
        is_active = getattr(account, 'is_active', None)
        if is_active is False:
            return {'error': 'This account has been suspended. Contact support.'}, 403

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

    account_name = getattr(account, 'name', getattr(account, 'company_name', ''))
    session['name'] = account_name
    session['email'] = account.email

    approval_status = None
    if role == 'company':
        approval_status = account.status
        session['status'] = approval_status
        session['company_id'] = account.id  # Set company_id for consistency
        session['company_name'] = getattr(account, 'company_name', '')

    user_payload = {
        'id': account.id,
        'name': account_name,
        'email': account.email,
        'role': role,
        'status': approval_status
    }

    if role == 'company':
        user_payload['company_id'] = account.id
        user_payload['company_name'] = getattr(account, 'company_name', '')
    elif role == 'user':
        user_payload['skills'] = getattr(account, 'skills', None)

    return {
        'message': 'Login successful',
        'role': role,
        'user': user_payload
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


def update_user_profile(user_id, name=None, email=None, password=None, skills=None):
    """
    Allow a logged-in user (job seeker) to update their profile (name, email, password, skills).

    Args:
        user_id (int): Primary key of the user to update.
        name (str, optional): New name.
        email (str, optional): New email (must be unique).
        password (str, optional): New plain text password to hash.
        skills (str, optional): Comma-separated skills string.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    if isinstance(user_id, dict):
        data = user_id
        user_id = data.get('user_id') or data.get('id')
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        skills = data.get('skills')

    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'User not found'}, 404

    updates_made = False

    if name is not None:
        name = (name or '').strip()
        if name:
            user.name = name
            updates_made = True
            session['name'] = name

    if email is not None:
        email = (email or '').strip().lower()
        if email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user_id:
                return {'error': 'Email is already registered'}, 409
            user.email = email
            updates_made = True
            session['email'] = email

    if password is not None and str(password).strip():
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user.password_hash = hashed_password
        updates_made = True

    if skills is not None:
        user.skills = (skills or '').strip()
        updates_made = True

    if not updates_made:
        return {'error': 'No fields to update'}, 400

    db.session.commit()

    return {
        'message': 'User profile updated successfully',
        'user': user.to_dict()
    }, 200


def update_company_profile(company_id, company_name=None, email=None, password=None, description=None):
    """
    Allow a logged-in company to update their profile (company_name, email, password, description).

    Args:
        company_id (int): Primary key of the company to update.
        company_name (str, optional): New company name.
        email (str, optional): New email (must be unique).
        password (str, optional): New plain text password to hash.
        description (str, optional): New company description.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    if isinstance(company_id, dict):
        data = company_id
        company_id = data.get('company_id') or data.get('id')
        company_name = data.get('company_name') or data.get('name')
        email = data.get('email')
        password = data.get('password')
        description = data.get('description')

    company = db.session.get(Company, company_id)
    if not company:
        return {'error': 'Company not found'}, 404

    updates_made = False

    if company_name is not None:
        company_name = (company_name or '').strip()
        if company_name:
            company.company_name = company_name
            updates_made = True
            session['name'] = company_name
            session['company_name'] = company_name

    if email is not None:
        email = (email or '').strip().lower()
        if email:
            existing_company = Company.query.filter_by(email=email).first()
            if existing_company and existing_company.id != company_id:
                return {'error': 'Email is already registered'}, 409
            company.email = email
            updates_made = True
            session['email'] = email

    if password is not None and str(password).strip():
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        company.password_hash = hashed_password
        updates_made = True

    if description is not None:
        description = (description or '').strip()
        company.description = description
        updates_made = True

    if not updates_made:
        return {'error': 'No fields to update'}, 400

    db.session.commit()

    return {
        'message': 'Company profile updated successfully',
        'company': company.to_dict()
    }, 200
