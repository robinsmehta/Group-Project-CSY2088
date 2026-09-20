# app/services/admin_service.py — Admin Business Logic
#
# Called by routes in admin_routes.py.
# Admin actions are the most powerful in the system — they can permanently
# delete user accounts, company profiles, and job listings, as well as
# approve companies so they can start posting jobs.
#
# For this reason, the @role_required('admin') decorator on every admin route
# is critical — it prevents any non-admin account from reaching these functions.
#
# When a parent record (Company, Job, or User) is deleted, all connected child
# records (jobs, applications) are automatically deleted too. This is configured
# via SQLAlchemy's cascade="all, delete-orphan" setting on the model relationships,
# so no orphaned rows are left behind in the database.

from app.extensions import db, bcrypt
from app.models.user import User
from app.models.company import Company
from app.models.job import Job
from app.models.application import Application
from app.models.admin import Admin


def get_pending_companies(search: str = None):
    """
    Return all companies that are still waiting for admin approval.
    Optionally filter by company name or email using a search term.

    Args:
        search (str, optional): Text to search for in company_name or email.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    q = Company.query.filter_by(status='pending')
    if search:
        term = f"%{search}%"
        q = q.filter((Company.company_name.ilike(term)) | (Company.email.ilike(term)))

    pending_companies = q.all()
    companies_data = [company.to_dict() for company in pending_companies]

    return {'companies': companies_data}, 200


def approve_company(company_id: int):
    """
    Approve a company account so it can log in and post job listings.

    Args:
        company_id (int): The ID of the company to approve.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    company = db.session.get(Company, company_id)
    if not company:
        return {'error': 'Company not found'}, 404

    company.status = 'approved'
    db.session.commit()

    return {
        'message': 'Company approved successfully',
        'company': company.to_dict()
    }, 200


def reject_company(company_id: int):
    """
    Reject a company account. The company will not be allowed to post jobs.

    Args:
        company_id (int): The ID of the company to reject.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    company = db.session.get(Company, company_id)
    if not company:
        return {'error': 'Company not found'}, 404

    company.status = 'rejected'
    db.session.commit()

    return {
        'message': 'Company rejected successfully',
        'company': company.to_dict()
    }, 200


def update_company_status(company_id: int, new_status: str):
    """
    Approve or reject a company by passing in the desired status string.
    A convenience wrapper around approve_company() and reject_company().

    Args:
        company_id (int): The company ID.
        new_status (str): 'approved' or 'rejected'.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    if new_status == 'approved':
        return approve_company(company_id)
    elif new_status == 'rejected':
        return reject_company(company_id)
    else:
        return {'error': f"Invalid status '{new_status}'. Allowed values: 'approved', 'rejected'"}, 400


def delete_job(job_id: int):
    """
    Permanently delete any job listing by ID.
    All applications for this job are automatically removed at the same time,
    because an application to a deleted job no longer makes sense.

    Args:
        job_id (int): The ID of the job to delete.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    job = db.session.get(Job, job_id)
    if not job:
        return {'error': 'Job not found'}, 404

    db.session.delete(job)
    db.session.commit()

    return {'message': 'Job deleted successfully'}, 200


def delete_user(user_id: int):
    """
    Permanently delete a job-seeker account.
    All applications submitted by this user are automatically removed too,
    because their applications have no valid applicant once the account is gone.

    Args:
        user_id (int): The ID of the user to delete.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'User not found'}, 404

    db.session.delete(user)
    db.session.commit()

    return {'message': 'User deleted successfully'}, 200


def delete_company(company_id: int):
    """
    Permanently delete a company account.
    All jobs posted by this company — and all applications for those jobs — are removed too.
    This three-level cascade keeps the database free of orphaned records.

    Args:
        company_id (int): The ID of the company to delete.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    company = db.session.get(Company, company_id)
    if not company:
        return {'error': 'Company not found'}, 404

    db.session.delete(company)
    db.session.commit()

    return {'message': 'Company deleted successfully'}, 200


def update_admin_profile(admin_id: int, name: str = None, email: str = None, password: str = None):
    """
    Let a logged-in admin update their own name, email, or password.
    Any field left blank (or omitted) will not be changed.

    Args:
        admin_id (int): The ID of the admin to update.
        name (str, optional): New display name.
        email (str, optional): New email address (must be unique among admins).
        password (str, optional): New plain text password (will be hashed before saving).

    Returns:
        tuple: (response_dict, http_status_code)
    """
    admin = db.session.get(Admin, admin_id)
    if not admin:
        return {'error': 'Admin not found'}, 404

    updates_made = False

    if name is not None:
        name = (name or '').strip()
        if name:
            admin.name = name
            updates_made = True

    if email is not None:
        email = (email or '').strip().lower()
        if email:
            # Check that the new email is not already taken by another admin
            existing_admin = Admin.query.filter_by(email=email).first()
            if existing_admin and existing_admin.id != admin_id:
                return {'error': 'Email is already registered'}, 409
            admin.email = email
            updates_made = True

    if password is not None and password.strip():
        # Scramble the new password before storing it
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        admin.password_hash = hashed_password
        updates_made = True

    if not updates_made:
        return {'error': 'No fields to update'}, 400

    db.session.commit()

    return {
        'message': 'Admin profile updated successfully',
        'admin': admin.to_dict()
    }, 200


def get_admin_stats():
    """
    Return platform-wide totals for the admin dashboard:
    total users, companies, jobs, applications, and pending company count.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    total_users = User.query.count()
    total_companies = Company.query.count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()
    pending_companies = Company.query.filter_by(status='pending').count()

    return {
        'stats': {
            'total_users': total_users,
            'total_companies': total_companies,
            'total_jobs': total_jobs,
            'total_applications': total_applications,
            'pending_companies': pending_companies
        }
    }, 200


