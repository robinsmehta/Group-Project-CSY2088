import pytest
from app import create_app
from app.extensions import db as _db
from app.models.company import Company
from app.models.user import User
from flask_bcrypt import generate_password_hash


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app_instance = create_app('testing')
    app_instance.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test_secret_key',
        'WTF_CSRF_ENABLED': False,
    })

    with app_instance.app_context():
        _db.create_all()
        yield app_instance
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Provide database instance with active context."""
    return _db


@pytest.fixture
def approved_company(app, db):
    """Helper fixture to create an approved company record."""
    hashed_pwd = generate_password_hash('password123').decode('utf-8')
    company = Company(
        company_name='Acme Corp',
        email='hr@acme.com',
        password_hash=hashed_pwd,
        description='Leading tech company',
        status='approved'
    )
    db.session.add(company)
    db.session.commit()
    return company


@pytest.fixture
def job_seeker(app, db):
    """Helper fixture to create a job seeker user record."""
    hashed_pwd = generate_password_hash('password123').decode('utf-8')
    user = User(
        name='Jane Doe',
        email='jane@example.com',
        password_hash=hashed_pwd
    )
    db.session.add(user)
    db.session.commit()
    return user
