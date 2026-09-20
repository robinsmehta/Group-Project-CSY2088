# app/models/user.py — User Model (Job Seeker)
#
# Defines the User database table using SQLAlchemy ORM.
# Table name: users
# Represents job seekers who register on the platform.

from datetime import datetime, timezone
from app.extensions import db


def _to_utc_iso(dt):
    """Convert a datetime object to UTC ISO format string (YYYY-MM-DDTHH:MM:SSZ)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat().replace('+00:00', 'Z')


class User(db.Model):
    """
    Represents a job-seeking user in the system.

    Relationships:
      - A User can have many job Applications (one-to-many).
    """

    __tablename__ = 'users'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Full name of the user
    name = db.Column(db.String(100), nullable=False)

    # Unique email address used as login identifier
    email = db.Column(db.String(150), unique=True, nullable=False)

    # Hashed password (never store plain text passwords)
    password_hash = db.Column(db.String(255), nullable=False)

    # Timestamp when account was created
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Active flag for suspension (admins can suspend access without deleting)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Job seeker skills (comma-separated, e.g. "React, Python, SQL")
    skills = db.Column(db.String(500), nullable=True)

    # Relationships
    applications = db.relationship(
        'Application',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    def __repr__(self):
        """String representation for debugging."""
        return f'<User id={self.id} email={self.email}>'

    def to_dict(self):
        """
        Converts the User object into a Python dictionary for JSON responses.
        Excludes sensitive fields like password_hash.
        """
        return {
            'id':         self.id,
            'name':       self.name,
            'email':      self.email,
            'skills':     self.skills,
            'created_at': _to_utc_iso(self.created_at),
            'is_active':  bool(self.is_active)
        }
