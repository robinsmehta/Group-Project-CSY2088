# app/models/job.py — Job Model
#
# Defines the Job database table using SQLAlchemy ORM.
# Table name: jobs
# Companies post job listings; job seekers browse and apply.
#
# Each Job belongs to exactly one Company (via company_id Foreign Key).

from datetime import datetime, timezone
from app.extensions import db


def _to_utc_iso(dt):
    """Convert a datetime object to UTC ISO format string (YYYY-MM-DDTHH:MM:SSZ)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat().replace('+00:00', 'Z')


class Job(db.Model):
    """
    Represents a job listing posted by a company.

    Relationships:
      - Belongs to ONE Company (many-to-one).
      - Can have MANY Applications (one-to-many).
    """

    __tablename__ = 'jobs'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key linking this job to the company that posted it
    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id'),
        nullable=False
    )

    # Job title (e.g., "Senior Python Developer")
    title = db.Column(db.String(200), nullable=False)

    # Full job description
    description = db.Column(db.Text, nullable=False)

    # Job location (e.g., "London, UK" or "Remote")
    location = db.Column(db.String(150), nullable=False)

    # Job category (e.g., "Software Engineering", "Marketing", "Finance")
    category = db.Column(db.String(100), nullable=True)

    # Employment type (e.g., "Full-time", "Part-time", "Remote", "Contract")
    job_type = db.Column(db.String(50), nullable=True)

    # Expected salary
    salary = db.Column(db.String(100), nullable=True)

    # Comma-separated list of required skills (e.g., "React, Python, SQL")
    skills = db.Column(db.String(500), nullable=True)

    # Closing date for the job listing
    closing_date = db.Column(db.DateTime, nullable=True)

    # Status flag ('active' or 'closed')
    status = db.Column(db.String(20), nullable=False, default='active')

    # Creation timestamp
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Last edit timestamp
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    company = db.relationship('Company', back_populates='jobs')
    applications = db.relationship(
        'Application',
        back_populates='job',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    def __repr__(self):
        """String representation for debugging."""
        return f'<Job id={self.id} title="{self.title}" company_id={self.company_id}>'

    @property
    def is_closed(self):
        """Check if the job's closing date has passed."""
        if self.closing_date:
            closing = self.closing_date
            if closing.tzinfo is None:
                closing = closing.replace(tzinfo=timezone.utc)
            return closing <= datetime.now(timezone.utc)
        return False

    def to_dict(self):
        """Converts the Job object into a Python dictionary for JSON responses."""
        computed_status = 'closed' if self.is_closed else (self.status or 'active')

        return {
            'id':                self.id,
            'company_id':        self.company_id,
            'company_name':      self.company.company_name if self.company else None,
            'title':             self.title,
            'description':       self.description,
            'location':          self.location,
            'category':          self.category,
            'job_type':          self.job_type,
            'salary':            self.salary,
            'skills':            self.skills,
            'closing_date':      _to_utc_iso(self.closing_date),
            'status':            computed_status,
            'application_count': self.applications.count() if hasattr(self.applications, 'count') else len(self.applications),
            'created_at':        _to_utc_iso(self.created_at),
            'updated_at':        _to_utc_iso(self.updated_at),
        }