def get_users(page: int = 1, per_page: int = 10, search: str = None):
    """
    Return a combined, paginated list of all users and companies for the admin user directory.
    Both types are merged into one list and sorted from newest to oldest.

    Args:
        page (int): Page number starting at 1.
        per_page (int): How many items to return per page.
        search (str, optional): Filter by name or email (case-insensitive).

    Returns:
        tuple: (response_dict, http_status_code)
    """
    page = max(1, int(page or 1))
    per_page = max(1, int(per_page or 10))

    # Fetch matching users (job seekers)
    u_q = User.query
    if search:
        term = f"%{search}%"
        u_q = u_q.filter((User.name.ilike(term)) | (User.email.ilike(term)))
    users = [
        {
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'role': 'Job Seeker',
            'type': 'user',
            'is_active': bool(u.is_active),
            'created_at': u.created_at.isoformat() if u.created_at else None
        }
        for u in u_q.all()
    ]

    # Fetch matching companies (employers)
    c_q = Company.query
    if search:
        term = f"%{search}%"
        c_q = c_q.filter((Company.company_name.ilike(term)) | (Company.email.ilike(term)))
    companies = [
        {
            'id': c.id,
            'name': c.company_name,
            'email': c.email,
            'role': 'Employer',
            'type': 'company',
            'is_active': bool(c.is_active),
            'created_at': c.created_at.isoformat() if c.created_at else None
        }
        for c in c_q.all()
    ]

    # Merge both lists and sort newest first
    combined = users + companies
    combined.sort(key=lambda x: x.get('created_at') or '', reverse=True)

    total = len(combined)
    start = (page - 1) * per_page
    end = start + per_page
    page_items = combined[start:end]

    return {
        'users': page_items,
        'total': total,
        'page': page,
        'per_page': per_page
    }, 200


def create_admin(name: str, email: str, password: str):
    """
    Create a new admin account. Only existing admins can trigger this action.

    Args:
        name (str): Admin display name.
        email (str): Admin login email.
        password (str): Plain text password (will be hashed before saving).

    Returns:
        tuple: (response_dict, http_status_code)
    """
    name = (name or '').strip()
    email = (email or '').strip().lower()
    password = password or ''

    if not name or not email or not password:
        return {'error': 'Name, email, and password are required fields'}, 400

    existing = Admin.query.filter_by(email=email).first()
    if existing:
        return {'error': 'Email is already registered'}, 409

    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    admin = Admin(name=name, email=email, password_hash=hashed)
    db.session.add(admin)
    db.session.commit()

    return {'message': 'Admin account created', 'admin': admin.to_dict()}, 201


def revoke_user(user_id: int):
    """
    Suspend a user account by setting is_active to False.
    The user's data stays in the database; they just cannot log in anymore.
    """
    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'User not found'}, 404
    user.is_active = False
    db.session.commit()
    return {'message': 'User revoked', 'user': user.to_dict()}, 200


def restore_user(user_id: int):
    """Reinstate a previously suspended user account so they can log in again."""
    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'User not found'}, 404
    user.is_active = True
    db.session.commit()
    return {'message': 'User restored', 'user': user.to_dict()}, 200


def revoke_company(company_id: int):
    """
    Suspend a company account by setting is_active to False.
    The company cannot log in or post jobs, but their data is not deleted.
    """
    company = db.session.get(Company, company_id)
    if not company:
        return {'error': 'Company not found'}, 404
    company.is_active = False
    db.session.commit()
    return {'message': 'Company revoked', 'company': company.to_dict()}, 200


def restore_company(company_id: int):
    """Reinstate a previously suspended company account so they can log in again."""
    company = db.session.get(Company, company_id)
    if not company:
        return {'error': 'Company not found'}, 404
    company.is_active = True
    db.session.commit()
    return {'message': 'Company restored', 'company': company.to_dict()}, 200
