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

    # ========================================================
    # TASK-008 — Add a "skills" field to store job skill tags
    # ========================================================
    #
    # PROBLEM:
    # The new Post Job form has a "Skills & Keywords" tag box where a company
    # types skills like "React", presses Enter, and gets a little removable
    # pill/tag for each one (built visually by Robins, see A4). Right now
    # there is nowhere in the database to save this information at all —
    # this column simply does not exist yet.
    #
    # WHAT YOU NEED TO DO:
    # 1. Add a new column below, similar to the other db.Column(...) lines
    #    in this class, for example:
    #        skills = db.Column(db.String(500), nullable=True)
    #    A simple text field is enough — store all the skills as ONE string,
    #    separated by commas (e.g. "React, Figma, SQL"), matching what the
    #    design's placeholder text already suggests. You do NOT need a
    #    separate table for this.
    # 2. Add "skills" to the `to_dict()` method further down in this file so
    #    it gets included when a job is sent to the frontend as JSON.
    # 3. After adding the column, you'll need to update the database schema
    #    (e.g. via a migration, or by recreating the local dev database —
    #    check init_db.py and the migrations/ folder for how this project
    #    manages schema changes).
    #
    # HOW THIS PART CONNECTS:
    # - job_routes.py (create_job / update_job) needs to accept "skills" as
    #   an updatable field so the Post Job / Edit Job form can save it.
    # - The job detail page (jobs/detail.html) needs to display these skills
    #   when someone views a job listing.
    #
    # WHAT "DONE" LOOKS LIKE:
    # You can add skills like "React, Figma, SQL" when posting a job, save
    # it, and see those exact skills displayed later when viewing that job.
    #
    # ASSIGNED TASK:
    # Simrika (D3) — Add the Skills & Keywords feature.
    # ========================================================

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
            # TODO — TASK-008 (continued): once you add the `skills` column
            # above, also add it here, e.g.  'skills': self.skills,
            # so it's actually sent to the frontend in the job's JSON data.
            'closing_date':      self.closing_date.isoformat() if self.closing_date else None,
            'status':            computed_status,
            'application_count': self.applications.count() if hasattr(self.applications, 'count') else len(self.applications),
            'created_at':        self.created_at.isoformat() if self.created_at else None,
            'updated_at':        self.updated_at.isoformat() if self.updated_at else None,
        }
