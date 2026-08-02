# ============================================================
# app/services/admin_service.py — Admin Business Logic
#
# This is the BUSINESS LOGIC LAYER for admin operations.
# Called by routes in admin_routes.py.
#
# SECURITY & ROLE PRIVILEGE NOTICE:
# Admin actions are the most destructive operations in the system.
# Admins can permanently delete user accounts, company profiles, and
# job listings, as well as authorize pending company accounts to access
# the employer portal.
#
# Therefore, strictly enforcing @role_required('admin') on all admin
# endpoints is CRITICAL to prevent privilege escalation, unauthorized
# data deletion, and unapproved company activations.
#
# DATA INTEGRITY & CASCADE BEHAVIOR:
# Cascading deletes are implemented via SQLAlchemy model relationships
# (cascade="all, delete-orphan") to guarantee relational data integrity.
# Hard-deleting parent entities (Company, Job, User) automatically cleans
# up all associated child records (Jobs, Applications) in MySQL, ensuring
# zero orphaned rows remain in the database.
# ============================================================

from app.extensions import db
from app.models.user import User
from app.models.company import Company
from app.models.job import Job
from app.models.application import Application


def get_pending_companies():
    """
    Retrieve all companies with status = 'pending'.

    Returns:
        tuple: (response_dict, http_status_code)
               200 OK with list of pending company dicts (including name, email, description, created_at).
    """
    pending_companies = Company.query.filter_by(status='pending').all()
    companies_data = [company.to_dict() for company in pending_companies]

    return {'companies': companies_data}, 200


def approve_company(company_id: int):
    """
    Approve a pending company account.

    Args:
        company_id (int): The ID of the company to approve.

    Returns:
        tuple: (response_dict, http_status_code)
               200 OK on success, 404 Not Found if company doesn't exist.
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
    Reject a pending company account.

    Args:
        company_id (int): The ID of the company to reject.

    Returns:
        tuple: (response_dict, http_status_code)
               200 OK on success, 404 Not Found if company doesn't exist.
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
    Helper function to update company status to either 'approved' or 'rejected'.

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
    Admin: Permanently delete any job listing by ID.

    CASCADE DECISION & EXPLANATION:
    When a Job is deleted, all Applications associated with that job are also
    automatically deleted via SQLAlchemy's `cascade="all, delete-orphan"` defined
    on the `Job.applications` relationship.
    
    Why: An application to a deleted job has no target listing or context, making
    it useless historical noise. Deleting related applications ensures data integrity
    and prevents orphaned foreign key references in the `applications` table.

    Args:
        job_id (int): The ID of the job to delete.

    Returns:
        tuple: (response_dict, http_status_code)
               200 OK on success, 404 Not Found if job doesn't exist.
    """
    job = db.session.get(Job, job_id)
    if not job:
        return {'error': 'Job not found'}, 404

    db.session.delete(job)
    db.session.commit()

    return {'message': 'Job deleted successfully'}, 200


def delete_user(user_id: int):
    """
    Admin: Permanently delete a user (job seeker) account by ID.

    CASCADE DECISION & EXPLANATION:
    When a User is deleted, all job Applications submitted by that user are also
    automatically deleted via SQLAlchemy's `cascade="all, delete-orphan"` defined
    on the `User.applications` relationship.

    Why: An application without an applicant user record is invalid and would break
    employer application review workflows. Deleting related applications preserves
    database referential integrity.

    Args:
        user_id (int): The ID of the user to delete.

    Returns:
        tuple: (response_dict, http_status_code)
               200 OK on success, 404 Not Found if user doesn't exist.
    """
    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'User not found'}, 404

    db.session.delete(user)
    db.session.commit()

    return {'message': 'User deleted successfully'}, 200


def delete_company(company_id: int):
    """
    Admin: Permanently delete a company account by ID.

    CASCADE DECISION & EXPLANATION:
    When a Company is deleted, all Jobs posted by that company AND all Applications
    submitted for those jobs are automatically deleted. This cascade is handled by
    SQLAlchemy's `cascade="all, delete-orphan"` on `Company.jobs`, which in turn cascades
    to `Job.applications`.

    Why: If a company account is deleted (e.g., fraudulent employer), all their active
    job postings and candidate applications lose their organizational context.
    Cascading deletes across all 3 levels cleans up all related records cleanly.

    Args:
        company_id (int): The ID of the company to delete.

    Returns:
        tuple: (response_dict, http_status_code)
               200 OK on success, 404 Not Found if company doesn't exist.
    """
    company = db.session.get(Company, company_id)
    if not company:
        return {'error': 'Company not found'}, 404

    db.session.delete(company)
    db.session.commit()

    return {'message': 'Company deleted successfully'}, 200


def get_admin_stats():
    """
    Get platform statistics for admin dashboard.

    Returns:
        tuple: (response_dict, http_status_code)
               200 OK with stats including total users, companies, jobs, applications
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
