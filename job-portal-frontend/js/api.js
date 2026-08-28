// js/api.js — Centralised API Client
// All HTTP calls go through this layer.
// Depends on: config.js (API_BASE_URL)

// ---------------------------------------------------------------------------
// Core fetch wrapper with session-cookie support
// ---------------------------------------------------------------------------
async function apiFetch(path, options = {}) {
    const url = `${API_BASE_URL}${path}`;
    const defaults = { credentials: 'include' };
    const merged = { ...defaults, ...options };
    if (merged.body && typeof merged.body === 'object' && !(merged.body instanceof FormData)) {
        merged.headers = { 'Content-Type': 'application/json', ...(merged.headers || {}) };
        merged.body = JSON.stringify(merged.body);
    }
    let res;
    try {
        res = await fetch(url, merged);
    } catch (networkErr) {
        // Network failure (backend unreachable, CORS block, offline, etc.)
        // Return the same {ok,status,data} shape callers already expect instead
        // of throwing, so every page's existing "couldn't load" fallback runs
        // instead of leaving the UI stuck on its loading state forever.
        console.warn(`[API] Network error calling ${url}:`, networkErr.message);
        return {
            ok: false,
            status: 0,
            data: { error: 'Could not reach the server. Please check your connection and try again.' }
        };
    }

    let data;
    try { data = await res.json(); } catch (_) { data = {}; }

    if (res.status === 401) {
        clearAuthState();
        if (typeof window !== 'undefined' && window.location) {
            window.location.href = resolveSitePath('auth/login.html');
        }
    }

    return { ok: res.ok, status: res.status, data };
}

// ===========================================================================
// AUTH
// ===========================================================================

async function apiLogin(email, password, role) {
    return apiFetch('/auth/login', { method: 'POST', body: { email, password, role } });
}

async function apiLogout() {
    return apiFetch('/auth/logout', { method: 'POST' });
}

async function apiRegisterUser(name, email, password) {
    return apiFetch('/auth/register/user', { method: 'POST', body: { name, email, password } });
}

async function apiRegisterCompany(company_name, email, password, description) {
    return apiFetch('/auth/register/company', { method: 'POST', body: { company_name, email, password, description } });
}

// ===========================================================================
// JOBS
// ===========================================================================

async function apiGetJobs(params = {}) {
    const qs = new URLSearchParams();
    if (params.keyword)  qs.set('keyword',  params.keyword);
    if (params.location) qs.set('location', params.location);
    if (params.category) qs.set('category', params.category);
    const query = qs.toString() ? `?${qs.toString()}` : '';
    return apiFetch(`/jobs${query}`);
}

async function apiGetJob(jobId) {
    return apiFetch(`/jobs/${jobId}`);
}

async function apiCreateJob(jobData) {
    return apiFetch('/jobs', { method: 'POST', body: jobData });
}

async function apiDeleteJob(jobId) {
    return apiFetch(`/jobs/${jobId}`, { method: 'DELETE' });
}

async function apiUpdateJob(jobId, jobData) {
    return apiFetch(`/jobs/${jobId}`, { method: 'PUT', body: jobData });
}

// ===========================================================================
// APPLICATIONS
// ===========================================================================

async function apiGetMyApplications() {
    return apiFetch('/applications/mine');
}

async function apiApplyToJob(jobId, resumeFile) {
    const formData = new FormData();
    formData.append('job_id', jobId);
    if (resumeFile) formData.append('resume', resumeFile);
    return apiFetch('/applications', { method: 'POST', body: formData });
}

async function apiGetJobApplicants(jobId) {
    return apiFetch(`/applications/job/${jobId}`);
}

async function apiUpdateApplicationStatus(applicationId, status) {
    return apiFetch(`/applications/${applicationId}/status`, {
        method: 'PUT',
        body: { status }
    });
}

// ===========================================================================
// TODO — TASK-010 (Sagar / B1): Add API helper functions for the shared
// Profile Edit popover.
//
// PROBLEM:
// The Profile Edit popover (built visually by Robins/A, wired up by you)
// needs to call the backend to save name/email/password changes. There are
// no functions in this file yet for that — only register/login exist above.
//
// WHAT YOU NEED TO DO:
// Add functions here, following the exact same pattern as apiLogin /
// apiRegisterUser above, one for each account type (they call the three
// backend routes Ugeesha/Simrika/Reeju are each adding — see the
// TASK-009 TODOs in app/routes/auth_routes.py on the backend):
//
//   async function apiUpdateMyProfile(role, payload) {
//       // role is 'user' | 'company' | 'admin' — pick the right endpoint,
//       // e.g. `/auth/me/${role}`, and PUT the payload (name/email/password,
//       // + description for company).
//       return apiFetch(`/auth/me/${role}`, { method: 'PUT', body: payload });
//   }
//
// HOW THIS PART CONNECTS:
// Your popover code in shared.js will call this function when the user
// clicks "Update" inside the Profile Edit popover.
//
// ASSIGNED TASK:
// Sagar (B1) — Build the Profile Edit popover's actual behavior.
// ===========================================================================

// TODO — TASK-011 (Reeju / E4): add a helper function here for the new
// "my application stats" endpoint once it exists on the backend (see the
// TASK-007 TODO in app/services/application_service.py), e.g.:
//   async function apiGetMyApplicationStats() {
//       return apiFetch('/applications/mine/stats');
//   }
// The User Dashboard's 4 stat numbers will call this.

// ===========================================================================
// ADMIN
// ===========================================================================

async function apiGetPendingCompanies(search) {
    const qs = new URLSearchParams();
    if (search) qs.set('search', search);
    const query = qs.toString() ? `?${qs.toString()}` : '';
    return apiFetch(`/admin/companies/pending${query}`);
}

async function apiGetUsers(page = 1, search, per_page) {
    const qs = new URLSearchParams();
    if (page) qs.set('page', String(page));
    if (per_page) qs.set('per_page', String(per_page));
    if (search) qs.set('search', search);
    const query = qs.toString() ? `?${qs.toString()}` : '';
    return apiFetch(`/admin/users${query}`);
}

async function apiCreateAdmin(name, email, password) {
    return apiFetch('/admin/admins', { method: 'POST', body: { name, email, password } });
}

async function apiRevokeUser(userId) {
    return apiFetch(`/admin/users/${userId}/revoke`, { method: 'PUT' });
}

async function apiRestoreUser(userId) {
    return apiFetch(`/admin/users/${userId}/restore`, { method: 'PUT' });
}

async function apiRevokeCompany(companyId) {
    return apiFetch(`/admin/companies/${companyId}/revoke`, { method: 'PUT' });
}

async function apiRestoreCompany(companyId) {
    return apiFetch(`/admin/companies/${companyId}/restore`, { method: 'PUT' });
}

async function apiApproveCompany(companyId) {
    return apiFetch(`/admin/companies/${companyId}/approve`, { method: 'PUT' });
}

async function apiRejectCompany(companyId) {
    return apiFetch(`/admin/companies/${companyId}/reject`, { method: 'PUT' });
}

async function apiAdminDeleteJob(jobId) {
    return apiFetch(`/admin/jobs/${jobId}`, { method: 'DELETE' });
}

async function apiAdminDeleteUser(userId) {
    return apiFetch(`/admin/users/${userId}`, { method: 'DELETE' });
}

async function apiAdminDeleteCompany(companyId) {
    return apiFetch(`/admin/companies/${companyId}`, { method: 'DELETE' });
}

async function apiGetAdminStats() {
    return apiFetch('/admin/stats');
}
