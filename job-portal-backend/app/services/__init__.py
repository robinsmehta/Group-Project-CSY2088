# ============================================================
# app/services/__init__.py
#
# Makes `services` a Python package.
# The services layer is the BUSINESS LOGIC layer in our 3-layer architecture.
#
# Architecture reminder:
#   Presentation (routes/) → Business Logic (services/) → Data Access (models/ + db)
#
# Each service file contains functions that:
#   1. Receive clean data from the route
#   2. Apply business rules (e.g., "duplicate check before saving")
#   3. Call the database through SQLAlchemy models
#   4. Return a (result_dict, http_status_code) tuple back to the route
# ============================================================
