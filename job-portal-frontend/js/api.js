// js/api.js — Centralised API Client
// Handles all HTTP requests to the backend API.
// Depends on: config.js (API_BASE_URL)

// Core fetch wrapper with session-cookie support
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
        // Return structured error response when network failure occurs
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

// Authentication API functions

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

async function apiUpdateMyProfile(payload) {
    const user = typeof getLoggedInUser === 'function' ? getLoggedInUser() : null;
    const role = user?.role;
    if (role === 'user') {
        return apiFetch('/auth/me/user', { method: 'PUT', body: payload });
    } else if (role === 'company') {
        return apiFetch('/auth/me/company', { method: 'PUT', body: payload });
    } else if (role === 'admin') {
        return apiFetch('/admin/profile', { method: 'PUT', body: payload });
    }
    return { ok: false, status: 400, data: { error: 'Unknown or unauthenticated user role' } };
}

// Job API functions

async function apiGetJobs(params = {}) {
    const qs = new URLSearchParams();
    if (params.keyword)   qs.set('keyword',   params.keyword);
    if (params.location)  qs.set('location',  params.location);
    if (params.category)  qs.set('category',  params.category);
    if (params.page)      qs.set('page',      String(params.page));
    if (params.per_page)  qs.set('per_page',  String(params.per_page));
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

// Application API functions

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

async function apiGetCompanyApplicants() {
    return apiFetch('/applications/company');
}

async function apiUpdateApplicationStatus(applicationId, status) {
    return apiFetch(`/applications/${applicationId}/status`, {
        method: 'PUT',
        body: { status }
    });
}

// Admin API functions

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

async function apiUpdateAdminProfile(name, email, password) {
    return apiFetch('/admin/profile', { method: 'PUT', body: { name, email, password } });
}
