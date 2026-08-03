# Job Portal — Frontend

## Overview

This directory contains the HTML5, CSS3, and JavaScript frontend application for the Job Portal. It interfaces with the Flask REST API backend to deliver interactive features for Job Seekers, Employers, and System Administrators.

## Project Structure

```text
job-portal-frontend/
├── index.html              # Landing homepage and portal entry
├── auth/
│   ├── register.html       # Account registration interface
│   └── login.html          # Account login interface
├── company/
│   ├── dashboard.html      # Company dashboard for job listing management
│   ├── post-job.html       # Form interface for submitting new job listings
│   └── applicants.html     # Candidate review and status tracking interface
├── jobs/
│   ├── listing.html        # Public job search and listing directory
│   └── detail.html         # Job details and application submission view
├── user/
│   └── dashboard.html      # Job seeker application tracking dashboard
├── admin/
│   └── dashboard.html      # Administrator management dashboard
├── css/
│   ├── style.css           # Core styling tokens, typography, navbar, and footer
│   ├── auth.css            # Authentication views styling
│   ├── jobs.css            # Job search and listing views styling
│   └── dashboard.css       # Shared dashboard layouts styling
├── js/
│   ├── config.js           # API base URL configuration
│   ├── auth.js             # API integrations for authentication (register, login, logout)
│   ├── applications.js     # API integrations for job applications
│   ├── admin.js            # API integrations for administrative functions
│   └── shared.js           # Utilities and UI helpers shared across views
└── assets/                 # Static visual assets (images, icons, vectors)
```

## Running the Application Locally

This project is designed to run with the frontend served by the Flask backend on
`http://127.0.0.1:5001/`.

> Important: Do not open the frontend separately via Live Server, Python
> `http.server`, or `file://`.
> Those approaches create a different origin and will break authentication
> because the Flask session cookie is same-site and only works from
> `http://127.0.0.1:5001`.

### Supported Local Run Mode
1. Start the Flask backend from the `job-portal-backend` directory:
```bash
cd job-portal-backend
python run.py
```
2. Open a browser to:
```text
http://127.0.0.1:5001/
```

The backend serves the frontend and API from the same host and port.

> **Note**: The backend API base URL is `http://127.0.0.1:5001/api`, matching the
> same-origin frontend deployment.

---

## Component Work Allocation

| Functional Area | Target Views and Styles |
|-----------------|-------------------------|
| Landing & Job Catalog | `index.html`, `jobs/listing.html`, `jobs/detail.html`, `css/jobs.css` |
| Authentication Views | `auth/register.html`, `auth/login.html`, `css/auth.css` |
| Employer Portal | `company/dashboard.html`, `company/post-job.html`, `company/applicants.html` |
| User & Admin Portals | `user/dashboard.html`, `admin/dashboard.html`, `css/dashboard.css` |
| API Integrations | Modules located within `js/` |

## Development Guidelines

1. **Centralized Configuration**: All API network requests must reference `API_BASE_URL` declared in `js/config.js`. Avoid hardcoding host URLs inside individual module files.
2. **Session Persistence**: HTTP fetch calls to protected endpoints must pass `{ credentials: 'include' }` to transmit server session cookies correctly.
3. **Modular Styling**: Maintain layout separation by placing shared baseline styles in `css/style.css` and view-specific rules within dedicated stylesheet files.
