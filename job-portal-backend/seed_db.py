import sys
from app import create_app
from app.extensions import db
from app.models import User, Company, Job, Admin
from flask_bcrypt import generate_password_hash

def seed_data():
    app = create_app()
    with app.app_context():
        print("🌱 Seeding database with mock data...")
        
        # 1. Add Job Seekers
        users = [
            User(name="Alice Smith", email="alice@example.com", password_hash=generate_password_hash("password123").decode('utf-8')),
            User(name="Bob Johnson", email="bob@example.com", password_hash=generate_password_hash("password123").decode('utf-8'))
        ]
        
        # Check if they exist to avoid unique constraint errors
        for u in users:
            if not User.query.filter_by(email=u.email).first():
                db.session.add(u)
                print(f"Added user: {u.email}")
        
        # 2. Add Companies (Status must be 'approved' for them to post jobs)
        companies = [
            Company(company_name="TechNova Inc", email="hr@technova.com", password_hash=generate_password_hash("password123").decode('utf-8'), description="A leading tech company.", status="approved"),
            Company(company_name="Global Solutions", email="careers@globalsolutions.com", password_hash=generate_password_hash("password123").decode('utf-8'), description="Global IT consulting firm.", status="approved")
        ]
        
        for c in companies:
            if not Company.query.filter_by(email=c.email).first():
                db.session.add(c)
                print(f"Added company: {c.email}")
                
        db.session.commit()
        
        # Get company IDs
        technova = Company.query.filter_by(email="hr@technova.com").first()
        global_sol = Company.query.filter_by(email="careers@globalsolutions.com").first()
        
        if technova and global_sol:
            # 3. Add Jobs
            jobs = [
                Job(company_id=technova.id, title="Senior Backend Engineer", description="We are looking for a Python expert with extensive Flask and Django experience...", location="Remote", category="Engineering", job_type="Full-time", salary="$120k - $150k"),
                Job(company_id=technova.id, title="Frontend Developer", description="React and Vue experience required. Strong understanding of CSS frameworks...", location="New York, NY", category="Engineering", job_type="Full-time", salary="$90k - $110k"),
                Job(company_id=technova.id, title="Product Manager", description="Lead our product strategy, work closely with engineering and marketing teams...", location="San Francisco, CA", category="Product", job_type="Full-time", salary="$130k - $160k"),
                Job(company_id=global_sol.id, title="Data Scientist", description="Analyze large datasets using Pandas, Numpy, and machine learning models...", location="London, UK", category="Data", job_type="Contract", salary="£600/day"),
                Job(company_id=global_sol.id, title="DevOps Engineer", description="Maintain AWS infrastructure, create CI/CD pipelines, ensure high availability...", location="Remote", category="Engineering", job_type="Full-time", salary="$110k - $140k"),
                Job(company_id=global_sol.id, title="Marketing Specialist", description="Drive our marketing campaigns, manage social media, track analytics...", location="Remote", category="Marketing", job_type="Part-time", salary="$40/hr")
            ]
            
            # Check if jobs exist before adding
            if Job.query.count() == 0:
                for j in jobs:
                    db.session.add(j)
                db.session.commit()
                print("✅ 6 Jobs added successfully!")
            else:
                print("ℹ️ Jobs already exist in the database, skipping job creation.")

        print("\n🎉 Seeding complete! Here are your test accounts:")
        print("--------------------------------------------------")
        print("1. Job Seeker (User):")
        print("   Email: alice@example.com")
        print("   Pass:  password123")
        print("--------------------------------------------------")
        print("2. Employer (Company) - Pre-approved:")
        print("   Email: hr@technova.com")
        print("   Pass:  password123")
        print("--------------------------------------------------")
        print("3. Admin (created via init_db.py):")
        print("   Email: admin@hirehub.com")
        print("   Pass:  admin123")
        print("==================================================")

if __name__ == '__main__':
    seed_data()
