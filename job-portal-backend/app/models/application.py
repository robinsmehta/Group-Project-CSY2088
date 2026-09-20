# app/models/application.py — Application Model
#
# Defines the Application database table using SQLAlchemy ORM.
# Table name: applications
# Tracks job applications submitted by job seekers for job listings.

from datetime import datetime, timezone
from app.extensions import db


def _to_utc_iso(dt):
    """Convert a datetime object to UTC ISO format string (YYYY-MM-DDTHH:MM:SSZ)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat().replace('+00:00', 'Z')


class Application(db.Model):
    """
    Represents a job application submitted by a user for a job listing.

    Relationships:
      - Belongs to ONE Job (many-to-one).
      - Belongs to ONE User (many-to-one).
    """

    __tablename__ = 'applications'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key → Job
    job_id = db.Column(
        db.Integer,
        db.ForeignKey('jobs.id'),
        nullable=False
    )

    # Foreign Key → User
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    # File path to the uploaded resume stored on the server
    resume_path = db.Column(db.String(300), nullable=True)

    # Review status: 'applied', 'under_review', 'shortlisted', 'rejected'
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

    # Submission timestamp
    applied_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Last status update timestamp
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    job = db.relationship('Job', back_populates='applications')
    user = db.relationship('User', back_populates='applications')

    def __repr__(self):
        """String representation for debugging."""
        return (
            f'<Application id={self.id} '
            f'user_id={self.user_id} '
            f'job_id={self.job_id} '
            f'status={self.status}>'
        )

    def to_dict(self):
        """Converts the Application object into a Python dictionary for JSON responses."""
        return {
            'id':          self.id,
            'job_id':      self.job_id,
            'user_id':     self.user_id,
            'resume_path': self.resume_path,
            'status':      self.status,
            'applied_at':  _to_utc_iso(self.applied_at),
            'updated_at':  _to_utc_iso(self.updated_at),
        }
