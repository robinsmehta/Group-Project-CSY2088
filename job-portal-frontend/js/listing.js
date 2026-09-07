// Job listing page logic.
// Depends on: config.js, shared.js, api.js.

document.addEventListener('DOMContentLoaded', () => {
    renderNavbar('jobs');
    renderFooter();

    loadInitialJobsAndFilters();

    document.getElementById('search-btn').addEventListener('click', fetchAndRenderJobs);
    document.getElementById('keyword-input').addEventListener('keydown', e => { if (e.key === 'Enter') fetchAndRenderJobs(); });
    document.getElementById('location-input').addEventListener('keydown', e => { if (e.key === 'Enter') fetchAndRenderJobs(); });

    document.querySelectorAll('.tag-pill').forEach(pill => {
        pill.addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('keyword-input').value = pill.textContent.trim();
            fetchAndRenderJobs();
        });
    });
});

async function loadInitialJobsAndFilters() {
    const { ok, data } = await apiGetJobs();
    const jobs = ok ? (data.jobs || (Array.isArray(data) ? data : [])) : [];
    buildFiltersFromJobs(jobs);
    fetchAndRenderJobs();
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
            return `<label class="checkbox-label"><div class="checkbox-left"><input type="checkbox" data-value="${escapeHtmlAttr(c)}" id="${id}"> ${escapeHtml(c)}</div><span class="count">${count}</span></label>`;
        }).join('');
    }
    if (typeContainer) {
        typeContainer.innerHTML = Array.from(typeMap.entries()).map(([t, count]) => {
            const id = `type-${cssSafe(t)}`;
            return `<label class="checkbox-label"><div class="checkbox-left"><input type="checkbox" data-value="${escapeHtmlAttr(t)}" id="${id}"> ${escapeHtml(t)}</div><span class="count">${count}</span></label>`;
        }).join('');
    }

    document.querySelectorAll('.filter-options input[type="checkbox"]').forEach(cb => cb.addEventListener('change', fetchAndRenderJobs));

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
        slider.addEventListener('change', fetchAndRenderJobs);
    }

    function cssSafe(s) { return String(s).replace(/[^a-z0-9]+/gi, '-').toLowerCase(); }
    function escapeHtmlAttr(s) { return String(s).replace(/"/g, '&quot;'); }
}

async function fetchAndRenderJobs() {
    const keyword = document.getElementById('keyword-input').value.trim();
    const location = document.getElementById('location-input').value.trim();
    const grid = document.getElementById('jobs-grid');
    const count = document.getElementById('results-count');

    grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:60px 0;color:#6B7280;">Loading...</div>';

    const selectedCategories = Array.from(document.querySelectorAll('.filter-section[data-filter="category"] .filter-options input[type="checkbox"]'))
        .filter(i => i.checked)
        .map(i => i.dataset.value);
    const selectedJobTypes = Array.from(document.querySelectorAll('.filter-section[data-filter="type"] .filter-options input[type="checkbox"]'))
        .filter(i => i.checked)
        .map(i => i.dataset.value);
    const salarySlider = document.querySelector('.range-slider');
    const maxSalary = salarySlider ? Number(salarySlider.value) : null;

    const { ok, data } = await apiGetJobs({ keyword, location });
    const jobs = ok ? (data.jobs || (Array.isArray(data) ? data : [])) : null;

    function parseSalaryNumber(s) {
        if (!s) return null;
        const m = String(s).replace(/[,$\s]/g, '').match(/(\d+)/);
        return m ? Number(m[1]) : null;
    }

    const filtered = (jobs || []).filter(job => {
        if (selectedCategories.length) {
            const jobCat = (job.category || 'Unspecified').trim();
            if (!selectedCategories.some(c => jobCat.toLowerCase().includes((c || '').toLowerCase()))) return false;
        }
        if (selectedJobTypes.length) {
            const jt = (job.job_type || 'Other').trim();
            if (!selectedJobTypes.some(t => jt.toLowerCase().includes((t || '').toLowerCase()))) return false;
        }
        if (maxSalary) {
            const sVal = parseSalaryNumber(job.salary);
            if (sVal !== null && sVal > maxSalary) return false;
        }
        return true;
    });

    if (!ok || !jobs) {
        grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:60px 0;color:#6B7280;">Could not load jobs. Make sure the backend is running.</div>';
        count.textContent = 'No jobs found';
        return;
    }
    if (filtered.length === 0) {
        grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:60px 0;color:#6B7280;">No jobs match your search criteria.</div>';
        count.textContent = '0 Jobs Found';
        return;
    }

    count.textContent = `Showing ${filtered.length} Job${filtered.length !== 1 ? 's' : ''}`;
    grid.innerHTML = filtered.map(job => buildListingCard(job)).join('');
}

function buildListingCard(job) {
    const company = escapeHtml(job.company_name || 'Unknown Company');
    const location = escapeHtml(job.location || 'Not specified');
    const salary = job.salary ? `<span class="salary-amount">${escapeHtml(job.salary)}</span>` : '';
    const posted = timeAgo(job.created_at);
    const category = job.category ? `<span class="meta-tag">🏷 ${escapeHtml(job.category)}</span>` : '';
    const jobType = job.job_type ? `<span class="meta-tag">💼 ${escapeHtml(job.job_type)}</span>` : '';
    return `
        <div class="job-card">
            <div class="job-card-top">
                <h4 class="job-card-title">${escapeHtml(job.title)}</h4>
                <div class="job-card-company">${company} • ${location}</div>
                <div class="job-details-meta">${category}${jobType}<span class="meta-tag">🕒 ${posted}</span></div>
            </div>
            <div class="job-card-bottom">
                ${salary}
                <a href="detail.html?id=${job.id}" class="btn-apply">View &amp; Apply</a>
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
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
}
