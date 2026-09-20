# app/services/auth_service.py — Authentication Business Logic
#
# This is the business logic layer for authentication.
# Routes in auth_routes.py call functions defined here.
#
# What this file handles:
#   - Checking for duplicate emails before doing anything expensive
#   - Scrambling (hashing) passwords with bcrypt before saving — we never store plain text
#   - Verifying passwords at login time using the same bcrypt library
#   - Starting and ending server-side sessions that keep users logged in
#   - Returning clean response data — password hashes are never included in API responses

from flask import session
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.company import Company
from app.models.admin import Admin

def register_user(name, email=None, password=None):
    """
    Create a new job-seeker account in the database.

    Args:
        name (str or dict): Full name or dict containing name, email, password.
        email (str, optional): User email address.
        password (str, optional): Plain text password to hash.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # Accept both positional arguments and a single dictionary for flexibility
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

    # Check for duplicate email BEFORE hashing the password.
    # Password hashing is intentionally slow (to resist brute-force attacks),
    # so rejecting duplicates first avoids doing that expensive work for nothing.
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return {'error': 'Email is already registered'}, 409

    # Scramble the password using bcrypt so we never store the real thing.
    # The result looks like '$2b$12$...' and is safe to store in the database.
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Save the new user record to the database
    new_user = User(
        name=name,
        email=email,
        password_hash=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()

    # Return the new user's details — but deliberately exclude the password hash
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
    Create a new company/employer account. The company starts with "pending" status
    and cannot post jobs until an admin approves them.

    Args:
        company_name (str or dict): Company name or dict with all fields.
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

    # Check for duplicate email before hashing the password
    existing_company = Company.query.filter_by(email=email).first()
    if existing_company:
        return {'error': 'Email is already registered'}, 409

    # Scramble the password before storing it
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # New companies always start as 'pending' — an admin must approve them before they can post jobs
    new_company = Company(
        company_name=company_name,
        email=email,
        password_hash=hashed_password,
        description=description,
        status='pending'
    )
    db.session.add(new_company)
    db.session.commit()

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
    Verify an account's credentials and start a session so the user stays logged in.
    Works for job seekers, companies, and admins. If no role is provided, we try
    to detect it automatically by searching each account table in order.

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

    # Find the account record — look up by role if given, otherwise try each table in turn
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

    # Use a generic error message so attackers cannot tell whether the email exists
    if not account:
        return {'error': 'Invalid email or password'}, 401

    # Check the password the user typed against the scrambled version we stored.
    # We can't compare them directly because hashing is one-way; bcrypt handles this safely.
    if not bcrypt.check_password_hash(account.password_hash, password):
        return {'error': 'Invalid email or password'}, 401

    # Block suspended accounts from logging in
    if role in ('user', 'company'):
        is_active = getattr(account, 'is_active', None)
        if is_active is False:
            return {'error': 'This account has been suspended. Contact support.'}, 403

    # Store the account's identity and role in the session so future requests stay logged in.
    # The session is backed by a signed browser cookie — users cannot forge or tamper with it.
    session.clear()  # Remove any leftover data from a previous session
    session['user_id'] = account.id
    session['role'] = role

    account_name = getattr(account, 'name', getattr(account, 'company_name', ''))
    session['name'] = account_name
    session['email'] = account.email

    approval_status = None
    if role == 'company':
        approval_status = account.status
        session['status'] = approval_status
        session['company_id'] = account.id
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
    End the current session so the user is logged out.
    Clearing the session means the browser's cookie is no longer accepted by the server.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    session.clear()
    return {'message': 'Logged out successfully'}, 200


def update_user_profile(user_id, name=None, email=None, password=None, skills=None):
    """
    Let a logged-in job seeker update their profile details.
    Only the fields you pass will be changed; omitted fields stay the same.

    Args:
        user_id (int): Primary key of the user to update.
        name (str, optional): New name.
        email (str, optional): New email (must be unique).
        password (str, optional): New plain text password (will be hashed before saving).
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
    Let a logged-in company update their profile details.
    Only the fields you pass will be changed; omitted fields stay the same.

    Args:
        company_id (int): Primary key of the company to update.
        company_name (str, optional): New company name.
        email (str, optional): New email (must be unique).
        password (str, optional): New plain text password (will be hashed before saving).
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
