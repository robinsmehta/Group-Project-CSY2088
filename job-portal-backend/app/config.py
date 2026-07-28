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
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-dev-secret-change-this')

    # --- Database ---
    # Build the SQLAlchemy connection URI from individual env variables.
    # Format: mysql+pymysql://user:password@host:port/database_name
    # pymysql is the driver that actually speaks to MySQL.
    DB_USER     = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST     = os.environ.get('DB_HOST', 'localhost')
    DB_PORT     = os.environ.get('DB_PORT', '3306')
    DB_NAME     = os.environ.get('DB_NAME', 'job_portal_db')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Disable SQLAlchemy's event system for object modifications (saves memory).
    # Set to True only if you need to track every change to model objects.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- File Uploads ---
    # Where uploaded résumé files will be stored on the server's filesystem.
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')

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
