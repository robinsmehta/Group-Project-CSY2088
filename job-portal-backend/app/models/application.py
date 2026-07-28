# ============================================================
# app/models/application.py — Application Model
#
# This file defines the Application (job application) table.
#
# Table name: applications
# Who uses this table: Tracks which User applied to which Job,
# along with the résumé file path and current review status.
#
# This is a JOIN TABLE between users and jobs —
# it sits in the middle and holds extra data about the relationship.
# ============================================================

from datetime import datetime, timezone
from app.extensions import db


class Application(db.Model):
    """
    Represents a job application submitted by a user for a job listing.

    Relationships:
      - Belongs to ONE Job (many-to-one).
        Access via: application_instance.job  →  Job object
      - Belongs to ONE User (many-to-one).
        Access via: application_instance.user  →  User object
    """

    __tablename__ = 'applications'

    # --- Columns ---

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key → Which job is this application for?
    job_id = db.Column(
        db.Integer,
        db.ForeignKey('jobs.id'),
        nullable=False
    )

    # Foreign Key → Which user submitted this application?
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    # File path to the uploaded résumé PDF stored on the server.
    # Example: "uploads/resumes/user_1_resume.pdf"
    # TODO: When saving a file, generate a safe unique filename and store path here.
    resume_path = db.Column(db.String(300), nullable=True)

    # Current review status of the application.
    # Workflow: applied → under_review → shortlisted or rejected
    # Companies update this as they review applications.
    status = db.Column(
        db.Enum(
            'applied',
            'under_review',
            'shortlisted',
            'rejected',
            name='application_status_enum'
        ),
        default='applied',
        nullable=False
    )

    # When the application was first submitted
    applied_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # When the application status was last changed
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # --- Relationships ---

    # Link back to the Job this application is for
    job = db.relationship('Job', back_populates='applications')

    # Link back to the User who applied
    user = db.relationship('User', back_populates='applications')

    # --- Helper Methods ---

    def __repr__(self):
        return (
            f'<Application id={self.id} '
            f'user_id={self.user_id} '
            f'job_id={self.job_id} '
            f'status={self.status}>'
        )

    def to_dict(self):
        """Serialise to dict for JSON API responses."""
        return {
            'id':          self.id,
            'job_id':      self.job_id,
            'user_id':     self.user_id,
            'resume_path': self.resume_path,
            'status':      self.status,
            'applied_at':  self.applied_at.isoformat() if self.applied_at else None,
            'updated_at':  self.updated_at.isoformat() if self.updated_at else None,
        }
