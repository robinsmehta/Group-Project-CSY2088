# ============================================================
# run.py — Application Entry Point
#
# This is the file you run to START the Flask server.
# It imports the app factory from app/__init__.py and starts it.
#
# Usage:
#   python run.py
#   OR (with Flask CLI):
#   flask --app run run
# ============================================================

from app import create_app  # Import the factory function that builds our Flask app

# Create the Flask application using the factory pattern
app = create_app()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    # debug=True enables the auto-reloader and shows detailed error pages.
    # IMPORTANT: Set debug=False in production!
    app.run(debug=True, host='0.0.0.0', port=port)

