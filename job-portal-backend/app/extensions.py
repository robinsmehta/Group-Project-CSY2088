# app/extensions.py — Flask Extension Instances
#
# Extension objects are created here (without an app context) to prevent circular imports.
# They are bound to the Flask application inside create_app() in app/__init__.py.

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_cors import CORS

# SQLAlchemy ORM for database operations
db = SQLAlchemy()

# Bcrypt for secure password hashing
bcrypt = Bcrypt()

# Flask-Migrate for database migrations
migrate = Migrate()

# Flask-CORS for handling cross-origin requests from the frontend
cors = CORS()
