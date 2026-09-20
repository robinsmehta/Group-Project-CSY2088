# CSY2088 Group Project: Job Portal

A web application designed to connect Job Seekers, Employers, and Platform Administrators.

- **Job Seekers**: Search for jobs, filter by keyword or location, upload resumes, and track job applications.
- **Employers (Companies)**: Post job openings, review candidates, and manage hiring statuses.
- **Administrators**: Review company registrations, manage users, and moderate job posts.

---

## Project Structure

```text
codes/
├── job-portal-backend/     # Python Flask backend server and database models
└── job-portal-frontend/    # HTML, CSS, and JavaScript web pages
```

---

## Quick Start Guide

### 1. Start the Backend Server

```bash
cd job-portal-backend
source venv/bin/activate   # On Windows: venv\Scripts\activate
python run.py
```

### 2. Open the App in Your Browser

Open your browser and navigate to:
**`http://127.0.0.1:5001/`**

> **Note**: The backend automatically serves the frontend pages on port 5001 so logins, sessions, and uploads work smoothly without extra setup. For detailed setup steps, refer to [job-portal-backend/README.md](job-portal-backend/README.md) and [job-portal-frontend/README.md](job-portal-frontend/README.md).
