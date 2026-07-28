# ============================================================
# app/models/__init__.py
#
# This file makes `models` a Python package and exports all model classes.
# Re-exporting them here allows clean imports such as:
#   from app.models import User, Company, Job, Application, Admin
# ============================================================

from .user import User
from .company import Company
from .job import Job
from .application import Application
from .admin import Admin

__all__ = ['User', 'Company', 'Job', 'Application', 'Admin']

