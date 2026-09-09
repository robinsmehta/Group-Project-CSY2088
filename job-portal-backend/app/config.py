# ============================================================
# app/config.py — Configuration Classes
#
# This file defines all the settings for the Flask application.
# It reads sensitive values (like database password) from environment
# variables instead of hardcoding them — this is a security best practice.
#
# python-dotenv automatically loads these variables from the .env file.
# ============================================================

import os
from dotenv import load_dotenv

import urllib.parse

# Load variables from .env file into os.environ
load_dotenv()


class Config:
    """
    Base configuration class.
    All settings shared across environments go here.
    Specific environments (Dev, Prod) can override these below.
    """

    # --- Security ---
    # SECRET_KEY is used by Flask to sign session cookies and CSRF tokens.
    # If someone knows this key, they can forge session data — keep it secret!
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')

    # --- Session Cookie Configuration ---
    # In this project’s local dev flow the frontend is served from the same host/port
    # as the Flask app, so the session cookie can stay same-site and work over plain HTTP.
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True   # Prevents JavaScript access to session cookies (XSS protection)
    SESSION_COOKIE_SECURE = False    # Local HTTP development does not use HTTPS

    # --- Database Configuration ---
    # We read database connection details from environment variables (.env file).
    # This keeps credentials secure and allows different settings in dev vs. production.
    #
    # DB_USER: MySQL database username (default: 'root')
    # DB_PASSWORD: Password for your MySQL user account (default: empty string '')
    # DB_HOST: Hostname or IP where MySQL is running (default: 'localhost')
    # DB_PORT: Port number MySQL server listens on (default: '3306')
    # DB_NAME: Database name created in MySQL (default: 'job_portal')
    DB_USER     = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST     = os.environ.get('DB_HOST', 'localhost')
    DB_PORT     = os.environ.get('DB_PORT', '3306')
    DB_NAME     = os.environ.get('DB_NAME', 'job_portal')

    # --- Connection String Structure Explanation ---
    # SQLAlchemy requires a connection string (Database URI) to know how to connect.
    # Structure:  mysql+pymysql://<user>:<password>@<host>:<port>/<db_name>
    #
    # Breakdown:
    # 1. mysql+pymysql  -> Engine dialect (MySQL) + Python connector driver (PyMySQL).
    # 2. <user>:<password> -> Your MySQL authentication credentials.
    #                       (We use urllib.parse.quote_plus so special chars in passwords like '@' don't break the URL)
    # 3. @<host>:<port>  -> Location and network port of the MySQL database server.
    # 4. /<db_name>      -> The target database schema created in MySQL.
    _encoded_password = urllib.parse.quote_plus(DB_PASSWORD) if DB_PASSWORD else ''
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{_encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Disable SQLAlchemy's event system for object modifications (saves memory).
    # Set to True only if you need to track every change to model objects.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- File Uploads ---
    # Where uploaded résumé files will be stored on the server's filesystem.
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')

    # Allowed extensions for uploaded résumé files
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

    # Maximum file upload size — 10 MB (in bytes: 10 * 1024 * 1024).
    # Flask will reject uploads larger than this automatically.
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB


class DevelopmentConfig(Config):
    """
    Development-specific settings.
    Enables debug mode so Flask shows detailed error tracebacks.
    """
    DEBUG = True


class ProductionConfig(Config):
    """
    Production-specific settings.
    Debug MUST be False so error details are never exposed to users.
    """
    DEBUG = False


# ----------------------------------------------------------------
# Config selector dictionary.
# create_app() will use this to pick the right config class
# based on the FLASK_ENV environment variable.
# ----------------------------------------------------------------
config_by_name = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,  # fallback
}
