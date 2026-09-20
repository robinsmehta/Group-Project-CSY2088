// js/job-detail.js — Job Details Page Logic
// Depends on: config.js, shared.js, api.js

let currentJobId = null;

document.addEventListener('DOMContentLoaded', async () => {
    const modal = document.getElementById('apply-modal');
    renderNavbar('jobs');

    if (modal) modal.style.display = 'none';

    const params = new URLSearchParams(window.location.search);
    currentJobId = params.get('id');

    if (!currentJobId) {
        const headerContent = document.getElementById('header-content');
        if (headerContent) headerContent.innerHTML = '<p class="jobs-style-fe25f4">No job ID specified.</p>';
        return;
    }

    const { ok, data } = await apiGetJob(currentJobId);
    const job = data?.job || null;

    if (!ok || !job || !job.id) {
        const headerContent = document.getElementById('header-content');
        if (headerContent) headerContent.innerHTML = '<p class="jobs-style-fe25f4">Job not found or has been removed.</p>';
        return;
    }

    renderJobDetail(job);

    const currentUser = getLoggedInUser();
    if (currentUser && currentUser.role === 'user') {
        const { ok: mok, data: mdata } = await apiGetMyApplications();
        const alreadyApplied = mok && Array.isArray(mdata.applications) &&
            mdata.applications.some(a => String(a.job_id) === String(currentJobId));
        if (alreadyApplied) {
            const btn = document.getElementById('open-apply-btn');
            if (btn) {
                btn.textContent = '✓ Already Applied';
                btn.disabled = true;
                btn.style.background = '#F3F4F6';
                btn.style.color = '#111827';
            }
        }
    }

    const closeBtn = document.getElementById('close-modal');
    if (closeBtn) closeBtn.addEventListener('click', () => { if (modal) modal.style.display = 'none'; });
    if (modal) modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });

    const applyForm = document.getElementById('apply-form');
    if (applyForm) {
        applyForm.addEventListener('submit', async (e) => {
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

            if (errDiv) errDiv.style.display = 'none';
            if (btn) {
                btn.disabled = true;
                btn.textContent = 'Submitting…';
            }

            const { ok: aok, data: adata } = await apiApplyToJob(currentJobId, resumeFile);

            if (aok) {
                if (modal) modal.style.display = 'none';
                showToast('Application submitted successfully!', 'success');
                // Update button on page
                const mainBtn = document.getElementById('open-apply-btn');
                if (mainBtn) {
                    mainBtn.textContent = '✓ Already Applied';
                    mainBtn.disabled = true;
                    mainBtn.style.background = '#F3F4F6';
                    mainBtn.style.color = '#111827';
                }
            } else {
                const msg = adata.error || adata.message || 'Failed to submit application.';
                if (errDiv) {
                    errDiv.textContent = msg;
                    errDiv.style.display = 'block';
                }
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = 'Submit Application';
                }
            }
        });
    }
});

function renderJobDetail(job) {
    const esc = (s) => { const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; };
    const postedAgo = timeAgo(job.created_at);
    const matchBadge = typeof computeSkillMatchBadge === 'function' ? computeSkillMatchBadge(job.skills) : '';

    document.title = `Job Portal — ${job.title || 'Job Details'}`;
    const postedDateEl = document.getElementById('header-posted-date');
    if (postedDateEl) postedDateEl.textContent = `POSTED ${postedAgo}`;

    // Header
    const headerContent = document.getElementById('header-content');
    if (headerContent) {
        headerContent.innerHTML = `
            <div class="jobs-style-f4b389">${esc(job.company_name || 'Unknown Company')}</div>
            <h1 class="jobs-style-2e5e62" style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                ${esc(job.title)}
                ${matchBadge}
            </h1>
            
            <div class="jobs-style-c4d0e1">
                <div class="jobs-style-e4b265">
                    <span class="jobs-style-2567d8">JOB TYPE</span>
                    <span class="jobs-style-3d896a">${esc(job.job_type || 'Full-time')}</span>
                </div>
                <div class="jobs-style-e4b265">
                    <span class="jobs-style-2567d8">LOCATION</span>
                    <span class="jobs-style-3d896a">${esc(job.location || 'Not specified')}</span>
                </div>
                <div class="jobs-style-e4b265">
                    <span class="jobs-style-2567d8">COMPENSATION</span>
                    <span class="jobs-style-3d896a">${esc(job.salary || 'Competitive')}</span>
                </div>
            </div>
        `;
    }

    // Description body
    let descHtml = (job.description || '').split('\n').filter(l => l.trim()).map(l => {
        const line = esc(l.trim());
        if (line.startsWith('- ') || line.startsWith('• ')) {
            return `<li class="jobs-style-b187d3">${line.substring(2)}</li>`;
        }
        return `<p class="jobs-style-da8c98">${line}</p>`;
    }).join('');
    
    // Formatting lists
    descHtml = descHtml.replace(/<\/li><li/g, '</li><li');
    if (descHtml.includes('<li')) {
        descHtml = descHtml.replace(/(<li.*<\/li>)/s, '<ul class="jobs-style-1d78b2">$1</ul>');
    }

    // Skills rendering
    let skillsHtml = '';
    if (job.skills && job.skills.trim()) {
        const skillTags = job.skills.split(',').map(s => s.trim()).filter(Boolean);
        if (skillTags.length > 0) {
            const pills = skillTags.map(skill => `<span class="skill-pill" style="display:inline-block; margin:4px 6px 4px 0; padding:6px 14px; background:#EEF2FF; color:#4F46E5; border:1px solid #C7D2FE; border-radius:20px; font-size:13px; font-weight:500;">${esc(skill)}</span>`).join('');
            skillsHtml = `
                <div style="margin-top: 28px; padding-top: 24px; border-top: 1px solid #E5E7EB;">
                    <h3 class="jobs-style-ce9cb6" style="margin-bottom: 12px;">Required Skills</h3>
                    <div class="skills-list">${pills}</div>
                </div>
            `;
        }
    }

    const card = document.getElementById('job-content-card');
    if (card) card.style.display = 'block';
    const descContent = document.getElementById('job-description-content');
    if (descContent) {
        descContent.innerHTML = `
            <h3 class="jobs-style-ce9cb6">About the Role</h3>
            ${descHtml || '<p class="jobs-style-5cfcf4">No description provided.</p>'}
            ${skillsHtml}
        `;
    }

    const openApplyBtn = document.getElementById('open-apply-btn');
    if (openApplyBtn) {
        openApplyBtn.addEventListener('click', () => {
            const user = getLoggedInUser();
            if (!user || user.role !== 'user') {
                showToast('Please log in as a job seeker to apply.', 'warning');
                setTimeout(() => window.location.href = '../auth/login.html', 1000);
                return;
            }
            const modal = document.getElementById('apply-modal');
            if (modal) modal.style.display = 'flex';
        });
    }
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
