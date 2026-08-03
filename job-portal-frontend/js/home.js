// js/home.js — Home page logic
// Depends on: config.js, shared.js

document.addEventListener('DOMContentLoaded', () => {
    renderNavbar('home');
    renderFooter();
    setHomeCtaLinks();
    loadHomeFeaturedJobs();
    renderCategories();
    wireHeroSearch();
    loadStats();
});

function setHomeCtaLinks() {
    document.getElementById('hero-browse-jobs')?.setAttribute('href', resolveSitePath('jobs/listing.html'));
    document.getElementById('view-all-jobs')?.setAttribute('href', resolveSitePath('jobs/listing.html'));
    document.getElementById('role-seeker-link')?.setAttribute('href', `${resolveSitePath('auth/register.html')}?role=seeker`);
    document.getElementById('role-employer-link')?.setAttribute('href', `${resolveSitePath('auth/register.html')}?role=employer`);
}

// Featured Jobs

async function loadHomeFeaturedJobs() {
    const grid = document.getElementById('featured-jobs-grid');
    if (!grid) return;

    try {
        const { ok, data } = await apiGetJobs();
        const jobs = ok ? (Array.isArray(data) ? data : (data.jobs || [])) : [];

        if (!jobs.length) {
            grid.innerHTML = `<div class="loading-message">No jobs available right now. Check back soon.</div>`;
            return;
        }

        grid.innerHTML = jobs.slice(0, 6).map(job => buildJobCard(job)).join('');
    } catch (err) {
        grid.innerHTML = `<div class="loading-message">Could not load jobs. Make sure the backend is running.</div>`;
        console.error('[Home] Error loading jobs:', err);
    }
}

function buildJobCard(job) {
    const initials = (job.company_name || job.company || 'C').charAt(0).toUpperCase();
    const salary   = job.salary    ? `<span class="job-salary">${job.salary}</span>` : '';
    const jobType  = job.job_type  ? `<span class="badge badge-${(job.job_type || '').toLowerCase().replace(/\s/g, '')}">${job.job_type}</span>` : '';
    const posted   = timeAgo(job.created_at || job.posted_date || '');

    return `
        <article class="job-card" onclick="window.location.href='${resolveSitePath(`jobs/detail.html`)}?id=${job.id}'" role="button" tabindex="0">
            <div class="job-card-top">
                <div class="job-company-logo">${initials}</div>
                <button class="job-bookmark" title="Save job" onclick="event.stopPropagation()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
                    </svg>
                </button>
            </div>
            <div class="job-card-body">
                <div class="job-title">${job.title || 'Untitled Role'}</div>
                <div class="job-company">${job.company_name || job.company || 'Company'}</div>
            </div>
            <div class="job-meta">
                ${job.location ? `
                    <span class="job-meta-item">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
                        </svg>
                        ${job.location}
                    </span>` : ''}
                ${job.category ? `
                    <span class="job-meta-item">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                        </svg>
                        ${job.category}
                    </span>` : ''}
            </div>
            <div class="job-card-footer">
                ${salary}
                <div class="job-type-tags">${jobType}</div>
                <span class="job-date">${posted}</span>
                <a href="${resolveSitePath(`jobs/detail.html`)}?id=${job.id}" class="arrow-btn" aria-label="View job details">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                </a>
            </div>
        </article>
    `;
}

// Stats

async function loadStats() {
    try {
        const { ok, data } = await apiGetJobs();
        const jobs = ok ? (Array.isArray(data) ? data : (data.jobs || [])) : [];

        const statJobs = document.getElementById('stat-jobs');
        const statCompanies = document.getElementById('stat-companies');

        if (statJobs) statJobs.textContent = jobs.length + '+';

        if (statCompanies) {
            const uniqueCompanies = new Set(jobs.map(j => j.company_name || j.company).filter(Boolean));
            statCompanies.textContent = uniqueCompanies.size + '+';
        }
    } catch (_) {}
}

// Category Grid

function renderCategories() {
    const grid = document.getElementById('categories-grid');
    if (!grid) return;

    const categories = [
        { label: 'Engineering',   icon: 'code',      query: 'Engineering' },
        { label: 'Design',        icon: 'pen-tool',  query: 'Design' },
        { label: 'Marketing',     icon: 'bar-chart', query: 'Marketing' },
        { label: 'Finance',       icon: 'dollar',    query: 'Finance' },
        { label: 'Healthcare',    icon: 'heart',     query: 'Healthcare' },
        { label: 'Education',     icon: 'book',      query: 'Education' },
        { label: 'Data Science',  icon: 'database',  query: 'Data' },
        { label: 'Customer Service', icon: 'headphones', query: 'Customer' },
    ];

    const iconSvg = {
        'code':       '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
        'pen-tool':   '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/></svg>',
        'bar-chart':  '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>',
        'dollar':     '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
        'heart':      '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
        'book':       '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
        'database':   '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
        'headphones': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>',
    };

    grid.innerHTML = categories.map(cat => `
        <a href="${resolveSitePath('jobs/listing.html')}?category=${encodeURIComponent(cat.query)}" class="category-card">
            <div class="category-icon">${iconSvg[cat.icon]}</div>
            <div class="category-info">
                <h4>${cat.label}</h4>
                <span>Browse openings</span>
            </div>
        </a>
    `).join('');
}

// Hero Search

function wireHeroSearch() {
    const btn      = document.getElementById('hero-search-btn');
    const keyword  = document.getElementById('hero-keyword');
    const location = document.getElementById('hero-location');

    function doSearch() {
        const kw  = keyword?.value.trim();
        const loc = location?.value.trim();
        const params = new URLSearchParams();
        if (kw)  params.set('keyword', kw);
        if (loc) params.set('location', loc);
        window.location.href = `${resolveSitePath('jobs/listing.html')}?${params.toString()}`;
    }

    btn?.addEventListener('click', doSearch);
    keyword?.addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });
    location?.addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });
}
