# app/models/company.py — Company Model (Employer)
#
# Defines the Company database table using SQLAlchemy ORM.
# Table name: companies
# Represents employers/companies that post job listings.
#
# Companies must be approved by an admin before posting jobs.
# New registrations default to "pending" status.

from datetime import datetime, timezone
from app.extensions import db


def _to_utc_iso(dt):
    """Convert a datetime object to UTC ISO format string (YYYY-MM-DDTHH:MM:SSZ)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat().replace('+00:00', 'Z')


class Company(db.Model):
    """
    Represents an employer/company in the system.

    Relationships:
      - A Company can post many Jobs (one-to-many).
    """

    __tablename__ = 'companies'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Official company name
    company_name = db.Column(db.String(150), nullable=False)

    # Unique email address used for login and notifications
    email = db.Column(db.String(150), unique=True, nullable=False)

    # Hashed password for authentication
    password_hash = db.Column(db.String(255), nullable=False)

    # Description of company, mission, etc.
    description = db.Column(db.Text, nullable=True)

    # Approval status: 'pending', 'approved', 'rejected'
    # New companies start as 'pending' and cannot post jobs until approved by an admin.
    status = db.Column(
        db.Enum('pending', 'approved', 'rejected', name='company_status_enum'),
        default='pending',
        nullable=False
    )

    # Timestamp when account was created
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Active flag (allows admins to suspend an approved company account)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    jobs = db.relationship(
        'Job',
        back_populates='company',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    def __repr__(self):
        """String representation for debugging."""
        return f'<Company id={self.id} name={self.company_name} status={self.status}>'

    def to_dict(self):
        """Converts the Company object into a Python dictionary for JSON responses."""
        return {
            'id':           self.id,
            'company_name': self.company_name,
            'email':        self.email,
            'description':  self.description,
            'status':       self.status,
            'created_at':   _to_utc_iso(self.created_at),
            'is_active':    bool(self.is_active)
        }
