# Job Portal — Backend (Flask API)

## Overview

This directory contains the Python and Flask backend service for the Job Portal web application. The application provides a RESTful API to manage user authentication, job postings, application submissions, and administrative oversight, connecting to a MySQL database using Flask-SQLAlchemy (ORM).

## System Design and Roles

The application provides functionality tailored to three primary user roles:
- **Employers (Companies)**: Register accounts (pending administrative approval) and manage job postings and candidate applications.
- **Job Seekers (Users)**: Register accounts, search and filter job listings, submit applications, and track application statuses.
- **Administrators**: Moderate platform accounts, approve company registrations, and manage system content.

## Project Structure

```text
job-portal-backend/
├── app/
│   ├── __init__.py          # Application factory initialization
│   ├── config.py            # Environment configurations (Database URI, secret keys, upload directory)
│   ├── extensions.py        # Shared extension instances (db, bcrypt, migrate, cors)
│   ├── models/              # SQLAlchemy model definitions (User, Company, Job, Application, Admin)
│   ├── routes/              # API blueprints and endpoint handlers
│   ├── services/            # Business logic layer (authentication, job workflows, application handling)
│   └── utils/               # Utilities and security decorators (role_required)
├── migrations/              # Database schema migration scripts (Flask-Migrate)
├── uploads/                 # Storage location for uploaded resume documents
├── requirements.txt         # Dependencies specification file
├── run.py                   # Main application entry point
├── init_db.py               # Database initialization script
├── .env.example             # Environment configuration template
└── .gitignore               # Ignored files and patterns for Git
```

## Local Development and Database Setup

Follow these instructions to configure the database, environment, and run the service locally.

### Step 1: Database Initialization
Ensure a MySQL server instance is running locally and execute the following query to create the database:
```sql
CREATE DATABASE job_portal;
```

### Step 2: Virtual Environment Configuration
Create and activate a Python virtual environment:
```bash
# Navigate to the backend directory
cd job-portal-backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS / Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Dependencies Installation
Install required packages using pip:
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration (`.env`)
Create a `.env` file from the provided template:
```bash
cp .env.example .env
```
Update `.env` with your local MySQL database credentials:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_mysql_password
DB_NAME=job_portal
SECRET_KEY=your_secure_secret_key
FLASK_ENV=development
```

### Step 5: Table Schema Generation
Run the database setup script to generate required tables (`users`, `companies`, `jobs`, `applications`, `admins`):
```bash
python init_db.py
```

### Step 6: Execute the Application Server
Start the Flask development server:
```bash
python run.py
```
The backend service listens on **http://127.0.0.1:5001** and also serves the frontend from the same origin.

> Important: For local development, open the app only at **http://127.0.0.1:5001/**.
> Do not serve the frontend separately via Live Server, Python `http.server`, or
> `file://` because session cookies are configured same-site and cross-origin
> access will prevent authentication from working.

### Step 7: Verify Service Health
Perform a HTTP GET request to verify API and database connectivity:
```http
GET http://localhost:5001/api/health
```
Expected `200 OK` response payload:
```json
{
  "status": "ok",
  "database": "connected",
  "message": "Flask server and MySQL database are successfully connected!"
}
```

---

## API Endpoints Reference

| Method | Endpoint | Description | Access Control |
|--------|----------|-------------|----------------|
| POST | `/api/auth/register/user` | Register job seeker account | Public |
| POST | `/api/auth/register/company` | Register company account (pending status) | Public |
| POST | `/api/auth/login` | Authenticate account and establish session | Public |
| POST | `/api/auth/logout` | Terminate active session | Authenticated |
| GET | `/api/jobs` | Retrieve approved job listings | Public |
| GET | `/api/jobs/<id>` | Retrieve single job detail | Public |
| POST | `/api/jobs` | Create new job posting | Company |
| PUT | `/api/jobs/<id>` | Update job posting | Company |
| DELETE | `/api/jobs/<id>` | Remove job posting | Company |
| POST | `/api/applications` | Submit application to a job | User |
| GET | `/api/applications/mine` | List user submitted applications | User |
| GET | `/api/jobs/<id>/applications` | List applicants for a job | Company |
| PUT | `/api/applications/<id>/status` | Update applicant status | Company |
| GET | `/api/admin/companies/pending` | List pending company registrations | Admin |
| PUT | `/api/admin/companies/<id>/approve` | Approve company registration | Admin |
| PUT | `/api/admin/companies/<id>/reject` | Reject company registration | Admin |
| DELETE | `/api/admin/jobs/<id>` | Administrative removal of job posting | Admin |
| DELETE | `/api/admin/users/<id>` | Administrative removal of user account | Admin |
| DELETE | `/api/admin/companies/<id>` | Administrative removal of company account | Admin |

## Development Standards and Best Practices

1. **Security**: Passwords are securely hashed using Bcrypt before storage. Password hashes must never be returned in API response bodies.
2. **Architecture**: Routes handle request parsing and response rendering; business rules reside strictly in `services/`.
3. **Environment Isolation**: Database credentials and secret keys must remain inside `.env` and must never be committed to repository tracking.
4. **Session Control**: Session cookie headers are validated via the `@role_required` decorator across protected API routes.
