# Job Portal — Team Task List

This document lists every problem from `Problem_Details.docx`, matched to a
Task ID, the exact file(s)/function(s) it lives in, and a difficulty rating.
Matching `TODO — TASK-XXX` comments have been placed directly in the code at
each location listed below — open the file and search for the Task ID to
find the exact spot to start working.

Legend: 🟢 Beginner  🟡 Intermediate  🔴 Advanced

---

## Naming Update (affects everyone, owned by Robins)

### TASK-001 — Naming update: "HireMe"/"HireHub" → "Job Portal"

**Title:** Replace all leftover old site names with "Job Portal"
**File(s):** All 10 pages in `job-portal-frontend/` (`index.html`,
`admin/dashboard.html`, `auth/login.html`, `auth/register.html`,
`company/applicants.html`, `company/dashboard.html`,
`company/post-job.html`, `jobs/detail.html`, `jobs/listing.html`,
`user/dashboard.html`) + `js/shared.js`
**Function/Section:** `<title>` tag on each page; `renderNavbar()` and
`renderFooter()` in `shared.js`
**Problem:** The project used two different old names inconsistently
("HireMe" on most pages, "HireHub" on `company/dashboard.html` and
`user/dashboard.html`). The site is now called "Job Portal".
**What to do:** As each page is rebuilt from Figma, update the `<title>`
and remove any other leftover old-name text (navbar brand, footer).
**Expected result:** No page or shared file contains "HireMe" or "HireHub"
anywhere — everything says "Job Portal".
**Difficulty:** 🟢 Beginner — pure find-and-replace text, no logic involved.

---

## Robins — UI Redesign & Implementation

### TASK-001 (see above) — A1: Naming update
Part of rebuilding every page — see TASK-001 above.

### TASK-020 / TASK-021 — A3 & A4: Shared Post/Edit Job form + Skills tag input

**Title:** Build one shared Post Job / Edit Job form, with a Skills tag input
**File(s):** `job-portal-frontend/company/post-job.html`
**Function/Section:** The `<form id="post-job-form">` element and the
"Step 3" section just above the description textarea
**Problem:** This page currently only handles CREATING a job (see the
`apiCreateJob` call in the `<script>` at the bottom). The new Figma design
wants ONE form that can act as either "Post Job" or "Edit Job" (with a red
"Delete Job" button and a different submit label in edit mode). It also
needs a new tag-input box for skills that doesn't exist yet.
**What to do:**
- A3: Turn this page into a shared create/edit form (see TASK-020 comment
  in the file for full detail).
- A4: Build a simple tag-input box — type a word, press Enter/comma, get a
  removable pill (see TASK-021 comment in the file).
**Files they may need to check:** `company/dashboard.html` (has an old,
separate "Edit Job" modal that this shared form is meant to replace — see
TASK-019 comment there), `jobs/detail.html` (skills need to display there
too — see TASK-008 comment).
**Expected result:** One HTML structure that Simrika (D2) can reuse for
both creating and editing jobs; a working tag input that produces a
comma-separated skills string.
**Difficulty:** 🟡 Intermediate — mostly layout/JS-UI work, but reused
across two workflows (create vs edit) so it needs care.

### TASK-002 — A2: Profile Edit popover (visual only)

**Title:** Build the Profile Edit popover's look
**File(s):** `job-portal-frontend/js/shared.js` (and new CSS)
**Function/Section:** `renderNavbar()` — the profile circle icon markup
(`navbar-user-avatar`)
**Problem:** There is no popover UI at all yet for editing a profile.
**What to do:** Build a small floating box (Name, Email, Password, +
Description for companies) that opens/closes from the navbar circle icon.
**Note:** The name label next to the circle (the "small addition" in the
brief) is already implemented — see the NOTE comment right above the
`authSection` template in `renderNavbar()`.
**Expected result:** Clicking the circle shows the popover; clicking away
or an "X" closes it; matches the Figma "Profile Edit" screens.
**Difficulty:** 🟢 Beginner — visual/CSS work, reused everywhere but
conceptually simple.

### TASK-023 — A1 (part of): Split Admin into 3 pages

