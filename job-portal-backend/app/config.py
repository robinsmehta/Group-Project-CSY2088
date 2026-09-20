# app/config.py — Configuration Classes
#
# Defines settings for the Flask application.
# Sensitive values (like database credentials) are loaded from environment variables (.env file).

import os
import urllib.parse
from dotenv import load_dotenv

# Load variables from .env file into os.environ
load_dotenv()


class Config:
    """
    Base configuration class. Shared settings across all environments.
    """

    # Secret key for session cookies and token signing
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')

    # Session Cookie Configuration
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True   # Prevents JavaScript access to session cookies
    SESSION_COOKIE_SECURE = False    # Local HTTP development does not use HTTPS

    # Database Credentials
    DB_USER     = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST     = os.environ.get('DB_HOST', 'localhost')
    DB_PORT     = os.environ.get('DB_PORT', '3306')
    DB_NAME     = os.environ.get('DB_NAME', 'job_portal')

    # Database Connection URI Format: mysql+pymysql://<user>:<password>@<host>:<port>/<db_name>
    _encoded_password = urllib.parse.quote_plus(DB_PASSWORD) if DB_PASSWORD else ''
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{_encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Disable modification tracking system to conserve memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File Upload Settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB limit


class DevelopmentConfig(Config):
    """Development configuration with debug mode enabled."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration with debug mode disabled."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration using an in-memory SQLite database."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Config mapping dictionary used by create_app()
config_by_name = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
    'default':     DevelopmentConfig,
}
