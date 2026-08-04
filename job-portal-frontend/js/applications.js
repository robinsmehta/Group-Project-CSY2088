// js/applications.js — Application Management & Status Tracking
//
// Refactored to use centralized API functions from api.js
// Used by: jobs/detail.html, user/dashboard.html, company/applicants.html
// Depends on: config.js, shared.js, api.js


// applyToJob(event)
// Uses apiApplyToJob from api.js
async function applyToJob(event) {
    if (event) event.preventDefault();
    const resumeFile = event?.target?.querySelector('#resume-file')?.files[0];
    const jobId = 1; // This should be passed as parameter in real usage
    const { ok, data } = await apiApplyToJob(jobId, resumeFile);
    console.log('[Application Route Connection - Apply]:', data);
    return { ok, data };
}


// loadMyApplications()
// Uses apiGetMyApplications from api.js
async function loadMyApplications() {
    const { ok, data } = await apiGetMyApplications();
    console.log('[Application Route Connection - My Applications]:', data);
    return { ok, data };
}


// loadJobApplicants(jobId)
// Uses apiGetJobApplicants from api.js
async function loadJobApplicants(jobId = 1) {
    const { ok, data } = await apiGetJobApplicants(jobId);
    console.log('[Application Route Connection - Job Applicants]:', data);
    return { ok, data };
}


// updateApplicationStatus(applicationId, newStatus)
// Uses apiUpdateApplicationStatus from api.js
async function updateApplicationStatus(applicationId = 1, newStatus = 'under_review') {
    const { ok, data } = await apiUpdateApplicationStatus(applicationId, newStatus);
    console.log('[Application Route Connection - Update Status]:', data);
    return { ok, data };
}

