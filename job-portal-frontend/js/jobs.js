// js/jobs.js — Job Listings: Browse, Search, Detail, Post, Edit, Delete
//
// Refactored to use centralized API functions from api.js
// Used by: index.html, jobs/listing.html, jobs/detail.html,
//          company/dashboard.html, company/post-job.html
// Depends on: config.js, shared.js, api.js


// loadJobs()
// Uses apiGetJobs from api.js
async function loadJobs() {
    const { ok, data } = await apiGetJobs();
    console.log('[Jobs Route Connection - Load Jobs]:', data);
    return { ok, data };
}


// loadFeaturedJobs()
// Uses apiGetJobs from api.js
async function loadFeaturedJobs() {
    return await loadJobs();
}


// searchJobs(query)
// Uses apiGetJobs with keyword parameter from api.js
async function searchJobs(query) {
    const { ok, data } = await apiGetJobs({ keyword: query });
    console.log('[Jobs Route Connection - Search Jobs]:', data);
    return { ok, data };
}


// loadJobDetail(jobId)
// Uses apiGetJob from api.js
async function loadJobDetail(jobId = 1) {
    const { ok, data } = await apiGetJob(jobId);
    console.log('[Jobs Route Connection - Job Detail]:', data);
    return { ok, data };
}


// postJob(event)
// Uses apiCreateJob from api.js
async function postJob(event) {
    if (event) event.preventDefault();
    const jobData = {
        title: 'Test Job',
        description: 'Test',
        location: 'Remote',
        category: 'Tech',
        salary: '$50k'
    };
    const { ok, data } = await apiCreateJob(jobData);
    console.log('[Jobs Route Connection - Post Job]:', data);
    return { ok, data };
}


// deleteJob(jobId)
// Uses apiDeleteJob from api.js
async function deleteJob(jobId) {
    const { ok, data } = await apiDeleteJob(jobId);
    console.log('[Jobs Route Connection - Delete Job]:', data);
    return { ok, data };
}

