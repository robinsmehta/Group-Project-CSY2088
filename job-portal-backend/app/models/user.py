# ============================================================
# app/models/user.py — User Model (Job Seeker)
#
# This file defines the User database table using SQLAlchemy ORM.
# Instead of writing SQL like "CREATE TABLE users (...)",
# we write a Python class and SQLAlchemy translates it to SQL.
#
# Table name: users
# Who uses this table: Job seekers who register on the platform.
# ============================================================

from datetime import datetime, timezone
from app.extensions import db  # Import the shared SQLAlchemy instance


class User(db.Model):
    """
    Represents a job-seeking user in the system.

    Relationships:
      - A User can have MANY Applications (one-to-many).
        Access via: user_instance.applications  →  list of Application objects
    """

    # Tell SQLAlchemy which table in MySQL to map this class to
    __tablename__ = 'users'

    # --- Columns ---

    # Primary Key: unique integer auto-incremented by MySQL for every new row
    id = db.Column(db.Integer, primary_key=True)

    # Full name of the user (e.g., "Jane Doe")
    # nullable=False means this field is REQUIRED — the DB will reject a row without it
    name = db.Column(db.String(100), nullable=False)

    # Email address — must be unique across all users (used as login identifier)
    email = db.Column(db.String(150), unique=True, nullable=False)

    # Hashed password — NEVER store plain text passwords!
    # bcrypt.generate_password_hash() will produce a string like '$2b$12$...'
    # that gets stored here. See auth_service.py for hashing logic.
    password_hash = db.Column(db.String(255), nullable=False)

    # Timestamp of when this user account was created.
    # default=lambda: datetime.now(timezone.utc) automatically fills this in
    # when a new User is inserted — you don't have to set it manually.
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Active flag for suspension (admins can revoke access without deleting)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # --- Relationships ---

    # One User → Many Applications
    # back_populates='user' creates a reverse link: application.user → User object
    # cascade='all, delete-orphan' ensures deleting a User automatically deletes all their Applications
    # lazy='dynamic' means applications aren't loaded from DB until you access this attribute
    applications = db.relationship(
        'Application',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    # --- Helper Methods ---

    def __repr__(self):
        """
        Developer-friendly string representation.
        Makes debugging easier — when you print a User object you'll see:
        <User id=1 email=jane@example.com>
        """
        return f'<User id={self.id} email={self.email}>'

    def to_dict(self):
        """
        Converts this User object into a plain Python dictionary
        so it can be serialised to JSON and returned in API responses.

        NOTE: We deliberately exclude password_hash — never send it to the client!
        """
        return {
            'id':         self.id,
            'name':       self.name,
            'email':      self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active':  bool(self.is_active)
        }
