# Job Portal — Backend (Flask API)

## What is this folder?

This is the **Python/Flask backend** for the Job Portal web application. It acts as the server and provides a REST API that the frontend communicates with via `fetch()` calls. It handles all the business logic — authentication, job management, applications, and admin controls — and connects to a MySQL database using SQLAlchemy ORM.

## Project Overview

We are building a controlled Job Portal where:
- **Companies** register and wait for admin approval before posting job listings.
- **Job Seekers (Users)** browse jobs, apply with a resume upload, and track their application status in real time.
- **Admins** moderate the platform — approving/rejecting companies and removing inappropriate content.

This solves the problem of large platforms (Indeed, LinkedIn) giving small companies little control, and leaving job seekers in the dark about their application status.

## Folder Structure

```
job-portal-backend/
├── app/
│   ├── __init__.py          ← Flask app factory (start reading here)
│   ├── config.py            ← Database URI, secret key, upload folder settings
│   ├── extensions.py        ← Shared extensions: db, bcrypt, migrate, cors
│   ├── models/              ← Database table definitions (User, Company, Job, etc.)
│   ├── routes/              ← API endpoints grouped by feature (auth, jobs, applications, admin)
│   ├── services/            ← Business logic layer (called by routes)
│   └── utils/               ← Shared helpers (e.g. role_required decorator)
├── migrations/              ← Auto-generated DB migration files (don't edit manually)
├── uploads/                 ← Where uploaded resumes are saved
├── venv/                    ← Python virtual environment (NOT in git)
├── requirements.txt         ← Python package list
├── run.py                   ← Start the Flask server with this file
├── .env.example             ← Copy this to .env and fill in your DB credentials
└── .gitignore               ← Files git should ignore (venv, .env, __pycache__, etc.)
```

## How to Run Locally

### 1. Clone the repo and navigate here
```bash
cd job-portal-backend
```

### 2. Create and activate the virtual environment
```bash
# Create (only needed once)
python3 -m venv venv

# Activate (do this every time you open a new terminal)
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your environment variables
```bash
# Copy the example file
cp .env.example .env

# Open .env and fill in your MySQL credentials:
# DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, SECRET_KEY
```

### 5. Make sure MySQL is running and create the database
```sql
CREATE DATABASE job_portal_db;
```

### 6. Run database migrations
```bash
flask db upgrade
```
> If this is your first time, run `flask db init` then `flask db migrate -m "initial"` first.

### 7. Start the Flask development server
```bash
python run.py
```

The API will be available at: **http://localhost:5001/api**

Test it with: **http://localhost:5001/api/health** — should return `{"status": "ok"}`

## API Endpoints Summary

| Method | URL | What it does |
|--------|-----|--------------|
| POST | `/api/auth/register/user` | Register a new job seeker |
| POST | `/api/auth/register/company` | Register a new company (pending approval) |
| POST | `/api/auth/login` | Login (user, company, or admin) |
| POST | `/api/auth/logout` | Logout current session |
| GET | `/api/jobs` | List all approved jobs |
| GET | `/api/jobs/<id>` | Get one job's details |
| POST | `/api/jobs` | Company posts a new job |
| PUT | `/api/jobs/<id>` | Company edits their job |
| DELETE | `/api/jobs/<id>` | Company deletes their job |
| POST | `/api/applications` | User applies to a job |
| GET | `/api/applications/mine` | User sees their own applications |
| GET | `/api/jobs/<id>/applications` | Company sees applicants for a job |
| PUT | `/api/applications/<id>/status` | Company updates applicant status |
| GET | `/api/admin/companies/pending` | Admin sees companies awaiting approval |
| PUT | `/api/admin/companies/<id>/approve` | Admin approves a company |
| PUT | `/api/admin/companies/<id>/reject` | Admin rejects a company |
| DELETE | `/api/admin/jobs/<id>` | Admin removes a job |
| DELETE | `/api/admin/users/<id>` | Admin removes a user |
| DELETE | `/api/admin/companies/<id>` | Admin removes a company |

## Notes for Teammates

- **Never edit files inside `venv/`** — that's your Python environment, not our code.
- **Never commit your `.env` file** — it contains your database password.
- If you add a new Python package, run `pip freeze > requirements.txt` to update the list.
- All `# TODO:` comments mark places where logic still needs to be added — search for them in any file.
