// js/applications.js — Application Management & Status Tracking
//
// Handles basic fetch() calls related to job applications and status updates.
// Used by: jobs/detail.html, user/dashboard.html, company/applicants.html
// Depends on: config.js (for API_BASE_URL), shared.js


// applyToJob(event)
// Sends basic POST request to /api/applications endpoint.
async function applyToJob(event) {
    if (event) event.preventDefault();
    try {
        const response = await fetch(`${API_BASE_URL}/applications`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_id: 1, user_id: 1, resume_path: 'uploads/sample.pdf' })
        });
        const data = await response.json();
        console.log('[Application Route Connection - Apply]:', data);
        return data;
    } catch (error) {
        console.error('[Application Route Error - Apply]:', error);
    }
}


// loadMyApplications()
// Sends basic GET request to /api/applications/mine endpoint.
async function loadMyApplications() {
    try {
        const response = await fetch(`${API_BASE_URL}/applications/mine`);
        const data = await response.json();
        console.log('[Application Route Connection - My Applications]:', data);
        return data;
    } catch (error) {
        console.error('[Application Route Error - My Applications]:', error);
    }
}


// loadJobApplicants(jobId)
// Sends basic GET request to /api/jobs/<id>/applications endpoint.
async function loadJobApplicants(jobId = 1) {
    try {
        const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/applications`);
        const data = await response.json();
        console.log('[Application Route Connection - Job Applicants]:', data);
        return data;
    } catch (error) {
        console.error('[Application Route Error - Job Applicants]:', error);
    }
}


// updateApplicationStatus(applicationId, newStatus)
// Sends basic PUT request to /api/applications/<id>/status endpoint.
async function updateApplicationStatus(applicationId = 1, newStatus = 'under_review') {
    try {
        const response = await fetch(`${API_BASE_URL}/applications/${applicationId}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        const data = await response.json();
        console.log('[Application Route Connection - Update Status]:', data);
        return data;
    } catch (error) {
        console.error('[Application Route Error - Update Status]:', error);
    }
}

