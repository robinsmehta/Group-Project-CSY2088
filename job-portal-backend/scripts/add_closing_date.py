"""
add_closing_date.py

Small helper to add the `closing_date` column to the `jobs` table
if it does not already exist. Run this from the project root using the
project virtualenv Python: `python scripts/add_closing_date.py`.

It uses the app factory so it will read the configured DB connection
from your Flask config and execute a safe ALTER TABLE when required.
"""
from sqlalchemy import text
from app import create_app
from app.extensions import db
from sqlalchemy import inspect


def main():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        cols = [c['name'] for c in inspector.get_columns('jobs')]
        if 'closing_date' in cols:
            print("Column 'closing_date' already exists on 'jobs'.")
        else:
            print("Adding 'closing_date' column to 'jobs' table...")
        # MySQL DATETIME is appropriate here; allow NULL for existing rows
        alter_sql = text("ALTER TABLE jobs ADD COLUMN closing_date DATETIME NULL")
        try:
            db.session.execute(alter_sql)
            db.session.commit()
            print("✅ Successfully added 'closing_date' column.")
        except Exception as e:
            print("❌ Failed to alter table:", e)
            print("You may need to run this with a DB user that has ALTER privileges.")

        # Add persistent status column if missing
        cols = [c['name'] for c in inspector.get_columns('jobs')]
        if 'status' not in cols:
            print("Adding 'status' column to 'jobs' table...")
            try:
                db.session.execute(text("ALTER TABLE jobs ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active'"))
                db.session.commit()
                print("✅ Successfully added 'status' column.")
            except Exception as e:
                print("❌ Failed to add 'status' column:", e)

        # Backfill closed status for already expired jobs
        try:
            db.session.execute(text("UPDATE jobs SET status='closed' WHERE closing_date IS NOT NULL AND closing_date <= NOW()"))
            db.session.commit()
            print("✅ Backfilled 'closed' status for expired jobs.")
        except Exception as e:
            print("⚠️  Failed to backfill statuses:", e)


if __name__ == '__main__':
    main()
