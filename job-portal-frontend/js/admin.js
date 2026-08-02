// js/admin.js — Admin Dashboard Operations
//
// Refactored to use centralized API functions from api.js
// Used by: admin/dashboard.html
// Depends on: config.js, shared.js, api.js


// loadPendingCompanies()
// Uses apiGetPendingCompanies from api.js
async function loadPendingCompanies() {
    const { ok, data } = await apiGetPendingCompanies();
    console.log('[Admin Route Connection - Pending Companies]:', data);
    return { ok, data };
}


// approveCompany(companyId)
// Uses apiApproveCompany from api.js
async function approveCompany(companyId = 1) {
    const { ok, data } = await apiApproveCompany(companyId);
    console.log('[Admin Route Connection - Approve Company]:', data);
    return { ok, data };
}


// rejectCompany(companyId)
// Uses apiRejectCompany from api.js
async function rejectCompany(companyId = 1) {
    const { ok, data } = await apiRejectCompany(companyId);
    console.log('[Admin Route Connection - Reject Company]:', data);
    return { ok, data };
}


// deleteAdminJob(jobId)
// Uses apiAdminDeleteJob from api.js
async function deleteAdminJob(jobId = 1) {
    const { ok, data } = await apiAdminDeleteJob(jobId);
    console.log('[Admin Route Connection - Delete Job]:', data);
    return { ok, data };
}


// deleteAdminUser(userId)
// Uses apiAdminDeleteUser from api.js
async function deleteAdminUser(userId = 1) {
    const { ok, data } = await apiAdminDeleteUser(userId);
    console.log('[Admin Route Connection - Delete User]:', data);
    return { ok, data };
}


// deleteAdminCompany(companyId)
// Uses apiAdminDeleteCompany from api.js
async function deleteAdminCompany(companyId = 1) {
    const { ok, data } = await apiAdminDeleteCompany(companyId);
    console.log('[Admin Route Connection - Delete Company]:', data);
    return { ok, data };
}