**Title:** Split the single admin dashboard into 3 real pages
**File(s):** `job-portal-frontend/admin/dashboard.html`
**Function/Section:** The `<section class="admin-hero">` intro, "Section 1:
Company Approvals", and "Section 2: User Directory" blocks
**Problem:** This is currently one long page; the team wants 3 separate
pages (Homepage, Company Approvals, User Directory) plus the existing "Add
Admin" popup kept as a popup (not a 4th page).
**What to do:** Split into 3 HTML files matching Figma; keep the Add Admin
popup pattern.
**Files they may need to check:** `js/shared.js` `renderNavbar()` (admin nav
link currently points at one page).
**Expected result:** 3 working admin pages + the existing popup carried over.
**Difficulty:** 🟡 Intermediate — mostly copy/restructure, some navigation
wiring to get right.

### TASK-025 — A5 & A6: Design consistency + CSS organization

**Title:** No `<style>` blocks in HTML; consistent shared styles
**File(s):** ALL 10 HTML pages (see TASK-001 list) + `css/style.css`
**Function/Section:** Every `<style>` block at the top of each page;
`:root` design tokens at the top of `css/style.css`
**Problem:** Every page has its own `<style>` block duplicating/diverging
from the shared CSS files, causing inconsistent buttons/spacing/colors.
**What to do:** Move all page-specific `<style>` rules into the right `.css`
file (global `style.css`, or a section-specific file like `auth.css`,
`jobs.css`, `dashboard.css`); reuse existing tokens/classes instead of
inventing new ones per page.
**Expected result:** No page has a `<style>` tag; everything still looks
correct via linked CSS files.
**Difficulty:** 🟡 Intermediate — not logically hard, but touches every
page and needs consistency checking across all of them.

---

## Sagar — Integration & Testing

### TASK-002 (continued) / TASK-010 — B1: Profile Edit popover behaviour

**Title:** Make the Profile Edit popover actually work
**File(s):** `job-portal-frontend/js/shared.js`, `job-portal-frontend/js/api.js`
**Function/Section:** New `initProfilePopover()` function (to be added near
`renderNavbar()` in `shared.js`); new `apiUpdateMyProfile()` helper (to be
added in `api.js`, see TASK-010 comment there)
**Problem:** Clicking the circle icon does nothing yet — no open/close,
no loading current info, no saving.
**What to do:** Wire the popover Robins builds (A2) to actually open/close,
pre-fill the current user's name/email, and save changes via the new
backend routes (TASK-009, owned by Ugeesha/Simrika/Reeju).
**Files they may need to check:** `app/routes/auth_routes.py` (TASK-009 —
the 3 backend routes this will call).
**Expected result:** On any page, the circle icon lets you update your
name/email/password, the same way everywhere.
**Difficulty:** 🟡 Intermediate — one shared implementation used by every
role, so needs to handle 3 slightly different payloads (user/company/admin).

### B2 — Fit all the pieces together

**Title:** Integration pass across C, D, and E's work
**File(s):** N/A — this is an ongoing process task, not a single code
location.
**What to do:** Regularly pull everyone's work together and click through
it, catching mismatches (e.g. a button whose ID doesn't match what the JS
expects).
**Expected result:** Fewer last-minute integration surprises.
**Difficulty:** 🟡 Intermediate — requires understanding the whole app, but
no new features to build.

### B3 — Write tests for the important features

**Title:** Automated tests for core flows
**File(s):** New test files (e.g. a new `tests/` folder in
`job-portal-backend/`) — none exist yet in the codebase.
**What to do:** Write tests for register, login, post job, apply to job,
approve/reject applicant, approve company, plus 1–2 full end-to-end flow
tests.
**Expected result:** Running the test suite catches breakage automatically.
**Difficulty:** 🔴 Advanced — requires understanding Flask test clients /
fixtures and touches most of the backend.

### B4 — Final full walkthrough (QA pass)

**Title:** Manual QA pass as each user type
**File(s):** N/A — manual testing across the whole site, after other
tasks are merged.
**What to do:** Use the site as a job seeker, company, and admin; note
anything broken or confusing.
**Expected result:** A list of issues found before submission.
**Difficulty:** 🟢 Beginner — no code changes, just careful testing and
note-taking (best done last, after most other tasks are merged).

---

## Ugeesha — Authentication & Admin

### TASK-005 — C1: Wire up Login and Register on the new pages

