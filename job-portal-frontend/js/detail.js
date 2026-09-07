// Job detail page logic.
// Depends on: config.js, shared.js, api.js.

let currentJobId = null;

document.addEventListener('DOMContentLoaded', async () => {
    renderNavbar('jobs');
    renderFooter();
    const modal = document.getElementById('apply-modal');
    if (!modal) return;
    modal.style.display = 'none';

    const params = new URLSearchParams(window.location.search);
    currentJobId = params.get('id');

    if (!currentJobId) {
        document.getElementById('header-content').innerHTML = '<p style="color:#DC2626;">No job ID specified.</p>';
        document.getElementById('job-content').innerHTML = '';
        document.getElementById('apply-sidebar').innerHTML = '';
        return;
    }

    const { ok, data } = await apiGetJob(currentJobId);
    const job = data?.job || null;
    if (!ok || !job || !job.id) {
        document.getElementById('header-content').innerHTML = '<p style="color:#DC2626;">Job not found or has been removed.</p>';
        document.getElementById('job-content').innerHTML = '';
        document.getElementById('apply-sidebar').innerHTML = '';
        return;
    }

    renderJobDetail(job, modal);

    const currentUser = getLoggedInUser();
    if (currentUser && currentUser.role === 'user') {
        const { ok: applicationsOk, data: applicationsData } = await apiGetMyApplications();
        const alreadyApplied = applicationsOk && Array.isArray(applicationsData.applications) &&
            applicationsData.applications.some(a => String(a.job_id) === String(currentJobId));
        if (alreadyApplied) {
            const btn = document.getElementById('open-apply-btn');
            if (btn) {
                btn.textContent = 'Already Applied';
                btn.disabled = true;
                btn.classList.add('btn-already-applied');
            }
        }
    }

    document.getElementById('close-modal').addEventListener('click', () => modal.style.display = 'none');
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });

    document.getElementById('apply-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const user = getLoggedInUser();
        if (!user || user.role !== 'user') {
            showToast('Please log in as a job seeker to apply.', 'error');
            setTimeout(() => window.location.href = '../auth/login.html', 1000);
            return;
        }
        const resumeFile = document.getElementById('resume-file').files[0];
        const errDiv = document.getElementById('apply-error');
        const btn = document.getElementById('apply-submit');
        errDiv.style.display = 'none';
        btn.disabled = true;
        btn.textContent = 'Submitting...';

        const { ok: applyOk, data: applyData } = await apiApplyToJob(currentJobId, resumeFile);
        if (applyOk) {
            modal.style.display = 'none';
            showToast('Application submitted successfully!', 'success');
        } else {
            errDiv.textContent = applyData.error || applyData.message || 'Failed to submit application.';
            errDiv.style.display = 'block';
            btn.disabled = false;
            btn.textContent = 'Submit Application';
        }
    });
});

function renderJobDetail(job, modal) {
    const esc = (s) => { const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; };
    const initials = (job.company_name || 'C').substring(0, 2).toUpperCase();
    const postedAgo = timeAgo(job.created_at);

    document.getElementById('header-content').innerHTML = `
        <div class="company-badge-icon">${initials}</div>
        <h1 class="job-title">${esc(job.title)}</h1>
        <div class="company-tags">
            <span class="tag-item">${esc(job.company_name || 'Unknown Company')}</span>
            <span class="tag-item">${esc(job.location || 'Not specified')}</span>
            ${job.category ? `<span class="tag-item">${esc(job.category)}</span>` : ''}
        </div>
        <div class="header-pills">
            <div class="pill-card"><label>POSTED</label><span>${postedAgo}</span></div>
            ${job.salary ? `<div class="pill-card"><label>SALARY</label><span>${esc(job.salary)}</span></div>` : ''}
        </div>
    `;

    const descHtml = (job.description || '').split('\n').filter(l => l.trim()).map(l => `<p>${esc(l)}</p>`).join('');
    document.getElementById('job-content').innerHTML = `
        <div class="section-block">
            <h3>About the Role</h3>
            ${descHtml || '<p>No description provided.</p>'}
        </div>
    `;

    document.getElementById('apply-sidebar').innerHTML = `
        <button class="btn-apply-now" id="open-apply-btn">Apply Now</button>
        <div class="sidebar-meta-list">
            <div class="sidebar-meta-item"><label>LOCATION</label><span>${esc(job.location || 'Not specified')}</span></div>
            ${job.salary ? `<div class="sidebar-meta-item"><label>SALARY</label><span>${esc(job.salary)}</span></div>` : ''}
            ${job.category ? `<div class="sidebar-meta-item"><label>CATEGORY</label><span>${esc(job.category)}</span></div>` : ''}
            <div class="sidebar-meta-item"><label>COMPANY</label><span>${esc(job.company_name || 'Unknown')}</span></div>
            <div class="sidebar-meta-item"><label>POSTED</label><span>${postedAgo}</span></div>
        </div>
    `;

    document.getElementById('apply-job-title').textContent = job.title;
    document.getElementById('open-apply-btn').addEventListener('click', () => {
        const user = getLoggedInUser();
        if (!user || user.role !== 'user') {
            showToast('Please log in as a job seeker to apply.', 'warning');
            setTimeout(() => window.location.href = '../auth/login.html', 1000);
            return;
        }
        modal.style.display = 'flex';
    });
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
