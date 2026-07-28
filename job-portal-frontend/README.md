# Job Portal — Frontend

## What is this folder?

This is the **plain HTML/CSS/JavaScript frontend** for the Job Portal web application. It communicates with the Flask backend API via `fetch()` calls. There is no framework — just vanilla HTML, CSS, and JavaScript — so every teammate can open a file and start working without needing to learn React, Vue, or anything extra.

## Project Overview

We are building a controlled Job Portal where:
- **Companies** register and wait for admin approval before posting job listings.
- **Job Seekers (Users)** browse jobs, apply with a resume upload, and track their application status in real time.
- **Admins** moderate the platform — approving/rejecting companies and removing inappropriate content.

This solves the problem of large platforms (Indeed, LinkedIn) giving small companies little control, and leaving job seekers in the dark about their application status.

## Folder Structure

```
job-portal-frontend/
├── index.html              ← Landing homepage (everyone sees this first)
├── auth/
│   ├── register.html       ← Registration page for users and companies
│   └── login.html          ← Login page
├── company/
│   ├── dashboard.html      ← Company: view, edit, delete their job listings
│   ├── post-job.html       ← Company: form to post a new job
│   └── applicants.html     ← Company: view applicants and update their status
├── jobs/
│   ├── listing.html        ← Public: browse and search all jobs
│   └── detail.html         ← Public: view one job and apply
├── user/
│   └── dashboard.html      ← User: view their applications and status
├── admin/
│   └── dashboard.html      ← Admin: approve companies, delete content
├── css/
│   ├── style.css           ← Global styles (navbar, footer, colours, fonts, buttons)
│   ├── auth.css            ← Styles for register/login pages
│   ├── jobs.css            ← Styles for job listing and detail pages
│   └── dashboard.css       ← Styles shared by company/user/admin dashboards
├── js/
│   ├── config.js           ← API base URL (change this if the backend port changes)
│   ├── auth.js             ← fetch() calls for register, login, logout
│   ├── jobs.js             ← fetch() calls for job listing, search, detail
│   ├── applications.js     ← fetch() calls for applying, status tracking
│   ├── admin.js            ← fetch() calls for admin actions
│   └── shared.js           ← Helper functions used across multiple pages
└── assets/                 ← Images, icons, logo (add files here as needed)
```

## How to Run Locally

The frontend is plain HTML — no build step needed.

### Option 1: Open directly in browser
Just double-click `index.html` to open it. However, `fetch()` calls to the API won't work this way due to browser security restrictions (CORS).

### Option 2: Use VS Code Live Server (Recommended)
1. Install the **Live Server** extension in VS Code.
2. Right-click `index.html` → **"Open with Live Server"**.
3. The frontend will run on `http://127.0.0.1:5500`.

### Option 3: Use Python's built-in server
```bash
cd job-portal-frontend
python3 -m http.server 5500
```
Then open `http://localhost:5500` in your browser.

> **Important:** Make sure the Flask backend is also running on port 5000 before testing any API calls. See the backend README for how to start it.

## Which file do I work in?

| Teammate's area | Files to edit |
|-----------------|---------------|
| Homepage & job listings | `index.html`, `jobs/listing.html`, `jobs/detail.html`, `css/jobs.css` |
| Auth pages (register/login) | `auth/register.html`, `auth/login.html`, `css/auth.css` |
| Company pages | `company/dashboard.html`, `company/post-job.html`, `company/applicants.html` |
| User & Admin pages | `user/dashboard.html`, `admin/dashboard.html`, `css/dashboard.css` |
| JavaScript / API connections | All files in `js/` |

## Notes for Teammates

- **All JavaScript API calls use `API_BASE_URL` from `js/config.js`** — never hardcode `http://localhost:5000` in a JS file directly.
- **Search for `<!-- TODO:` in HTML files** to find where you need to add content.
- **Search for `// TODO:` in JS files** to find where fetch() calls and logic need to be written.
- **CSS files are split by page area** — edit `style.css` for global styles, and the specific CSS file for your page.
- **Don't put your styles in the HTML file** — keep CSS in the `css/` folder.