**Title:** Preserve existing login/register logic on Robins' new pages
**File(s):** `job-portal-frontend/auth/login.html`,
`job-portal-frontend/auth/register.html`
**Function/Section:** The `<script>` block at the bottom of each page
(login form submit handler)
**Problem:** The login logic already works today — the risk is losing it
when Robins rebuilds the page HTML/CSS.
**What to do:** Make sure the element IDs the script expects
(`login-form`, `login-email`, `login-password`, `login-role`, etc.) still
match the new page, or update the script to match new IDs.
**Expected result:** New-look pages behave exactly like the old site
(correct role, correct redirect, clear error on wrong password).
**Difficulty:** 🟢 Beginner — logic already exists, just needs
reconnecting to new HTML.

### TASK-023 — C2: Backend wiring for the 3 admin pages + Add Admin popup

**Title:** Connect the 3 admin pages to existing backend features
**File(s):** `job-portal-frontend/admin/dashboard.html`,
`job-portal-backend/app/routes/admin_routes.py` (reference only — this
backend file already works and needs no changes)
**Function/Section:** See TASK-023 comment in `admin/dashboard.html`
**Problem:** Most of the backend for approvals/user directory/revoke
already works — this task is mostly about wiring the new 3-page layout
(built by Robins, A1) to those existing working endpoints, plus building
the Add Admin popup using the same pattern as the Profile Edit popover.
**Expected result:** All 3 admin pages work end-to-end; Add Admin popup
creates a real admin account.
**Difficulty:** 🟡 Intermediate — mostly reconnecting existing working
backend calls to new page structure.

### TASK-009c — C3: Admin's own Profile Edit (new backend route)

**Title:** Let a logged-in admin update their own name/email/password
**File(s):** `job-portal-backend/app/routes/auth_routes.py`,
`job-portal-backend/app/services/auth_service.py`
**Function/Section:** See the TASK-009 comment block above the
`company_test_route` in `auth_routes.py`, and the note above
`register_user()` in `auth_service.py`
**Problem:** No route exists at all for an admin to edit their own account.
**What to do:** Add a new `PUT /api/auth/me/admin` route + service function,
following the pattern of `register_user`/`register_company`. Hash any new
password with `bcrypt.generate_password_hash(...)` before saving.
**Files they may need to check:** `app/models/admin.py` (the Admin model).
**Expected result:** An admin can change their password and it works next
login.
**Difficulty:** 🟡 Intermediate — new route + service function, needs
correct password hashing and session handling.

### TASK-004 — C4: Remove the "Forgot Password" link

**Title:** Remove the dead "Forgot Password?" link
**File(s):** `job-portal-frontend/auth/login.html`
**Function/Section:** The `<a href="#" class="forgot-link">` element (see
TASK-004 comment directly above it)
**Problem:** This link goes nowhere and does nothing.
**What to do:** Delete the element (and unused CSS rule) — do not build a
forgot-password feature.
**Expected result:** New login page has no such link.
**Difficulty:** 🟢 Beginner — delete a few lines.

---

## Simrika — Company Side

### TASK-020 — D2: Shared Post Job / Edit Job logic

**Title:** Make the shared form (A3) actually save/create/edit/delete jobs
**File(s):** `job-portal-frontend/company/post-job.html`,
`job-portal-frontend/company/dashboard.html`
**Function/Section:** See TASK-020 comment in `post-job.html`; existing
`apiCreateJob`/`apiUpdateJob`/`apiDeleteJob` calls to reuse from
`js/api.js`; existing `deleteJob()` confirm-dialog pattern in
`company/dashboard.html` to reuse for the new Delete Job button.
**Problem:** Once Robins (A3) builds one shared form, nothing yet makes it
work in both "create" and "edit" modes.
**What to do:** Wire create mode (already partly working) and add edit
mode (load existing job into the form, save back to the same job); wire
"Delete Job" with a confirm prompt.
**Expected result:** One form creates new jobs AND edits/deletes existing
ones correctly.
**Difficulty:** 🟡 Intermediate — needs careful state handling for the two
modes.

### TASK-008 — D3: Skills & Keywords feature (backend + wiring)

