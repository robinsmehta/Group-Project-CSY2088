// ============================================================
// js/jobs.js — Job Listings: Browse, Search, Detail, Post, Edit, Delete
//
// Handles basic fetch() calls related to job listings.
// Used by: index.html, jobs/listing.html, jobs/detail.html,
//          company/dashboard.html, company/post-job.html
// Depends on: config.js (for API_BASE_URL), shared.js
// ============================================================


// ------------------------------------------------------------
// loadJobs()
// Sends basic GET request to /api/jobs endpoint.
// ------------------------------------------------------------
async function loadJobs() {
    try {
        const response = await fetch(`${API_BASE_URL}/jobs`);
        const data = await response.json();
        console.log('[Jobs Route Connection - Load Jobs]:', data);
        return data;
    } catch (error) {
        console.error('[Jobs Route Error - Load Jobs]:', error);
    }
}


// ------------------------------------------------------------
// loadFeaturedJobs()
// Sends basic GET request to /api/jobs endpoint.
// ------------------------------------------------------------
async function loadFeaturedJobs() {
    return await loadJobs();
}


// ------------------------------------------------------------
// searchJobs(query)
// Sends basic GET request with search query.
// ------------------------------------------------------------
async function searchJobs(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/jobs?search=${encodeURIComponent(query || '')}`);
        const data = await response.json();
        console.log('[Jobs Route Connection - Search Jobs]:', data);
        return data;
    } catch (error) {
        console.error('[Jobs Route Error - Search Jobs]:', error);
    }
}


// ------------------------------------------------------------
// loadJobDetail(jobId)
// Sends basic GET request to /api/jobs/<id> endpoint.
// ------------------------------------------------------------
async function loadJobDetail(jobId = 1) {
    try {
        const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
        const data = await response.json();
        console.log('[Jobs Route Connection - Job Detail]:', data);
        return data;
    } catch (error) {
        console.error('[Jobs Route Error - Job Detail]:', error);
    }
}


// ------------------------------------------------------------
// postJob(event)
// Sends basic POST request to /api/jobs endpoint.
// ------------------------------------------------------------
async function postJob(event) {
    if (event) event.preventDefault();
    try {
        const response = await fetch(`${API_BASE_URL}/jobs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: 'Test Job', description: 'Test', location: 'Remote', category: 'Tech', salary: '$50k' })
        });
        const data = await response.json();
        console.log('[Jobs Route Connection - Post Job]:', data);
        return data;
    } catch (error) {
        console.error('[Jobs Route Error - Post Job]:', error);
    }
}


// ------------------------------------------------------------
// deleteJob(jobId)
// Sends basic DELETE request to /api/jobs/<id> endpoint.
// ------------------------------------------------------------
async function deleteJob(jobId) {
    try {
        const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`, { method: 'DELETE' });
        const data = await response.json();
        console.log('[Jobs Route Connection - Delete Job]:', data);
        return data;
    } catch (error) {
        console.error('[Jobs Route Error - Delete Job]:', error);
    }
}

