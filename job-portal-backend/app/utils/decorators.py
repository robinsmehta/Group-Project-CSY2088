# app/utils/decorators.py — Custom Route Decorators
#
# A decorator wraps a route handler function to run security checks
# before executing the actual route logic.
#
# In Flask, decorators are applied to route functions using the @ syntax, e.g.:
#   @auth_bp.route('/company/test')
#   @role_required('company')
#   def company_test_route():
#       ...

from functools import wraps
from flask import session, jsonify
from app.extensions import db
from app.models.user import User
from app.models.company import Company


def role_required(role: str):
    """
    Route protection decorator factory.

    Checks:
      1. Is there an active session? (user_id and role present in session)
      2. Does the session role match the required role argument?
      3. Is the account active (not suspended)?

    Returns:
      - 401 Unauthorized: If no active login session exists
      - 403 Forbidden: If logged-in user lacks the required role or account is suspended
      - Route Handler Result: If authentication and authorization checks pass
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Step 1: Check if the user is logged in
            user_id = session.get('user_id')
            user_role = session.get('role')

            if not user_id or not user_role:
                return jsonify({
                    'error': 'Authentication required. Please log in to access this resource.'
                }), 401

            # Step 2: Check if the user has the required role
            if user_role != role:
                return jsonify({
                    'error': f'Access denied. Required role: {role}, your role: {user_role}'
                }), 403

            # Step 3: Check that the account is still active (not suspended)
            if user_role == 'user':
                u = db.session.get(User, user_id)
                if u and getattr(u, 'is_active', True) is False:
                    return jsonify({'error': 'Account suspended'}), 403
            elif user_role == 'company':
                c = db.session.get(Company, user_id)
                if c and getattr(c, 'is_active', True) is False:
                    return jsonify({'error': 'Company account suspended'}), 403

            # Step 4: Allow the request to proceed to the route handler
            return f(*args, **kwargs)

        return decorated_function
    return decorator