**Title:** Add a `skills` field to jobs and save/display it
**File(s):** `job-portal-backend/app/models/job.py`,
`job-portal-backend/app/routes/job_routes.py`,
`job-portal-backend/app/services/job_service.py`,
`job-portal-frontend/company/post-job.html`,
`job-portal-frontend/company/dashboard.html`,
`job-portal-frontend/jobs/detail.html`
**Function/Section:** `Job` model class + `to_dict()` (model);
`updatable_fields` list (routes); `create_job()` and `update_job()`
(service); form submit handlers (frontend); `renderJobDetail()` (detail page)
**Problem:** There is currently NO database field to store skills at all.
**What to do:** Add the `skills` column (simple comma-separated string,
e.g. "React, Figma, SQL"), include it in `to_dict()`, allow it in
create/update, and read/send it from the Post Job / Edit Job forms; display
it on the job detail page.
**Expected result:** Add "React, Figma, SQL" when posting a job, see it
saved and displayed later on that job's detail page.
**Difficulty:** 🟡 Intermediate — touches model, two service functions,
two routes, and three frontend files, but each change is small.

### TASK-009b — D4: Company Profile editing (new backend route)

**Title:** Let a logged-in company update name/email/password/description
**File(s):** `job-portal-backend/app/routes/auth_routes.py`,
`job-portal-backend/app/services/auth_service.py`
**Function/Section:** See TASK-009 comment block in `auth_routes.py`; note
above `register_user()` in `auth_service.py`
**Problem:** No route exists for a company to edit its own account,
including the description (which currently can only be set once, at
registration).
**What to do:** Add `PUT /api/auth/me/company` + service function, same
pattern as C3/E7. Make sure `description` is included and can be updated.
**Expected result:** A company can update all 4 fields, including setting
a new description for the first time since registration.
**Difficulty:** 🟡 Intermediate — same shape as C3/E7, one extra field.

### TASK-018 — D5: Show companies their approval status clearly

**Title:** Warn not-yet-approved companies on their dashboard
**File(s):** `job-portal-frontend/company/dashboard.html`
**Function/Section:** `DOMContentLoaded` handler, right after the "Set User
Greeting" block (see TASK-018 comment)
**Problem:** A pending/rejected company only discovers they can't post jobs
when they try and get a confusing backend error.
**What to do:** Check `user.status` (already available from
`getLoggedInUser()`) and show a clear banner if `'pending'` or `'rejected'`.
**Expected result:** A brand-new company sees "Your account is waiting for
approval" immediately on login — no guessing.
**Difficulty:** 🟢 Beginner — the status is already available; just needs
a conditional banner.

### TASK-006 — D6: Fix the résumé download security problem (MOST CRITICAL)

**Title:** Add an ownership check to the résumé download route
**File(s):** `job-portal-backend/app/routes/application_routes.py`
**Function/Section:** `download_resume()` (see the large TASK-006 comment
directly above it)
**Problem:** Anyone with the URL can download any candidate's résumé —
there is no login or ownership check at all.
**What to do:** Require login; only allow (a) the job seeker who uploaded
it, or (b) the company that owns the job it was submitted to. Return 403
for everyone else.
**Files they may need to check:** `app/models/application.py` (Application
model, to look up who owns the résumé);
`job-portal-frontend/company/applicants.html` (existing download link, for
context); `job-portal-frontend/user/dashboard.html` (TASK-017 — the new
"View CV" link that depends on this fix).
**Expected result:** Only the two allowed people can open a given résumé
link; everyone else gets "not allowed."
**Difficulty:** 🔴 Advanced — security-sensitive; must correctly handle
both allowed cases (job seeker AND company) without breaking either.

### TASK-024 — D7: Limit the applicant status dropdown to 4 statuses

**Title:** Verify the status dropdown only shows the 4 agreed statuses
**File(s):** `job-portal-frontend/company/applicants.html`
**Function/Section:** The `<select onchange="handleStatusChange(...)">`
dropdown (see TASK-024 comment directly above it)
**Problem:** Need to confirm no 5th status (like "Interview Scheduled" or
"Offered", seen elsewhere in the old kanban board) ever gets shown or
saved here.
**What to do:** Double-check wording/casing matches
`app/models/application.py`'s Enum exactly (`applied`, `under_review`,
`shortlisted`, `rejected`).
**Expected result:** Only these 4 options ever appear or get saved.
**Difficulty:** 🟢 Beginner — this already looks correct; mostly a
verification task.

---

## Reeju — Job Seeker & Public Pages

### E1 — Wire up the Homepage

**Title:** Load real featured jobs + correct CTA links
**File(s):** `job-portal-frontend/js/home.js`
**Function/Section:** `loadHomeFeaturedJobs()`, `setHomeCtaLinks()`
**Problem/Status:** This already works today (loads real jobs, wires
"Browse All Jobs" / "Get Started" links). No TODO was added here — just
double-check it still works once Robins (A1) rebuilds `index.html`'s HTML/
CSS, since this script depends on specific element IDs
(`featured-jobs-grid`, `hero-browse-jobs`, etc.).
**Difficulty:** 🟢 Beginner — verification only, logic already exists.

