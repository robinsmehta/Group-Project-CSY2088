# ============================================================
# app/models/admin.py — Admin Model
#
# This file defines the Admin database table.
#
# Table name: admins
# Who uses this table: Platform administrators who can:
#   - Approve or reject company accounts
#   - Remove inappropriate job listings or user accounts
#
# Admins are separate from regular Users and Companies —
# they have a completely different account and elevated privileges.
# ============================================================

from app.extensions import db


class Admin(db.Model):
    """
    Represents a platform administrator.

    Admins are created directly in the database (or via a seeding script),
    NOT through a public registration endpoint, to prevent unauthorized
    admin account creation.
    """

    __tablename__ = 'admins'

    # --- Columns ---

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Admin's display name (e.g., "Super Admin")
    name = db.Column(db.String(100), nullable=False)

    # Admin's login email — must be unique
    email = db.Column(db.String(150), unique=True, nullable=False)

    # Hashed password — same bcrypt approach as User and Company
    # TODO (auth_service.py): Hash with bcrypt before saving
    password_hash = db.Column(db.String(255), nullable=False)

    # NOTE: Admins intentionally have NO created_at field and NO relationships —
    # admins are managed outside the normal user flow.
    # If you need audit logs later, add created_at and a separate audit table.

    # --- Helper Methods ---

    def __repr__(self):
        return f'<Admin id={self.id} email={self.email}>'

    def to_dict(self):
        """Serialise to dict for JSON API responses. Excludes password_hash."""
        return {
            'id':    self.id,
            'name':  self.name,
            'email': self.email,
        }
