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
│   ├── jobs.js             # API integrations for job search and management
│   ├── applications.js     # API integrations for job applications
│   ├── admin.js            # API integrations for administrative functions
│   └── shared.js           # Utilities and UI helpers shared across views
└── assets/                 # Static visual assets (images, icons, vectors)
```

## Running the Application Locally

The frontend relies on standard Web API standards. Serve the files over HTTP to enable API integration and CORS credentials support.

### Method 1: VS Code Live Server (Recommended)
1. Install the **Live Server** extension in VS Code.
2. Right-click `index.html` and select **Open with Live Server**.
3. Access the application at `http://127.0.0.1:5500`.

### Method 2: Python HTTP Server Module
```bash
cd job-portal-frontend
python3 -m http.server 5500
```
Access the application by navigating to `http://localhost:5500` in your web browser.

> **Note**: Ensure the backend API service is running on `http://localhost:5001/api` prior to executing API requests.

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
