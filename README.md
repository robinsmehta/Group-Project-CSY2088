# CSY2088 Group Project: Job Portal

A controlled web application connecting Job Seekers, Employers, and Admins.

## Project Architecture

This repository is split into two distinct, modular folders:

```
codes/
├── job-portal-backend/     ← Python (Flask) REST API backend
└── job-portal-frontend/    ← Plain HTML / CSS / JavaScript frontend
```

---

## 🚀 Quick Start Guide

### 1. Run the Backend API
```bash
cd job-portal-backend
source venv/bin/activate
python run.py
```
> The API will start on **`http://localhost:5001/api`**. See [job-portal-backend/README.md]

### 2. Run the Frontend
Open `job-portal-frontend/index.html` using **VS Code Live Server** (or run `python3 -m http.server 5500` inside `job-portal-frontend`).
> See [job-portal-frontend/README.md] for individual page assignments and JavaScript guidelines.
