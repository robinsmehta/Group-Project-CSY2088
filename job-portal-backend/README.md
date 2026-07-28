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

## How to Run & Connect Database Locally

Follow these step-by-step instructions to set up the MySQL database, configure your environment, initialize tables, and verify the backend server.

### Step 1: Make sure MySQL is running & create the database
Open your MySQL terminal or GUI client (such as MySQL Workbench or phpMyAdmin) and run:
```sql
CREATE DATABASE job_portal;
```

### Step 2: Create and activate your Python virtual environment
```bash
# Navigate to the backend directory (if not already there)
cd job-portal-backend

# Create virtual environment (only needed once)
python3 -m venv venv

# Activate virtual environment (run this every time you open a new terminal)
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set up environment variables (`.env`)
```bash
# Copy the template file to create your local .env file
cp .env.example .env

# Open .env in your code editor and fill in your real MySQL password:
# DB_USER=root
# DB_PASSWORD=your_actual_mysql_password
# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=job_portal
# SECRET_KEY=your_secret_key_here
```

### Step 5: Run the table creation script
To automatically generate all 5 database tables (`users`, `companies`, `jobs`, `applications`, `admins`) in your MySQL database:
```bash
python init_db.py
```
*(Alternatively, you can also use the Flask CLI command: `flask init-db` or Flask-Migrate: `flask db upgrade`)*

### Step 6: Start the Flask server
```bash
python run.py
```
The Flask API server will start on: **http://localhost:5001/api**

### Step 7: Confirm database connection via health check endpoint
Open your browser or Postman and visit:
```http
GET http://localhost:5001/api/health
```
If the database connection is wired up correctly, you will receive a `200 OK` JSON response:
```json
{
  "status": "ok",
  "database": "connected",
  "message": "Flask server and MySQL database are successfully connected!"
}
```

---

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
