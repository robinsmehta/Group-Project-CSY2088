# ============================================================
# app/extensions.py — Flask Extension Instances
#
# We create extension objects HERE (outside of create_app) so
# that they can be imported anywhere in the codebase without
# causing circular imports.
#
# The pattern is:
#   1. Create the extension object here (not tied to any app yet)
#   2. In create_app() inside app/__init__.py, call extension.init_app(app)
#      to attach it to the actual Flask app instance.
#
# This is called the "Application Factory" pattern and is the
# recommended Flask project structure.
# ============================================================

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_cors import CORS

# --- SQLAlchemy (ORM) ---
# db is the main object we use to define models and query the database.
# Usage in models:  class User(db.Model): ...
# Usage in routes:  db.session.add(obj) / db.session.commit()
db = SQLAlchemy()

# --- Bcrypt (Password Hashing) ---
# bcrypt provides secure password hashing.
# Usage example (to be implemented in auth_service.py):
#   hashed = bcrypt.generate_password_hash(plain_password).decode('utf-8')
#   bcrypt.check_password_hash(hashed, plain_password)  # returns True/False
bcrypt = Bcrypt()

# --- Flask-Migrate (Database Migrations) ---
# migrate tracks changes to SQLAlchemy models and generates SQL scripts
# to update the database schema without losing existing data.
# Usage:
#   flask db init     → set up migrations folder (run once)
#   flask db migrate  → auto-generate a migration file from model changes
#   flask db upgrade  → apply pending migrations to the database
migrate = Migrate()

# --- Flask-CORS (Cross-Origin Resource Sharing) ---
# cors allows the React/Vue/HTML frontend (running on a different port)
# to make API requests to this Flask server.
# Without this, the browser will block the requests for security reasons.
cors = CORS()
