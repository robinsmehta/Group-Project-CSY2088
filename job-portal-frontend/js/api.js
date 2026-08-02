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
    const res = await fetch(url, merged);
    let data;
    try { data = await res.json(); } catch (_) { data = {}; }
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
// ADMIN
// ===========================================================================

async function apiGetPendingCompanies() {
    return apiFetch('/admin/companies/pending');
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
