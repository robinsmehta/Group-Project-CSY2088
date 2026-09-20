# app/__init__.py — Flask Application Factory
#
# Creates and configures the Flask application instance using the Application Factory pattern.

import os
from flask import Flask, jsonify, send_from_directory
from sqlalchemy import text
from .config import config_by_name
from .extensions import db, bcrypt, migrate, cors


def create_app(config_name: str = None) -> Flask:
    """
    Application Factory Function.

    Args:
        config_name (str): One of 'development', 'production', or 'testing'.
                           If not provided, reads FLASK_ENV from environment.

    Returns:
        Flask: A fully configured Flask application instance.
    """

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # 1. Load Configuration
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # 2. Ensure the uploads folder exists
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # 3. Initialise Extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, supports_credentials=True, resources={
        r"/api/*": {
            "origins": ["http://127.0.0.1:5001"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": True
        }
    })

    # 4. Serve static frontend assets from the same origin in local development
    frontend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'job-portal-frontend'))

    @app.route('/', defaults={'path': ''}, methods=['GET'])
    @app.route('/<path:path>', methods=['GET'])
    def serve_frontend(path):
        """
        Serves HTML pages and static files (CSS, JS) from the job-portal-frontend directory.
        Falls back to index.html for non-API frontend routing.
        """
        if path.startswith('api/') or path == 'api':
            return jsonify({'error': 'Not Found'}), 404

        safe_path = path or 'index.html'
        full_path = os.path.join(frontend_root, safe_path)

        if os.path.isdir(full_path):
            full_path = os.path.join(full_path, 'index.html')

        if os.path.exists(full_path):
            relative_path = os.path.relpath(full_path, frontend_root).replace(os.sep, '/')
            return send_from_directory(frontend_root, relative_path)

        return send_from_directory(frontend_root, 'index.html')

    # 5. Register Blueprints (Route Groups)
    from .routes.auth_routes        import auth_bp
    from .routes.job_routes         import job_bp
    from .routes.application_routes import application_bp
    from .routes.admin_routes       import admin_bp

    app.register_blueprint(auth_bp,        url_prefix='/api/auth')
    app.register_blueprint(job_bp,         url_prefix='/api/jobs')
    app.register_blueprint(application_bp, url_prefix='/api/applications')
    app.register_blueprint(admin_bp,       url_prefix='/api/admin')

    # 6. Import all models so Flask-Migrate & db.create_all() detect them
    from .models import user, company, job, application, admin  # noqa: F401

    # 7. Database Health-Check & Test Routes
    from .utils.decorators import role_required

    @app.route('/api/company/test', methods=['GET'])
    @role_required('company')
    def company_test_route():
        """Protected test endpoint for verifying company role authorization."""
        from flask import session
        return jsonify({
            'message': 'Access granted: Company protected route test successful',
            'company_id': session.get('user_id'),
            'role': session.get('role'),
            'approval_status': session.get('status')
        }), 200

    @app.route('/api/session/debug', methods=['GET'])
    def session_debug():
        """Debugging endpoint that returns current session contents."""
        from flask import session
        return jsonify({
            'session_data': dict(session),
            'user_id': session.get('user_id'),
            'role': session.get('role'),
            'company_id': session.get('company_id'),
            'status': session.get('status')
        }), 200

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """
        Database & API Health Check Endpoint.

        Queries the database to verify connectivity.
        Returns 200 OK if connected, or 500 Error if connection fails.
        """
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({
                "status": "ok",
                "database": "connected",
                "message": "Flask server and MySQL database are successfully connected!"
            }), 200
        except Exception as e:
            return jsonify({
                "status": "error",
                "database": "disconnected",
                "error": str(e),
                "message": "Failed to connect to MySQL database. Check your .env settings and ensure MySQL server is running."
            }), 500

    # 8. Register Flask CLI Commands
    @app.cli.command("init-db")
    def init_db_command():
        """Flask CLI command to initialize database tables: flask init-db"""
        from init_db import init_database
        init_database()

    return app
