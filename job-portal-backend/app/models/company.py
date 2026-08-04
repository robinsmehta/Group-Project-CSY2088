# ============================================================
# app/models/company.py — Company Model (Employer)
#
# This file defines the Company database table using SQLAlchemy ORM.
#
# Table name: companies
# Who uses this table: Employers/companies that post job listings.
#
# Companies must be APPROVED by an admin before they can post jobs.
# New companies default to "pending" status.
# ============================================================

from datetime import datetime, timezone
from app.extensions import db


class Company(db.Model):
    """
    Represents an employer/company in the system.

    Relationships:
      - A Company can post MANY Jobs (one-to-many).
        Access via: company_instance.jobs  →  list of Job objects
    """

    __tablename__ = 'companies'

    # --- Columns ---

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # The official name of the company (e.g., "Google LLC")
    company_name = db.Column(db.String(150), nullable=False)

    # Email used for login and contact — must be unique
    email = db.Column(db.String(150), unique=True, nullable=False)

    # Hashed password for company account login
    # TODO (auth_service.py): Hash with bcrypt before saving
    password_hash = db.Column(db.String(255), nullable=False)

    # Optional: a paragraph describing the company, its mission, size, etc.
    # Text (vs String) allows longer content without a fixed character limit
    description = db.Column(db.Text, nullable=True)

    # Approval status — set by an Admin.
    # Possible values (enforced by MySQL ENUM): 'pending', 'approved', 'rejected'
    # New companies start as 'pending' and cannot post jobs until an admin approves them.
    status = db.Column(
        db.Enum('pending', 'approved', 'rejected', name='company_status_enum'),
        default='pending',
        nullable=False
    )

    # Timestamp when the company account was registered
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Active flag separate from `status` (approved/pending/rejected)
    # `is_active` allows admins to suspend an otherwise-approved company.
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # --- Relationships ---

    # One Company → Many Jobs
    # cascade='all, delete-orphan' means: if a Company is deleted from the DB,
    # all its Jobs are also automatically deleted (no orphaned job records).
    jobs = db.relationship(
        'Job',
        back_populates='company',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    # --- Helper Methods ---

    def __repr__(self):
        return f'<Company id={self.id} name={self.company_name} status={self.status}>'

    def to_dict(self):
        """Serialise to dict for JSON API responses. Excludes password_hash."""
        return {
            'id':           self.id,
            'company_name': self.company_name,
            'email':        self.email,
            'description':  self.description,
            'status':       self.status,
            'created_at':   self.created_at.isoformat() if self.created_at else None,
            'is_active':    bool(self.is_active)
        }
