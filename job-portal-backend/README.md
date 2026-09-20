# Job Portal — Backend

This directory contains the Python (Flask) backend server and database logic for the Job Portal.

---

## What It Does

The backend connects to a MySQL database and handles API requests for three types of users:
- **Job Seekers**: Create accounts, search jobs, apply with resumes, and track application status.
- **Employers**: Register accounts, post job listings, and review job applicants.
- **Administrators**: Approve or reject company accounts, manage users, and moderate job posts.

---

## Folder Layout

```text
job-portal-backend/
├── app/
│   ├── __init__.py          # Sets up the Flask application
│   ├── config.py            # Database and application settings
│   ├── extensions.py        # Database and security plugins (SQLAlchemy, Bcrypt, CORS)
│   ├── models/              # Database tables (User, Company, Job, Application, Admin)
│   ├── routes/              # URL endpoints (Auth, Jobs, Applications, Admin)
│   ├── services/            # Core business rules and database logic
│   └── utils/               # Helper utilities and security checks
├── migrations/              # Database schema history
├── uploads/                 # Storage folder for uploaded resume PDFs
├── requirements.txt         # Required Python packages
├── run.py                   # Main script to start the server
├── init_db.py               # Database setup script
├── seed_db.py               # Script to add sample test data
└── .env.example             # Template for database credentials
```

---

## How to Set Up and Run

### Step 1: Create the MySQL Database
Make sure MySQL server is running locally, then create a blank database:
```sql
CREATE DATABASE job_portal;
```

### Step 2: Create a Virtual Environment
```bash
cd job-portal-backend
python3 -m venv venv

# Activate it:
# On macOS / Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Required Packages
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Settings (`.env`)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` in a text editor and set your local MySQL password:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=job_portal
SECRET_KEY=your_secret_key
FLASK_ENV=development
```

### Step 5: Initialize Database Tables
Create all database tables (`users`, `companies`, `jobs`, `applications`, `admins`):
```bash
python init_db.py
```

### Step 6: (Optional) Add Sample Test Data
To add sample users, companies, and job listings for testing:
```bash
python seed_db.py
```
**Default Test Accounts:**
- **Job Seeker**: `alice@example.com` / `password123`
- **Employer**: `hr@technova.com` / `password123`
- **Admin**: `admin@hirehub.com` / `admin123`

### Step 7: Start the Server
```bash
python run.py
```
The server will start at **http://127.0.0.1:5001/**.

---

## Core API Endpoints

| Method | URL Path | What It Does | Who Can Access |
|--------|----------|--------------|----------------|
| POST | `/api/auth/register/user` | Register a job seeker account | Everyone |
| POST | `/api/auth/register/company` | Register a company account (starts as pending) | Everyone |
| POST | `/api/auth/login` | Log into an account | Everyone |
| POST | `/api/auth/logout` | Log out of an active account | Logged-in Users |
| GET | `/api/jobs` | Get job listings with search/filters | Everyone |
| GET | `/api/jobs/<id>` | View details for a single job | Everyone |
| POST | `/api/jobs` | Post a new job | Employers |
| PUT | `/api/jobs/<id>` | Edit a job posting | Employers |
| DELETE | `/api/jobs/<id>` | Delete a job posting | Employers |
| POST | `/api/applications` | Apply for a job with a resume | Job Seekers |
| GET | `/api/applications/mine` | View submitted job applications | Job Seekers |
| GET | `/api/applications/job/<id>` | View applicants for a specific job | Employers |
| PUT | `/api/applications/<id>/status` | Change application status | Employers |
| GET | `/api/admin/companies/pending` | View pending company applications | Admins |
| PUT | `/api/admin/companies/<id>/approve` | Approve a company account | Admins |
| PUT | `/api/admin/companies/<id>/reject` | Reject a company account | Admins |
| GET | `/api/admin/stats` | View platform statistics | Admins |

---

## Automated Tests
To run unit and integration tests:
```bash
pytest
```
