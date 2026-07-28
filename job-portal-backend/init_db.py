# ============================================================
# init_db.py — Database Initialization Script
#
# This script connects Flask to MySQL using SQLAlchemy and
# automatically creates all 5 tables (users, companies, jobs,
# applications, admins) defined in the models.
#
# Usage:
#   python init_db.py
# ============================================================

import sys
from sqlalchemy import inspect, text
from app import create_app
from app.extensions import db

# Import all SQLAlchemy models to ensure their table definitions are registered with db.metadata
from app.models import User, Company, Job, Application, Admin  # noqa: F401


def init_database():
    """
    Connects to MySQL, tests connectivity, and calls db.create_all()
    to create all missing database tables.
    """
    print("==================================================")
    print("🚀 Starting Job Portal Database Initialization")
    print("==================================================")

    # 1. Create Flask app instance to access configuration and SQLAlchemy context
    app = create_app()

    with app.app_context():
        db_host = app.config.get('DB_HOST', 'localhost')
        db_port = app.config.get('DB_PORT', '3306')
        db_name = app.config.get('DB_NAME', 'job_portal')
        db_user = app.config.get('DB_USER', 'root')

        print(f"📡 Target Database : {db_name}")
        print(f"🖥️  Server Address  : {db_host}:{db_port}")
        print(f"👤 Database User   : {db_user}")
        print("--------------------------------------------------")

        try:
            # 2. Test database connection before creating tables
            print("🔍 Testing connection to MySQL server...")
            db.session.execute(text("SELECT 1"))
            print("✅ Successfully connected to MySQL database!")

            # 3. Create all tables defined in SQLAlchemy models
            print("🔨 Generating tables from SQLAlchemy models...")
            db.create_all()

            # 4. Verify created tables using SQLAlchemy inspector
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()

            expected_tables = ['users', 'companies', 'jobs', 'applications', 'admins']
            
            print("--------------------------------------------------")
            print("🎉 Database setup complete! Detected tables:")
            for table_name in sorted(existing_tables):
                status = "✅" if table_name in expected_tables else "ℹ️"
                print(f"   {status} Table: '{table_name}'")
            print("--------------------------------------------------")
            print("All 5 core tables are verified and ready for use!")

        except Exception as e:
            print("--------------------------------------------------")
            print("❌ Error initializing MySQL database!")
            print(f"Details: {e}")
            print("\n💡 Troubleshooting Steps:")
            print(f"1. Is MySQL running locally on port {db_port}?")
            print(f"2. Have you created the database in MySQL? Run SQL command:")
            print(f"   CREATE DATABASE {db_name};")
            print(f"3. Are your credentials (DB_USER, DB_PASSWORD) correct in your .env file?")
            print("==================================================")
            sys.exit(1)


if __name__ == '__main__':
    init_database()
