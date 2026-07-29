# CSY2088 Group Project: Job Portal

A web application designed to connect Job Seekers, Employers, and Platform Administrators.

## Project Architecture

This repository follows a decoupled architecture separating the backend API service from the frontend presentation layer:

```text
codes/
├── job-portal-backend/     # Python (Flask) REST API service and database models
└── job-portal-frontend/    # HTML5, CSS3, and JavaScript frontend application
```

---

## Quick Start Guide

### 1. Run the Backend API Service

```bash
cd job-portal-backend
source venv/bin/activate
python run.py
```

The API service runs by default at `http://localhost:5001/api`. For complete backend setup instructions, database initialization, and configuration details, refer to [job-portal-backend/README.md](job-portal-backend/README.md).

### 2. Run the Frontend Application

Launch the frontend via VS Code Live Server or Python HTTP server module:

```bash
cd job-portal-frontend
python3 -m http.server 5500
```

Open `http://localhost:5500` in your web browser. Refer to [job-portal-frontend/README.md](job-portal-frontend/README.md) for page mapping and JavaScript development guidelines.
