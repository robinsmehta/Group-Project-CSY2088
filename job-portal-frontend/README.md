# Job Portal — Frontend

This directory contains the user interface (HTML, CSS, JavaScript) for the Job Portal.

---

## Folder Layout

```text
job-portal-frontend/
├── index.html              # Home page and landing screen
├── auth/
│   ├── register.html       # Sign up page (Job Seekers & Companies)
│   └── login.html          # Log in page
├── company/
│   ├── dashboard.html      # Employer dashboard (manage job posts)
│   ├── post-job.html       # Form to post a new job opening
│   └── applicants.html     # View and manage job candidates
├── jobs/
│   ├── listing.html        # Search and filter job listings
│   └── detail.html         # View job details and apply
├── user/
│   └── dashboard.html      # Job seeker dashboard (track applications)
├── admin/
│   ├── dashboard.html      # Admin overview dashboard
│   ├── company-approvals.html # Approve or reject new companies
│   └── user-directory.html # Manage platform users and accounts
├── css/
│   ├── style.css           # Global layout, navigation, and theme styles
│   ├── auth.css            # Styles for login and sign up pages
│   ├── jobs.css            # Styles for job search and details
│   ├── dashboard.css       # Shared styles for dashboards
│   └── admin.css           # Styles for admin pages
└── js/
    ├── config.js           # Server URL configuration
    ├── api.js              # Functions for communicating with the backend API
    ├── auth.js             # Form handling for login and registration
    ├── shared.js           # Shared utilities (navbar, notifications, skill badges)
    ├── home.js             # Logic for the home page
    ├── job-listing.js      # Logic for job filtering and pagination
    ├── job-detail.js       # Logic for job details and applying
    └── user-dashboard.js   # Logic for tracking user applications
```

---

## How to Run

1. Start the backend server from `job-portal-backend`:
   ```bash
   cd job-portal-backend
   python run.py
   ```
2. Open your web browser and navigate to:
   ```text
   http://127.0.0.1:5001/
   ```

The backend automatically serves these HTML pages, ensuring login sessions and cookies work correctly.

---

## Simple Development Tips

- **API Server URL**: Defined once in `js/config.js` (`API_BASE_URL`).
- **Styles**: Global styles belong in `css/style.css`. Page-specific styles belong in dedicated CSS files.
- **Helper Functions**: Navbar rendering, user state checks, and notifications live in `js/shared.js`.
