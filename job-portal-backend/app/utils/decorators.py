# ============================================================
# app/utils/decorators.py — Custom Route Decorators
#
# A DECORATOR is a function that wraps another function to add
# behaviour before or after it runs — without changing its code.
#
# In Flask, decorators are applied to route handler functions
# using the @ syntax, e.g.:
#
#   @auth_bp.route('/company/test')
#   @role_required('company')
#   def company_test_route():
#       ...
# ============================================================

from functools import wraps
from flask import session, jsonify


def role_required(role: str):
    """
    Route protection decorator factory.

    Checks:
      1. Is there an active session? (user_id and role present in session)
      2. Does the session role match the required role argument?

    Returns:
      - 401 Unauthorized: If no active login session exists
      - 403 Forbidden: If logged-in user lacks the required role
      - Route Handler Result: If authentication and authorization checks pass
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # ------------------------------------------------
            # Step 1: Check if the user is logged in (active session)
            # ------------------------------------------------
            # When a user logs in, auth_service sets session['user_id'] and session['role'].
            # If these session keys are missing, the user has not authenticated.
            user_id = session.get('user_id')
            user_role = session.get('role')

            if not user_id or not user_role:
                return jsonify({
                    'error': 'Authentication required. Please log in to access this resource.'
                }), 401

            # ------------------------------------------------
            # Step 2: Check if the user has the required role
            # ------------------------------------------------
            # Even if authenticated, a job seeker ('user') should not access company or admin endpoints.
            # Compare current session role against the required decorator parameter.
            if user_role != role:
                return jsonify({
                    'error': f'Access denied. Required role: {role}, your role: {user_role}'
                }), 403

            # ------------------------------------------------
            # Step 3: Allow the request to proceed to the route handler
            # ------------------------------------------------
            # Both authentication and authorization checks passed cleanly.
            return f(*args, **kwargs)

        return decorated_function
    return decorator
