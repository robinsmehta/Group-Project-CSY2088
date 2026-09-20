// js/job-listing.js — Job Listings Page Logic
// Depends on: config.js, shared.js, api.js

document.addEventListener('DOMContentLoaded', () => {
    renderNavbar('jobs');

    loadInitialJobsAndFilters();

    document.getElementById('search-btn').addEventListener('click', () => loadJobs(1));
    document.getElementById('keyword-input').addEventListener('keydown', e => { if (e.key === 'Enter') loadJobs(1); });
    document.getElementById('location-input').addEventListener('keydown', e => { if (e.key === 'Enter') loadJobs(1); });

    document.querySelectorAll('.tag-pill').forEach(pill => {
        pill.addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('keyword-input').value = pill.textContent.trim();
            loadJobs(1);
        });
    });
});

async function loadInitialJobsAndFilters() {
    // Fetch all jobs (high per_page) to build sidebar filter counts, then load page 1.
    const { ok, data } = await apiGetJobs({ per_page: 1000 });
    const jobs = ok ? (data.jobs || (Array.isArray(data) ? data : [])) : [];
    buildFiltersFromJobs(jobs);
    loadJobs(1);
}

function buildFiltersFromJobs(jobs) {
    const catMap = new Map();
    const typeMap = new Map();
    let highestSalary = 0;

    function parseSalaryNumber(s) {
        if (!s) return null;
        const m = String(s).replace(/[,$\s]/g, '').match(/(\d+)/);
        return m ? Number(m[1]) : null;
    }

    jobs.forEach(j => {
        const c = (j.category || 'Unspecified').trim();
        catMap.set(c, (catMap.get(c) || 0) + 1);
        const t = (j.job_type || 'Other').trim();
        typeMap.set(t, (typeMap.get(t) || 0) + 1);
        const s = parseSalaryNumber(j.salary);
        if (s && s > highestSalary) highestSalary = s;
    });

    const catContainer = document.querySelector('.filter-section[data-filter="category"] .filter-options');
    const typeContainer = document.querySelector('.filter-section[data-filter="type"] .filter-options');
    if (catContainer) {
        catContainer.innerHTML = Array.from(catMap.entries()).map(([c, count]) => {
            const id = `cat-${cssSafe(c)}`;
            return `<label class="checkbox-label jobs-style-20e5a0"><div class="checkbox-left jobs-style-877e9a"><input type="checkbox" data-value="${escapeHtmlAttr(c)}" id="${id}" class="jobs-style-150e43"> ${escapeHtml(c)}</div><span class="count jobs-style-a837ea">${count}</span></label>`;
        }).join('');
    }
    if (typeContainer) {
        typeContainer.innerHTML = Array.from(typeMap.entries()).map(([t, count]) => {
            const id = `type-${cssSafe(t)}`;
            return `<label class="checkbox-label jobs-style-20e5a0"><div class="checkbox-left jobs-style-877e9a"><input type="checkbox" data-value="${escapeHtmlAttr(t)}" id="${id}" class="jobs-style-150e43"> ${escapeHtml(t)}</div><span class="count jobs-style-a837ea">${count}</span></label>`;
        }).join('');
    }

    document.querySelectorAll('.filter-options input[type="checkbox"]').forEach(cb => cb.addEventListener('change', () => loadJobs(1)));

    const slider = document.querySelector('.range-slider');
    const rangeValues = slider ? slider.nextElementSibling : null;
    if (slider) {
        const maxVal = highestSalary ? Math.ceil(highestSalary / 1000) * 1000 : 200000;
        slider.max = maxVal;
        slider.value = maxVal;
        if (rangeValues) {
            const mid = Math.round(Number(slider.value) / 1000);
            const span = rangeValues.querySelector('span:nth-child(2)');
            if (span) span.textContent = `$${mid}k`;
        }
        slider.addEventListener('input', () => {
            if (rangeValues) {
                const mid = Math.round(Number(slider.value) / 1000);
                const span = rangeValues.querySelector('span:nth-child(2)');
                if (span) span.textContent = `$${mid}k`;
            }
        });
        slider.addEventListener('change', () => loadJobs(1));
    }

    function cssSafe(s) { return String(s).replace(/[^a-z0-9]+/gi, '-').toLowerCase(); }
    function escapeHtmlAttr(s) { return String(s).replace(/"/g, '&quot;'); }
}

async function loadJobs(page = 1) {
    const keyword  = document.getElementById('keyword-input').value.trim();
    const location = document.getElementById('location-input').value.trim();
    const grid     = document.getElementById('jobs-grid');
    const count    = document.getElementById('results-count');
    const paginationEl = document.querySelector('.pagination');

    grid.innerHTML = `<div class="jobs-style-4991c0">Loading…</div>`;

    const selectedCategories = Array.from(document.querySelectorAll('.filter-section[data-filter="category"] .filter-options input[type="checkbox"]'))
        .filter(i => i.checked)
        .map(i => i.dataset.value);

    const selectedJobTypes = Array.from(document.querySelectorAll('.filter-section[data-filter="type"] .filter-options input[type="checkbox"]'))
        .filter(i => i.checked)
        .map(i => i.dataset.value);

    const salarySlider = document.querySelector('.range-slider');
    const maxSalary = salarySlider ? Number(salarySlider.value) : null;

    const { ok, data } = await apiGetJobs({ keyword, location, page, per_page: 10 });

    if (!ok || !data) {
        grid.innerHTML = `<div class="jobs-style-4991c0">Could not load jobs. Make sure the backend is running.</div>`;
        count.textContent = 'No jobs found';
        if (paginationEl) paginationEl.innerHTML = '';
        return;
    }

    const allJobs    = data.jobs || (Array.isArray(data) ? data : []);
    const totalPages  = data.total_pages || 1;
    const totalCount  = data.count       || allJobs.length;
    const currentPage = data.page        || page;

    function parseSalaryNumber(s) {
        if (!s) return null;
        const m = String(s).replace(/[,$\s]/g, '').match(/(\d+)/);
        return m ? Number(m[1]) : null;
    }

    // Apply client-side filters (category / type / salary) on the returned page slice
    const filtered = allJobs.filter(job => {
        if (selectedCategories.length) {
            const jobCat = (job.category || 'Unspecified').trim();
            const matchCat = selectedCategories.some(c => jobCat.toLowerCase().includes((c || '').toLowerCase()));
            if (!matchCat) return false;
        }
        if (selectedJobTypes.length) {
            const jt = (job.job_type || 'Other').trim();
            const matchType = selectedJobTypes.some(t => jt.toLowerCase().includes((t || '').toLowerCase()));
            if (!matchType) return false;
        }
        if (maxSalary) {
            const sVal = parseSalaryNumber(job.salary);
            if (sVal === null) return true;
            if (sVal > maxSalary) return false;
        }
        return true;
    });

    if (filtered.length === 0) {
        grid.innerHTML = `<div class="jobs-style-4991c0">No jobs match your search criteria.</div>`;
        count.textContent = '0 Jobs Found';
        if (paginationEl) paginationEl.innerHTML = '';
        return;
    }

    count.textContent = `Showing ${filtered.length} of ${totalCount} Job${totalCount !== 1 ? 's' : ''}`;
    grid.innerHTML = filtered.map(job => buildListingCard(job)).join('');

    // -----------------------------------------------------------------------
    // Re-render pagination buttons — same ellipsis pattern as user-directory
    // -----------------------------------------------------------------------
    if (paginationEl) {
        const pages = [];
        for (let i = 1; i <= Math.min(3, totalPages); i++) pages.push(i);
        if (totalPages > 3) pages.push('...', totalPages);

        const prevDisabled = currentPage <= 1 ? 'disabled' : '';
        const nextDisabled = currentPage >= totalPages ? 'disabled' : '';

        let html = `<button class="page-btn" onclick="loadJobs(${currentPage - 1})" ${prevDisabled}>&lt;</button>`;

        html += pages.map(p => {
            if (p === '...') return `<span style="padding:0 4px;color:var(--color-text-muted,#9CA3AF)">…</span>`;
            const isActive = p === currentPage;
            return `<button class="page-btn${isActive ? ' active' : ''}" onclick="loadJobs(${p})">${p}</button>`;
        }).join('');

        html += `<button class="page-btn" onclick="loadJobs(${currentPage + 1})" ${nextDisabled}>&gt;</button>`;

        paginationEl.innerHTML = html;
    }
}

function buildListingCard(job) {
    const company  = escapeHtml(job.company_name || 'Unknown Company');
    const location = escapeHtml(job.location    || 'Not specified');
    const posted   = timeAgo(job.created_at);
    const matchBadge = typeof computeSkillMatchBadge === 'function' ? computeSkillMatchBadge(job.skills) : '';

    // Format salary or fallback
    const salaryText = job.salary ? escapeHtml(job.salary) : 'Salary undisclosed';

    return `
        <div class="job-card jobs-style-f6e458">
            <div>
                <!-- Title & Time -->
                <div class="jobs-style-77472d">
                    <h4 class="jobs-style-598323">${escapeHtml(job.title)}</h4>
                    <div class="jobs-style-fc029c">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                        ${posted}
                    </div>
                </div>

                <!-- Company & Location -->
                <div class="jobs-style-cbc0b4">${company}</div>
                <div class="jobs-style-9d8feb">${location}</div>

                <!-- Job Type Badge & Match Badge -->
                <div class="jobs-style-1265ee" style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                    ${job.job_type ? `<span class="jobs-style-668e21">${escapeHtml(job.job_type)}</span>` : ''}
                    ${matchBadge}
                </div>
            </div>

            <!-- Footer: Salary & Apply -->
            <div class="jobs-style-668074">
                <span class="jobs-style-f777da">${salaryText}</span>
                <a href="detail.html?id=${job.id}" class="jobs-style-872ee8" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">Apply Now</a>
            </div>
        </div>`;
}

function escapeHtml(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

function timeAgo(isoStr) {
    if (!isoStr) return 'Recently';
    const diff = Date.now() - new Date(isoStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60)  return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24)   return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
}
