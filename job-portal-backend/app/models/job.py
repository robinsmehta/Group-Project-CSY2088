# ============================================================
# app/models/job.py — Job Model
#
# This file defines the Job database table using SQLAlchemy ORM.
#
# Table name: jobs
# Who uses this table: Companies post job listings; users browse and apply.
#
# Each Job must belong to exactly one Company (enforced by the FK constraint).
# ============================================================

from datetime import datetime, timezone
from app.extensions import db


class Job(db.Model):
    """
    Represents a job listing posted by a company.

    Relationships:
      - Belongs to ONE Company (many-to-one).
        Access via: job_instance.company  →  Company object
      - Can have MANY Applications (one-to-many).
        Access via: job_instance.applications  →  list of Application objects
    """

    __tablename__ = 'jobs'

    # --- Columns ---

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key: links this job to the company that posted it.
    # db.ForeignKey('companies.id') tells MySQL: company_id must exist in companies.id
    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id'),
        nullable=False
    )

    # Short job title (e.g., "Senior Python Developer")
    title = db.Column(db.String(200), nullable=False)

    # Full job description: responsibilities, requirements, etc.
    description = db.Column(db.Text, nullable=False)

    # Where the job is located (e.g., "London, UK" or "Remote")
    location = db.Column(db.String(150), nullable=False)

    # Job category (e.g., "Software Engineering", "Marketing", "Finance")
    # TODO: You could turn this into an ENUM or a separate table later
    category = db.Column(db.String(100), nullable=True)

    # Employment type (e.g., "Full-time", "Part-time", "Remote", "Contract", "Freelance")
    job_type = db.Column(db.String(50), nullable=True)

    # Expected salary (e.g., "£40,000 - £50,000 per year")
    # Stored as a string for flexibility (ranges, "Negotiable", etc.)
    salary = db.Column(db.String(100), nullable=True)

    # Optional closing date for the job listing.
    # When this date passes, the listing is considered closed.
    closing_date = db.Column(db.DateTime, nullable=True)

    # Persistent status column to reflect current state ('active'|'closed')
    status = db.Column(db.String(20), nullable=False, default='active')

    # When the job listing was created
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # When the job listing was last edited.
    # onupdate= automatically sets this to "now" every time the record is changed.
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # --- Relationships ---

    # Many Jobs → One Company (the inverse of Company.jobs)
    # back_populates='jobs' connects this to Company.jobs
    company = db.relationship('Company', back_populates='jobs')

    # One Job → Many Applications
    # If a Job is deleted, all its Applications are also deleted (cascade)
    applications = db.relationship(
        'Application',
        back_populates='job',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    # --- Helper Methods ---

    def __repr__(self):
        return f'<Job id={self.id} title="{self.title}" company_id={self.company_id}>'

    @property
    def is_closed(self):
        if self.closing_date:
            closing = self.closing_date
            # If stored datetime is offset-naive, assume UTC for comparison
            if closing.tzinfo is None:
                closing = closing.replace(tzinfo=timezone.utc)
            return closing <= datetime.now(timezone.utc)
        return False

    def to_dict(self):
        """Serialise to dict for JSON API responses."""
        # Compute status: if closing_date passed treat as closed, otherwise use stored status
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
            'closing_date':      self.closing_date.isoformat() if self.closing_date else None,
            'status':            computed_status,
            'application_count': self.applications.count() if hasattr(self.applications, 'count') else len(self.applications),
            'created_at':        self.created_at.isoformat() if self.created_at else None,
            'updated_at':        self.updated_at.isoformat() if self.updated_at else None,
        }
