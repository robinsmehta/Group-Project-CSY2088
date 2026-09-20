# app/models/admin.py — Admin Model
#
# Defines the Admin database table using SQLAlchemy ORM.
# Table name: admins
# Represents platform administrators who review companies and manage system resources.

from app.extensions import db


class Admin(db.Model):
    """
    Represents a platform administrator.

    Admin accounts are created directly in the database or seeding scripts
    rather than public registration routes to ensure security.
    """

    __tablename__ = 'admins'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Admin display name
    name = db.Column(db.String(100), nullable=False)

    # Admin login email address
    email = db.Column(db.String(150), unique=True, nullable=False)

    # Hashed password
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        """String representation for debugging."""
        return f'<Admin id={self.id} email={self.email}>'

    def to_dict(self):
        """Converts the Admin object into a Python dictionary for JSON responses."""
        return {
            'id':    self.id,
            'name':  self.name,
            'email': self.email,
        }
