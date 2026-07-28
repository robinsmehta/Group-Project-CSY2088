# ============================================================
# app/services/admin_service.py — Admin Business Logic
#
# This is the BUSINESS LOGIC LAYER for admin operations.
# Called by routes in admin_routes.py.
#
# Responsibilities:
#   - Retrieve pending companies for review
#   - Change company approval status (approve/reject)
#   - Hard-delete users, companies, and jobs from the database
# ============================================================

from app.extensions import db
from app.models.user    import User
from app.models.company import Company
from app.models.job     import Job


def get_pending_companies():
    """
    Retrieve all companies with status = 'pending'.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Query the database for pending companies
    # pending = Company.query.filter_by(status='pending').all()
    # return {'companies': [c.to_dict() for c in pending]}, 200

    return {'message': 'get_pending_companies service stub — not yet implemented'}, 200


def update_company_status(company_id: int, new_status: str):
    """
    Approve or reject a company by changing its status field.

    Args:
        company_id (int): The company to update.
        new_status (str): Either 'approved' or 'rejected'.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Find the company (404 if not found)
    # company = Company.query.get(company_id)
    # if not company:
    #     return {'error': 'Company not found'}, 404

    # TODO: Update status and commit
    # company.status = new_status
    # db.session.commit()

    # TODO: Optionally send an email notification to the company
    # send_status_email(company.email, new_status)  ← implement email sending later

    # return {'message': f'Company {new_status}', 'company': company.to_dict()}, 200

    return {'message': f'update_company_status({company_id}, {new_status}) stub — not yet implemented'}, 200


def delete_job(job_id: int):
    """
    Admin: delete any job listing by ID.

    Args:
        job_id (int): The job to delete.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Find the job (404 if missing)
    # job = Job.query.get(job_id)
    # if not job:
    #     return {'error': 'Job not found'}, 404

    # TODO: Delete and commit (cascade removes applications too)
    # db.session.delete(job)
    # db.session.commit()
    # return {'message': 'Job deleted by admin'}, 200

    return {'message': f'admin delete_job({job_id}) stub — not yet implemented'}, 200


def delete_user(user_id: int):
    """
    Admin: delete a user account by ID.

    Args:
        user_id (int): The user to delete.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Find the user (404 if missing)
    # user = User.query.get(user_id)
    # if not user:
    #     return {'error': 'User not found'}, 404

    # TODO: Delete and commit (cascade removes their applications too)
    # db.session.delete(user)
    # db.session.commit()
    # return {'message': 'User deleted by admin'}, 200

    return {'message': f'admin delete_user({user_id}) stub — not yet implemented'}, 200


def delete_company(company_id: int):
    """
    Admin: delete a company account by ID.

    Args:
        company_id (int): The company to delete.

    Returns:
        tuple: (response_dict, http_status_code)
    """
    # TODO: Find the company (404 if missing)
    # company = Company.query.get(company_id)
    # if not company:
    #     return {'error': 'Company not found'}, 404

    # TODO: Delete and commit (cascade removes all their jobs and applications too)
    # db.session.delete(company)
    # db.session.commit()
    # return {'message': 'Company deleted by admin'}, 200

    return {'message': f'admin delete_company({company_id}) stub — not yet implemented'}, 200