### TASK-022 — E2: Wire up Job Listing and Job Detail pages (Apply CV popup)

**Title:** Restyle the working Apply flow to match the new "Apply CV" popup
**File(s):** `job-portal-frontend/jobs/detail.html`
**Function/Section:** The `#apply-modal` element (see TASK-022 comment
directly above it); the `apiApplyToJob` call further down in the `<script>`
**Problem:** The apply logic (upload résumé, create application) already
works — it just needs to be restyled to the new "Choose File" / "Submit
Application" popup look.
**What to do:** Restyle the modal to match Figma; verify the existing
upload/submit logic still works with the new HTML.
**Expected result:** Clicking "Apply Now" opens the new-look popup and
still successfully submits an application.
**Difficulty:** 🟢 Beginner — mostly restyling already-working logic.

### TASK-012 / TASK-017 — E3: User Dashboard's application list

**Title:** Replace the 6-column Kanban board with a 4-status "Recent
Applications" list
**File(s):** `job-portal-frontend/user/dashboard.html`
**Function/Section:** The `.kanban-board` HTML (see TASK-012 comment near
the Stats Grid) and `renderKanbanCards()` (see TASK-017 comment directly
above it)
**Problem:** Currently shows 6 statuses (including "interview_scheduled"
and "offered", which aren't real statuses); new design wants a simple list
showing only the 4 real statuses (`applied`, `under_review`, `shortlisted`,
`rejected` — see `app/models/application.py`).
**What to do:** Once Robins (A1) rebuilds the HTML as a list, rewrite
`renderKanbanCards()` to build list rows instead of 6 kanban columns.
**Expected result:** Dashboard shows a clean list of applications, only
ever using the 4 real statuses.
**Difficulty:** 🟡 Intermediate — needs care to remove all 6-status logic
consistently and not miss a spot.

### TASK-007 / TASK-011 — E4: User Dashboard's stat numbers

**Title:** Build and display the 4 application-count stats
**File(s):** `job-portal-backend/app/services/application_service.py`
(new function), `job-portal-backend/app/routes/application_routes.py` (new
route), `job-portal-frontend/js/api.js` (new helper, see TASK-011),
`job-portal-frontend/user/dashboard.html` (wire the numbers in, see the
note inside the `DOMContentLoaded` handler)
**Function/Section:** New `get_my_application_stats()` function (backend);
new `GET /api/applications/mine/stats` route; new `apiGetMyApplicationStats()`
(frontend)
**Problem:** No counting logic exists anywhere yet for a single job
seeker's own applications by status.
**What to do:** Add the backend function + route, the frontend API helper,
then call it on dashboard load and fill in the 4 stat boxes at the top of
the page.
**Expected result:** If 3 of 10 applications are "Shortlisted", the
dashboard shows "3" — correctly, every time.
**Difficulty:** 🟡 Intermediate — spans backend (new function + route) and
frontend (new API call + rendering), but each piece is simple.

### TASK-015 — E5: Remove the fake sample applications

**Title:** Delete `fallbackApps` fake data; show a real empty state instead
**File(s):** `job-portal-frontend/user/dashboard.html`
**Function/Section:** `const fallbackApps = [...]` and its use inside
`initKanbanBoard()` (see TASK-015 comment directly above the array)
**Problem:** A brand-new job seeker with zero real applications currently
sees 4 fake, made-up applications instead of a real empty message.
**What to do:** Delete the fake array and its usage; show a friendly
"You haven't applied to any jobs yet" message with a link to
`jobs/listing.html` (reuse the `showEmpty()` helper from `shared.js`).
**Expected result:** New users see an honest empty state, not fake data.
**Difficulty:** 🟢 Beginner — delete some code, add a simple message.

### TASK-016 — E6: Fix the "old data stuck on screen" bug

**Title:** Always fetch fresh applications instead of using cached data
**File(s):** `job-portal-frontend/user/dashboard.html`
**Function/Section:** `getApplicationsState()` / `saveApplicationsState()`
and their use inside `initKanbanBoard()` (see TASK-016 comment directly
above them)
**Problem:** The dashboard checks `sessionStorage` first and may show
stale data instead of asking the server every time.
**What to do:** Stop using sessionStorage as a cache for this list; always
call `apiGetMyApplications()` fresh on page load.
**Expected result:** Apply to a job, go straight to the dashboard, and see
it appear immediately — no logout required.
**Difficulty:** 🟢 Beginner — remove a caching shortcut, always fetch fresh.

### TASK-009a — E7: Job Seeker Profile editing (new backend route)

**Title:** Let a logged-in job seeker update their name/email/password
**File(s):** `job-portal-backend/app/routes/auth_routes.py`,
`job-portal-backend/app/services/auth_service.py`
**Function/Section:** See TASK-009 comment block in `auth_routes.py`; note
above `register_user()` in `auth_service.py`
**Problem:** No route exists yet for a job seeker to edit their own account.
**What to do:** Add `PUT /api/auth/me/user` + service function, same
pattern as C3/D4. Hash any new password before saving.
**Expected result:** A job seeker can update their name/email/password and
it works on next login.
**Difficulty:** 🟡 Intermediate — same shape as C3/D4.

### TASK-014 — E8: Move JavaScript out of the HTML pages

**Title:** Extract inline `<script>` logic into separate .js files
**File(s):** `job-portal-frontend/user/dashboard.html` (primary — see
TASK-014 comment above the `<script>` tags), also worth checking
`index.html`, `jobs/listing.html`, `jobs/detail.html` for the same pattern
**Problem:** A lot of page logic is written directly inside the HTML file
in a `<script>` block instead of its own `.js` file.
**What to do:** Move the logic (e.g. into `js/user-dashboard.js`) and link
to it the same way `config.js`/`shared.js`/`api.js` are already linked.
**Expected result:** Cleaner HTML files; logic lives in dedicated `.js`
files.
**Difficulty:** 🟢 Beginner — mostly copy-paste + fixing the `<script src>` tag.

### TASK-017 — E9: Let job seekers view their own CV after applying

**Title:** Add a "View CV" link to each application row
**File(s):** `job-portal-frontend/user/dashboard.html`
**Function/Section:** `renderKanbanCards()` (see TASK-017 comment, same
location as the E3 task above — these two are combined in one comment
block since they touch the same function)
**Problem:** Once a job seeker applies, there's currently no way to view
their uploaded résumé again.
**What to do:** Add a small "View CV" link above the status text on each
application row, pointing at `app.resume_url` (the same download link
Simrika secures in D6/TASK-006). This only works correctly once TASK-006
is done.
**Expected result:** Clicking "View CV" next to any application opens the
exact résumé file that was uploaded for it.
**Difficulty:** 🟢 Beginner — small addition, but depends on D6 (TASK-006)
being finished first.

---

## Quick Reference — Task ID → Files

| Task ID | Files |
|---|---|
| TASK-001 | All 10 HTML pages, `js/shared.js` |
| TASK-002 | `js/shared.js` |
| TASK-003 | All 10 HTML pages (same insertion point as TASK-001) |
| TASK-004 | `auth/login.html` |
| TASK-005 | `auth/login.html`, `auth/register.html` |
| TASK-006 | `app/routes/application_routes.py` |
| TASK-007 | `app/services/application_service.py` |
| TASK-008 | `app/models/job.py`, `app/routes/job_routes.py`, `app/services/job_service.py`, `company/post-job.html`, `company/dashboard.html`, `jobs/detail.html` |
| TASK-009 | `app/routes/auth_routes.py`, `app/services/auth_service.py` |
| TASK-010 | `js/api.js` |
| TASK-011 | `js/api.js`, `user/dashboard.html` |
| TASK-012 | `user/dashboard.html` |
| TASK-014 | `user/dashboard.html` |
| TASK-015 | `user/dashboard.html` |
| TASK-016 | `user/dashboard.html` |
| TASK-017 | `user/dashboard.html` |
| TASK-018 | `company/dashboard.html` |
| TASK-019 | `company/dashboard.html` |
| TASK-020 | `company/post-job.html` |
| TASK-021 | `company/post-job.html` |
| TASK-022 | `jobs/detail.html` |
| TASK-023 | `admin/dashboard.html` |
| TASK-024 | `company/applicants.html` |
| TASK-025 | All 10 HTML pages, `css/style.css` |

**Not tied to a single code location (process tasks):** B2 (integration
pass), B3 (write tests — new files), B4 (final QA walkthrough).
