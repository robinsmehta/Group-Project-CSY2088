# ============================================================
# app/utils/decorators.py — Custom Route Decorators
#
# A DECORATOR is a function that wraps another function to add
# behaviour before or after it runs — without changing its code.
#
# In Flask, decorators are applied to route handler functions
# using the @ syntax, e.g.:
#
#   @app.route('/protected')
#   @role_required('admin')
#   def protected_route():
#       ...
#
# The role_required decorator below will (once implemented) check
# that the current user has the correct role before allowing the
# route handler to execute. If not, it returns a 401/403 response.
# ============================================================

from functools import wraps
from flask import jsonify  # , session  ← Uncomment when implementing


def role_required(role: str):
    """
    Route protection decorator factory.

    Usage:
        @role_required('user')       ← only logged-in users can access
        @role_required('company')    ← only logged-in companies can access
        @role_required('admin')      ← only logged-in admins can access

    Args:
        role (str): The required role. Must be 'user', 'company', or 'admin'.

    Returns:
        A decorator function that wraps the route handler.

    How it will work (once implemented):
        1. Check if there is an active session (i.e., someone is logged in).
        2. Check if session['role'] matches the required role.
        3. If yes → allow the route handler to run normally.
        4. If no session → return 401 Unauthorized ("You must be logged in").
        5. If wrong role → return 403 Forbidden ("You don't have permission").
    """

    def decorator(f):
        """
        The actual decorator returned by role_required(role).
        @wraps(f) preserves the original function's name and docstring —
        important for Flask to correctly identify route handlers.
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            """
            This inner function runs BEFORE the route handler every time
            the endpoint is called.
            """

            # ------------------------------------------------
            # TODO: Step 1 — Check if the user is logged in
            # ------------------------------------------------
            # We store login state in the Flask session dictionary.
            # If 'role' is not in the session, nobody is logged in.
            #
            # from flask import session
            # if 'role' not in session:
            #     return jsonify({'error': 'Authentication required. Please log in.'}), 401

            # ------------------------------------------------
            # TODO: Step 2 — Check if the user has the right role
            # ------------------------------------------------
            # Even if logged in, the role must match what this route requires.
            #
            # if session.get('role') != role:
            #     return jsonify({
            #         'error': f'Access denied. This endpoint requires role: {role}'
            #     }), 403

            # ------------------------------------------------
            # TODO: Step 3 — Allow the request to proceed
            # ------------------------------------------------
            # If we passed both checks above, call the original route handler.
            # *args and **kwargs pass through any URL parameters (e.g. job_id).
            #
            # return f(*args, **kwargs)

            # ------------------------------------------------
            # Temporary: pass-through (no protection yet)
            # Remove this line once you implement the TODOs above!
            # ------------------------------------------------
            return f(*args, **kwargs)

        return decorated_function
    return decorator
