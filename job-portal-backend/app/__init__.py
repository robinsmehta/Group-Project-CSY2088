# ============================================================
# app/__init__.py — Flask Application Factory
#
# This file is the heart of the application. It defines the
# create_app() function, which:
#   1. Creates a Flask app instance
#   2. Loads configuration (from config.py)
#   3. Initialises all extensions (db, bcrypt, cors, migrate)
#   4. Registers all Blueprints (route groups)
#
# WHY a factory function?
#   - Makes testing easier (you can create multiple app instances)
#   - Avoids circular imports (extensions are created before the app)
#   - Follows Flask best practices for larger projects
# ============================================================

import os
from flask import Flask
from .config import config_by_name
from .extensions import db, bcrypt, migrate, cors


def create_app(config_name: str = None) -> Flask:
    """
    Application Factory Function.

    Args:
        config_name (str): One of 'development', 'production', or 'default'.
                           If not provided, reads FLASK_ENV from environment.

    Returns:
        Flask: A fully configured Flask application instance.
    """

    # If no config name given, read FLASK_ENV from environment (default: 'development')
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    # Create the Flask application instance.
    # __name__ tells Flask where to find templates and static files.
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # --------------------------------------------------------
    # 1. Load Configuration
    # --------------------------------------------------------
    # Apply the matching config class (DevelopmentConfig or ProductionConfig)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # --------------------------------------------------------
    # 2. Ensure the uploads folder exists
    # --------------------------------------------------------
    # Flask won't create this directory automatically — we do it here.
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # --------------------------------------------------------
    # 3. Initialise Extensions
    # --------------------------------------------------------
    # init_app() binds each extension to this specific app instance.
    db.init_app(app)                    # Connect SQLAlchemy to the app + DB
    bcrypt.init_app(app)                # Attach Bcrypt for password hashing
    migrate.init_app(app, db)           # Attach Flask-Migrate (needs both app and db)
    cors.init_app(app, resources={      # Allow all origins on all /api/* routes
        r"/api/*": {"origins": "*"}     # TODO: In production, restrict to your frontend domain
    })

    # --------------------------------------------------------
    # 4. Register Blueprints (Route Groups)
    # --------------------------------------------------------
    # Each Blueprint is a group of related routes defined in a separate file.
    # We import them here (inside the function) to avoid circular imports.
    from .routes.auth_routes        import auth_bp
    from .routes.job_routes         import job_bp
    from .routes.application_routes import application_bp
    from .routes.admin_routes       import admin_bp

    # Register each blueprint with a URL prefix.
    # All auth routes will start with /api/auth/...
    app.register_blueprint(auth_bp,        url_prefix='/api/auth')
    app.register_blueprint(job_bp,         url_prefix='/api/jobs')
    app.register_blueprint(application_bp, url_prefix='/api/applications')
    app.register_blueprint(admin_bp,       url_prefix='/api/admin')

    # --------------------------------------------------------
    # 5. Import all models so Flask-Migrate can detect them
    # --------------------------------------------------------
    # Even though we don't use the models directly here,
    # SQLAlchemy needs to "see" them before it can create/migrate tables.
    from .models import user, company, job, application, admin  # noqa: F401

    # --------------------------------------------------------
    # 6. Simple health-check route
    # --------------------------------------------------------
    @app.route('/api/health')
    def health_check():
        """
        Health Check Endpoint.
        GET /api/health
        Returns a simple JSON response to confirm the server is running.
        Useful for testing that the server started correctly.
        """
        return {'status': 'ok', 'message': 'Job Portal API is running'}, 200

    return app
