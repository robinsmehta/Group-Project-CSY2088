// ============================================================
// js/admin.js — Admin Dashboard Operations
//
// Handles basic fetch() calls for administrator moderation actions.
// Used by: admin/dashboard.html
// Depends on: config.js (for API_BASE_URL), shared.js
// ============================================================


// ------------------------------------------------------------
// loadPendingCompanies()
// Sends basic GET request to /api/admin/companies/pending endpoint.
// ------------------------------------------------------------
async function loadPendingCompanies() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/companies/pending`);
        const data = await response.json();
        console.log('[Admin Route Connection - Pending Companies]:', data);
        return data;
    } catch (error) {
        console.error('[Admin Route Error - Pending Companies]:', error);
    }
}


// ------------------------------------------------------------
// approveCompany(companyId)
// Sends basic PUT request to /api/admin/companies/<id>/approve endpoint.
// ------------------------------------------------------------
async function approveCompany(companyId = 1) {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/companies/${companyId}/approve`, { method: 'PUT' });
        const data = await response.json();
        console.log('[Admin Route Connection - Approve Company]:', data);
        return data;
    } catch (error) {
        console.error('[Admin Route Error - Approve Company]:', error);
    }
}


// ------------------------------------------------------------
// rejectCompany(companyId)
// Sends basic PUT request to /api/admin/companies/<id>/reject endpoint.
// ------------------------------------------------------------
async function rejectCompany(companyId = 1) {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/companies/${companyId}/reject`, { method: 'PUT' });
        const data = await response.json();
        console.log('[Admin Route Connection - Reject Company]:', data);
        return data;
    } catch (error) {
        console.error('[Admin Route Error - Reject Company]:', error);
    }
}


// ------------------------------------------------------------
// deleteAdminJob(jobId)
// Sends basic DELETE request to /api/admin/jobs/<id> endpoint.
// ------------------------------------------------------------
async function deleteAdminJob(jobId = 1) {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/jobs/${jobId}`, { method: 'DELETE' });
        const data = await response.json();
        console.log('[Admin Route Connection - Delete Job]:', data);
        return data;
    } catch (error) {
        console.error('[Admin Route Error - Delete Job]:', error);
    }
}


// ------------------------------------------------------------
// deleteAdminUser(userId)
// Sends basic DELETE request to /api/admin/users/<id> endpoint.
// ------------------------------------------------------------
async function deleteAdminUser(userId = 1) {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, { method: 'DELETE' });
        const data = await response.json();
        console.log('[Admin Route Connection - Delete User]:', data);
        return data;
    } catch (error) {
        console.error('[Admin Route Error - Delete User]:', error);
    }
}


// ------------------------------------------------------------
// deleteAdminCompany(companyId)
// Sends basic DELETE request to /api/admin/companies/<id> endpoint.
// ------------------------------------------------------------
async function deleteAdminCompany(companyId = 1) {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/companies/${companyId}`, { method: 'DELETE' });
        const data = await response.json();
        console.log('[Admin Route Connection - Delete Company]:', data);
        return data;
    } catch (error) {
        console.error('[Admin Route Error - Delete Company]:', error);
    }
}

